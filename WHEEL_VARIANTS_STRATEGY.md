# NIFTY Setuptools Migration - Wheel Variants Strategy

## Overview

This document outlines the strategy for building multiple wheel variants of NIFTY to separate open-source and commercial solver dependencies, providing users with clear choices based on their licensing preferences and requirements.

## Wheel Variants

### 1. Core Variant (`nifty`)
**Target**: General users preferring open-source solutions
**Solvers**: GLPK (open-source)
**Features**: All core functionality with open-source dependencies only

### 2. Commercial Variant (`nifty-commercial`)
**Target**: Enterprise users with commercial solver licenses
**Solvers**: GUROBI, CPLEX, GLPK
**Features**: All functionality including commercial solver support

## Implementation Architecture

### Package Naming Strategy

```python
# Wheel variant configuration
WHEEL_VARIANTS = {
    "core": {
        "package_name": "nifty",
        "description": "Graph-based segmentation algorithms (open-source solvers only)",
        "solvers": ["glpk"],
        "exclude_solvers": ["gurobi", "cplex"],
        "wheel_tag": "",  # Standard wheel
    },
    "commercial": {
        "package_name": "nifty-commercial", 
        "description": "Graph-based segmentation algorithms (with commercial solver support)",
        "solvers": ["glpk", "gurobi", "cplex"],
        "exclude_solvers": [],
        "wheel_tag": "-commercial",
    }
}
```

### Build Backend Modifications

```python
# Enhanced build backend for variant support
class NiftyBuildBackend:
    def __init__(self, variant="core"):
        self.variant = variant
        self.variant_config = WHEEL_VARIANTS[variant]
        self.feature_detector = FeatureDetector(variant_config=self.variant_config)
        self.submodule_handler = SubmoduleHandler()
        self.extension_builder = ExtensionBuilder(variant_config=self.variant_config)
    
    def build_wheel(self, wheel_directory, config_settings=None, metadata_directory=None):
        """Build wheel for specific variant."""
        print(f"Building NIFTY wheel variant: {self.variant}")
        
        # Detect features based on variant configuration
        features = self.feature_detector.detect_variant_features()
        
        # Filter out excluded solvers
        for excluded_solver in self.variant_config["exclude_solvers"]:
            features[excluded_solver] = False
        
        # Build extensions with variant-specific features
        extensions = self.extension_builder.build_all_extensions(features)
        
        # Create wheel with variant-specific metadata
        return self._create_variant_wheel(wheel_directory, extensions, features)
```

### Enhanced Feature Detection

```python
class FeatureDetector:
    def __init__(self, variant_config=None):
        self.variant_config = variant_config or WHEEL_VARIANTS["core"]
    
    def detect_variant_features(self) -> Dict[str, bool]:
        """Detect features based on variant configuration."""
        all_features = self.detect_all_features()
        
        # Filter features based on variant
        variant_features = all_features.copy()
        
        # Exclude commercial solvers for core variant
        for excluded_solver in self.variant_config["exclude_solvers"]:
            variant_features[excluded_solver] = False
            print(f"Excluding {excluded_solver} for {self.variant_config['package_name']} variant")
        
        # Only include allowed solvers
        allowed_solvers = self.variant_config["solvers"]
        for solver in ["gurobi", "cplex", "glpk"]:
            if solver not in allowed_solvers:
                variant_features[solver] = False
        
        return variant_features
    
    def _detect_commercial_solvers_with_warning(self) -> Dict[str, bool]:
        """Detect commercial solvers with licensing warnings."""
        solvers = {}
        
        # GUROBI detection with license warning
        if self._detect_gurobi():
            print("WARNING: GUROBI detected - commercial license required")
            print("See: https://www.gurobi.com/products/gurobi-optimizer/")
            solvers["gurobi"] = True
        else:
            solvers["gurobi"] = False
        
        # CPLEX detection with license warning  
        if self._detect_cplex():
            print("WARNING: CPLEX detected - commercial license required")
            print("See: https://www.ibm.com/products/ilog-cplex-optimization-studio")
            solvers["cplex"] = True
        else:
            solvers["cplex"] = False
        
        return solvers
```

## Updated pyproject.toml Configurations

