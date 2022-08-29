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

#ifndef UPDOWNSIM_H
#define UPDOWNSIM_H
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <map>
#include <utility>

#include "debug.h"
#include "updown.h"

namespace UpDown {

/**
 * @brief Wrapper class that allows simulation of runtime calls
 *
 * This class inherits from UDRuntime_t, and it overwrites the methods
 * such that they can be simulated using a memory region.
 *
 * This class does not use polymorphism. It just oversubscribes the
 * methods, wrapping the original implementation of the runtime
 *

 *
 */

class SimUDRuntime_t : public UDRuntime_t {
private:
  uint8_t *MappedMemory;
  uint8_t *ScratchpadMemory;
  uint8_t *ControlMemory;

public:
  /**
   * @brief Allocate memory for the simulation of the updown
   *
   * This function allocates the MappedMemory, the Scratchpad memory
   * and the Control Memory, used for the simulation. Then it changes
   * the MachineConfig object to use these pointers instead of the
   * default ones for these three memory regions.
   *
   * @todo We are allocating the whole address space. We could behave more
   * like a driver and translate it to the actual available memory.
   * This means. It should not allocate the reserved space for expansion.
   */
  void initMemoryArrays();

  /**
   * @brief Construct a new SimUDRuntime_t object
   *
   * This constructor calls initMemoryArrays() to set the simulated memory
   * regions.
   *
   */
  SimUDRuntime_t() : UDRuntime_t() {
    UPDOWN_INFOMSG("Initializing Simulated Runtime with defautl params");
    initMemoryArrays();
    // Recalculate address map
    calc_addrmap();
  }

  /**
   * @brief Construct a new udruntime t object
   *
   * This constructor calls initMemoryArrays() to set the simulated memory
   * regions. The pointers of ud_machine_t.MappedMemBase, ud_machine_t.UDbase
   * ud_machine_t.SPMemBase and ud_machine_t.ControlBase will be ignored and
   * overwritten.
   *
   * @param machineConfig Machine configuration
   */
  SimUDRuntime_t(ud_machine_t machineConfig) : UDRuntime_t(machineConfig) {
    UPDOWN_INFOMSG("Initializing runtime with custom machineConfig");
    initMemoryArrays();
    // Recalculate address map
    calc_addrmap();
  }

  ~SimUDRuntime_t() {
    delete MappedMemory;
    delete ScratchpadMemory;
    delete ControlMemory;
  }

  /**
   * @brief Start_execution simulator
   *
   * @todo we should start the UD Emulator here
   *
   * @param ud_id
   * @param lane_num
   */
  void start_exec(uint8_t ud_id, uint8_t lane_num);
};

} // namespace UpDown

#endif