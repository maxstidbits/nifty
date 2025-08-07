#!/usr/bin/env python3
"""
NIFTY setuptools build script with custom C++ extension building.

This setup.py provides:
- Version extraction from C++ header files
- Feature detection for optional dependencies
- Custom build_ext command for C++ extensions
- Git submodule handling
- Cross-platform compilation settings
"""

import os
import sys
import glob
import subprocess
import re
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

# Core build dependencies
import numpy as np
import pybind11
from pybind11.setup_helpers import Pybind11Extension, build_ext
from pybind11 import get_cmake_dir

# Setuptools imports
from setuptools import setup, find_packages, Extension
from setuptools.command.build_ext import build_ext as _build_ext


class VersionExtractor:
    """Extract version information from C++ header files."""
    
    @staticmethod
    def get_version() -> str:
        """Extract version from nifty_config.hxx."""
        version_file = Path("include/nifty/nifty_config.hxx")
        if not version_file.exists():
            raise RuntimeError(f"Version file not found: {version_file}")
        
        version_regex = r"#define NIFTY_VERSION_(MAJOR|MINOR|PATCH)\s+(\d+)"
        versions = {}
        
        with open(version_file) as f:
            for line in f:
                match = re.match(version_regex, line.strip())
                if match:
                    versions[match.group(1).lower()] = int(match.group(2))
        
        if len(versions) != 3:
            raise RuntimeError("Could not extract complete version from nifty_config.hxx")
        
        return f"{versions['major']}.{versions['minor']}.{versions['patch']}"


