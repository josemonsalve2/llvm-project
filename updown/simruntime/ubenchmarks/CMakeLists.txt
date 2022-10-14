if (UPDOWNRT_ENABLE_UBENCH)

    set(UPDOWNSIMRT_UBENCH_SRC 
        eventrate/eventRate.cpp
    )

    set(UPDOWNSIMRT_PYTHON_UBENCH_SRC
        eventrate/eventRateEFA.py
    )
        set(UPDOWN_RUNTIME_UBENCH_INSTALL_PATH "${UPDOWN_RUNTIME_INSTALL_DIR}/ubenchmarks")

        foreach (UBENCH_SRC ${UPDOWNSIMRT_UBENCH_SRC})
            get_filename_component(BARENAME ${UBENCH_SRC} NAME)
            string(REGEX REPLACE "[.]cpp$" "" UBENCH_NAME ${BARENAME})
            add_executable(${UBENCH_NAME} ${UBENCH_SRC})
            target_link_libraries(${UBENCH_NAME} UpDownSimRuntimeStatic)

            INSTALL(TARGETS ${UBENCH_NAME}
                RUNTIME DESTINATION ${UPDOWN_RUNTIME_UBENCH_INSTALL_PATH}
            )
        endforeach()

        INSTALL(FILES ${UPDOWNSIMRT_PYTHON_UBENCH_SRC} DESTINATION ${UPDOWN_RUNTIME_UBENCH_INSTALL_PATH})

endif(UPDOWNRT_ENABLE_UBENCH)