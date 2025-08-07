# NIFTY Setuptools Migration - Example Configurations

## 1. pyproject.toml

```toml
[build-system]
requires = [
    "setuptools>=64",
    "pybind11>=2.10.0",
    "numpy>=1.19.0",
    "wheel",
]
build-backend = "nifty_build_backend"

[project]
name = "nifty"
dynamic = ["version", "description"]
authors = [
    {name = "Thorsten Beier", email = "derthorstenbeier@gmail.com"},
]
readme = "README.md"
license = {text = "MIT"}
requires-python = ">=3.8"
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "Intended Audience :: Science/Research",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: C++",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Scientific/Engineering",
    "Topic :: Scientific/Engineering :: Image Processing",
    "Topic :: Scientific/Engineering :: Artificial Intelligence",
]
keywords = [
    "graph",
    "segmentation",
    "multicut",
    "image-processing",
    "computer-vision",
]
dependencies = [
    "numpy>=1.19.0",
    "scikit-image",
]

[project.optional-dependencies]
solvers = [
    "gurobipy",  # Optional: GUROBI solver
]
hdf5 = [
    "h5py>=3.0.0",  # Optional: HDF5 support
]
z5 = [
    "z5py>=2.0.5",  # Optional: Z5 support
]
dev = [
    "pytest>=6.0",
    "pytest-cov",
    "black",
    "isort",
    "mypy",
]
docs = [
    "sphinx>=4.0",
    "sphinx-rtd-theme",
    "myst-parser",
]

[project.urls]
Homepage = "https://github.com/DerThorsten/nifty"
Documentation = "https://nifty.readthedocs.io/"
Repository = "https://github.com/DerThorsten/nifty.git"
Issues = "https://github.com/DerThorsten/nifty/issues"

[tool.setuptools]
zip-safe = false
include-package-data = true

[tool.setuptools.packages.find]
where = ["src/python/module"]
include = ["nifty*"]

[tool.setuptools.package-data]
nifty = ["*.so", "*.pyd", "*.dll"]

[tool.black]
line-length = 88
target-version = ['py38']
include = '\.pyi?$'
extend-exclude = '''
/(
  # directories
  \.eggs
  | \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | build
  | dist
)/
'''

[tool.isort]
profile = "black"
multi_line_output = 3
line_length = 88
known_first_party = ["nifty"]

[tool.mypy]
python_version = "3.8"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
```

## 2. MANIFEST.in

```
# Include source files
recursive-include src/python/lib *.cxx *.hxx *.hpp *.h
recursive-include src/python/module *.py

# Include C++ headers
recursive-include include *.hxx *.hpp *.h

# Include git submodules (selected files only)
recursive-include externals/LP_MP/include *.hpp *.h
recursive-include externals/LP_MP/lib *.cpp *.hpp *.h *.cxx
recursive-include externals/LP_MP/external/meta/include *.hpp *.h
recursive-include externals/LP_MP/external/Catch/include *.hpp *.h
recursive-include externals/LP_MP/external/cpp_sort/include *.hpp *.h
recursive-include externals/LP_MP/external/opengm/include *.hpp *.h *.hxx
recursive-include externals/LP_MP/external/PEGTL *.hpp *.h
recursive-include externals/LP_MP/external/cereal/include *.hpp *.h
recursive-include externals/LP_MP/external/tclap/include *.h

recursive-include externals/qpbo *.cpp *.h

# Configuration and documentation
include pyproject.toml
include MANIFEST.in
include README.md
include LICENSE
include SETUPTOOLS_MIGRATION_STRATEGY.md
include TECHNICAL_SPECIFICATIONS.md

# Exclude unwanted files
global-exclude *.pyc
global-exclude __pycache__
global-exclude .git*
global-exclude CMakeLists.txt
global-exclude *.cmake
global-exclude .DS_Store
global-exclude *.so
global-exclude *.pyd
global-exclude *.dll
global-exclude build/*
global-exclude dist/*
global-exclude *.egg-info/*

# Exclude test files from distribution
global-exclude */test/*
global-exclude */tests/*
prune src/test
prune src/python/test

# Exclude documentation source
prune docsrc

# Exclude conda recipe
prune conda-recipe

# Exclude scripts
prune scripts
```

## 3. Custom Build Backend (nifty_build_backend.py)

