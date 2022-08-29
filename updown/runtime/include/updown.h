/*
 * Copyright (c) 2021 University of Chicago and Argonne National Laboratory
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are
 * met: redistributions of source code must retain the above copyright
 * notice, this list of conditions and the following disclaimer;
 * redistributions in binary form must reproduce the above copyright
 * notice, this list of conditions and the following disclaimer in the
 * documentation and/or other materials provided with the distribution;
 * neither the name of the copyright holders nor the names of its
 * contributors may be used to endorse or promote products derived from
 * this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
 * "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
 * LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
 * A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
 * OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
 * SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
 * LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
 * DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
 * THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
 * OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 *
 * Author - Jose M Monsalve Diaz
 *
 */

#ifndef UPDOWN_H
#define UPDOWN_H
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <map>
#include <utility>

#include "debug.h"
#include "updown_config.h"

namespace UpDown {

// Depending of the word size we change the pointer type
#if DEF_WORD_SIZE == 4
typedef uint32_t word_t;
#elif DEF_WORD_SIZE == 8
typedef uint64_t word_t;
#else
#error Unknown default word size
#endif

typedef word_t *ptr_t;
static constexpr uint8_t ANY_THREAD = 0xFF;

/**
 * @brief Class that holds information about the operands.
 *
 * Contains a pointer to data and the number of operands.
 * data is an array of ptr_t, representing each word in the
 * operand buffer when copied.
 *
 *
 */
class operands_t {
private:
  // Number of operands 8 bits long. Up to 256 operands are allowed
  uint8_t NumOperands;
  // Pointer to the data to consider operands. Consecutive array of operands
  ptr_t Data;

public:
  /**
   * @brief Construct a new empty operands_t object
   *
   * Set the Data pointer to null and NumOperands to 0
   */
  operands_t() : NumOperands(0), Data(nullptr) {}

  /**
   * @brief Copy Constructor
   *
   * @param o other object
   */
  operands_t(const operands_t &o)
      : NumOperands(o.NumOperands),
        Data((ptr_t)malloc(sizeof(word_t) * (NumOperands + 1))) {
    // Copy the data
    if (NumOperands != 0)
      std::memcpy(o.Data, Data, sizeof(word_t) * (NumOperands + 1));
  }

  /**
   * @brief Copy Constructor
   *
   * @param o other object
   */
  operands_t(operands_t &&o) : NumOperands(o.NumOperands), Data(o.Data) {
    // Reset the other operand's pointer
    o.Data = nullptr;
  }

  /**
   * @brief Construct a new operands_t opbejct, setting the operands
   *
   * @param num Number of operaqnds
   * @param oper Operand value
   * @param cont Continuation event
   *
   * @todo This should avoid using memcpy
   */
  operands_t(uint8_t num, ptr_t oper = nullptr, word_t cont = 0)
      : NumOperands(num),
        Data((ptr_t)malloc(sizeof(word_t) *
                           (NumOperands + 1))) { // TODO: Avoid this malloc

    Data[0] = cont; // Fake continuation

    // TODO: This should be a memcpy?
    for (uint8_t i = 1; i < NumOperands + 1; i++)
      Data[i] = oper[i - 1];
  }

  /**
   * @brief Get the pointer to Data
   *
   * @return ptr_t pointer to data
   */
  ptr_t get_Data() { return Data; }

  /**
   * @brief Get the NumOperands
   *
   * @return uint8_t number of operands
   */
  uint8_t get_NumOperands() { return NumOperands; }

  ~operands_t() { delete Data; }
};

/**
 * @brief Contains information of an event in the UpDown
 *
 * This class constructs the information of the event word based on
 * each of its parameters. It also contains a pointer to the operands
 * that is used when sending the event
 *
 * @todo UpDown ID is not being used
 * @todo, event_t considers a 4 byte word size
 */
class event_t {
private:
  uint8_t UdId;       // UpDown ID
  uint8_t LaneId;     // Lane ID
  uint8_t ThreadId;   // Thread ID. ANY_THREAD for any thread
  uint8_t EventLabel; // Number representing the event label

  operands_t *Operands; // Operands to be sent with this event

