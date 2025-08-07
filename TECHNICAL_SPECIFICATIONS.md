# NIFTY Setuptools Migration - Technical Specifications

## 1. Custom Build Backend Architecture

### Build Backend Interface
```python
# nifty_build_backend.py
import os
import sys
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any
import pybind11
from pybind11.setup_helpers import Pybind11Extension, build_ext

class NiftyBuildBackend:
    """Custom build backend for NIFTY project."""
    
    def __init__(self):
        self.feature_detector = FeatureDetector()
        self.submodule_handler = SubmoduleHandler()
        self.extension_builder = ExtensionBuilder()
    
    def get_requires_for_build_wheel(self, config_settings=None):
        """Return build requirements."""
        return [
            "setuptools>=64",
            "pybind11>=2.10.0",
            "numpy>=1.19.0",
            "wheel",
        ]
    
    def prepare_metadata_for_build_wheel(self, metadata_directory, config_settings=None):
        """Prepare metadata for wheel build."""
        # Generate METADATA file with dynamic version
        version = self._extract_version()
        metadata_content = self._generate_metadata(version)
        
        metadata_path = Path(metadata_directory) / "METADATA"
        metadata_path.write_text(metadata_content)
        
        return metadata_path.name
    
    def build_wheel(self, wheel_directory, config_settings=None, metadata_directory=None):
        """Build wheel package."""
        # 1. Initialize git submodules
        self.submodule_handler.ensure_submodules()
        
        # 2. Detect available features
        features = self.feature_detector.detect_all_features()
        
        # 3. Generate configuration header
        self._generate_config_header(features)
        
        # 4. Build extensions
        extensions = self.extension_builder.build_all_extensions(features)
        
        # 5. Create wheel
        return self._create_wheel(wheel_directory, extensions)
```

### Feature Detection System
```python
class FeatureDetector:
    """Detect available system dependencies and optional features."""
    
    def __init__(self):
        self.detected_features = {}
        self.system_info = self._get_system_info()
    
    def detect_all_features(self) -> Dict[str, bool]:
        """Detect all available features."""
        features = {}
        
        # Core dependencies (required)
        features.update(self._detect_core_dependencies())
        
        # Optional dependencies
        features.update(self._detect_optional_dependencies())
        
        # Compiler features
        features.update(self._detect_compiler_features())
        
        return features
    
    def _detect_core_dependencies(self) -> Dict[str, bool]:
        """Detect required core dependencies."""
        return {
            "boost": self._detect_boost(),
            "xtensor": self._detect_xtensor(),
            "xtensor_python": self._detect_xtensor_python(),
            "pybind11": self._detect_pybind11(),
        }
    
    def _detect_optional_dependencies(self) -> Dict[str, bool]:
        """Detect optional dependencies."""
        return {
            "gurobi": self._detect_gurobi(),
            "cplex": self._detect_cplex(),
            "glpk": self._detect_glpk(),
            "hdf5": self._detect_hdf5(),
            "z5": self._detect_z5(),
            "fastfilters": self._detect_fastfilters(),
        }
    
    def _detect_boost(self) -> bool:
        """Detect Boost libraries."""
        try:
            # Try pkg-config first
            result = subprocess.run(
                ["pkg-config", "--exists", "boost"],
                capture_output=True, check=False
            )
            if result.returncode == 0:
                return True
            
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
        except Exception:
            return False
    
    def _detect_gurobi(self) -> bool:
        """Detect GUROBI solver."""
        # Check environment variables
        if os.environ.get("GUROBI_HOME"):
            gurobi_path = Path(os.environ["GUROBI_HOME"])
            if (gurobi_path / "include" / "gurobi_c++.h").exists():
                return True
        
        # Check common installation paths
        common_paths = [
            "/opt/gurobi*/include",
            "C:/gurobi*/include",
        ]
        
        import glob
        for pattern in common_paths:
            if glob.glob(pattern):
                return True
        
        return False
```

