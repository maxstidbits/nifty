# NIFTY - N-Dimensional Image Feature Toolkit for Python

[![PyPI version](https://badge.fury.io/py/nifty.svg)](https://badge.fury.io/py/nifty)
[![Python versions](https://img.shields.io/pypi/pyversions/nifty.svg)](https://pypi.org/project/nifty/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Build Status](https://github.com/DerThorsten/nifty/workflows/Build%20Wheels/badge.svg)](https://github.com/DerThorsten/nifty/actions)

A comprehensive toolkit for graph-based image analysis, multicut optimization, and n-dimensional image processing. NIFTY provides efficient C++ implementations with Python bindings for complex image segmentation and analysis tasks.

## 🚀 Quick Start

### Installation

**Simple installation from PyPI (Recommended):**

```bash
pip install nifty
```

**For development or latest features:**

```bash
git clone --recursive https://github.com/DerThorsten/nifty.git
cd nifty
pip install -e .
```

### Basic Usage

```python
import nifty
import numpy as np

# Create a simple graph
graph = nifty.graph.UndirectedGraph(5)
graph.insertEdge(0, 1)
graph.insertEdge(1, 2)
graph.insertEdge(2, 3)
graph.insertEdge(3, 4)

print(f"Graph has {graph.numberOfNodes()} nodes and {graph.numberOfEdges()} edges")

# Check available features
print(f"NIFTY version: {nifty.__version__}")
nifty.print_version_info()
```

## 📦 Setuptools Migration

**NIFTY has migrated from CMake to setuptools!** This brings several benefits:

- **Simple installation**: Just `pip install nifty`
- **PyPI distribution**: Standard Python package management
- **Automatic dependency handling**: No manual configuration needed
- **Better error messages**: Clear guidance when dependencies are missing

**xtensor-python Migration**: As part of this migration, NIFTY now uses a custom xtensor-python source from https://github.com/maxstidbits/xtensor-python that includes the completed setuptools/pip migration. This ensures full compatibility with the new build system and provides a seamless installation experience.

### Migration Benefits

| Before (CMake) | After (Setuptools) |
|----------------|-------------------|
| Complex multi-step build | Single `pip install` command |
| Manual dependency setup | Automatic dependency detection |
| Platform-specific instructions | Cross-platform compatibility |
| Build configuration required | Runtime feature detection |

## 🔧 Installation Options

### Core Installation

```bash
# Basic installation with core features
pip install nifty
```

### With Optional Dependencies

```bash
# Install with HDF5 support
pip install nifty[hdf5]

# Install with solver support (GLPK)
pip install nifty[solvers]

# Install with Z5 support
pip install nifty[z5]

# Install all optional dependencies
pip install nifty[hdf5,solvers,z5]

# Development installation
pip install nifty[dev]
```

### System Requirements

**Core Dependencies (automatically installed):**
- Python ≥ 3.8
- NumPy ≥ 1.19.0
- scikit-image

**System Dependencies (must be installed separately):**
- **xtensor** ≥ 0.26.0 (C++ tensor library)
- **xtensor-python** ≥ 0.28.0 (Python bindings for xtensor - now installed via pip from custom source)
- **Boost** ≥ 1.63.0 (C++ libraries)
- C++17 compatible compiler

**Note**: xtensor-python is now installed from a custom GitHub source that includes the completed setuptools/pip migration. This ensures compatibility with the new build system.

**Optional Dependencies:**
- **HDF5**: For HDF5 file format support
- **GLPK**: Open-source linear programming solver
- **Z5**: Chunked array storage format
- **OpenMP**: Parallel processing support

## 🛠️ System Dependency Installation

### Ubuntu/Debian

```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install -y \
    build-essential \
    python3-dev \
    libboost-all-dev \
    libxtensor-dev \
    libhdf5-dev \
    libglpk-dev

# Install xtensor-python from custom GitHub source
pip install git+https://github.com/maxstidbits/xtensor-python.git

# Install NIFTY
pip install nifty[hdf5,solvers]
```

### macOS (Homebrew)

```bash
# Install system dependencies
brew install boost xtensor hdf5 glpk

# Install xtensor-python from custom GitHub source
pip install git+https://github.com/maxstidbits/xtensor-python.git

# Install NIFTY
pip install nifty[hdf5,solvers]
```

### Windows

```bash
# Using conda (recommended for Windows)
conda install -c conda-forge boost xtensor hdf5 glpk

# Install xtensor-python from custom GitHub source
pip install git+https://github.com/maxstidbits/xtensor-python.git

# Install NIFTY
pip install nifty[hdf5,solvers]
```

### Conda Environment

```bash
# Create conda environment with dependencies
conda create -n nifty-env -c conda-forge python=3.11 boost xtensor
conda activate nifty-env

# Install xtensor-python from custom GitHub source
pip install git+https://github.com/maxstidbits/xtensor-python.git

# Install NIFTY
pip install nifty
```

## 🔍 Feature Detection

NIFTY automatically detects available features at runtime:

```python
import nifty

# Check what features are available
info = nifty.get_version_info()
print("Available features:")
for feature, available in info['features'].items():
    status = "✓" if available else "✗"
    print(f"  {status} {feature.lower().replace('with_', '')}")

# Check specific features
if hasattr(nifty, 'hdf5'):
    print("HDF5 support is available")
else:
    print("HDF5 support is not available")
```

## 🚨 Troubleshooting

### Common Installation Issues

#### Missing xtensor/xtensor-python

**Error:** `fatal error: xtensor/xarray.hpp: No such file or directory`

**Solution:**
```bash
# Install xtensor via system package manager
# Ubuntu/Debian
sudo apt-get install libxtensor-dev

# macOS
brew install xtensor

# Conda
conda install -c conda-forge xtensor

# Install xtensor-python from custom GitHub source
pip install git+https://github.com/maxstidbits/xtensor-python.git
```

#### Missing Boost

**Error:** `fatal error: boost/graph/adjacency_list.hpp: No such file`

**Solution:**
```bash
# Ubuntu/Debian
sudo apt-get install libboost-all-dev

# macOS
brew install boost

# Conda
conda install -c conda-forge boost
```

#### Compiler Issues

**Error:** `Microsoft Visual C++ 14.0 is required` (Windows)

**Solution:** Install Visual Studio Build Tools or use conda:
```bash
conda install -c conda-forge compilers
```

#### Import Errors

**Error:** `ImportError: cannot import name '_nifty'`

**Solution:** Check that C++ extensions were built correctly:
```python
import nifty
print(nifty.__file__)  # Should show installed location
nifty.print_version_info()  # Check build status
```

### Debug Mode

Enable verbose output for troubleshooting:

```bash
export NIFTY_DEBUG=1
pip install nifty -v
```

### Getting Help

If you encounter issues:

1. **Check system dependencies**: Ensure xtensor, xtensor-python, and Boost are installed
2. **Verify Python version**: NIFTY requires Python ≥ 3.8
3. **Check compiler**: Ensure C++17 support is available
4. **Review error messages**: Look for specific missing dependencies
5. **Use conda**: Consider using conda for dependency management on Windows

## 📚 Documentation

- **[Installation Guide](INSTALL.md)**: Detailed installation instructions
- **[Migration Guide](MIGRATION_GUIDE.md)**: Migrating from CMake to setuptools
- **[Contributing Guide](CONTRIBUTING.md)**: Development setup and guidelines
- **[API Documentation](https://nifty.readthedocs.io/)**: Complete API reference

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and guidelines.

### Quick Development Setup

```bash
# Clone with submodules
git clone --recursive https://github.com/DerThorsten/nifty.git
cd nifty

# Install in development mode
pip install -e .[dev]

# Run tests
python -m pytest src/python/test/
```

## 📄 License

NIFTY is released under the MIT License. See [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- **xtensor**: Modern C++ tensor library
- **pybind11**: Python bindings for C++
- **Boost**: C++ libraries
- **Contributors**: All the developers who have contributed to NIFTY

## 📈 Project Status

- **Stable**: Core functionality is stable and well-tested
- **Active Development**: Regular updates and improvements
- **Community Driven**: Open to contributions and feedback

---

**Need help?** Open an issue on [GitHub](https://github.com/DerThorsten/nifty/issues) or check our [documentation](https://nifty.readthedocs.io/).