  word_t EventWord; // Concatenated event word that contains all the fields

public:
  /**
   * @brief Construct a new empty event object
   *
   */
  event_t()
      : UdId(0), LaneId(0), ThreadId(0xFF), EventLabel(0), Operands(nullptr),
        EventWord(((LaneId << 24) & 0xff000000) |
                  ((ThreadId << 16) & 0xff0000) | ((0 << 8) & 0xff00) |
                  (EventLabel & 0xff)) {
    UPDOWN_INFOMSG("Creating a new event label = %d, lane_id = %d, "
                   "thread_id = %d, num_operands = %d, ev_word = %X",
                   EventLabel, LaneId, ThreadId, 0, EventWord);
  }

  /**
   * @brief Construct a new event_t object
   *
   * @param e_label
   * @param udid
   * @param lid
   * @param tid
   * @param operands
   */
  event_t(uint8_t e_label, uint8_t udid, uint8_t lid = 0,
          uint8_t tid = ANY_THREAD, operands_t *operands = nullptr)
      : UdId(udid), LaneId(lid), ThreadId(tid), EventLabel(e_label),
        Operands(operands),
        EventWord(
            ((LaneId << 24) & 0xff000000) | ((ThreadId << 16) & 0xff0000) |
            (((Operands != nullptr ? Operands->get_NumOperands() : 0) << 8) &
             0xff00) |
            (EventLabel & 0xff)) {
    UPDOWN_INFOMSG("Creating a new event label = %d, lane_id = %d, "
                   "thread_id = %d, num_operands = %d, ev_word = %X",
                   EventLabel, LaneId, ThreadId,
                   (Operands != nullptr) ? Operands->get_NumOperands() : 0,
                   EventWord);
  }

  /**
   * @brief Set the event word object with new values
   *
   * @param e_label the ID of the event in the updown
   * @param noperands the number of operands
   * @param lid Lane ID
   * @param tid Thread ID
   */
  void set_event(uint8_t e_label, uint8_t udid, uint8_t lid = 0,
                 uint8_t tid = ANY_THREAD, operands_t *operands = nullptr) {
    EventLabel = e_label;
    LaneId = lid;
    UdId = udid;
    ThreadId = tid;
    Operands = operands;
    EventWord =
        ((LaneId << 24) & 0xff000000) | ((ThreadId << 16) & 0xff0000) |
        (((Operands != nullptr ? Operands->get_NumOperands() : 0) << 8) &
         0xff00) |
        (EventLabel & 0xff);
    UPDOWN_INFOMSG("Setting the event word = %d, lane_id = %d, "
                   "thread_id = %d, num_operands = %d, ev_word = %X",
                   EventLabel, LaneId, ThreadId,
                   (Operands != nullptr) ? Operands->get_NumOperands() : 0,
                   EventWord);
  }

  word_t get_EventWord() { return EventWord; }
  operands_t *get_Operands() { return Operands; }
  void set_operands(operands_t *ops) { Operands = ops; }
  uint8_t get_UdId() { return UdId; }
  uint8_t get_LaneId() { return LaneId; }
  uint8_t get_ThreadId() { return ThreadId; }
  uint8_t get_EventLabel() { return EventLabel; }
  uint8_t get_NumOperands() {
    return (Operands != nullptr) ? Operands->get_NumOperands() : 0;
  }
  ptr_t get_OperandsData() {
    return (Operands != nullptr) ? Operands->get_Data() : nullptr;
  }
};

/**
 * @brief Structure containing the machine configuration.
 *
 * This structure can be used to change the parameters of the runtime, during
 * runtime construction.
 */

struct ud_machine_t {
  // Offsets for addrs space
  uint64_t MapMemBase = BASE_MAPPED_ADDR;         // Base address for memory map
  uint64_t UDbase = BASE_SPMEM_ADDR;              // Base address for upstream
  uint64_t SPMemBase = BASE_SPMEM_ADDR;           // ScratchPad Base address
  uint64_t ControlBase = BASE_CTRL_ADDR;          // Base for control operands
  uint64_t EventQueueOffset = EVENT_QUEUE_OFFSET; // Offset for Event Queues
  uint64_t OperandQueueOffset =
      OPERAND_QUEUE_OFFSET;                     // Offset for Operands Queues
  uint64_t StartExecOffset = START_EXEC_OFFSET; // Offset for Start Exec signal
  uint64_t LockOffset = LOCK_OFFSET;            // Offset for Lock signal

