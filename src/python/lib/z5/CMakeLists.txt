
addPythonModule(
    NESTED_NAME
        nifty/z5
    SOURCES
        z5.cxx
        dataset_wrapper.cxx
    LIBRARIES
        ${Z5_COMPRESSION_LIBRARIES} 
        ${FILESYSTEM_LIBRARIES} 
        Threads::Threads
)
