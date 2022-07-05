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

int32_t __tgt_rtl_register_lib(__tgt_bin_desc *Desc) {
  // Create the IPU model device
  poplar::IPUModel ipuModel;
  poplar::Device device = ipuModel.createDevice();
  poplar::Target target = device.getTarget();

  // Create the Graph object
  poplar::Graph graph(target);

  // Add codelets to the graph
  graph.addCodelets("tut3_codelets.cpp");

  // Add variables to the graph
  poplar::Tensor v1 = graph.addVariable(poplar::FLOAT, {4}, "v1");
  poplar::Tensor v2 = graph.addVariable(poplar::FLOAT, {4}, "v2");
  for (unsigned i = 0; i < 4; ++i) {
    graph.setTileMapping(v1[i], i);
    graph.setTileMapping(v2[i], i);
  }

  // Create a control program that is a sequence of steps
  poplar::program::Sequence prog;

  // Add steps to initialize the variables
  poplar::Tensor c1 = graph.addConstant<float>(poplar::FLOAT, {4}, {1.0, 1.5, 2.0, 2.5});
  graph.setTileMapping(c1, 0);
  prog.add(poplar::program::Copy(c1, v1));

  poplar::ComputeSet computeSet = graph.addComputeSet("computeSet");
  for (unsigned i = 0; i < 4; ++i) {
    poplar::VertexRef vtx = graph.addVertex(computeSet, "SumVertex");
    graph.connect(vtx["in"], v1.slice(i, 4));
    graph.connect(vtx["out"], v2[i]);
    graph.setTileMapping(vtx, i);
    graph.setPerfEstimate(vtx, 20);
  }

  // Add step to execute the compute set
  prog.add(poplar::program::Execute(computeSet));

  // Add step to print out v2
  prog.add(poplar::program::PrintTensor("v2", v2));

  // Create the engine
  poplar::Engine engine(graph, prog);
  engine.load(device);

  // Run the control program
  std::cout << "Running program\n";
  engine.run(0);
  std::cout << "Program complete\n";

  return 0;
}

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
