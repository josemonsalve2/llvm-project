


  add_llvm_library(UpDownRuntime MODULE src/updown.cpp)
  include_directories(BEFORE
    include
  )

  INSTALL(TARGETS UpDownRuntime
      LIBRARY DESTINATION lib
      ARCHIVE DESTINATION lib
      RUNTIME DESTINATION bin
      INCLUDES DESTINATION include
  )


  #target_link_libraries(UpDownRuntime PRIVATE)