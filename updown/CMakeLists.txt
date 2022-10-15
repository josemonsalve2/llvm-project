cmake_minimum_required(VERSION 3.13.4)

if ("${CMAKE_SOURCE_DIR}" STREQUAL "${CMAKE_CURRENT_SOURCE_DIR}")
  set(UPDOWN_STANDALONE_BUILD TRUE)
  project(UpDown C CXX)
endif()

## Function needed for building support for jinja templates
function (build_jinja)
  ## Adding for Jinja C++ Lite
  set (LIB_BUILD_TYPE STATIC)
  if(UNIX)
      SET(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11")
      set (LIB_BUILD_TYPE SHARED)
  endif()

  # https://cmake.org/Wiki/CMake_RPATH_handling
  SET(CMAKE_INSTALL_RPATH "${CMAKE_INSTALL_PREFIX}/lib")
  SET(CMAKE_INSTALL_RPATH_USE_LINK_PATH TRUE)
  SET(CMAKE_MACOSX_RPATH TRUE)

  execute_process(COMMAND python -V ERROR_VARIABLE python_test)
  if(${python_test} MATCHES "Python 2\\.7\\..*")
      #message("Python 2.7 found")
      OPTION(PYTHON_AVAILABLE "Facilitates development, not needed for normal build." ON)
  else()
      OPTION(PYTHON_AVAILABLE "Facilitates development, not needed for normal build." OFF)
  endif()

  add_library(Jinja2CppLight ${LIB_BUILD_TYPE} Jinja2CppLight/src/Jinja2CppLight.cpp Jinja2CppLight/src/stringhelper.cpp)

  if(PYTHON_AVAILABLE)
      add_custom_target(
          cog
          python ${CMAKE_CURRENT_SOURCE_DIR}/Jinja2CppLight/thirdparty/cogapp/cog.py -q -I ${CMAKE_CURRENT_SOURCE_DIR}/Jinja2CppLight/cog-batteries -r ${CMAKE_CURRENT_SOURCE_DIR}/Jinja2CppLight/src/*.h ${CMAKE_CURRENT_SOURCE_DIR}/Jinja2CppLight/src/*.cpp ${CMAKE_CURRENT_SOURCE_DIR}/Jinja2CppLight/test/*.cpp ${CMAKE_CURRENT_SOURCE_DIR}/Jinja2CppLight/test/*.h
      )
      add_dependencies(Jinja2CppLight cog)
  endif(PYTHON_AVAILABLE)

  INSTALL(TARGETS Jinja2CppLight
      LIBRARY DESTINATION lib
      ARCHIVE DESTINATION lib
      RUNTIME DESTINATION bin
  )
  install(FILES Jinja2CppLight/src/Jinja2CppLight.h Jinja2CppLight/src/stringhelper.h DESTINATION include/Jinja2CppLight)

endfunction(build_jinja)


## Building support for jinja templates
build_jinja()


set(UPDOWN_INSTALL_DIR "updown")
set(UPDOWN_HEADERS_INSTALL_PATH "${UPDOWN_INSTALL_DIR}/include")
set(UPDOWN_LIB "${UPDOWN_INSTALL_DIR}/lib")
set(UPDOWN_BIN "${UPDOWN_INSTALL_DIR}/bin")


add_compile_definitions(BASE_PATH="${CMAKE_INSTALL_PREFIX}")

if (UPDOWN_ENABLE_DEBUG)
  add_compile_definitions(DEBUG_MODE=1)
  set(UPDOWN_DEBUG True)
else()
  set(UPDOWN_DEBUG False)
endif()

include_directories(BEFORE
    common/include
    runtime/include
    simruntime/include)

## Building the python syntax plugin
if(LLVM_ENABLE_PLUGINS)
  add_llvm_library(UpDownRecodePython MODULE pythonsyntax.cpp PLUGIN_TOOL clang)
  include_directories(BEFORE
    ${CMAKE_CURRENT_SOURCE_DIR}/../clang/include
    ${CMAKE_CURRENT_BINARY_DIR}/../../tools/clang/include
    Jinja2CppLight/src
  )
  set(LLVM_LINK_COMPONENTS
    Support
  )

  target_link_libraries(UpDownRecodePython PRIVATE
    Jinja2CppLight
    clangAST
    clangBasic
    clangParse
    clangLex
    )

  set_target_properties(UpDownRecodePython PROPERTIES PUBLIC_HEADER 
      "common/include/debug.h")

  INSTALL(TARGETS UpDownRecodePython
    LIBRARY DESTINATION ${UPDOWN_LIB}
    ARCHIVE DESTINATION ${UPDOWN_LIB}
    RUNTIME DESTINATION ${UPDOWN_BIN}
    INCLUDES DESTINATION ${UPDOWN_HEADERS_INSTALL_PATH}
    PUBLIC_HEADER DESTINATION ${UPDOWN_HEADERS_INSTALL_PATH}
  )

  install(FILES templates/python.jinja DESTINATION templates)
else()
  install(FILES common/include/debug.h DESTINATION ${UPDOWN_HEADERS_INSTALL_PATH})
endif()

## Building runtime system

add_subdirectory(runtime)
add_subdirectory(simruntime)
add_subdirectory(ubenchmarks)