  // Machine config and capacities
  uint64_t CapNumUDs = NUM_UDS_CAPACITY;              // Max number of UpDowns
  uint64_t CapNumLanes = NUM_LANES_CAPACITY;          // Max number of UpDowns
  uint64_t CapSPmemPerLane = SPMEM_CAPACITY_PER_LANE; // Max bank size per lane
  uint64_t CapControlPerLane =
      CONTROL_CAPACITY_PER_LANE;     // Max Control Sigs and regs per lane
  uint64_t NumUDs = DEF_NUM_UDS;     // Number of UpDowns
  uint64_t NumLanes = DEF_NUM_LANES; // Number of lanes

  // Sizes for memories
  uint64_t MapMemSize = DEF_MAPPED_SIZE; // Mapped Memory size
  uint64_t SPBankSize =
      DEF_SPMEM_BANK_SIZE; // Local Momory (scratchpad) Bank Size
  uint64_t SPBankSizeWords =
      DEF_SPMEM_BANK_SIZE * DEF_WORD_SIZE; // LocalMemorySize in Words
};

/**
 * @brief Class containing the UpDown Runtime
 *
 * This class is the entry point of the UpDown runtime, it manages all
 * the necessary state, keeps track of pointers and memory allocation
 * and coordinates execution of code.
 *
 */
class UDRuntime_t {
private:
  /**
   * @brief Struct containing all the base addresses
   *
   * Base addresses are locations in memory where the
   * top to updown communication happens.
   *
   * ## Current Memory Structure
   * The memory is organized in two: Scratchpad memory and
   * Control mapped registers and queues
   *
   * ### Scratchpad memory address space
   * \verbatim
   *        MEMORY                     SIZE
   *   |--------------|  <-- Scratchpad Base Address
   *   |              |
   *   |   SPMEM UD0  |
   *   |              |
   *   |--------------|  <-- CapacityPerLane * CapacityNumLanes
   *   |              |
   *   |   SPMEM UD1  |
   *   |              |
   *   |--------------|  <-- 2 * CapacityPerLane * CapacityNumLanes
   *   |      ...     |
   *   |--------------|
   *   |              |
   *   |   SPMEM UDN  |
   *   |              |
   *   |--------------|  <-- NumUDs * CapacityPerLane * CapacityNumLanes
   * \endverbatim
   *
   * ### Scratchpad memory for 1 UD
   * \verbatim
   *        MEMORY                     SIZE
   *   |--------------|  <-- Scratchpad Base Address
   *   |              |
   *   |    Lane 0    |
   *   |              |
   *   |* * * * * * * |  <-- SPmem BankSize
   *   | * * * * * * *|    |
   *   |* * * * * * * |    | For expansion purposes
   *   | * * * * * * *|    |
   *   |--------------|  <-- CapacityPerLane
   *   |              |
   *   |    Lane 1    |
   *   |              |
   *   |* * * * * * * |  <-- CapacityPerLane + SPmem BankSize
   *   | * * * * * * *|    |
   *   |* * * * * * * |    | For expansion purposes
   *   | * * * * * * *|    |
   *   |--------------|  <-- 2 * CapacityPerLane
   *   |      ...     |
   *   |--------------|  <-- (NumLanes-1)*CapacityPerLane
   *   |              |
   *   |    Lane N    |
   *   |              |
   *   |* * * * * * * |  <-- (NumLanes-1)*CapacityPerLane + SPmem BankSize
   *   | * * * * * * *|    |
   *   |* * * * * * * |    | For expansion purposes
   *   | * * * * * * *|    |
   *   |--------------|  <-- (NumLanes) * CapacityPerLane
   *   | * * * * * * *|
   *   |* * * * * * * |   -|
   *   | * * * * * * *|    | For expansion purposes
   *   |* * * * * * * |   -|
   *   | * * * * * * *|
   *   |--------------|  <-- CapacityPerLane * CapacityNumLanes
   * \endverbatim
   *
   * ### Control signals memory address space
   * \verbatim
   *        MEMORY                     SIZE
   *   |--------------|  <-- Control Base Address
   *   |              |
   *   |  CONTROL UD0 |
   *   |              |
   *   |--------------|  <-- CapacityControlPerLane * CapacityNumLanes
   *   |              |
   *   |  CONTROL UD1 |
   *   |              |
   *   |--------------|  <-- 2 * CapacityControlPerLane * CapacityNumLanes
   *   |      ...     |
   *   |--------------|
   *   |              |
   *   |  CONTROL UD2 |
   *   |              |
   *   |--------------|  <-- NumUDs * CapacityControlPerLane * CapacityNumLanes
   * \endverbatim
   *
   * ### Scratchpad memory for 1 UD
   * \verbatim
   *        MEMORY                     SIZE
   *   |--------------|  <-- Control Base Address
   *   |    Lane 0    |
   *   |  Event Queue |
   *   | Oprnds Queue |
   *   |  Start Exec  |
   *   |     Lock     |
   *   |* * * * * * * |   -|
   *   | * * * * * * *|    |
   *   |* * * * * * * |    | For expansion purposes
   *   | * * * * * * *|    |
   *   |--------------|  <-- CapacityControlPerLane
   *   |    Lane 1    |
   *   |  Event Queue |
   *   | Oprnds Queue |
   *   |  Start Exec  |
   *   |     Lock     |
   *   |* * * * * * * |   -|
   *   | * * * * * * *|    |
   *   |* * * * * * * |    | For expansion purposes
   *   | * * * * * * *|    |
   *   |--------------|  <-- 2 * CapacityControlPerLane
   *   |      ...     |
   *   |--------------|  <-- (NumLanes-1) * CapacityControlPerLane
   *   |    Lane N    |
   *   |  Event Queue |
   *   | Oprnds Queue |
   *   |  Start Exec  |
   *   |     Lock     |
   *   |* * * * * * * |   -|
   *   | * * * * * * *|    |
   *   |* * * * * * * |    | For expansion purposes
   *   | * * * * * * *|    |
   *   |--------------|  <-- NumLanes * CapacityControlPerLane
   *   | * * * * * * *|
   *   |* * * * * * * |   -|
   *   | * * * * * * *|    | For expansion purposes
   *   |* * * * * * * |   -|
   *   | * * * * * * *|
   *   |--------------|  <-- CapacityControlPerLane * CapacityNumLanes
   * \endverbatim
   *
   */
  struct base_addr_t {
    volatile ptr_t mmaddr;
    volatile ptr_t spaddr;
    volatile ptr_t ctrlAddr;
  };