class FeatureDetector:
    """Detect available system dependencies and optional features."""
    
    def __init__(self):
        self.detected_features = {}
        self.system_info = self._get_system_info()
    
    def _get_system_info(self) -> Dict[str, Any]:
        """Get system information for platform-specific detection."""
        import platform
        return {
            "system": platform.system().lower(),
            "machine": platform.machine().lower(),
            "python_version": sys.version_info,
        }
    
    def detect_all_features(self) -> Dict[str, bool]:
        """Detect all available features."""
        print("Detecting available features...")
        
        features = {}
        
        # Core dependencies (required)
        features.update(self._detect_core_dependencies())
        
        # Optional dependencies
        features.update(self._detect_optional_dependencies())
        
        # Compiler features
        features.update(self._detect_compiler_features())
        
        self._print_feature_summary(features)
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
            "fastfilters": self._detect_fastfilters(),
        }
    
    def _detect_compiler_features(self) -> Dict[str, bool]:
        """Detect compiler-specific features."""
        return {
            "cpp17": self._detect_cpp17(),
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
        except FileNotFoundError:
            pass
        
        # Try common installation paths
        common_paths = [
            "/usr/include/boost",
            "/usr/local/include/boost",
            "/opt/homebrew/include/boost",  # macOS Homebrew
            "C:/boost",  # Windows
            "/opt/conda/include/boost",  # Conda
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
            if result.returncode == 0:
                return True
        except FileNotFoundError:
            pass
        
        # Fallback: check common paths
        common_paths = [
            "/usr/include/xtensor",
            "/usr/local/include/xtensor",
            "/opt/homebrew/include/xtensor",
            "/opt/conda/include/xtensor",
        ]
        return any(Path(path).exists() for path in common_paths)
    
    def _detect_xtensor_python(self) -> bool:
        """Detect xtensor-python library.
        
        Note: This project uses a custom xtensor-python source from:
        https://github.com/maxstidbits/xtensor-python.git
        """
        try:
            result = subprocess.run(
                ["pkg-config", "--exists", "xtensor-python"],
                capture_output=True, check=False
            )
            if result.returncode == 0:
                return True
        except FileNotFoundError:
            pass
        
        # Check for pip-installed xtensor-python (including GitHub source)
        try:
            import site
            site_packages = site.getsitepackages()
            for site_pkg in site_packages:
                xtensor_python_path = Path(site_pkg) / "xtensor_python" / "include" / "xtensor-python"
                if xtensor_python_path.exists():
                    return True
        except Exception:
            pass
        
        # Fallback: check common system paths
        common_paths = [
            "/usr/include/xtensor-python",
            "/usr/local/include/xtensor-python",
            "/opt/homebrew/include/xtensor-python",
            "/opt/conda/include/xtensor-python",
            # Additional paths for pip-installed packages
            str(Path.home() / ".local" / "include" / "xtensor-python"),
        ]
        return any(Path(path).exists() for path in common_paths)
    
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
    
    def _detect_fastfilters(self) -> bool:
        """Detect FastFilters library."""
        try:
            import fastfilters
            return True
        except ImportError:
            return False
    
    def _detect_cpp17(self) -> bool:
        """Detect C++17 support."""
        # Simple test compilation
        test_code = """
        #include <optional>
        int main() { std::optional<int> x; return 0; }
        """
        
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.cpp', delete=False) as f:
                f.write(test_code)
                test_file = f.name
            
            result = subprocess.run(
                ["c++", "-std=c++17", test_file, "-o", "/dev/null"],
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
    
    def _print_feature_summary(self, features: Dict[str, bool]):
        """Print summary of detected features."""
        print("\nFeature Detection Summary:")
        print("=" * 40)
        
        required_features = ["boost", "xtensor", "xtensor_python", "pybind11", "numpy"]
        optional_features = ["gurobi", "cplex", "glpk", "hdf5", "z5", "lp_mp", "qpbo", "openmp", "fastfilters"]
        
        print("Required features:")
        for feature in required_features:
            status = "✓" if features.get(feature, False) else "✗"
            print(f"  {status} {feature}")
        
        print("\nOptional features:")
        for feature in optional_features:
            status = "✓" if features.get(feature, False) else "✗"
            print(f"  {status} {feature}")
        
        print("=" * 40)


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
    
    def __init__(self, features: Dict[str, bool]):
        self.features = features
        self.extensions_config = self._load_extensions_config()
    
    def _load_extensions_config(self) -> Dict[str, Dict]:
        """Load extension configuration."""
        return {
            "nifty._nifty": {
                "sources": ["src/python/lib/nifty.cxx"],
                "include_dirs": ["include"],
                "dependencies": ["boost", "xtensor", "xtensor_python", "pybind11", "numpy"],
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
                "dependencies": ["boost", "xtensor", "xtensor_python", "pybind11", "numpy"],
                "optional_dependencies": ["hdf5"],
            },
            
            "nifty.hdf5._hdf5": {
                "sources": ["src/python/lib/hdf5/hdf5.cxx"],
                "include_dirs": ["include"],
                "dependencies": ["boost", "xtensor", "xtensor_python", "pybind11", "numpy", "hdf5"],
                "optional": True,
            },
            
            "nifty.z5._z5": {
                "sources": ["src/python/lib/z5/z5.cxx"],
                "include_dirs": ["include"],
                "dependencies": ["boost", "xtensor", "xtensor_python", "pybind11", "numpy", "z5"],
                "optional": True,
            },
        }
    
    def build_all_extensions(self) -> List[Pybind11Extension]:
        """Build all extensions based on available features."""
        extensions = []
        
        for ext_name, ext_config in self.extensions_config.items():
            # Check if extension can be built
            if not self._can_build_extension(ext_config):
                if not ext_config.get("optional", False):
                    raise RuntimeError(f"Required extension {ext_name} cannot be built")
                print(f"Skipping optional extension: {ext_name}")
                continue
            
            # Build extension
            print(f"Building extension: {ext_name}")
            extension = self._build_extension(ext_name, ext_config)
            extensions.append(extension)
        
        return extensions
    
    def _can_build_extension(self, ext_config: Dict) -> bool:
        """Check if extension can be built with available features."""
        # Check required dependencies
        for dep in ext_config.get("dependencies", []):
            if not self.features.get(dep, False):
                return False
        
        return True
    
    def _build_extension(self, name: str, config: Dict) -> Pybind11Extension:
        """Build a single extension."""
        # Collect sources
        sources = []
        for source_pattern in config["sources"]:
            if "*" in source_pattern:
                sources.extend(glob.glob(source_pattern))
            else:
                sources.append(source_pattern)
        
        # Collect include directories
        include_dirs = config["include_dirs"].copy()
        include_dirs.append(np.get_include())
        include_dirs.append(pybind11.get_include())
        
        # Add system include directories
        include_dirs.extend(self._get_system_include_dirs())
        
        # Collect compile flags
        compile_flags = []
        compile_flags.extend(self._get_feature_compile_flags())
        
        # Collect link libraries
        link_libraries = []
        link_libraries.extend(self._get_feature_link_libraries())
        
        # Create extension
        extension = Pybind11Extension(
            name,
            sources=sources,
            include_dirs=include_dirs,
            cxx_std=17,
            define_macros=self._get_feature_macros(),
            libraries=link_libraries,
            extra_compile_args=compile_flags,
        )
        
        return extension
    
    def _get_system_include_dirs(self) -> List[str]:
        """Get system include directories based on available features."""
        include_dirs = []
        
        # Add common system paths
        common_paths = [
            "/usr/include",
            "/usr/local/include",
            "/opt/homebrew/include",
            "/opt/conda/include",
        ]
        
        for path in common_paths:
            if Path(path).exists():
                include_dirs.append(path)
        
        # Include site-packages paths for pip-installed packages
        if self.features.get("xtensor_python"):
            try:
                import site
                for site_pkg in site.getsitepackages():
                    xtensor_python_include = Path(site_pkg) / "xtensor_python" / "include"
                    if xtensor_python_include.exists():
                        include_dirs.append(str(xtensor_python_include))
                        print(f"Found xtensor-python include path: {xtensor_python_include}")
                
                # Also check user site-packages for --user installations
                try:
                    user_site = site.getusersitepackages()
                    if user_site:
                        user_xtensor_python_include = Path(user_site) / "xtensor_python" / "include"
                        if user_xtensor_python_include.exists():
                            include_dirs.append(str(user_xtensor_python_include))
                            print(f"Found xtensor-python include path (user): {user_xtensor_python_include}")
                except Exception:
                    # getusersitepackages() might not be available in all environments
                    pass
                    
            except Exception as e:
                print(f"Warning: Could not detect site-packages paths for xtensor-python: {e}")
                # Fallback to common user installation paths
                fallback_paths = [
                    str(Path.home() / ".local" / "lib" / f"python{sys.version_info.major}.{sys.version_info.minor}" / "site-packages" / "xtensor_python" / "include"),
                ]
                for fallback_path in fallback_paths:
                    if Path(fallback_path).exists():
                        include_dirs.append(fallback_path)
                        print(f"Found xtensor-python include path (fallback): {fallback_path}")
        
        return include_dirs
    
    def _get_feature_compile_flags(self) -> List[str]:
        """Get compile flags based on available features."""
        flags = []
        
        if self.features.get("openmp"):
            flags.append("-fopenmp")
        
        # Platform-specific flags
        if sys.platform.startswith("win"):
            flags.extend(["/O2", "/DNOMINMAX"])
        else:
            flags.extend(["-O3", "-fPIC"])
        
        return flags
    
    def _get_feature_link_libraries(self) -> List[str]:
        """Get link libraries based on available features."""
        libraries = []
        
        if self.features.get("openmp"):
            if sys.platform.startswith("win"):
                libraries.append("openmp")
            else:
                libraries.append("gomp")
        
        return libraries
    
    def _get_feature_macros(self) -> List[Tuple[str, str]]:
        """Get preprocessor macros based on available features."""
        macros = []
        
        for feature, available in self.features.items():
            if available:
                macro_name = f"WITH_{feature.upper()}"
                macros.append((macro_name, "1"))
        
        return macros


class CustomBuildExt(build_ext):
    """Custom build_ext command with feature detection and submodule handling."""
    
    def run(self):
        """Run the build process with custom logic."""
        print("Starting NIFTY build process...")
        
        # Initialize git submodules
        print("Ensuring git submodules are available...")
        submodule_handler = SubmoduleHandler()
        submodule_handler.ensure_submodules()
        
        # Detect features
        feature_detector = FeatureDetector()
        features = feature_detector.detect_all_features()
        
        # Generate configuration header
        self._generate_config_header(features)
        
        # Build extensions
        extension_builder = ExtensionBuilder(features)
        extensions = extension_builder.build_all_extensions()
        
        # Update distribution extensions
        self.distribution.ext_modules = extensions
        
        # Run standard build process
        super().run()
    
    def _generate_config_header(self, features: Dict[str, bool]):
        """Generate build configuration header."""
        config_dir = Path("build") / "config"
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
        version = VersionExtractor.get_version()
        version_parts = version.split('.')
        header_content.extend([
            "",
            f"#define NIFTY_VERSION_MAJOR {version_parts[0]}",
            f"#define NIFTY_VERSION_MINOR {version_parts[1]}",
            f"#define NIFTY_VERSION_PATCH {version_parts[2]}",
        ])
        
        config_header = config_dir / "nifty_build_config.h"
        config_header.write_text("\n".join(header_content))
        
        print(f"Generated configuration header: {config_header}")


def main():
    """Main setup function."""
    # Extract version
    version = VersionExtractor.get_version()
    
    # Find packages
    packages = find_packages(where=".")
    packages = [pkg for pkg in packages if pkg.startswith("nifty")]
    
    # Setup configuration
    setup(
        name="nifty",
        version=version,
        packages=packages,
        package_dir={},
        zip_safe=False,
        include_package_data=True,
        cmdclass={
            "build_ext": CustomBuildExt,
        },
        # Extensions will be dynamically added by CustomBuildExt
        ext_modules=[],
    )


if __name__ == "__main__":
    main()