


  add_library(UpDownRuntime SHARED src/updown.cpp)
  add_library(UpDownRuntimeStatic SHARED src/updown.cpp)

  include_directories(BEFORE
    include
  )

  set(UPDOWN_RUNTIME_INSTALL_DIR "updown")

  set_target_properties(UpDownRuntime PROPERTIES PUBLIC_HEADER 
      "include/updown.h;include/updown_config.h")

  set(UPDOWN_RUNTIME_HEADERS_INSTALL_PATH "${UPDOWN_RUNTIME_INSTALL_DIR}/include")
  set(UPDOWN_RUNTIME_LIB "${UPDOWN_RUNTIME_INSTALL_DIR}/lib")
  set(UPDOWN_RUNTIME_BIN "${UPDOWN_RUNTIME_INSTALL_DIR}/bin")

  INSTALL(TARGETS UpDownRuntime
      LIBRARY DESTINATION ${UPDOWN_RUNTIME_LIB}
      ARCHIVE DESTINATION ${UPDOWN_RUNTIME_LIB}
      RUNTIME DESTINATION ${UPDOWN_RUNTIME_BIN}
      INCLUDES DESTINATION ${UPDOWN_RUNTIME_HEADERS_INSTALL_PATH}
      PUBLIC_HEADER DESTINATION ${UPDOWN_RUNTIME_HEADERS_INSTALL_PATH}
  )

  INSTALL(TARGETS UpDownRuntimeStatic
      LIBRARY DESTINATION ${UPDOWN_RUNTIME_LIB}
  )

  add_subdirectory(tests)
  #target_link_libraries(UpDownRuntime PUBLIC)