  /**
   * @brief This is a class to manage the mapped memory
   *
   * This class cosiders memory allocation and deallocation
   * it contains all the information needed to do this.
   */
  class ud_mapped_memory_t {
  private:
    /**
     * @brief A region in memory.
     *
     * This struct represents a region in memory, full or empty
     *
     */
    struct mem_region_t {
      uint64_t size; // Size of the region
      bool free;     // Is the region free or being used
    };

    // Map to keep track of the free and used regions.
    std::map<void *, mem_region_t> regions;

  public:
    /**
     * @brief Construct a new ud_mapped_memory_t object
     *
     * Initializes the regions with a single region
     * that is free and contains all the elements
     *
     * @param machine information from the description of the current machine
     */
    ud_mapped_memory_t(ud_machine_t &machine) {
      UPDOWN_INFOMSG("Initializing Mapped Memory Manager for %lu at %lX", 
                      machine.MapMemSize, machine.MapMemBase);
      // Create the first segment
      void *baseAddr = reinterpret_cast<void *>(machine.MapMemBase);
      regions[baseAddr] = {machine.MapMemSize, true};
    }

    /**
     * @brief Get a new region in memory
     *
     * This is equivalent to malloc, it finds a free region that
     * can allocate the current size, and, if there is free space
     * left, it creates a new region with the remaining free space.
     *
     * @param size size to be allocated
     * @return void* pointer to the allocated memory
     */
    void *get_region(uint64_t size) {
      UPDOWN_INFOMSG("Allocating new region of size %u", size); 
      // Iterate over the regions finding one that fits
      auto used_reg = regions.end();
      for (auto it = regions.begin(); it != regions.end(); ++it) {
        // Check if region is free and have enough size
        if (it->second.free && size <= it->second.size) {
          UPDOWN_INFOMSG("Found a region at %lX", reinterpret_cast<uint64_t>(it->first)); 
          used_reg = it;
          break;
        }
      }
      // Check if we found space
      if (used_reg == regions.end()) {
        UPDOWN_ERROR("Allocator run out of memory. Cannot allocate %lu bytes",
                     size);
        return nullptr;
      }
      // split the new region
      used_reg->second.free = false;
      uint64_t new_size = used_reg->second.size - size;
      used_reg->second.size = size;
      // Create a new empty region
      if (new_size != 0) {
        void *new_reg = static_cast<char *>(used_reg->first) + size;
        regions[new_reg] = {new_size, true};
        UPDOWN_INFOMSG("Creating a new region %lX with the remaining size %lu", 
                        reinterpret_cast<uint64_t>(new_reg), new_size); 
      }
      UPDOWN_INFOMSG("Returning region %lX = {%lu, %s}",
                      reinterpret_cast<uint64_t>(used_reg->first), used_reg->second.size, 
                      (used_reg->second.free)? "Free":"Used"); 
      // Return the new pointer
      return used_reg->first;
    }

