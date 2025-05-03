find_package(Python REQUIRED COMPONENTS NumPy Interpreter Development)
include_directories(${Python_NumPy_INCLUDE_DIRS})

find_package(xtensor-python REQUIRED)
include_directories(${xtensor-python_INCLUDE_DIRS})

find_package(pybind11 CONFIG REQUIRED)
include_directories(${pybind11_INCLUDE_DIRS})

add_subdirectory(test)
add_subdirectory(lib)

# Normalize the install directory.
file(TO_CMAKE_PATH
  "${CMAKE_BINARY_DIR}/python/nifty"
  _NIFTY_PY_DIR
)

# Now use the normalized path in the install() call.
install(
  DIRECTORY "${_NIFTY_PY_DIR}"
  DESTINATION "${Python_SITELIB}"
)