### Core Variant (pyproject.toml)

```toml
[build-system]
requires = [
    "setuptools>=64",
    "pybind11>=2.10.0", 
    "numpy>=1.19.0",
    "wheel",
]
build-backend = "nifty_build_backend:core"

[project]
name = "nifty"
dynamic = ["version", "description"]
authors = [
    {name = "Thorsten Beier", email = "derthorstenbeier@gmail.com"},
]
readme = "README.md"
license = {text = "MIT"}
requires-python = ">=3.8"
description = "Graph-based segmentation algorithms (open-source solvers only)"
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers", 
    "Intended Audience :: Science/Research",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: C++",
    "Programming Language :: Python :: 3",
    "Topic :: Scientific/Engineering",
    "Topic :: Scientific/Engineering :: Image Processing",
]
keywords = [
    "graph",
    "segmentation", 
    "multicut",
    "image-processing",
    "open-source",
]
dependencies = [
    "numpy>=1.19.0",
    "scikit-image",
]

[project.optional-dependencies]
glpk = [
    "glpk",  # Open-source linear programming solver
]
hdf5 = [
    "h5py>=3.0.0",
]
z5 = [
    "z5py>=2.0.5", 
]
dev = [
    "pytest>=6.0",
    "pytest-cov",
    "black",
    "isort",
]

[project.urls]
Homepage = "https://github.com/DerThorsten/nifty"
Repository = "https://github.com/DerThorsten/nifty.git"
Issues = "https://github.com/DerThorsten/nifty/issues"
```

### Commercial Variant (pyproject-commercial.toml)

```toml
[build-system]
requires = [
    "setuptools>=64",
    "pybind11>=2.10.0",
    "numpy>=1.19.0", 
    "wheel",
]
build-backend = "nifty_build_backend:commercial"

[project]
name = "nifty-commercial"
dynamic = ["version", "description"]
authors = [
    {name = "Thorsten Beier", email = "derthorstenbeier@gmail.com"},
]
readme = "README-commercial.md"
license = {text = "MIT"}
requires-python = ">=3.8"
description = "Graph-based segmentation algorithms (with commercial solver support)"
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "Intended Audience :: Science/Research", 
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: C++",
    "Programming Language :: Python :: 3",
    "Topic :: Scientific/Engineering",
    "Topic :: Scientific/Engineering :: Image Processing",
]
keywords = [
    "graph",
    "segmentation",
    "multicut", 
    "image-processing",
    "gurobi",
    "cplex",
    "commercial-solvers",
]
dependencies = [
    "numpy>=1.19.0",
    "scikit-image",
]

[project.optional-dependencies]
solvers = [
    "gurobipy",  # Commercial: GUROBI solver
    # Note: CPLEX Python API must be installed separately
]
glpk = [
    "glpk",  # Open-source fallback
]
hdf5 = [
    "h5py>=3.0.0",
]
z5 = [
    "z5py>=2.0.5",
]
dev = [
    "pytest>=6.0",
    "pytest-cov", 
    "black",
    "isort",
]

[project.urls]
Homepage = "https://github.com/DerThorsten/nifty"
Repository = "https://github.com/DerThorsten/nifty.git"
Issues = "https://github.com/DerThorsten/nifty/issues"
Commercial-Solvers = "https://github.com/DerThorsten/nifty/blob/main/COMMERCIAL_SOLVERS.md"
```

## Build Backend Entry Points

### nifty_build_backend/__init__.py

```python
"""Build backend with variant support."""

from .core import (
    get_requires_for_build_wheel,
    get_requires_for_build_sdist,
    prepare_metadata_for_build_wheel,
    build_wheel as build_wheel_core,
    build_sdist,
)

# Core variant (default)
def build_wheel(wheel_directory, config_settings=None, metadata_directory=None):
    """Build core variant wheel."""
    return build_wheel_core(wheel_directory, config_settings, metadata_directory)

# Commercial variant entry point
def build_wheel_commercial(wheel_directory, config_settings=None, metadata_directory=None):
    """Build commercial variant wheel."""
    from .commercial import build_wheel as build_commercial
    return build_commercial(wheel_directory, config_settings, metadata_directory)

# Variant-specific backends
core = __import__(__name__ + '.core', fromlist=[''])
commercial = __import__(__name__ + '.commercial', fromlist=[''])
```