    /**
     * @brief Remove a region
     *
     * This is equivalent to free. It removes a region from the map
     * and extends the region before or after this one if they are free.
     * Otherwise it creates a new free region
     *
     * @param ptr Pointer to be free. It must be a pointer in the regions map
     *
     */
    void remove_region(void *ptr) {
      UPDOWN_INFOMSG("Freeing the space at %lX", reinterpret_cast<uint64_t>(ptr)); 
      // Find location to free
      auto it = regions.find(ptr);
      if (it == regions.end() || it->second.free) {
        UPDOWN_ERROR("Trying to free pointer %lX that is not in the regions"
                     " or the region is free (double free?)",
                     reinterpret_cast<uint64_t>(ptr));
        return;
      }
      // merge left if free
      if (it != regions.begin() && std::prev(it, 1)->second.free) {
        uint64_t size = it->second.size;
        it--;
        it->second.size += size;
        UPDOWN_INFOMSG("Merging left %lX to %lX, adding %lu for a total of region with %lu", 
                        reinterpret_cast<uint64_t>(it->first), reinterpret_cast<uint64_t>(std::next(it, 1)->first),
                        size, it->second.size); 
        UPDOWN_INFOMSG("Removing previous region at %lX", 
                        reinterpret_cast<uint64_t>(it->first)); 
        regions.erase(std::next(it, 1));

      }
      // merge right if free
      auto nextIt = std::next(it, 1);
      if (nextIt != regions.end() && nextIt->second.free) {
        uint64_t size = nextIt->second.size;
        it->second.size += size;
        UPDOWN_INFOMSG("Merging right %lX to %lX, adding %lu for a total of region with %lu", 
                        reinterpret_cast<uint64_t>(it->first), reinterpret_cast<uint64_t>(nextIt->first),
                        size, it->second.size); 
        UPDOWN_INFOMSG("Removing previous region at %lX", 
                        reinterpret_cast<uint64_t>(it->first)); 
        regions.erase(nextIt);
      }

      // Check if there were no merges
      if (it->first == ptr) {
        UPDOWN_INFOMSG("No merges performed, just freeing %lX = {%lu, %s}", 
                        reinterpret_cast<uint64_t>(it->first), (it->second.size),
                        (it->second.free)? "Free":"Used"); 
        it->second.free = true;
      }
    }
  };


protected:
  /**
   * @brief container for all base addresses
   *
   */
  base_addr_t BaseAddrs;

  /**
   * @brief Contains configuration parameters of the machine abstraction
   *
   */
  ud_machine_t MachineConfig;

  /**
   * @brief
   *
   */
  ud_mapped_memory_t *MappedMemoryManager;

  /**
   * @brief Initializes the base addresses for queues and states
   *
   * This function initializes BaseAddrs according to the configuration
   * file for their use in the rest of the runtime
   *
   */
  void calc_addrmap();

  /**
   * @brief
   *
   * @param num
   * @return uint32_t
   */
  uint32_t change_endian(uint32_t num);

