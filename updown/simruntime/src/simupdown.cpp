#include "simupdown.h"
#include <cstdio>
#include <cstdlib>

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
  UPDOWN_INFOMSG("MapMemBase changed to 0x%lX", MappedMemory);
  this->MachineConfig.UDbase = reinterpret_cast<uint64_t>(ScratchpadMemory);
  this->MachineConfig.SPMemBase = reinterpret_cast<uint64_t>(ScratchpadMemory);
  UPDOWN_INFOMSG("SPMemBase and UDbase changed to 0x%lX", ScratchpadMemory);
  this->MachineConfig.ControlBase = reinterpret_cast<uint64_t>(ControlMemory);
  UPDOWN_INFOMSG("ControlBase changed to 0x%lX", ControlMemory);
}

void SimUDRuntime_t::start_exec(uint8_t ud_id, uint8_t lane_num) {
  UDRuntime_t::start_exec(ud_id, lane_num);
  // TODO:
  // ADD CALL TO THE UPDOWN EMULATOR HERE
}

} // namespace UpDown