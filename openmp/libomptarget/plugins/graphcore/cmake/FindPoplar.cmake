# Distributed under the OSI-approved BSD 3-Clause License.  See accompanying
# file Copyright.txt or https://cmake.org/licensing for details.

#[=======================================================================[.rst:
FindPoplar
-------

Finds the poplar library.

Imported Targets
^^^^^^^^^^^^^^^^

This module provides the following imported targets, if found:

Result Variables
^^^^^^^^^^^^^^^^

This will define the following variables:

``Poplar_FOUND``
  True if the system has the Foo library.
``Poplar_VERSION``
  The version of the Foo library which was found.
``Poplar_INCLUDE_DIRS``
  Include directories needed to use Foo.
``Poplar_LIBRARIES``
  Libraries needed to link to Foo.

Cache Variables
^^^^^^^^^^^^^^^

The following cache variables may also be set:

``Poplar_INCLUDE_DIR``
  The directory containing ``foo.h``.
``Poplar_LIBRARY``
  The path to the Foo library.

#]=======================================================================]

if (NOT Poplar_ROOT) 
	set(Poplar_ROOT /software_releases/poplar_sdk-ubuntu_18_04-2.0.0+481-79b41f85d1/poplar-ubuntu_18_04-2.0.0+108156-165bbd8a64)
endif()

#message("Searching for poplar")
set(Poplar_FOUND TRUE)
set(Poplar_VERSION 2.0)
set(Poplar_INCLUDE_DIRS ${Poplar_ROOT}/include)
set(Poplar_LIBRARIES poplar)
set(Poplar_LIBRARY poplar)
set(Poplar_INCLUDE_DIR ${Poplar_ROOT}/include)

#message("Found Poplar: ${Poplar_FOUND} - ${Poplar_VERSION} - ${Poplar_INCLUDE_DIRS} - ${Poplar_LIBRARIES}")
