//===--------------------- rtl.cpp - Remote RTL Plugin --------------------===//
//
// Part of the LLVM Project, under the Apache License v2.0 with LLVM Exceptions.
// See https://llvm.org/LICENSE.txt for license information.
// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
//
//===----------------------------------------------------------------------===//
//
// RTL for Host.
//
//===----------------------------------------------------------------------===//

#include <cstddef>
#include <iostream>
#include <memory>
#include <string>

#include "omptarget.h"
#include "omptargetplugin.h"

#include <poplar/Engine.hpp>
#include <poplar/Graph.hpp>
#include <poplar/IPUModel.hpp>

#define TARGET_NAME RPC
#define DEBUG_PREFIX "Target " GETNAME(TARGET_NAME) " RTL"


// Exposed library API function
#ifdef __cplusplus
extern "C" {
#endif

class PoplarProgram {
  poplar::program::Sequence prog;
  poplar::Graph graph;
  poplar::Engine *engine;

public:
  PoplarProgram() = delete;
  PoplarProgram(poplar::Target t) : graph(t), engine(nullptr) {
    std::cout << "PoplarProgram constructor\n";
  }

  // move consrtuctor
  PoplarProgram(PoplarProgram &&other) {
    std::cout << "PoplarProgram move constructor\n";
    prog = std::move(other.prog);
    graph = std::move(other.graph);
    engine = other.engine;
    other.engine = nullptr;
  }

  void addStep(poplar::program::Program &step) { prog.add(step); }

  poplar::Graph &getGraph() { return graph; }

  void run() {
    if (engine == nullptr)
      engine = new poplar::Engine(graph, prog);

    std::cout << "Running program\n";
    engine->run(0);
    std::cout << "Program complete\n";
  }

  ~PoplarProgram() { std::cout << "PoplarProgram destructor\n"; }
};

class DeviceRTLty {
  poplar::IPUModel ipuModel;
  poplar::Device device;
  poplar::Target target;

  std::vector<PoplarProgram> programs;

public:
  DeviceRTLty() {
    device = ipuModel.createDevice();
    target = device.getTarget();
    std::cout << "DeviceRTLty constructor\n";
  }

  void loadCodelets(std::string codeletFile) {
    std::cout << "Loading codelets from " << codeletFile << "\n";
    for (auto &prog : programs) {
      prog.getGraph().addCodelets(codeletFile);
    }
  }

  poplar::IPUModel &getIPUModel() { return ipuModel; }
  poplar::Device &getDevice() { return device; }
  poplar::Target &getTarget() { return target; }

  int addNewProgram() {
    programs.emplace_back(target);
    return programs.size() - 1;
  }

  ~DeviceRTLty() { std::cout << "DeviceRTLty destructor\n"; }
};

DeviceRTLty DeviceRTL;

int32_t __tgt_rtl_register_lib(__tgt_bin_desc *Desc) { return 0; }

int32_t __tgt_rtl_unregister_lib(__tgt_bin_desc *Desc) {
  return 0;
}

int32_t __tgt_rtl_is_valid_binary(__tgt_device_image *Image) {
  return 0;
}

int32_t __tgt_rtl_number_of_devices() {
  return 1;
}

int32_t __tgt_rtl_init_device(int32_t DeviceId) {
  return 0;
}

int64_t __tgt_rtl_init_requires(int64_t RequiresFlags) {
  return 0;
}

__tgt_target_table *__tgt_rtl_load_binary(int32_t DeviceId,
                                          __tgt_device_image *Image) {
  return NULL;
}

int32_t __tgt_rtl_is_data_exchangable(int32_t SrcDevId, int32_t DstDevId) {
  return 0;
}

void *__tgt_rtl_data_alloc(int32_t DeviceId, int64_t Size, void *HstPtr,
                           int32_t Kind) {
  return NULL;
}

int32_t __tgt_rtl_data_submit(int32_t DeviceId, void *TgtPtr, void *HstPtr,
                              int64_t Size) {
  return 0;
}

int32_t __tgt_rtl_data_retrieve(int32_t DeviceId, void *HstPtr, void *TgtPtr,
                                int64_t Size) {
  return 0;
}

int32_t __tgt_rtl_data_delete(int32_t DeviceId, void *TgtPtr) {
  return 0;
}

int32_t __tgt_rtl_data_exchange(int32_t SrcDevId, void *SrcPtr,
                                int32_t DstDevId, void *DstPtr, int64_t Size) {
  return 0;
}


int32_t __tgt_rtl_run_target_region(int32_t DeviceId, void *TgtEntryPtr,
                                    void **TgtArgs, ptrdiff_t *TgtOffsets,
                                    int32_t ArgNum) {
  return 0;
}

int32_t __tgt_rtl_run_target_team_region(int32_t DeviceId, void *TgtEntryPtr,
                                         void **TgtArgs, ptrdiff_t *TgtOffsets,
                                         int32_t ArgNum, int32_t TeamNum,
                                         int32_t ThreadLimit,
                                         uint64_t LoopTripCount) {
  return 0;
}

// Exposed library API function
#ifdef __cplusplus
}
#endif
