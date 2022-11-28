if (UPDOWNRT_ENABLE_APPS)

    set(UPDOWN_RUNTIME_INSTALL_DIR "updown")

    set(UPDOWNSIMRT_APPS_SRC 
        mapreduce/updownMapReduce.cpp
        pagerank/pagerank_upstream_padding.cpp
    )

    include_directories(
        common/glib-adv
        common/glib-core
        common/snap-adv
        common/snap-core
        common/snap-exp
    )

    set(UPDOWNSIMRT_PYTHON_APPS_SRC
        mapreduce/GenMapreduceEFA.py
        pagerank/GenPagerankEFA.py
    )
    set(UPDOWN_RUNTIME_APPS_INSTALL_PATH "${UPDOWN_RUNTIME_INSTALL_DIR}/apps")

    set(CMAKE_CXX_FLAGS ${CMAKE_CXX_FLAGS}  -fopenmp)
    foreach (APPS_SRC ${UPDOWNSIMRT_APPS_SRC})
        get_filename_component(BARENAME ${APPS_SRC} NAME)
        string(REGEX REPLACE "[.]cpp$" "" APPS_NAME ${BARENAME})
        add_executable(${APPS_NAME} ${APPS_SRC} common/snap-core/Snap.o)
        target_link_libraries(${APPS_NAME} UpDownSimRuntimeStatic m)

        INSTALL(TARGETS ${APPS_NAME}
            RUNTIME DESTINATION ${UPDOWN_RUNTIME_APPS_INSTALL_PATH}
        )
    endforeach()

    INSTALL(FILES ${UPDOWNSIMRT_PYTHON_APPS_SRC} DESTINATION ${UPDOWN_RUNTIME_APPS_INSTALL_PATH})

endif(UPDOWNRT_ENABLE_APPS)