  /**
   * @brief Get the aligned offset object
   *
   * @param ud_id
   * @param lane_num
   * @param offset
   * @return uint64_t
   */
  uint64_t inline get_lane_aligned_offset(uint8_t ud_id, uint8_t lane_num,
                                          uint32_t offset = 0);

public:
  UDRuntime_t() {
    UPDOWN_INFOMSG("Initializing runtime"); 
    calc_addrmap();
    MappedMemoryManager = new ud_mapped_memory_t(this->MachineConfig);
  }

  UDRuntime_t(ud_machine_t machineConfig) : MachineConfig(machineConfig) {
    UPDOWN_INFOMSG("Initializing runtime with custom machineConfig"); 
    calc_addrmap();
    MappedMemoryManager = new ud_mapped_memory_t(this->MachineConfig);
  }

  ~UDRuntime_t() { delete MappedMemoryManager; }

  /**
   * @brief Sends an event to the UpDown
   *
   * Sends a new event to the updown event queues. Information about the
   * destination of the event is defined in the ev parameter, including
   * destination UD_ID, lane_id, thread_id. The event_t also contains the
   * operands
   *
   * @param ev the event to be sent
   */
  void send_event(event_t ev);

  /**
   * @brief Signal lane to start execution
   * 
   * @param ud_id UpDown ID
   * @param lane_num lane to signal
   */
  void start_exec(uint8_t ud_id, uint8_t lane_num);

  /**
   * @brief Memory allocator for the mapped memory
   *
   * Mapped memory is a region in DRAM that can be accessed
   * from updown. This is necessary due to the lack of support for
   * virtual memories in the UpDown. The UpDown
   * will be able to use pointers directly into this region
   * without need for address translation.
   *
   * @todo: This should be thread safe?
   *
   * @param size size in words
   * @return void * Pointer to the location.
   */

  void *mm_malloc(uint64_t size);

  /**
   * @brief Free an already existing memory allocation
   *
   * Mapped memory is a region in DRAM that can be accessed
   * from updown. This is necessary due to the lack of support for
   * virtual memories in the UpDown. The UpDown
   * will be able to use pointers directly into this region
   * without need for address translation.
   *
   * @todo: This should be thread safe?
   *
   * @param size size in words
   * @return void * Pointer to the location.
   */

  void mm_free(void *ptr);

  /**
   * @brief Copy to mapped memory from top
   *
   * Mapped memory is a region in DRAM that can be accessed
   * from updown. This is necessary due to the lack of support for
   * virtual memories in the UpDown. The UpDown
   * will be able to use pointers directly into this region
   * without need for address translation.
   *
   * @param offset Destination offset within the memory mapped region
   * @param src Source pointer
   * @param size size in words
   */

  void t2mm_memcpy(uint64_t offset, ptr_t src, uint64_t size = 1);

  /**
   * @brief Copy from mapped memory to top
   *
   * Mapped memory is a region in DRAM that can be accessed
   * from updown. This is necessary due to the lack of support for
   * virtual memories in the UpDown. The UpDown
   * will be able to use pointers directly into this region
   * without need for address translation.
   *
   * @param offset Destination offset within the memory mapped region
   * @param dst Source pointer
   * @param size size in words
   */

  void mm2t_memcpy(uint64_t offset, ptr_t dst, uint64_t size = 1);

  /**
   * @brief Copy data from the top to the scratchpad memory
   *
   * This function sends data to the bank associated with the lane_num
   * The address is calculated based on the offset.
   *
   * @param ud_id UpDown number
   * @param lane_num lane bank
   * @param offset offset within bank
   * @param size_num_words The number of words to be copied to the scratchpad
   * memory
   * @param data pointer to the top data to be copied over to the lane
   */
  void t2ud_memcpy(uint8_t ud_id, uint8_t lane_num, uint32_t offset = 0,
                   uint64_t size = 1, ptr_t data = nullptr);

  /**
   * @brief Copy data from the scratchpad memory to the top
   *
   * @param ud_id UpDown number
   * @param lane_num lane bank
   * @param offset offset within bank
   * @param size_num_words The number of words to be copied from the scratchpad
   * memory
   * @param data pointer to the top data to be contain values from the
   * scratchpad memory
   */
  void ud2t_memcpy(uint8_t ud_id, uint8_t lane_num, uint32_t offset = 0,
                   uint64_t size = 1, ptr_t data = nullptr);

