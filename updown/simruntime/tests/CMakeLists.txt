if (UPDOWNRT_ENABLE_TESTS)

    set(UPDOWNSIMRT_TESTS_SRC 
        simrt_send_event.cpp
    )

        set(UPDOWN_RUNTIME_TESTS_INSTALL_PATH "${UPDOWN_RUNTIME_INSTALL_DIR}/tests")

        foreach (TEST_SRC ${UPDOWNSIMRT_TESTS_SRC})
            string(REGEX REPLACE "[.]cpp$" "" TEST_NAME ${TEST_SRC})
            add_executable(${TEST_NAME} ${TEST_SRC})
            target_link_libraries(${TEST_NAME} UpDownSimRuntime)

            INSTALL(TARGETS ${TEST_NAME}
                RUNTIME DESTINATION ${UPDOWN_RUNTIME_TESTS_INSTALL_PATH}
            )
        endforeach()

endif(UPDOWNRT_ENABLE_TESTS)