### nifty_build_backend/core.py

```python
"""Core variant build backend (open-source solvers only)."""

from .base import NiftyBuildBackend, WHEEL_VARIANTS

def build_wheel(wheel_directory, config_settings=None, metadata_directory=None):
    """Build core variant wheel."""
    backend = NiftyBuildBackend(variant="core")
    return backend.build_wheel(wheel_directory, config_settings, metadata_directory)

# ... other functions
```

### nifty_build_backend/commercial.py

```python
"""Commercial variant build backend (with commercial solver support)."""

from .base import NiftyBuildBackend, WHEEL_VARIANTS

def build_wheel(wheel_directory, config_settings=None, metadata_directory=None):
    """Build commercial variant wheel."""
    backend = NiftyBuildBackend(variant="commercial")
    return backend.build_wheel(wheel_directory, config_settings, metadata_directory)

# ... other functions
```

## Runtime Configuration Updates

### Enhanced Runtime Detection

```python
# nifty/configuration.py
class RuntimeConfiguration:
    """Runtime configuration with variant awareness."""
    
    def __init__(self):
        self._feature_cache = {}
        self._build_config = self._load_build_config()
        self._variant = self._detect_variant()
    
    def _detect_variant(self) -> str:
        """Detect which variant is installed."""
        try:
            import nifty
            if hasattr(nifty, '__variant__'):
                return nifty.__variant__
            else:
                # Check package name
                import pkg_resources
                try:
                    pkg_resources.get_distribution('nifty-commercial')
                    return 'commercial'
                except pkg_resources.DistributionNotFound:
                    return 'core'
        except ImportError:
            return 'core'
    
    @property
    def variant(self) -> str:
        """Get installed variant."""
        return self._variant
    
    @property
    def has_commercial_solvers(self) -> bool:
        """Check if commercial solvers are supported."""
        return self._variant == 'commercial'
    
    def get_available_solvers(self) -> List[str]:
        """Get list of available solvers."""
        solvers = []
        
        # Always check for GLPK (open-source)
        if self.has_glpk:
            solvers.append('glpk')
        
        # Check commercial solvers only if variant supports them
        if self.has_commercial_solvers:
            if self.has_gurobi:
                solvers.append('gurobi')
            if self.has_cplex:
                solvers.append('cplex')
        
        return solvers
    
    def require_commercial_solver(self, solver_name: str) -> None:
        """Require a commercial solver with helpful error message."""
        if not self.has_commercial_solvers:
            raise ImportError(
                f"Commercial solver '{solver_name}' is not available in the core variant. "
                f"Please install the commercial variant: pip install nifty-commercial"
            )
        
        if not getattr(self, f"has_{solver_name}", False):
            raise ImportError(
                f"Commercial solver '{solver_name}' is not available. "
                f"Please install the solver and its Python bindings."
            )
```

## CI/CD Pipeline for Multiple Variants

### GitHub Actions Workflow