```python
"""Custom build backend for NIFTY project."""

import os
import sys
import glob
import subprocess
import re
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import tempfile
import shutil

# Import build dependencies
import pybind11
from pybind11.setup_helpers import Pybind11Extension, build_ext
import numpy as np


def get_requires_for_build_wheel(config_settings=None):
    """Return build requirements."""
    return [
        "setuptools>=64",
        "pybind11>=2.10.0",
        "numpy>=1.19.0",
        "wheel",
    ]


def get_requires_for_build_sdist(config_settings=None):
    """Return build requirements for source distribution."""
    return get_requires_for_build_wheel(config_settings)


def prepare_metadata_for_build_wheel(metadata_directory, config_settings=None):
    """Prepare metadata for wheel build."""
    backend = NiftyBuildBackend()
    return backend.prepare_metadata_for_build_wheel(metadata_directory, config_settings)


def build_wheel(wheel_directory, config_settings=None, metadata_directory=None):
    """Build wheel package."""
    backend = NiftyBuildBackend()
    return backend.build_wheel(wheel_directory, config_settings, metadata_directory)


def build_sdist(sdist_directory, config_settings=None):
    """Build source distribution."""
    backend = NiftyBuildBackend()
    return backend.build_sdist(sdist_directory, config_settings)


class NiftyBuildBackend:
    """Custom build backend for NIFTY project."""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.feature_detector = FeatureDetector()
        self.submodule_handler = SubmoduleHandler()
        self.extension_builder = ExtensionBuilder()
        
    def prepare_metadata_for_build_wheel(self, metadata_directory, config_settings=None):
        """Prepare metadata for wheel build."""
        metadata_dir = Path(metadata_directory)
        metadata_dir.mkdir(parents=True, exist_ok=True)
        
        # Extract version
        version = self._extract_version()
        
        # Generate METADATA file
        metadata_content = self._generate_metadata(version)
        metadata_path = metadata_dir / "METADATA"
        metadata_path.write_text(metadata_content)
        
        return metadata_path.name
    
    def build_wheel(self, wheel_directory, config_settings=None, metadata_directory=None):
        """Build wheel package."""
        print("Starting NIFTY wheel build...")
        
        # 1. Initialize git submodules
        print("Initializing git submodules...")
        self.submodule_handler.ensure_submodules()
        
        # 2. Detect available features
        print("Detecting available features...")
        features = self.feature_detector.detect_all_features()
        self._print_feature_summary(features)
        
        # 3. Generate configuration header
        print("Generating build configuration...")
        self._generate_config_header(features)
        
        # 4. Build extensions
        print("Building C++ extensions...")
        extensions = self.extension_builder.build_all_extensions(features)
        
        # 5. Create wheel using setuptools
        print("Creating wheel...")
        return self._create_wheel_with_setuptools(wheel_directory, extensions, features)
    
    def build_sdist(self, sdist_directory, config_settings=None):
        """Build source distribution."""
        print("Building source distribution...")
        
        # Ensure submodules are included
        self.submodule_handler.ensure_submodules()
        
        # Use setuptools to create sdist
        from setuptools import setup
        from setuptools.command.sdist import sdist
        
        # Create temporary setup.py for sdist
        setup_py_content = self._generate_setup_py_for_sdist()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(setup_py_content)
            setup_py_path = f.name
        
        try:
            # Run sdist command
            sys.argv = ['setup.py', 'sdist', '--dist-dir', sdist_directory]
            exec(compile(open(setup_py_path).read(), setup_py_path, 'exec'))
            
            # Find created sdist
            sdist_files = list(Path(sdist_directory).glob('*.tar.gz'))
            if sdist_files:
                return sdist_files[0].name
            else:
                raise RuntimeError("Failed to create source distribution")
        finally:
            os.unlink(setup_py_path)
    
    def _extract_version(self) -> str:
        """Extract version from C++ header file."""
        version_file = self.project_root / "include" / "nifty" / "nifty_config.hxx"
        version_regex = r"#define NIFTY_VERSION_(MAJOR|MINOR|PATCH)\s+(\d+)"
        
        versions = {}
        with open(version_file) as f:
            for line in f:
                match = re.match(version_regex, line.strip())
                if match:
                    versions[match.group(1).lower()] = int(match.group(2))
        
        if len(versions) != 3:
            raise RuntimeError("Could not extract version from nifty_config.hxx")
        
        return f"{versions['major']}.{versions['minor']}.{versions['patch']}"
    
    def _generate_metadata(self, version: str) -> str:
        """Generate METADATA file content."""
        return f"""Name: nifty
Version: {version}
Summary: Graph-based segmentation algorithms
Author: Thorsten Beier
Author-email: derthorstenbeier@gmail.com
License: MIT
Classifier: Development Status :: 4 - Beta
Classifier: Intended Audience :: Developers
Classifier: Intended Audience :: Science/Research
Classifier: License :: OSI Approved :: MIT License
Classifier: Programming Language :: C++
Classifier: Programming Language :: Python :: 3
Classifier: Topic :: Scientific/Engineering
Requires-Dist: numpy>=1.19.0
Requires-Dist: scikit-image
"""
    
    def _print_feature_summary(self, features: Dict[str, bool]):
        """Print summary of detected features."""
        print("\nFeature Detection Summary:")
        print("=" * 40)
        
        required_features = ["boost", "xtensor", "xtensor_python", "pybind11"]
        optional_features = ["gurobi", "cplex", "glpk", "hdf5", "z5", "lp_mp", "qpbo"]
        
        print("Required features:")
        for feature in required_features:
            status = "✓" if features.get(feature, False) else "✗"
            print(f"  {status} {feature}")
        
        print("\nOptional features:")
        for feature in optional_features:
            status = "✓" if features.get(feature, False) else "✗"
            print(f"  {status} {feature}")
        
        print("=" * 40)
    
    def _generate_config_header(self, features: Dict[str, bool]):
        """Generate build configuration header."""
        config_dir = self.project_root / "build" / "config"
        config_dir.mkdir(parents=True, exist_ok=True)
        
        header_content = [
            "#pragma once",
            "// Auto-generated build configuration",
            "// DO NOT EDIT MANUALLY",
            "",
        ]
        
        # Add feature macros
        for feature, available in features.items():
            if available:
                macro_name = f"WITH_{feature.upper()}"
                header_content.append(f"#define {macro_name}")
        
        # Add version information
        version_parts = self._extract_version().split('.')
        header_content.extend([
            "",
            f"#define NIFTY_VERSION_MAJOR {version_parts[0]}",
            f"#define NIFTY_VERSION_MINOR {version_parts[1]}",
            f"#define NIFTY_VERSION_PATCH {version_parts[2]}",
        ])
        
        config_header = config_dir / "nifty_build_config.h"
        config_header.write_text("\n".join(header_content))
        
        return str(config_header)
    
    def _create_wheel_with_setuptools(self, wheel_directory: str, extensions: List[Pybind11Extension], features: Dict[str, bool]) -> str:
        """Create wheel using setuptools."""
        from setuptools import setup, find_packages
        from setuptools.command.build_ext import build_ext
        
        # Prepare package data
        package_data = {}
        packages = find_packages(where="src/python/module")
        
        # Create setup configuration
        setup_kwargs = {
            "name": "nifty",
            "version": self._extract_version(),
            "packages": packages,
            "package_dir": {"": "src/python/module"},
            "ext_modules": extensions,
            "zip_safe": False,
            "python_requires": ">=3.8",
            "install_requires": [
                "numpy>=1.19.0",
                "scikit-image",
            ],
        }
        
        # Build wheel
        wheel_path = self._run_setuptools_build_wheel(wheel_directory, setup_kwargs)
        
        return wheel_path


class FeatureDetector:
    """Detect available system dependencies and optional features."""
    
    def detect_all_features(self) -> Dict[str, bool]:
        """Detect all available features."""
        features = {}
        
        # Core dependencies (required)
        features.update(self._detect_core_dependencies())
        
        # Optional dependencies
        features.update(self._detect_optional_dependencies())
        
        return features
    
    def _detect_core_dependencies(self) -> Dict[str, bool]:
        """Detect required core dependencies."""
        return {
            "boost": self._detect_boost(),
            "xtensor": self._detect_xtensor(),
            "xtensor_python": self._detect_xtensor_python(),
            "pybind11": True,  # Always available as build requirement
            "numpy": True,     # Always available as build requirement
        }
    
    def _detect_optional_dependencies(self) -> Dict[str, bool]:
        """Detect optional dependencies."""
        return {
            "gurobi": self._detect_gurobi(),
            "cplex": self._detect_cplex(),
            "glpk": self._detect_glpk(),
            "hdf5": self._detect_hdf5(),
            "z5": self._detect_z5(),
            "lp_mp": self._detect_lp_mp(),
            "qpbo": self._detect_qpbo(),
            "openmp": self._detect_openmp(),
        }
    
    def _detect_boost(self) -> bool:
        """Detect Boost libraries."""
        # Try pkg-config first
        try:
            result = subprocess.run(
                ["pkg-config", "--exists", "boost"],
                capture_output=True, check=False
            )
            if result.returncode == 0:
                return True
        except FileNotFoundError:
            pass
        
        # Try common installation paths
        common_paths = [
            "/usr/include/boost",
            "/usr/local/include/boost",
            "/opt/homebrew/include/boost",  # macOS Homebrew
            "C:/boost",  # Windows
        ]
        
        for path in common_paths:
            if Path(path).exists():
                return True
        
        return False
    
    def _detect_xtensor(self) -> bool:
        """Detect xtensor library."""
        try:
            result = subprocess.run(
                ["pkg-config", "--exists", "xtensor"],
                capture_output=True, check=False
            )
            return result.returncode == 0
        except FileNotFoundError:
            # Fallback: check common paths
            common_paths = [
                "/usr/include/xtensor",
                "/usr/local/include/xtensor",
                "/opt/homebrew/include/xtensor",
            ]
            return any(Path(path).exists() for path in common_paths)
    
    def _detect_xtensor_python(self) -> bool:
        """Detect xtensor-python library."""
        try:
            result = subprocess.run(
                ["pkg-config", "--exists", "xtensor-python"],
                capture_output=True, check=False
            )
            if result.returncode == 0:
                return True
        except FileNotFoundError:
            pass
        
        # Check if installed via pip from GitHub source
        try:
            import subprocess
            result = subprocess.run(
                ["python", "-c", "import xtensor_python"],
                capture_output=True, check=False
            )
            return result.returncode == 0
        except:
            return False
    
    def _detect_gurobi(self) -> bool:
        """Detect GUROBI solver."""
        # Check environment variables
        if os.environ.get("GUROBI_HOME"):
            gurobi_path = Path(os.environ["GUROBI_HOME"])
            if (gurobi_path / "include" / "gurobi_c++.h").exists():
                return True
        
        # Check common installation paths
        common_patterns = [
            "/opt/gurobi*/include/gurobi_c++.h",
            "C:/gurobi*/include/gurobi_c++.h",
        ]
        
        for pattern in common_patterns:
            if glob.glob(pattern):
                return True
        
        return False
    
    def _detect_cplex(self) -> bool:
        """Detect CPLEX solver."""
        # Check environment variables
        if os.environ.get("CPLEX_ROOT_DIR"):
            cplex_path = Path(os.environ["CPLEX_ROOT_DIR"])
            if (cplex_path / "include" / "ilcplex").exists():
                return True
        
        return False
    
    def _detect_glpk(self) -> bool:
        """Detect GLPK solver."""
        try:
            result = subprocess.run(
                ["pkg-config", "--exists", "glpk"],
                capture_output=True, check=False
            )
            return result.returncode == 0
        except FileNotFoundError:
            return False
    
    def _detect_hdf5(self) -> bool:
        """Detect HDF5 library."""
        try:
            result = subprocess.run(
                ["pkg-config", "--exists", "hdf5"],
                capture_output=True, check=False
            )
            return result.returncode == 0
        except FileNotFoundError:
            return False
    
    def _detect_z5(self) -> bool:
        """Detect Z5 library."""
        # Z5 is typically installed via conda or pip
        try:
            import z5py
            return True
        except ImportError:
            return False
    
    def _detect_lp_mp(self) -> bool:
        """Detect LP_MP availability (via git submodule)."""
        lp_mp_path = Path("externals/LP_MP")
        return lp_mp_path.exists() and (lp_mp_path / "include").exists()
    
    def _detect_qpbo(self) -> bool:
        """Detect QPBO availability (via git submodule)."""
        qpbo_path = Path("externals/qpbo")
        return qpbo_path.exists() and list(qpbo_path.glob("*.h"))
    
    def _detect_openmp(self) -> bool:
        """Detect OpenMP support."""
        # Simple test compilation
        test_code = """
        #include <omp.h>
        int main() { return omp_get_num_threads(); }
        """
        
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.cpp', delete=False) as f:
                f.write(test_code)
                test_file = f.name
            
            result = subprocess.run(
                ["c++", "-fopenmp", test_file, "-o", "/dev/null"],
                capture_output=True, check=False
            )
            
            return result.returncode == 0
        except Exception:
            return False
        finally:
            try:
                os.unlink(test_file)
            except:
                pass


class SubmoduleHandler:
    """Handle git submodules for external dependencies."""
    
    def __init__(self):
        self.submodules = {
            "externals/LP_MP": {
                "url": "https://github.com/pawelswoboda/LP_MP.git",
            },
            "externals/qpbo": {
                "url": "https://github.com/DerThorsten/qpbo",
            },
        }
    
    def ensure_submodules(self):
        """Ensure all required submodules are available."""
        for submodule_path in self.submodules:
            if not Path(submodule_path).exists():
                self._initialize_submodule(submodule_path)
    
    def _initialize_submodule(self, submodule_path: str):
        """Initialize a git submodule."""
        try:
            print(f"Initializing submodule: {submodule_path}")
            subprocess.run(
                ["git", "submodule", "update", "--init", "--recursive", submodule_path],
                check=True,
                cwd=Path.cwd()
            )
        except subprocess.CalledProcessError:
            # Fallback: clone directly
            config = self.submodules[submodule_path]
            print(f"Fallback: cloning {config['url']} to {submodule_path}")
            subprocess.run(
                ["git", "clone", config["url"], submodule_path],
                check=True
            )


class ExtensionBuilder:
    """Build C++ extensions with proper dependency handling."""
    
    def __init__(self):
        self.extensions_config = self._load_extensions_config()
    
    def build_all_extensions(self, available_features: Dict[str, bool]) -> List[Pybind11Extension]:
        """Build all extensions based on available features."""
        extensions = []
        
        for ext_name, ext_config in self.extensions_config.items():
            # Check if extension can be built
            if not self._can_build_extension(ext_config, available_features):
                if not ext_config.get("optional", False):
                    raise RuntimeError(f"Required extension {ext_name} cannot be built")
                print(f"Skipping optional extension: {ext_name}")
                continue
            
            # Build extension
            print(f"Building extension: {ext_name}")
            extension = self._build_extension(ext_name, ext_config, available_features)
            extensions.append(extension)
        
        return extensions
    
    def _load_extensions_config(self) -> Dict[str, Dict]:
        """Load extension configuration."""
        return {
            "nifty._nifty": {
                "sources": ["src/python/lib/nifty.cxx"],
                "include_dirs": ["include"],
                "dependencies": ["boost", "xtensor", "pybind11"],
                "optional_dependencies": ["gurobi", "cplex", "glpk"],
            },
            
            "nifty.graph._graph": {
                "sources": [
                    "src/python/lib/graph/graph.cxx",
                    "src/python/lib/graph/undirected_list_graph.cxx",
                    "src/python/lib/graph/undirected_grid_graph.cxx",
                    "src/python/lib/graph/edge_weighted_watersheds.cxx",
                    "src/python/lib/graph/node_weighted_watersheds.cxx",
                    "src/python/lib/graph/edge_contraction_graph_undirected_graph.cxx",
                    "src/python/lib/graph/export_shortest_path_dijkstra.cxx",
                    "src/python/lib/graph/connected_components.cxx",
                    "src/python/lib/graph/label_propagation.cxx",
                    "src/python/lib/graph/accumulate_long_range_affinities.cxx",
                ],
                "include_dirs": ["include"],
                "dependencies": ["boost", "xtensor", "pybind11"],
                "optional_dependencies": ["hdf5"],
            },
            
            "nifty.hdf5._hdf5": {
                "sources": ["src/python/lib/hdf5/hdf5.cxx"],
                "include_dirs": ["include"],
                "dependencies": ["boost", "xtensor", "pybind11", "hdf5"],
                "optional": True,
            },
        }
    
    def _can_build_extension(self, ext_config: Dict, features: Dict[str, bool]) -> bool:
        """Check if extension can be built with available features."""
        # Check required dependencies
        for dep in ext_config.get("dependencies", []):
            if not features.get(dep, False):
                return False
        
        return True
    
    def _build_extension(self, name: str, config: Dict, features: Dict[str, bool]) -> Pybind11Extension:
        """Build a single extension."""
        # Collect sources
        sources = config["sources"].copy()
        
        # Collect include directories
        include_dirs = config["include_dirs"].copy()
        include_dirs.append(np.get_include())
        include_dirs.append(pybind11.get_include())
        
        # Add system include directories
        include_dirs.extend(self._get_system_include_dirs(features))
        
        # Collect compile flags
        compile_flags = []
        compile_flags.extend(self._get_feature_compile_flags(features))
        
        # Collect link libraries
        link_libraries = []
        link_libraries.extend(self._get_feature_link_libraries(features))
        
        # Create extension
        extension = Pybind11Extension(
            name,
            sources=sources,
            include_dirs=include_dirs,
            cxx_std=17,
            define_macros=self._get_feature_macros(features),
            libraries=link_libraries,
        )
        
        return extension
    
    def _get_system_include_dirs(self, features: Dict[str, bool]) -> List[str]:
        """Get system include directories based on available features."""
        include_dirs = []
        
        if features.get("boost"):
            # Add boost include directories
            boost_paths = [
                "/usr/include",
                "/usr/local/include",
                "/opt/homebrew/include",
            ]
            include_dirs.extend(boost_paths)
        
        return include_dirs
    
    def _get_feature_compile_flags(self, features: Dict[str, bool]) -> List[str]:
        """Get compile flags based on available features."""
        flags = []
        
        if features.get("openmp"):
            flags.append("-fopenmp")
        
        return flags
    
    def _get_feature_link_libraries(self, features: Dict[str, bool]) -> List[str]:
        """Get link libraries based on available features."""
        libraries = []
        
        if features.get("openmp"):
            libraries.append("gomp")
        
        return libraries
    
    def _get_feature_macros(self, features: Dict[str, bool]) -> List[Tuple[str, str]]:
        """Get preprocessor macros based on available features."""
        macros = []
        
        for feature, available in features.items():
            if available:
                macro_name = f"WITH_{feature.upper()}"
                macros.append((macro_name, "1"))
        
        return macros
```

