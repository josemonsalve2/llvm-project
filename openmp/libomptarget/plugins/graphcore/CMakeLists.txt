##===----------------------------------------------------------------------===##
# Part of the LLVM Project, under the Apache License v2.0 with LLVM Exceptions.
# See https://llvm.org/LICENSE.txt for license information.
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
#
##===----------------------------------------------------------------------===##
#
# Build a plugin for graphcore.
#
##===----------------------------------------------------------------------===#

if (NOT(CMAKE_SYSTEM_NAME MATCHES "Linux"))
  libomptarget_say("Not building remote offloading plugin: only support Linux hosts.")
  return()
endif()


if (NOT(LIBOMPTARGET_ENABLE_EXPERIMENTAL_GRAPHCORE_PLUGIN))
  return()
endif()

set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} ${CMAKE_CURRENT_SOURCE_DIR}/cmake)

find_package(Poplar)

if(Poplar_FOUND)
  libomptarget_say("Building graphcore offloading plugin.")
  libomptarget_say("Using Poplar: ${Poplar_FOUND} ${Poplar_VERSION} ${Poplar_LIBRARIES} ${Poplar_LIBRARY} ${Poplar_INCLUDE_DIRS}")
  add_subdirectory(src)
else()
  libopmptarget_say("Not building Graphcore Offloading Plugin. Could not find the Poplar library")
endif()