## 2. Extension Building System

### Extension Configuration
```python
class ExtensionBuilder:
    """Build C++ extensions with proper dependency handling."""
    
    def __init__(self):
        self.extensions_config = self._load_extensions_config()
        self.build_order = self._compute_build_order()
    
    def _load_extensions_config(self) -> Dict[str, Dict]:
        """Load extension configuration."""
        return {
            "nifty._nifty": {
                "sources": ["src/python/lib/nifty.cxx"],
                "include_dirs": ["include"],
                "dependencies": ["boost", "xtensor", "pybind11"],
                "optional_dependencies": ["gurobi", "cplex", "glpk"],
                "compile_flags": [],
                "link_libraries": [],
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
            
            "nifty.graph.opt.multicut._multicut": {
                "sources": [
                    "src/python/lib/graph/opt/multicut/multicut.cxx",
                    "src/python/lib/graph/opt/multicut/multicut_objective.cxx",
                    "src/python/lib/graph/opt/multicut/multicut_visitor_base.cxx",
                    "src/python/lib/graph/opt/multicut/multicut_base.cxx",
                    "src/python/lib/graph/opt/multicut/multicut_factory.cxx",
                    "src/python/lib/graph/opt/multicut/multicut_ilp.cxx",
                    "src/python/lib/graph/opt/multicut/multicut_decomposer.cxx",
                    "src/python/lib/graph/opt/multicut/multicut_greedy_additive.cxx",
                    "src/python/lib/graph/opt/multicut/multicut_greedy_fixation.cxx",
                    "src/python/lib/graph/opt/multicut/fusion_move_based.cxx",
                    "src/python/lib/graph/opt/multicut/cc_fusion_move_based.cxx",
                    "src/python/lib/graph/opt/multicut/perturb_and_map.cxx",
                    "src/python/lib/graph/opt/multicut/chained_solvers.cxx",
                    "src/python/lib/graph/opt/multicut/cgc.cxx",
                    "src/python/lib/graph/opt/multicut/kernighan_lin.cxx",
                ],
                "include_dirs": ["include"],
                "dependencies": ["boost", "xtensor", "pybind11"],
                "optional_dependencies": ["gurobi", "cplex", "glpk"],
            },
            
            "nifty.hdf5._hdf5": {
                "sources": ["src/python/lib/hdf5/hdf5.cxx"],
                "include_dirs": ["include"],
                "dependencies": ["boost", "xtensor", "pybind11", "hdf5"],
                "optional": True,
            },
            
            "nifty.z5._z5": {
                "sources": ["src/python/lib/z5/z5.cxx"],
                "include_dirs": ["include"],
                "dependencies": ["boost", "xtensor", "pybind11", "z5"],
                "optional": True,
            },
        }
    
    def build_all_extensions(self, available_features: Dict[str, bool]) -> List[Pybind11Extension]:
        """Build all extensions based on available features."""
        extensions = []
        
        for ext_name in self.build_order:
            ext_config = self.extensions_config[ext_name]
            
            # Check if extension can be built
            if not self._can_build_extension(ext_config, available_features):
                if not ext_config.get("optional", False):
                    raise RuntimeError(f"Required extension {ext_name} cannot be built")
                continue
            
            # Build extension
            extension = self._build_extension(ext_name, ext_config, available_features)
            extensions.append(extension)
        
        return extensions
    
    def _build_extension(self, name: str, config: Dict, features: Dict[str, bool]) -> Pybind11Extension:
        """Build a single extension."""
        # Collect sources
        sources = config["sources"].copy()
        
        # Add submodule sources if needed
        if "lp_mp" in config.get("optional_dependencies", []) and features.get("lp_mp"):
            sources.extend(self._get_lp_mp_sources())
        
        if "qpbo" in config.get("optional_dependencies", []) and features.get("qpbo"):
            sources.extend(self._get_qpbo_sources())
        
        # Collect include directories
        include_dirs = config["include_dirs"].copy()
        include_dirs.extend(self._get_system_include_dirs(features))
        
        # Collect compile flags
        compile_flags = config.get("compile_flags", []).copy()
        compile_flags.extend(self._get_feature_compile_flags(features))
        
        # Collect link libraries
        link_libraries = config.get("link_libraries", []).copy()
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
```

