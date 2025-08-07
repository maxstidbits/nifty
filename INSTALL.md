# NIFTY Installation Guide

This guide provides comprehensive installation instructions for NIFTY, covering all platforms and dependency scenarios. NIFTY has migrated from CMake to setuptools, making installation much simpler while maintaining all functionality.

## Table of Contents

- [System Requirements](#system-requirements)
- [Quick Installation](#quick-installation)
- [Platform-Specific Instructions](#platform-specific-instructions)
- [Dependency Installation](#dependency-installation)
- [Building from Source](#building-from-source)
- [Optional Dependencies](#optional-dependencies)
- [Troubleshooting](#troubleshooting)
- [Verification](#verification)

## System Requirements

### Minimum Requirements

- **Python**: 3.8 or higher
- **Operating System**: Linux, macOS, or Windows
- **Memory**: 4GB RAM (8GB recommended for large datasets)
- **Disk Space**: 500MB for installation

### Required System Dependencies

These **must be installed before** installing NIFTY:

#### Core Dependencies (Required)

1. **xtensor** ≥ 0.26.0
   - Modern C++ tensor library
   - **Critical**: NIFTY will not build without this

2. **xtensor-python** ≥ 0.28.0
   - Python bindings for xtensor
   - **Critical**: Required for Python integration
   - **Note**: Now installed via pip from custom GitHub source (https://github.com/maxstidbits/xtensor-python)

3. **Boost** ≥ 1.63.0
   - C++ libraries collection
   - **Critical**: Core algorithms depend on Boost

4. **C++17 Compiler**
   - GCC ≥ 7.0, Clang ≥ 5.0, or MSVC ≥ 2019
   - **Critical**: C++17 features are used throughout

#### Build Dependencies

- **pybind11** ≥ 2.10.0 (automatically installed)
- **NumPy** ≥ 1.19.0 (automatically installed)
- **setuptools** ≥ 64 (automatically installed)

## Quick Installation

### Option 1: PyPI Installation (Recommended)

```bash
# Install system dependencies first (see platform sections below)
# Then install NIFTY
pip install nifty
```

### Option 2: Conda Installation (Easiest for Windows)

```bash
# Create environment with all dependencies
conda create -n nifty-env -c conda-forge python=3.11 boost xtensor
conda activate nifty-env

# Install xtensor-python from custom GitHub source
pip install git+https://github.com/maxstidbits/xtensor-python.git

# Install NIFTY
pip install nifty
```

### Option 3: Development Installation

```bash
git clone --recursive https://github.com/DerThorsten/nifty.git
cd nifty
pip install -e .
```

## Platform-Specific Instructions

### Ubuntu/Debian Linux

#### Step 1: Install System Dependencies

```bash
# Update package list
sudo apt-get update

# Install core dependencies
sudo apt-get install -y \
    build-essential \
    python3-dev \
    python3-pip \
    libboost-all-dev \
    libxtensor-dev

# Install xtensor-python from custom GitHub source
pip install git+https://github.com/maxstidbits/xtensor-python.git

# Install optional dependencies
sudo apt-get install -y \
    libhdf5-dev \
    libglpk-dev \
    libomp-dev
```

#### Step 2: Install NIFTY

```bash
# Basic installation
pip install nifty

# With optional features
pip install nifty[hdf5,solvers]
```

#### Troubleshooting Ubuntu/Debian

**Issue**: `libxtensor-dev` not found
```bash
# Add universe repository (Ubuntu)
sudo add-apt-repository universe
sudo apt-get update

# Or install xtensor from conda-forge and xtensor-python from GitHub
conda install -c conda-forge xtensor
pip install git+https://github.com/maxstidbits/xtensor-python.git
```

### CentOS/RHEL/Fedora

#### Step 1: Install System Dependencies

```bash
# CentOS/RHEL 8+
sudo dnf install -y \
    gcc-c++ \
    python3-devel \
    boost-devel

# Install xtensor from conda (not available in system repos)
conda install -c conda-forge xtensor

# Install xtensor-python from custom GitHub source
pip install git+https://github.com/maxstidbits/xtensor-python.git

# Fedora
sudo dnf install -y \
    gcc-c++ \
    python3-devel \
    boost-devel \
    xtensor-devel

# Install xtensor-python from custom GitHub source
pip install git+https://github.com/maxstidbits/xtensor-python.git
```

#### Step 2: Install NIFTY

```bash
pip install nifty
```

### macOS

#### Step 1: Install Homebrew (if not installed)

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

#### Step 2: Install System Dependencies

```bash
# Install core dependencies
brew install boost xtensor

# Install xtensor-python from custom GitHub source
pip install git+https://github.com/maxstidbits/xtensor-python.git

# Install optional dependencies
brew install hdf5 glpk libomp

# Install Python if needed
brew install python@3.11
```

#### Step 3: Install NIFTY

```bash
# Basic installation
pip install nifty

# With optional features
pip install nifty[hdf5,solvers]
```

#### Troubleshooting macOS

**Issue**: Compiler not found
```bash
# Install Xcode command line tools
xcode-select --install
```

**Issue**: OpenMP not found
```bash
# Install libomp
brew install libomp

# Set environment variables
export CC=clang
export CXX=clang++
export LDFLAGS="-L$(brew --prefix libomp)/lib"
export CPPFLAGS="-I$(brew --prefix libomp)/include"
```

### Windows

#### Option 1: Conda (Recommended)

```bash
# Install Miniconda or Anaconda first
# Then create environment with dependencies
conda create -n nifty-env -c conda-forge python=3.11 boost xtensor
conda activate nifty-env

# Install xtensor-python from custom GitHub source
pip install git+https://github.com/maxstidbits/xtensor-python.git

# Install NIFTY
pip install nifty
```

#### Option 2: vcpkg + Visual Studio

```powershell
# Install vcpkg
git clone https://github.com/Microsoft/vcpkg.git
cd vcpkg
.\bootstrap-vcpkg.bat

# Install dependencies
.\vcpkg install boost:x64-windows xtensor:x64-windows

# Set environment variables
$env:CMAKE_TOOLCHAIN_FILE = "C:\path\to\vcpkg\scripts\buildsystems\vcpkg.cmake"

# Install NIFTY
pip install nifty
```

#### Troubleshooting Windows

**Issue**: `Microsoft Visual C++ 14.0 is required`
```bash
# Install Visual Studio Build Tools
# Or use conda environment (recommended)
conda install -c conda-forge compilers
```

**Issue**: Long path names
```powershell
# Enable long paths in Windows
New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force
```

## Dependency Installation Details

### xtensor and xtensor-python

These are **critical dependencies** that must be installed before NIFTY:

#### Via Package Manager

```bash
# Ubuntu/Debian
sudo apt-get install libxtensor-dev

# macOS
brew install xtensor

# Conda (all platforms)
conda install -c conda-forge xtensor

# xtensor-python from custom GitHub source (all platforms)
pip install git+https://github.com/maxstidbits/xtensor-python.git
```

#### From Source (if package not available)

```bash
# xtensor
git clone https://github.com/xtensor-stack/xtensor.git
cd xtensor
mkdir build && cd build
cmake .. -DCMAKE_INSTALL_PREFIX=/usr/local
make install

# xtensor-python (use pip installation instead)
pip install git+https://github.com/maxstidbits/xtensor-python.git

# Alternative: build from source if needed
# git clone https://github.com/maxstidbits/xtensor-python.git
# cd xtensor-python
# mkdir build && cd build
# cmake .. -DCMAKE_INSTALL_PREFIX=/usr/local
# make install
```

### Boost Libraries

```bash
# Ubuntu/Debian
sudo apt-get install libboost-all-dev

# macOS
brew install boost

# CentOS/RHEL/Fedora
sudo dnf install boost-devel

# Conda
conda install -c conda-forge boost
```

### Compiler Requirements

#### Linux/macOS
```bash
# Check compiler version
gcc --version  # Should be ≥ 7.0
clang --version  # Should be ≥ 5.0

# Install if needed
# Ubuntu/Debian
sudo apt-get install build-essential

# macOS
xcode-select --install
```

#### Windows
- Visual Studio 2019 or later
- Or use conda compilers: `conda install -c conda-forge compilers`

## Building from Source

### Prerequisites

Ensure all system dependencies are installed first.

### Step-by-Step Build

```bash
# 1. Clone repository with submodules
git clone --recursive https://github.com/DerThorsten/nifty.git
cd nifty

# 2. Verify submodules are initialized
git submodule status
# Should show LP_MP and qpbo submodules

# 3. Install in development mode
pip install -e .

# 4. Or build wheel
pip install build
python -m build
```

### Build Configuration

The build system automatically detects available features:

```bash
# Enable debug output
export NIFTY_DEBUG=1
pip install -e . -v
```

### Git Submodules

NIFTY uses git submodules for external libraries:

- **LP_MP**: Advanced optimization algorithms
- **QPBO**: Quadratic pseudo-boolean optimization

```bash
# Initialize submodules if missing
git submodule update --init --recursive

# Update submodules
git submodule update --remote
```

## Optional Dependencies

### HDF5 Support

```bash
# Install HDF5
# Ubuntu/Debian
sudo apt-get install libhdf5-dev

# macOS
brew install hdf5

# Conda
conda install -c conda-forge hdf5

# Install NIFTY with HDF5 support
pip install nifty[hdf5]
```

### Solver Support (GLPK)

```bash
# Install GLPK
# Ubuntu/Debian
sudo apt-get install libglpk-dev

# macOS
brew install glpk

# Conda
conda install -c conda-forge glpk

# Install NIFTY with solver support
pip install nifty[solvers]
```

### Z5 Support

```bash
# Install Z5 dependencies
# Conda (recommended)
conda install -c conda-forge z5py

# Install NIFTY with Z5 support
pip install nifty[z5]
```

### Commercial Solvers (Optional)

#### GUROBI

```bash
# Install GUROBI (requires license)
# Download from https://www.gurobi.com/
# Set environment variables
export GUROBI_HOME=/path/to/gurobi
export PATH=$PATH:$GUROBI_HOME/bin
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$GUROBI_HOME/lib

# Install Python package
pip install gurobipy
```

#### CPLEX

```bash
# Install CPLEX (requires license)
# Download from IBM
# Set environment variables
export CPLEX_ROOT_DIR=/path/to/cplex

# Install Python package
pip install cplex
```

## Troubleshooting

### Common Build Errors

#### Missing xtensor

**Error**: `fatal error: xtensor/xarray.hpp: No such file or directory`

**Solution**:
```bash
# Install xtensor and xtensor-python
conda install -c conda-forge xtensor
pip install git+https://github.com/maxstidbits/xtensor-python.git
# Or use system package manager (see platform sections)
```

#### Missing Boost

**Error**: `fatal error: boost/graph/adjacency_list.hpp: No such file`

**Solution**:
```bash
# Install Boost development headers
sudo apt-get install libboost-all-dev  # Ubuntu/Debian
brew install boost                      # macOS
conda install -c conda-forge boost     # Conda
```

#### Compiler Issues

**Error**: `error: 'std::optional' is not a member of 'std'`

**Solution**: Ensure C++17 compiler is used:
```bash
# Check compiler version
gcc --version  # Should be ≥ 7.0

# Set compiler explicitly
export CC=gcc-9
export CXX=g++-9
```

#### Git Submodule Issues

**Error**: `externals/LP_MP not found`

**Solution**:
```bash
# Initialize submodules
git submodule update --init --recursive

# If still failing, clone manually
git clone https://github.com/pawelswoboda/LP_MP.git externals/LP_MP
```

#### Windows-Specific Issues

**Error**: `Microsoft Visual C++ 14.0 is required`

**Solution**:
```bash
# Use conda environment (recommended)
conda create -n nifty-env -c conda-forge python=3.11 compilers
conda activate nifty-env

# Or install Visual Studio Build Tools
```

### Runtime Issues

#### Import Errors

**Error**: `ImportError: cannot import name '_nifty'`

**Solution**:
```python
# Check installation
import nifty
print(nifty.__file__)
nifty.print_version_info()

# Reinstall if needed
pip uninstall nifty
pip install nifty
```

#### Feature Not Available

**Error**: `ImportError: HDF5 support not available`

**Solution**:
```bash
# Install HDF5 and reinstall NIFTY
sudo apt-get install libhdf5-dev  # Ubuntu/Debian
pip uninstall nifty
pip install nifty[hdf5]
```

### Debug Mode

Enable detailed build information:

```bash
export NIFTY_DEBUG=1
export NIFTY_VERBOSE=1
pip install nifty -v
```

### Getting Help

1. **Check system dependencies**: Verify xtensor, xtensor-python, and Boost are installed
2. **Review error messages**: Look for specific missing dependencies
3. **Use conda**: Consider conda for complex dependency management
4. **Check compiler**: Ensure C++17 support
5. **Open an issue**: [GitHub Issues](https://github.com/DerThorsten/nifty/issues)

## Verification

### Test Installation

```python
import nifty
import numpy as np

# Check version
print(f"NIFTY version: {nifty.__version__}")

# Check features
nifty.print_version_info()

# Test basic functionality
graph = nifty.graph.UndirectedGraph(5)
graph.insertEdge(0, 1)
print(f"Graph created with {graph.numberOfNodes()} nodes")

# Test timer
with nifty.Timer("Test operation"):
    import time
    time.sleep(0.1)
```

### Performance Test

```python
import nifty
import numpy as np
import time

# Create larger graph for performance test
n_nodes = 10000
graph = nifty.graph.UndirectedGraph(n_nodes)

# Add random edges
np.random.seed(42)
n_edges = 50000
edges = np.random.randint(0, n_nodes, size=(n_edges, 2))

start_time = time.time()
for i, j in edges:
    if i != j:
        graph.insertEdge(int(i), int(j))

end_time = time.time()
print(f"Added {graph.numberOfEdges()} edges in {end_time - start_time:.3f} seconds")
```

### Feature Test

```python
import nifty

# Test all available features
features = nifty.get_version_info()['features']
for feature, available in features.items():
    status = "✓" if available else "✗"
    print(f"{status} {feature.lower().replace('with_', '')}")

# Test optional modules
optional_modules = ['hdf5', 'z5']
for module in optional_modules:
    try:
        mod = getattr(nifty, module)
        print(f"✓ {module} module available")
    except AttributeError:
        print(f"✗ {module} module not available")
```

## Installation Summary

1. **Install system dependencies** (xtensor, xtensor-python, Boost)
2. **Choose installation method** (PyPI, conda, or source)
3. **Install NIFTY** with desired optional features
4. **Verify installation** with test scripts
5. **Report issues** if problems persist

The setuptools migration has made NIFTY installation much simpler, but proper system dependency installation remains crucial for successful builds.