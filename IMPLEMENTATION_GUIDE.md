# NIFTY Setuptools Migration - Implementation Guide

## Overview

This guide provides step-by-step instructions for implementing the setuptools migration strategy for the NIFTY project. The migration will transform NIFTY from a CMake-based build system to a modern setuptools-based system suitable for PyPI distribution.

## Prerequisites

### Development Environment
- Python 3.8+ with development headers
- C++17 compatible compiler (GCC 7+, Clang 5+, MSVC 2019+)
- Git with submodule support
- pkg-config (recommended for dependency detection)

### Required Dependencies
- setuptools >= 64
- pybind11 >= 2.10.0
- numpy >= 1.19.0
- wheel
- boost >= 1.63.0
- xtensor >= 0.26.0
- xtensor-python >= 0.28.0 (installed from https://github.com/maxstidbits/xtensor-python)

### Optional Dependencies
- GUROBI (commercial solver)
- CPLEX (commercial solver)
- GLPK (open-source solver)
- HDF5 (data format support)
- Z5 (chunked array format)
- OpenMP (parallel processing)

## Implementation Phases

### Phase 1: Foundation Setup (Week 1-2)

#### Step 1.1: Create Build Backend Structure
```bash
# Create build backend directory
mkdir -p nifty_build_backend
touch nifty_build_backend/__init__.py
```

#### Step 1.2: Implement Core Build Backend
Create [`nifty_build_backend/__init__.py`](nifty_build_backend/__init__.py:1) with the custom build backend implementation from [`EXAMPLE_CONFIGURATIONS.md`](EXAMPLE_CONFIGURATIONS.md:1).

#### Step 1.3: Create pyproject.toml
Copy the [`pyproject.toml`](pyproject.toml:1) configuration from the examples and place it in the project root.

#### Step 1.4: Create MANIFEST.in
Copy the [`MANIFEST.in`](MANIFEST.in:1) configuration from the examples to control file inclusion.

#### Step 1.5: Test Basic Setup
```bash
# Test build backend loading
python -c "import nifty_build_backend; print('Build backend loaded successfully')"

# Test version extraction
python -c "
from nifty_build_backend import NiftyBuildBackend
backend = NiftyBuildBackend()
print(f'Version: {backend._extract_version()}')
"
```

### Phase 2: Feature Detection System (Week 2-3)

#### Step 2.1: Implement Feature Detector
Create the [`FeatureDetector`](FeatureDetector:1) class in [`nifty_build_backend/feature_detection.py`](nifty_build_backend/feature_detection.py:1):

```python
# nifty_build_backend/feature_detection.py
from .feature_detection import FeatureDetector

# Test feature detection
detector = FeatureDetector()
features = detector.detect_all_features()
print("Detected features:", features)
```

#### Step 2.2: Test Feature Detection
```bash
# Test on different systems
python -c "
from nifty_build_backend.feature_detection import FeatureDetector
detector = FeatureDetector()
features = detector.detect_all_features()
for feature, available in features.items():
    status = '✓' if available else '✗'
    print(f'{status} {feature}')
"
```

#### Step 2.3: Implement Configuration Header Generation
Test configuration header generation:
```bash
python -c "
from nifty_build_backend import NiftyBuildBackend
backend = NiftyBuildBackend()
features = backend.feature_detector.detect_all_features()
config_header = backend._generate_config_header(features)
print('Configuration header generated successfully')
"
```

### Phase 3: Git Submodule Integration (Week 3-4)

#### Step 3.1: Implement Submodule Handler
Create [`nifty_build_backend/submodule_handler.py`](nifty_build_backend/submodule_handler.py:1):

```python
# Test submodule initialization
from nifty_build_backend.submodule_handler import SubmoduleHandler
handler = SubmoduleHandler()
handler.ensure_submodules()
```

#### Step 3.2: Test Submodule Integration
```bash
# Clean submodules for testing
rm -rf externals/LP_MP externals/qpbo

# Test submodule initialization
python -c "
from nifty_build_backend.submodule_handler import SubmoduleHandler
handler = SubmoduleHandler()
handler.ensure_submodules()
print('Submodules initialized successfully')
"

# Verify submodules exist
ls -la externals/
```

### Phase 4: Extension Building System (Week 4-5)

#### Step 4.1: Implement Extension Builder
Create [`nifty_build_backend/extension_builder.py`](nifty_build_backend/extension_builder.py:1) with the [`ExtensionBuilder`](ExtensionBuilder:1) class.

#### Step 4.2: Test Core Extension Building
```bash
# Test building core extension only
python -c "
from nifty_build_backend.extension_builder import ExtensionBuilder
from nifty_build_backend.feature_detection import FeatureDetector

detector = FeatureDetector()
features = detector.detect_all_features()

builder = ExtensionBuilder()
# Build only core extension for testing
core_config = builder.extensions_config['nifty._nifty']
extension = builder._build_extension('nifty._nifty', core_config, features)
print(f'Core extension created: {extension.name}')
"
```

#### Step 4.3: Implement Incremental Extension Building
Start with core extensions and gradually add more complex ones:

1. **Core module**: [`nifty._nifty`](nifty._nifty:1)
2. **Graph modules**: [`nifty.graph._graph`](nifty.graph._graph:1)
3. **Tools modules**: [`nifty.tools._tools`](nifty.tools._tools:1)
4. **Optional modules**: [`nifty.hdf5._hdf5`](nifty.hdf5._hdf5:1), [`nifty.z5._z5`](nifty.z5._z5:1)

### Phase 5: Python Module Structure (Week 5-6)

#### Step 5.1: Reorganize Python Modules
```bash
# Create new module structure
mkdir -p src/python/module/nifty/{graph,tools,hdf5,z5}

# Copy existing Python files
cp -r src/python/module/nifty/* src/python/module/nifty/
```

#### Step 5.2: Update Module Imports
Update [`src/python/module/nifty/__init__.py`](src/python/module/nifty/__init__.py:1) to handle optional imports:

```python
# Add to nifty/__init__.py
from .configuration import RuntimeConfiguration

# Global configuration instance
config = RuntimeConfiguration()

# Conditional imports based on build configuration
try:
    from . import hdf5
except ImportError:
    hdf5 = None

try:
    from . import z5
except ImportError:
    z5 = None
```

#### Step 5.3: Create Runtime Configuration
Implement [`src/python/module/nifty/configuration.py`](src/python/module/nifty/configuration.py:1) from the examples.

### Phase 6: Build Testing (Week 6-7)

#### Step 6.1: Test Source Distribution Build
```bash
# Build source distribution
python -m build --sdist

# Verify sdist contents
tar -tzf dist/nifty-*.tar.gz | head -20
```

#### Step 6.2: Test Wheel Build
```bash
# Build wheel
python -m build --wheel

# Verify wheel contents
python -m zipfile -l dist/nifty-*.whl
```

#### Step 6.3: Test Installation
```bash
# Create test environment
python -m venv test_env
source test_env/bin/activate

# Install from wheel
pip install dist/nifty-*.whl

# Test basic functionality
python -c "
import nifty
print(f'NIFTY version: {nifty.__version__}')
print(f'Available features: {nifty.config.get_available_features()}')
"
```

### Phase 7: Cross-Platform Testing (Week 7-8)

#### Step 7.1: Linux Testing
```bash
# Test on Ubuntu/Debian
sudo apt-get install build-essential python3-dev libboost-all-dev libxtensor-dev
pip install git+https://github.com/maxstidbits/xtensor-python.git

# Test on CentOS/RHEL
sudo yum install gcc-c++ python3-devel boost-devel
conda install -c conda-forge xtensor
pip install git+https://github.com/maxstidbits/xtensor-python.git

# Build and test
python -m build
pip install dist/nifty-*.whl
python -c "import nifty; print('Linux build successful')"
```

#### Step 7.2: macOS Testing
```bash
# Install dependencies via Homebrew
brew install boost xtensor
pip install git+https://github.com/maxstidbits/xtensor-python.git

# Build and test
python -m build
pip install dist/nifty-*.whl
python -c "import nifty; print('macOS build successful')"
```

#### Step 7.3: Windows Testing
```powershell
# Install dependencies via vcpkg or conda
conda install boost xtensor
pip install git+https://github.com/maxstidbits/xtensor-python.git

# Build and test
python -m build
pip install dist/nifty-*.whl
python -c "import nifty; print('Windows build successful')"
```

### Phase 8: CI/CD Integration (Week 8-9)

#### Step 8.1: GitHub Actions Workflow
Create [`.github/workflows/build-wheels.yml`](.github/workflows/build-wheels.yml:1):

```yaml
name: Build Wheels

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]
  release:
    types: [ published ]

jobs:
  build_wheels:
    name: Build wheels on ${{ matrix.os }}
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        python-version: ['3.8', '3.9', '3.10', '3.11', '3.12']

    steps:
    - uses: actions/checkout@v4
      with:
        submodules: recursive

    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build wheel

    - name: Install system dependencies (Ubuntu)
      if: runner.os == 'Linux'
      run: |
        sudo apt-get update
        sudo apt-get install -y libboost-all-dev libxtensor-dev
        pip install git+https://github.com/maxstidbits/xtensor-python.git

    - name: Install system dependencies (macOS)
      if: runner.os == 'macOS'
      run: |
        brew install boost xtensor
        pip install git+https://github.com/maxstidbits/xtensor-python.git

    - name: Build wheel
      run: python -m build --wheel

    - name: Test wheel
      run: |
        pip install dist/*.whl
        python -c "import nifty; print('Build successful')"

    - name: Upload wheels
      uses: actions/upload-artifact@v3
      with:
        name: wheels
        path: dist/*.whl
```

#### Step 8.2: PyPI Publishing Workflow
Create [`.github/workflows/publish.yml`](.github/workflows/publish.yml:1):

```yaml
name: Publish to PyPI

on:
  release:
    types: [ published ]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
      with:
        submodules: recursive

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build twine

    - name: Build package
      run: python -m build

    - name: Publish to PyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
      run: twine upload dist/*
```

### Phase 9: Documentation and Migration (Week 9-10)

#### Step 9.1: Update Documentation
Update [`README.md`](README.md:1) with new installation instructions:

```markdown
## Installation

### From PyPI (Recommended)
```bash
pip install nifty
```

### From Source
```bash
git clone --recursive https://github.com/DerThorsten/nifty.git
cd nifty
pip install .
```

### Optional Dependencies
```bash
# For HDF5 support
pip install nifty[hdf5]

# For solver support
pip install nifty[solvers]

# For development
pip install nifty[dev]
```
```

#### Step 9.2: Create Migration Guide
Document the migration process for existing users:

```markdown
## Migration from CMake Build

### For Users
- **Old**: Complex CMake build process
- **New**: Simple `pip install nifty`

### For Developers
- **Old**: `mkdir build && cd build && cmake .. && make`
- **New**: `pip install -e .` for development builds

### Feature Detection
- **Old**: CMake options (`-DWITH_GUROBI=ON`)
- **New**: Automatic runtime detection
```

#### Step 9.3: Deprecation Notice
Add deprecation notice to CMake build:

```cmake
# Add to CMakeLists.txt
message(WARNING 
    "CMake build is deprecated and will be removed in v2.0. "
    "Please migrate to setuptools build: pip install ."
)
```

## Validation and Testing

### Functional Testing Checklist

- [ ] **Core functionality**: Basic graph operations work
- [ ] **Extension loading**: All C++ extensions load correctly
- [ ] **Feature detection**: Runtime feature detection works
- [ ] **Optional dependencies**: Graceful handling of missing dependencies
- [ ] **Version consistency**: Version matches between C++ and Python
- [ ] **Cross-platform**: Builds work on Linux, macOS, Windows
- [ ] **Python versions**: Compatible with Python 3.8-3.12

### Performance Testing

```python
# Performance comparison script
import time
import nifty

# Test core operations
def benchmark_core_operations():
    # Create test graph
    graph = nifty.graph.UndirectedGraph(1000)
    
    # Benchmark graph operations
    start_time = time.time()
    for i in range(100):
        # Perform typical operations
        pass
    end_time = time.time()
    
    print(f"Core operations: {end_time - start_time:.3f}s")

if __name__ == "__main__":
    benchmark_core_operations()
```

### Memory Testing

```python
# Memory usage testing
import psutil
import nifty

def test_memory_usage():
    process = psutil.Process()
    initial_memory = process.memory_info().rss
    
    # Create large graph
    graph = nifty.graph.UndirectedGraph(100000)
    
    final_memory = process.memory_info().rss
    memory_increase = (final_memory - initial_memory) / 1024 / 1024
    
    print(f"Memory increase: {memory_increase:.2f} MB")

if __name__ == "__main__":
    test_memory_usage()
```

## Troubleshooting

### Common Issues

#### Build Failures

**Issue**: `error: Microsoft Visual C++ 14.0 is required`
**Solution**: Install Visual Studio Build Tools on Windows

**Issue**: `fatal error: boost/graph/adjacency_list.hpp: No such file`
**Solution**: Install Boost development headers
```bash
# Ubuntu/Debian
sudo apt-get install libboost-all-dev

# macOS
brew install boost

# Windows
vcpkg install boost
```

#### Runtime Issues

**Issue**: `ImportError: cannot import name '_nifty'`
**Solution**: Check that C++ extensions were built correctly
```python
import nifty
print(nifty.__file__)  # Should show installed location
```

**Issue**: Feature not available despite installation
**Solution**: Check runtime configuration
```python
import nifty
print(nifty.config.get_available_features())
```

### Debug Mode

Enable debug mode for detailed build information:
```bash
export NIFTY_DEBUG=1
pip install -e . -v
```

## Success Metrics

### Technical Metrics
- [ ] Build time < 10 minutes on CI
- [ ] Wheel size < 50MB
- [ ] Memory usage within 10% of CMake build
- [ ] Performance within 5% of CMake build

### User Experience Metrics
- [ ] Installation time < 2 minutes
- [ ] Zero configuration for basic usage
- [ ] Clear error messages for missing dependencies
- [ ] Comprehensive documentation

## Next Steps

1. **Phase 1-2**: Implement foundation and feature detection
2. **Phase 3-4**: Add submodule handling and extension building
3. **Phase 5-6**: Restructure Python modules and test builds
4. **Phase 7-8**: Cross-platform testing and CI/CD setup
5. **Phase 9-10**: Documentation and migration completion

## Support and Maintenance

### Long-term Maintenance
- Regular dependency updates
- Python version compatibility testing
- Performance regression testing
- Security vulnerability monitoring

### Community Support
- Migration assistance for existing users
- Documentation improvements
- Bug fixes and feature requests
- Performance optimization

This implementation guide provides a comprehensive roadmap for migrating NIFTY from CMake to setuptools while maintaining all existing functionality and improving the user experience.