```yaml
name: Build Wheel Variants

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]
  release:
    types: [ published ]

jobs:
  build_core_wheels:
    name: Build Core Wheels
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

    - name: Install open-source dependencies
      run: |
        # Install GLPK and other open-source dependencies
        if [ "$RUNNER_OS" == "Linux" ]; then
          sudo apt-get update
          sudo apt-get install -y libboost-all-dev libglpk-dev
        elif [ "$RUNNER_OS" == "macOS" ]; then
          brew install boost glpk
        fi
      shell: bash

    - name: Build core wheel
      run: |
        cp pyproject.toml pyproject-build.toml
        python -m build --wheel --config-setting variant=core

    - name: Test core wheel
      run: |
        pip install dist/nifty-*.whl
        python -c "
        import nifty
        print(f'Variant: {nifty.config.variant}')
        print(f'Available solvers: {nifty.config.get_available_solvers()}')
        assert 'gurobi' not in nifty.config.get_available_solvers()
        print('Core variant test passed')
        "

    - name: Upload core wheels
      uses: actions/upload-artifact@v3
      with:
        name: core-wheels-${{ matrix.os }}-py${{ matrix.python-version }}
        path: dist/nifty-*.whl

  build_commercial_wheels:
    name: Build Commercial Wheels
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

    - name: Install dependencies (including commercial solver headers)
      run: |
        # Install open-source dependencies
        if [ "$RUNNER_OS" == "Linux" ]; then
          sudo apt-get update
          sudo apt-get install -y libboost-all-dev libglpk-dev
        elif [ "$RUNNER_OS" == "macOS" ]; then
          brew install boost glpk
        fi
        
        # Note: Commercial solver headers would be installed here
        # For CI, we build with headers but without runtime libraries
      shell: bash

    - name: Build commercial wheel
      run: |
        cp pyproject-commercial.toml pyproject-build.toml
        python -m build --wheel --config-setting variant=commercial

    - name: Test commercial wheel (basic)
      run: |
        pip install dist/nifty_commercial-*.whl
        python -c "
        import nifty
        print(f'Variant: {nifty.config.variant}')
        print(f'Commercial solvers supported: {nifty.config.has_commercial_solvers}')
        print('Commercial variant test passed')
        "

    - name: Upload commercial wheels
      uses: actions/upload-artifact@v3
      with:
        name: commercial-wheels-${{ matrix.os }}-py${{ matrix.python-version }}
        path: dist/nifty_commercial-*.whl

  publish_to_pypi:
    name: Publish to PyPI
    needs: [build_core_wheels, build_commercial_wheels]
    runs-on: ubuntu-latest
    if: github.event_name == 'release'

    steps:
    - name: Download all wheels
      uses: actions/download-artifact@v3

    - name: Publish core variant to PyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
      run: |
        pip install twine
        twine upload core-wheels-*/*.whl

    - name: Publish commercial variant to PyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN_COMMERCIAL }}
      run: |
        twine upload commercial-wheels-*/*.whl
```

## User Documentation

### Installation Guide

```markdown
# NIFTY Installation Guide

## Choose Your Variant

### Core Variant (Recommended for most users)
Open-source solvers only (GLPK). No commercial license requirements.

```bash
pip install nifty
```

### Commercial Variant
Includes support for commercial solvers (GUROBI, CPLEX) in addition to open-source ones.

```bash
pip install nifty-commercial
```

**Note**: Commercial solvers require separate licenses and installation of solver software.

## Solver Setup

### Open-Source Solvers (Core Variant)
- **GLPK**: Automatically detected if installed system-wide

### Commercial Solvers (Commercial Variant Only)
- **GUROBI**: Requires GUROBI license and `gurobipy` package
- **CPLEX**: Requires CPLEX license and Python API installation

## Feature Detection

Check available features:

```python
import nifty

# Check variant
print(f"Installed variant: {nifty.config.variant}")

# Check available solvers
print(f"Available solvers: {nifty.config.get_available_solvers()}")

# Check specific solver
if nifty.config.has_gurobi:
    print("GUROBI is available")
else:
    print("GUROBI is not available")
```

## Migration Between Variants

### From Core to Commercial
```bash
pip uninstall nifty
pip install nifty-commercial
```

### From Commercial to Core
```bash
pip uninstall nifty-commercial
pip install nifty
```

**Note**: Both variants cannot be installed simultaneously.
```

## Benefits of This Approach

### For Users
1. **Clear Choice**: Users can choose based on their licensing preferences
2. **No Bloat**: Core users don't get commercial solver dependencies
3. **Easy Migration**: Simple pip commands to switch variants
4. **Transparent Licensing**: Clear separation of open-source vs commercial components

### For Developers
1. **Simplified Maintenance**: Single codebase with variant-specific builds
2. **Clear Testing**: Separate CI pipelines for each variant
3. **Flexible Distribution**: Different PyPI packages for different use cases
4. **License Compliance**: No accidental inclusion of commercial solver bindings

### For the Ecosystem
1. **Open Source First**: Default installation is fully open-source
2. **Commercial Option**: Enterprise users can opt-in to commercial features
3. **Clear Documentation**: Users understand what they're installing
4. **Compliance**: Respects both open-source and commercial licensing models

This wheel variants strategy provides a clean separation between open-source and commercial solver support while maintaining a unified codebase and user experience.