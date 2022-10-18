if (UPDOWNRT_ENABLE_TESTS)

    set(UPDOWNSIMRT_TESTS_SRC 
        simrt_send_event.cpp
        simrt_pyEmu_memcpy.cpp
        simrt_pyEmu_mm_memcpy.cpp
        simrt_pyEmu_sendevent.cpp
        simrt_memcpy.cpp
        simrt_mm_memcpy.cpp
    )

    set(UPDOWNSIMRT_PYTHON_TESTS_SRC
        simpleEFA.py
        memcpyEFA.py
    )
        set(UPDOWN_RUNTIME_TESTS_INSTALL_PATH "${UPDOWN_RUNTIME_INSTALL_DIR}/tests")

        foreach (TEST_SRC ${UPDOWNSIMRT_TESTS_SRC})
            string(REGEX REPLACE "[.]cpp$" "" TEST_NAME ${TEST_SRC})
            add_executable(${TEST_NAME} ${TEST_SRC})
            target_link_libraries(${TEST_NAME} UpDownSimRuntimeStatic)

            INSTALL(TARGETS ${TEST_NAME}
                RUNTIME DESTINATION ${UPDOWN_RUNTIME_TESTS_INSTALL_PATH}
            )
        endforeach()

        INSTALL(FILES ${UPDOWNSIMRT_PYTHON_TESTS_SRC} DESTINATION ${UPDOWN_RUNTIME_TESTS_INSTALL_PATH})

endif(UPDOWNRT_ENABLE_TESTS)