## 3. Git Submodule Integration

### Submodule Handler
```python
class SubmoduleHandler:
    """Handle git submodules for external dependencies."""
    
    def __init__(self):
        self.submodules = {
            "externals/LP_MP": {
                "url": "https://github.com/pawelswoboda/LP_MP.git",
                "sources": [
                    "lib/**/*.cpp",
                    "lib/**/*.cxx",
                ],
                "include_dirs": [
                    "include",
                    "lib",
                    "external/meta/include",
                    "external/Catch/include",
                    "external/cpp_sort/include",
                    "external/opengm/include",
                    "external/PEGTL",
                    "external/cereal/include",
                    "external/tclap/include",
                ],
                "compile_flags": ["-DLP_MP_PARALLEL"],
                "required_features": ["openmp"],
            },
            
            "externals/qpbo": {
                "url": "https://github.com/DerThorsten/qpbo",
                "sources": ["*.cpp"],
                "include_dirs": ["."],
                "compile_flags": [],
            },
        }
    
    def ensure_submodules(self):
        """Ensure all required submodules are available."""
        for submodule_path, config in self.submodules.items():
            if not Path(submodule_path).exists():
                self._initialize_submodule(submodule_path)
            elif not self._is_submodule_updated(submodule_path):
                self._update_submodule(submodule_path)
    
    def _initialize_submodule(self, submodule_path: str):
        """Initialize a git submodule."""
        try:
            subprocess.run(
                ["git", "submodule", "update", "--init", "--recursive", submodule_path],
                check=True,
                cwd=Path.cwd()
            )
        except subprocess.CalledProcessError as e:
            # Fallback: clone directly
            config = self.submodules[submodule_path]
            subprocess.run(
                ["git", "clone", config["url"], submodule_path],
                check=True
            )
    
    def get_submodule_sources(self, submodule_path: str) -> List[str]:
        """Get source files from a submodule."""
        config = self.submodules[submodule_path]
        sources = []
        
        base_path = Path(submodule_path)
        for pattern in config["sources"]:
            sources.extend(glob.glob(str(base_path / pattern), recursive=True))
        
        return sources
    
    def get_submodule_includes(self, submodule_path: str) -> List[str]:
        """Get include directories from a submodule."""
        config = self.submodules[submodule_path]
        base_path = Path(submodule_path)
        
        return [str(base_path / inc_dir) for inc_dir in config["include_dirs"]]
```

## 4. Configuration Generation

### Dynamic Configuration Header
```python
def generate_config_header(features: Dict[str, bool]) -> str:
    """Generate nifty_build_config.h with detected features."""
    
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
    version = extract_version_from_header()
    header_content.extend([
        "",
        f"#define NIFTY_VERSION_MAJOR {version['major']}",
        f"#define NIFTY_VERSION_MINOR {version['minor']}",
        f"#define NIFTY_VERSION_PATCH {version['patch']}",
    ])
    
    # Add compiler information
    header_content.extend([
        "",
        f"#define NIFTY_CXX_STANDARD 17",
        f"#define NIFTY_BUILD_TYPE \"Release\"",
    ])
    
    return "\n".join(header_content)

def extract_version_from_header() -> Dict[str, int]:
    """Extract version from C++ header."""
    version_file = Path("include/nifty/nifty_config.hxx")
    version_regex = r"#define NIFTY_VERSION_(MAJOR|MINOR|PATCH)\s+(\d+)"
    
    versions = {}
    with open(version_file) as f:
        for line in f:
            match = re.match(version_regex, line.strip())
            if match:
                versions[match.group(1).lower()] = int(match.group(2))
    
    return versions
```

