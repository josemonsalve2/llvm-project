if (UPDOWNRT_ENABLE_TESTS)

set(UPDOWNRT_TESTS_SRC operands_t.cpp event_t.cpp)

    foreach (TEST_SRC ${UPDOWNRT_TESTS_SRC})
        string(REGEX REPLACE "[.]cpp$"
                             "" TEST_NAME ${TEST_SRC})
            add_executable(${TEST_NAME} ${TEST_SRC})
                target_link_libraries(${TEST_NAME} UpDownRuntime) endforeach()

                    endif(UPDOWNRT_ENABLE_TESTS)