find_package(Python REQUIRED COMPONENTS NumPy Interpreter Development)
include_directories(${Python_NumPy_INCLUDE_DIRS})

find_package(xtensor-python REQUIRED)
include_directories(${xtensor-python_INCLUDE_DIRS})

find_package(pybind11 CONFIG REQUIRED)
include_directories(${pybind11_INCLUDE_DIRS})

add_subdirectory(test)
add_subdirectory(lib)

# message(STATUS "Python_SITELIB ${Python_SITELIB}")
# Seems like with cmake 4 this is no longer so forgiving???
# This line will convert backslashes to forward slash
# which are "safer" for cmake
file(TO_CMAKE_PATH "${Python_SITELIB}" Python_SITELIB)
# message(STATUS "Python_SITELIB ${Python_SITELIB}")

install(DIRECTORY "${CMAKE_BINARY_DIR}/python/nifty"
    DESTINATION ${Python_SITELIB})