## 4. Runtime Configuration Module

```python
# src/python/module/nifty/configuration.py
"""Runtime configuration and feature detection for NIFTY."""

import importlib
import warnings
from typing import Dict, Optional, Any


class RuntimeConfiguration:
    """Runtime feature detection and configuration."""
    
    def __init__(self):
        self._feature_cache = {}
        self._build_config = self._load_build_config()
    
    def _load_build_config(self) -> Dict[str, bool]:
        """Load build-time configuration."""
        try:
            from . import _nifty
            # Access build-time configuration from C++ module
            config_obj = _nifty.Configuration()
            return {
                "gurobi": config_obj.WITH_GUROBI,
                "cplex": config_obj.WITH_CPLEX,
                "glpk": config_obj.WITH_GLPK,
                "hdf5": config_obj.WITH_HDF5,
                "z5": config_obj.WITH_Z5,
                "lp_mp": config_obj.WITH_LP_MP,
                "qpbo": config_obj.WITH_QPBO,
                "fastfilters": config_obj.WITH_FASTFILTERS,
            }
        except ImportError:
            return {}
    
    @property
    def has_gurobi(self) -> bool:
        """Check if GUROBI is available."""
        if "gurobi" not in self._feature_cache:
            self._feature_cache["gurobi"] = self._check_gurobi()
        return self._feature_cache["gurobi"]
    
    def _check_gurobi(self) -> bool:
        """Check GUROBI availability."""
        # Check build-time availability
        if not self._build_config.get("gurobi", False):
            return False
        
        # Check runtime availability
        try:
            import gurobipy
            return True
        except ImportError:
            return False
    
    @property
    def has_cplex(self) -> bool:
        """Check if CPLEX is available."""
        if "cplex" not in self._feature_cache:
            self._feature_cache["cplex"] = self._check_cplex()
        return self._feature_cache["cplex"]
    
    def _check_cplex(self) -> bool:
        