  /**
   * @brief Test a memory location in the updwon bank for the expected value
   *
   * Reads the updown scratchpad memory bank, and check if the value is equal to
   * the expected value. Returns true if the values are equal
   *
   * @param ud_id UpDown number
   * @param lane_num LaneID to check
   * @param offset offset within the memory bank
   * @param expected value that is expected in the memory bank
   * @return word_t
   */
  bool test_addr(uint8_t ud_id, uint8_t lane_num, uint32_t offset = 0,
                 word_t expected = 1);

  /**
   * @brief Test a memory location in the updown bank for the expected value.
   * Wait until it is the expected value
   *
   * Spinwaiting on a location of the updown scratchpad memory bank until the
   * value read is the expected value. Uses lane_test_memory.
   *
   * @param lane_num LaneID to check
   * @param offset offset within the memory bank
   * @param expected value that is expected in the memory bank
   */
  void test_wait_addr(uint8_t ud_id, uint8_t lane_num, uint32_t offset = 0,
                      word_t expected = 1);

  /**
   * @brief Helper function to dump current base addresses
   *
   */
  void dumpBaseAddrs() {
    printf("  mmaddr     = 0x%lX\n"
           "  spaddr    = 0x%lX\n"
           "  ctrlAddr  = 0x%lX\n",
           reinterpret_cast<uint64_t>(BaseAddrs.mmaddr),
           reinterpret_cast<uint64_t>(BaseAddrs.spaddr),
           reinterpret_cast<uint64_t>(BaseAddrs.ctrlAddr));
  }

  /**
   * @brief Helper function to dump current Machine Config
   *
   */
  void dumpMachineConfig() {
    printf("  MapMemBase          = 0x%lX\n"
           "  UDbase              = 0x%lX\n"
           "  SPMemBase           = 0x%lX\n"
           "  ControlBase         = 0x%lX\n"
           "  EventQueueOffset    = (0x%lX)%lu\n"
           "  OperandQueueOffset  = (0x%lX)%lu\n"
           "  StartExecOffset     = (0x%lX)%lu\n"
           "  LockOffset          = (0x%lX)%lu\n"
           "  CapNumUDs           = (0x%lX)%lu\n"
           "  CapNumLanes         = (0x%lX)%lu\n"
           "  CapSPmemPerLane     = (0x%lX)%lu\n"
           "  CapControlPerLane   = (0x%lX)%lu\n"
           "  NumUDs              = (0x%lX)%lu\n"
           "  NumLanes            = (0x%lX)%lu\n"
           "  MapMemSize          = (0x%lX)%lu\n"
           "  SPBankSize          = (0x%lX)%lu\n"
           "  SPBankSizeWords     = (0x%lX)%lu\n",
           MachineConfig.MapMemBase, MachineConfig.UDbase,
           MachineConfig.SPMemBase, MachineConfig.ControlBase,
           MachineConfig.EventQueueOffset, MachineConfig.EventQueueOffset,
           MachineConfig.OperandQueueOffset, MachineConfig.OperandQueueOffset,
           MachineConfig.StartExecOffset, MachineConfig.StartExecOffset,
           MachineConfig.LockOffset, MachineConfig.LockOffset,
           MachineConfig.CapNumUDs, MachineConfig.CapNumUDs,
           MachineConfig.CapNumLanes, MachineConfig.CapNumLanes,
           MachineConfig.CapSPmemPerLane, MachineConfig.CapSPmemPerLane,
           MachineConfig.CapControlPerLane, MachineConfig.CapControlPerLane,
           MachineConfig.NumUDs, MachineConfig.NumUDs, MachineConfig.NumLanes,
           MachineConfig.NumLanes, MachineConfig.MapMemSize,
           MachineConfig.MapMemSize, MachineConfig.SPBankSize,
           MachineConfig.SPBankSize, MachineConfig.SPBankSizeWords,
           MachineConfig.SPBankSizeWords);
  }
};

} // namespace UpDown

#endif