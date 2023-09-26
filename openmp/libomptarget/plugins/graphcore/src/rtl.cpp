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

/// Each PoplarProgram object has its own graph and engine
class PoplarProgram {
  poplar::program::Sequence prog;
  poplar::Graph graph;
  poplar::Device *device;
  poplar::Engine *engine;
  std::vector<poplar::ComputeSet> computeSets;
  std::vector<poplar::VertexRef> vertices;

public:
  PoplarProgram() = delete;
  PoplarProgram(poplar::Target t, poplar::Device& d) : graph(t), device(&d), engine(nullptr) {
    std::cout << "PoplarProgram constructor\n";


    // Load the codelets to the program
    //TODO: get codeletFilename here
    std::string codeletFile = "codelets.cpp";
    graph.addCodelets(codeletFile);


  }

  // move constructor 
  PoplarProgram(PoplarProgram &&other) {
    std::cout << "PoplarProgram move constructor\n";
    prog = std::move(other.prog);
    graph = std::move(other.graph);
    engine = other.engine;
    device = other.device;
    other.engine = nullptr;
  }

  // Add a computeSet and returns its ID
  int addComputeSet() {
    computeSets.emplace_back(graph.addComputeSet());
    return computeSets.size() - 1;
  }

  // Add a vertex to a computeSet and returns its ID
  int addVertexToComputeSet(int computeSetID, std::string codeletName) {
    auto &computeSet = computeSets[computeSetID];
    auto vertex = graph.addVertex(computeSet, codeletName);
    vertices.push_back(vertex);

    return vertices.size() - 1;
  }

  // Get a computeSet by ID
  poplar::ComputeSet &getComputeSet(int computeSetID) {
    return computeSets[computeSetID];
  }

  void addStep(poplar::program::Program &step) { prog.add(step); }

  poplar::Graph &getGraph() { return graph; }

  void run() {
    // Add execute step to each computeSet
    for (auto &computeSet : computeSets) {
      prog.add(poplar::program::Execute(computeSet));
    }

    //TODO: check if this will ever be not null
    if (engine == nullptr)
      engine = new poplar::Engine(graph, prog);

    // TODO: check because this seems cosmologically wrong....
    engine->load(*device);

    // Round robin associate each vertex with a tile
    int tile = 0;
    for (auto &vertex : vertices) {
      tile = (tile + 1) % graph.getTarget().getNumTiles();
      graph.setTileMapping(vertex, tile);
    }


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

  // moved to program constructor
  // void loadCodelets(std::string codeletFile) {
  //   std::cout << "Loading codelets from " << codeletFile << "\n";
  //   for (auto &prog : programs) {
  //     prog.getGraph().addCodelets(codeletFile);
  //   }
  // }

  poplar::IPUModel &getIPUModel() { return ipuModel; }
  poplar::Device &getDevice() { return device; }
  poplar::Target &getTarget() { return target; }

  // Returns the ID of the new program
  int addNewProgram() {
    programs.emplace_back(target, device);

    // Will we ever pop programs? If so, this will need to be changed
    return programs.size() - 1;
  }

  // Returns the ID of the new computeSet
  int newComputeSet(int programID) {
    auto &prog = programs[programID];
    int newComputeSetID = prog.addComputeSet();

    return newComputeSetID;
  }

  int addVertex(int computeSetID, int programID, std::string codeletName){
    auto &prog = programs[programID];
    auto &computeSet = prog.getComputeSet(computeSetID);

    int vertexId = prog.addVertexToComputeSet(computeSetID, codeletName);

    return vertexId;
  }

  void runProgram(int programID) {
    auto &prog = programs[programID];
    prog.run();
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
