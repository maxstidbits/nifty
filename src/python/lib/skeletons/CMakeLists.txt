
addPythonModule(
    NESTED_NAME 
        nifty/skeletons
    SOURCES
        skeletons.cxx
        evaluation.cxx
    LIBRARIES
        ${Z5_COMPRESSION_LIBRARIES}
        ${FILESYSTEM_LIBRARIES}    
        Threads::Threads
)
