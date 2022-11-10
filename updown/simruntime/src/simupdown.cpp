#include "simupdown.h"
#include <cstdio>
#include <cstdlib>
#include <fcntl.h>
#include <sys/mman.h>
#include <vector>
#include <utility>
#include "upstream_pyintf.hh"

namespace UpDown {

void SimUDRuntime_t::initMemoryArrays() {
  // Initializing arrays containning mapped memory
  UPDOWN_INFOMSG("Allocating %lu bytes for mapped memory",
                 this->MachineConfig.MapMemSize);
  MappedMemory = new uint8_t[this->MachineConfig.MapMemSize];
  uint64_t size_spmem = this->MachineConfig.CapNumUDs *
                        this->MachineConfig.CapNumLanes *
                        this->MachineConfig.CapSPmemPerLane;
  UPDOWN_INFOMSG("Allocating %lu bytes for Scratchpad memory", size_spmem);
  ScratchpadMemory = new uint8_t[size_spmem];

  uint64_t size_control = this->MachineConfig.CapNumUDs *
                          this->MachineConfig.CapNumLanes *
                          this->MachineConfig.CapControlPerLane;
  UPDOWN_INFOMSG("Allocating %lu bytes for control", size_control);
  ControlMemory = new uint8_t[size_control];

  // Changing the base locations for the simulated memory regions
  this->MachineConfig.MapMemBase = reinterpret_cast<uint64_t>(MappedMemory);
  UPDOWN_INFOMSG("MapMemBase changed to 0x%lX", this->MachineConfig.MapMemBase);
  this->MachineConfig.UDbase = reinterpret_cast<uint64_t>(ScratchpadMemory);
  this->MachineConfig.SPMemBase = reinterpret_cast<uint64_t>(ScratchpadMemory);
  UPDOWN_INFOMSG("SPMemBase and UDbase changed to 0x%lX",
                 this->MachineConfig.SPMemBase);
  this->MachineConfig.ControlBase = reinterpret_cast<uint64_t>(ControlMemory);
  UPDOWN_INFOMSG("ControlBase changed to 0x%lX",
                 this->MachineConfig.ControlBase);
  // ReInit Memory Manager with new machine configuration
  reset_memory_manager();
}

void SimUDRuntime_t::initPythonInterface(EmulatorLogLevel printLevel) {
  upstream_pyintf = new Upstream_PyIntf(MachineConfig.NumLanes, programFile,
                                        programName, simulationDir, 0,
                                        MachineConfig.SPBankSize, LogFileName);

  // Get UPDOWN_SIM_ITERATIONS from env variable
  if (char *EnvStr = getenv("UPDOWN_SIM_ITERATIONS"))
      max_sim_iterations = std::stoi(EnvStr);
  UPDOWN_INFOMSG("Running with UPDOWN_SIM_ITERATIONS = %d", max_sim_iterations);

  // This creates a set of files used to communicate with the python word
  // Each lane must have a file. The emulator class uses the same files to
  // read and write data.
  int *fd = new int[MachineConfig.NumLanes];

  sendmap = new uint32_t *[MachineConfig.NumLanes];
  for (unsigned int i = 0; i < MachineConfig.NumLanes; i++) {
    fd[i] = -1;
    std::string file_name = "./lane" + std::to_string(i) + "_send.txt";
    if ((fd[i] = open(file_name.c_str(), O_RDWR, 0)) == -1) {
      UPDOWN_ERROR("unable to open %s", file_name.c_str());
      exit(EXIT_FAILURE);
    }
    sendmap[i] =
        (uint32_t *)mmap(NULL /*addr*/, 262144 * sizeof(uint32_t) /*lenght*/,
                         PROT_READ | PROT_WRITE /*prot*/, MAP_SHARED /*flags*/,
                         fd[i] /*file_descriptor*/, 0 /*offset*/);

    if (sendmap[i] == MAP_FAILED) {
      UPDOWN_ERROR("SendMap Failed");
      exit(EXIT_FAILURE);
    }
  }
  upstream_pyintf->set_print_level(printLevel);

  delete fd;
}



void SimUDRuntime_t::send_event(event_t ev) {
  // Perform the regular access. This will have no effect
  UDRuntime_t::send_event(ev);
  if (!python_enabled) return;

  if (ev.get_NumOperands() != 0) {
    for (uint8_t i = 0; i < ev.get_NumOperands() + 1; i++)
      upstream_pyintf->insert_operand(ev.get_OperandsData()[i],
                                      ev.get_LaneId());
  } else {
    upstream_pyintf->insert_operand(0, ev.get_LaneId());
  }
  upstream_pyintf->insert_event(ev.get_EventWord(), ev.get_NumOperands(),
                                ev.get_LaneId());
}


void SimUDRuntime_t::executeSingleLane(uint8_t ud_id, uint8_t lane_num) {
  UPDOWN_INFOMSG("Executing a new event in lane %d. events left = %d", lane_num,
                  upstream_pyintf->getEventQ_Size(lane_num));

  emulator_stats stats;
  int exec_state = upstream_pyintf->execute(0, &stats, lane_num);
  UPDOWN_INFOMSG("C++ Process executed python process - Returned %d - events left %d",
                  exec_state, upstream_pyintf->getEventQ_Size(lane_num));

  // Execution_state is useful for messages to communicate with memory.
  // exec_state is:
  //   -1    -> Yeld terminate
  //   0     -> Yeld without messages to send
  //   N > 0 -> Yeld with N messages to send. (N also available in
  //   sendmap[lane][0] below)
  if (exec_state > 0 || ((exec_state == -1) && (stats.num_sends > 0))) {
    uint32_t numsend = sendmap[lane_num][0];
    UPDOWN_INFOMSG("Lane: %d Messages to be sent - numMessages :%d",
                    lane_num, numsend);

    // Variable to manage the offset within the sendmap memory mapped file
    int offset = 1;

    // send out requests to memory for the size specified
    for (int i = 0; i < numsend; i++) {
      uint32_t lane_id; // Lane ID for continuation
      uint32_t sevent;  // Dest Event
      uint64_t sdest;   // Dest Addr / Lane Num
      uint32_t scont;   // Continuation Word
      uint32_t ssize;   // Size in bytes
      uint32_t smode_0; // Mode - lane/mem
      uint32_t smode_1; // Mode - return to same lane?
      uint32_t smode_2; // Mode - load/store

      uint32_t mode = sendmap[lane_num][offset++];
      smode_0 = (mode & 0x1);
      smode_1 = (mode & 0x2) >> 1;
      smode_2 = (mode & 0x4) >> 2;
      UPDOWN_INFOMSG("Send Mode: mode:%d, 0:%d, 1:%d, 2:%d", mode, smode_0,
                      smode_1, smode_2);

      uint32_t sm_cycle =
          sendmap[lane_num][offset++]; //[8*i+2]; Not used here

      sevent = sendmap[lane_num][offset++]; //[8*i+3];

      // Depending on smode_0, we determine the direction of the memory access
      if (smode_0 == 0) { // DRAM Memory bound
        // Destination address is split in two since the UpDown address space
        // is 32 bits
        uint64_t lower = sendmap[lane_num][offset++]; //[8*i+5];
        uint64_t upper = sendmap[lane_num][offset++]; //[8*i+4];
        sdest = (lower & 0xffffffff) | ((upper << 32) & 0xffffffff00000000);
        UPDOWN_INFOMSG("Memory Bound Load: %d, Store: %d", !smode_2,
                        smode_2);
        UPDOWN_INFOMSG("Send Dest: %lX, Upper: %lX, Lower: %lX", sdest,
                        upper, lower);
      } else { // Scratchpad Memory Bound to another lane
        sdest = sendmap[lane_num][offset++];         //[8*i+4];
        uint32_t temp = sendmap[lane_num][offset++]; //[8*i+5];
        UPDOWN_INFOMSG("Send Lane: %d, Temp: %d", sdest, temp);
        UPDOWN_ERROR_IF(sdest != temp,
                        "Temp %d is not the same as the destination %d", sdest, temp);
      }

      // Get continuation and size
      scont = sendmap[lane_num][offset++]; //[8*i+6];
      ssize = sendmap[lane_num][offset++]; //[8*i+7];
      UPDOWN_INFOMSG("Send Cont: %d, Size: %d", scont, ssize);
      uint8_t sdata[ssize];
      uint32_t sdata_32[ssize / 4];

      // Obtain the data to be sent
      if (smode_0 == 1) {
        UPDOWN_INFOMSG("Send data to lane: %d, Size:%d", sdest, ssize);
        for (int j = 0; j < ssize / 4; j++) {
          sdata_32[j] = sendmap[lane_num][offset++]; //[8*i+8+j];
          UPDOWN_INFOMSG("data[%d]: %d", j, sdata_32[j]);
        }
      }
      // Store operation
      if (smode_2 == 1) {
        for (int j = 0; j < ssize; j += 4) {
          sdata[j] = (uint8_t)(sendmap[lane_num][offset + (j / 4)] &
                                0xff); //[8*i+8+(j/4)] & 0xff);
          sdata[j + 1] =
              (uint8_t)((sendmap[lane_num][offset + (j / 4)] & 0xff00) >> 8);
          sdata[j + 2] =
              (uint8_t)((sendmap[lane_num][offset + (j / 4)] & 0xff0000) >>
                        16);
          sdata[j + 3] =
              (uint8_t)((sendmap[lane_num][offset + (j / 4)] & 0xff000000) >>
                        24);
          offset++;
          UPDOWN_INFOMSG(
              "Send Data[0]: %d, Data:[1]: %d, Data[2]: %d, Data[3]: %d",
              sdata[j], sdata[j + 1], sdata[j + 2], sdata[j + 3]);
        }
      }
      // The continuation Lane ID
      lane_id = (scont & 0xff000000) >> 24;
      UPDOWN_INFOMSG("Send LaneID:%d", lane_id);

      if (!smode_0) { // memory bound messages
        // TODO: Send message to memory
        if (!smode_2) {
          // Loads
          UPDOWN_INFOMSG(
              "Loading from Mapped Memory address: %lX, size: %d", sdest,
              ssize);

          ptr_t src = reinterpret_cast<ptr_t>(sdest);
          ptr_t dst = reinterpret_cast<ptr_t>(sdata);
          std::memcpy(dst, src, ssize);
          uint32_t edata = 0;
          uint32_t fake_cont = 0xffffffff;
          upstream_pyintf->insert_operand(
              fake_cont, lane_id); // Insert continuation first!
          for (int i = 0; i < ssize / 4; i++) {
            edata = ((((sdata[4 * i + 3] & 0xff) << 24) & 0xff000000) |
                      (((sdata[4 * i + 2] & 0xff) << 16) & 0x00ff0000) |
                      (((sdata[4 * i + 1] & 0xff) << 8) & 0x0000ff00) |
                      (((sdata[4 * i] & 0xff)) & 0x000000ff));
            UPDOWN_INFOMSG("edata[%d]:%d", i, edata);
            upstream_pyintf->insert_operand(edata, lane_id);
          }
          upstream_pyintf->insert_event(scont, ssize / 4, lane_id);

        } else {
          // Stores
          UPDOWN_INFOMSG("Storing to Mapped Memory address: %lX, size: %d",
                          sdest, ssize);

          ptr_t src = reinterpret_cast<ptr_t>(sdata);
          ptr_t dst = reinterpret_cast<ptr_t>(sdest);
          std::memcpy(dst, src, ssize);

          uint32_t fake_cont = 0xffffffff;
          upstream_pyintf->insert_operand(
              fake_cont, lane_id); // Insert continuation first!
          upstream_pyintf->insert_event(scont, 0, lane_id);
        }
      } else {
        // Sending message to Scratchpad of another lane
        upstream_pyintf->insert_operand(scont,
                                        sdest); // insert continuation first
        UPDOWN_INFOMSG("LaneNum: %d, OB[0]: %d (0x%X)", sdest, scont, scont);
        for (int i = 0; i < ssize / 4; i++) {
          upstream_pyintf->insert_operand(
              sdata_32[i], sdest); // insert all collected operands
          UPDOWN_INFOMSG("LaneNum:%d, OB[%d]: %d (0x%X)", sdest, i + 1,
                          sdata_32[i], sdata_32[i]);
        }
        upstream_pyintf->insert_event(sevent, ssize / 4,
                                      sdest); // insert all collected operands
      }
    }
  }
  if (exec_state == -1) {
    UPDOWN_INFOMSG("Lane: %d Yielded and Terminated - Writing result now",
                    lane_num);
  }
}


void SimUDRuntime_t::start_exec(uint8_t ud_id, uint8_t lane_num) {
  // Perform the regular access. This will have no effect
  UDRuntime_t::start_exec(ud_id, lane_num);
  if (!python_enabled) return;

  // Then we do a round robin execution of all the lanes while
  // there is something executing
  bool something_exec;
  uint64_t num_iterations = 0;
  do {
    something_exec = false;
    for (int ud = 0; ud < this->MachineConfig.NumUDs; ud++) {
      for (int ln = 0; ln < this->MachineConfig.NumLanes; ln++) {
        if (upstream_pyintf->getEventQ_Size(ln) > 0) {
          UPDOWN_INFOMSG("Dumping Event Queue of lane %d", ln);
          upstream_pyintf->dumpEventQueue(ln);
          something_exec = true;
          executeSingleLane(ud, ln);
        }
      }
    }
  } while(something_exec && (!max_sim_iterations || ++num_iterations < max_sim_iterations));
}

void SimUDRuntime_t::t2ud_memcpy(void* data, uint64_t size, uint8_t ud_id,
                                 uint8_t lane_num, uint32_t offset) {
  UDRuntime_t::t2ud_memcpy(data, size, ud_id, lane_num, offset);
  if (!python_enabled) return;
  uint64_t addr = UDRuntime_t::get_lane_physical_memory(ud_id, lane_num, offset);
  ptr_t data_ptr = reinterpret_cast<word_t*>(data);
  for (int i = 0; i < size/sizeof(word_t); i++) {
    // Address is local
    upstream_pyintf->insert_scratch(addr, *data_ptr);
    addr += sizeof(word_t);
    data_ptr++;
  }
}

void SimUDRuntime_t::ud2t_memcpy(void* data, uint64_t size, uint8_t ud_id,
                                 uint8_t lane_num, uint32_t offset) {
  uint64_t addr = UDRuntime_t::get_lane_physical_memory(ud_id, lane_num, offset);
  uint64_t apply_offset = UDRuntime_t::get_lane_aligned_offset(ud_id, lane_num, offset);
  apply_offset /= sizeof(word_t);
  ptr_t base = BaseAddrs.spaddr + apply_offset;
  if (python_enabled)
    upstream_pyintf->read_scratch(addr, reinterpret_cast<uint8_t *>(base), size);
  UDRuntime_t::ud2t_memcpy(data, size, ud_id, lane_num, offset);
}

bool SimUDRuntime_t::test_addr(uint8_t ud_id, uint8_t lane_num, uint32_t offset,
                               word_t expected) {
  uint64_t addr = UDRuntime_t::get_lane_physical_memory(ud_id, lane_num, offset);
  uint64_t apply_offset = UDRuntime_t::get_lane_aligned_offset(ud_id, lane_num, offset);
  apply_offset /= sizeof(word_t);
  ptr_t base = BaseAddrs.spaddr + apply_offset;
  if (python_enabled) {
    start_exec(ud_id, lane_num);
    upstream_pyintf->read_scratch(addr, reinterpret_cast<uint8_t *>(base), sizeof(word_t));
  }
  UDRuntime_t::test_addr(ud_id, lane_num, offset, expected);
}

void SimUDRuntime_t::test_wait_addr(uint8_t ud_id, uint8_t lane_num,
                                    uint32_t offset, word_t expected) {

  while (!test_addr(ud_id, lane_num, offset, expected));
  // The bottom call will never hold since we're holding here
  UDRuntime_t::test_wait_addr(ud_id, lane_num, offset, expected);
}

} // namespace UpDown