## 5. Runtime Feature Detection

### Python Runtime Configuration
```python
# nifty/configuration.py
"""Runtime configuration and feature detection."""

import importlib
import warnings
from typing import Dict, Optional

class RuntimeConfiguration:
    """Runtime feature detection and configuration."""
    
    def __init__(self):
        self._feature_cache = {}
        self._build_config = self._load_build_config()
    
    def _load_build_config(self) -> Dict[str, bool]:
        """Load build-time configuration."""
        try:
            from . import _build_config
            return _build_config.FEATURES
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
        """Check CPLEX availability."""
        if not self._build_config.get("cplex", False):
            return False
        
        try:
            import cplex
            return True
        except ImportError:
            return False
    
    @property
    def has_hdf5(self) -> bool:
        """Check if HDF5 is available."""
        if "hdf5" not in self._feature_cache:
            self._feature_cache["hdf5"] = self._check_hdf5()
        return self._feature_cache["hdf5"]
    
    def _check_hdf5(self) -> bool:
        """Check HDF5 availability."""
        if not self._build_config.get("hdf5", False):
            return False
        
        try:
            import h5py
            return True
        except ImportError:
            return False
    
    def get_available_features(self) -> Dict[str, bool]:
        """Get all available features."""
        return {
            "gurobi": self.has_gurobi,
            "cplex": self.has_cplex,
            "glpk": self.has_glpk,
            "hdf5": self.has_hdf5,
            "z5": self.has_z5,
            "lp_mp": self.has_lp_mp,
            "qpbo": self.has_qpbo,
        }
    
    def require_feature(self, feature: str) -> None:
        """Require a specific feature, raise error if not available."""
        if not getattr(self, f"has_{feature}", False):
            raise ImportError(
                f"Feature '{feature}' is not available. "
                f"Please install the required dependencies."
            )

# Global configuration instance
config = RuntimeConfiguration()
```

## 6. Wheel Building Pipeline

### Cross-platform Build Configuration
```python
class WheelBuilder:
    """Build wheels for different platforms."""
    
    def __init__(self):
        self.platform_configs = {
            "linux": {
                "compiler_flags": ["-fPIC", "-O3"],
                "linker_flags": ["-Wl,--strip-all"],
                "libraries": ["stdc++fs"],
            },
            "darwin": {
                "compiler_flags": ["-fPIC", "-O3"],
                "linker_flags": ["-Wl,-dead_strip"],
                "libraries": ["c++experimental"],
            },
            "win32": {
                "compiler_flags": ["/O2", "/DNOMINMAX"],
                "linker_flags": [],
                "libraries": [],
            },
        }
    
    def build_wheel(self, wheel_directory: str, config_settings: Optional[Dict] = None) -> str:
        """Build wheel for current platform."""
        platform = self._detect_platform()
        platform_config = self.platform_configs[platform]
        
        # Configure build environment
        self._setup_build_environment(platform_config)
        
        # Build extensions
        extensions = self._build_extensions_for_platform(platform)
        
        # Create wheel
        wheel_path = self._create_wheel(wheel_directory, extensions)
        
        return wheel_path
    
    def _setup_build_environment(self, platform_config: Dict):
        """Set up platform-specific build environment."""
        # Set compiler flags
        os.environ["CXXFLAGS"] = " ".join([
            os.environ.get("CXXFLAGS", ""),
            *platform_config["compiler_flags"]
        ])
        
        # Set linker flags
        os.environ["LDFLAGS"] = " ".join([
            os.environ.get("LDFLAGS", ""),
            *platform_config["linker_flags"]
        ])
```

This technical specification provides the detailed implementation architecture for the NIFTY setuptools migration, covering all major components from build backend to wheel distribution.