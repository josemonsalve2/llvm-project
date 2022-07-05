##===----------------------------------------------------------------------===##
#
# Part of the LLVM Project, under the Apache License v2.0 with LLVM Exceptions.
# See https://llvm.org/LICENSE.txt for license information.
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
#
##===----------------------------------------------------------------------===##
#
# Build a plugin for graphcore offloading.
#
##===----------------------------------------------------------------------===##

cmake_minimum_required(VERSION 3.13.4)

# Define the suffix for the runtime messaging dumps.
add_definitions(-DTARGET_NAME=GRAPHCORE)

include_directories(${LIBOMPTARGET_SRC_DIR})
include_directories(${LIBOMPTARGET_INCLUDE_DIR})
include_directories(${Poplar_INCLUDE_DIRS})

add_library(omptarget.rtl.graphcore SHARED
        ${LIBOMPTARGET_SRC_FILES}
        rtl.cpp
)

# Install plugin under the lib destination folder.
install(TARGETS omptarget.rtl.graphcore LIBRARY DESTINATION "${OPENMP_INSTALL_LIBDIR}")


target_link_libraries(omptarget.rtl.graphcore
  ${Poplar_LIBRARIES}
  ${OPENMP_PTHREAD_LIB}
  omp
  "-Wl,--version-script=${CMAKE_CURRENT_SOURCE_DIR}/../../exports")

# Report to the parent scope that we are building a plugin for Graphcore.
set(LIBOMPTARGET_SYSTEM_TARGETS "${LIBOMPTARGET_SYSTEM_TARGETS} ${tmachine_triple}-Graphcore" PARENT_SCOPE)
