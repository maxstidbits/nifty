"""
NIFTY - N-Dimensional Image Feature Toolkit for Python

A comprehensive toolkit for graph-based image analysis, multicut optimization,
and n-dimensional image processing.
"""

from __future__ import absolute_import
from __future__ import print_function

import os
import re
import sys
import time
import types
import numpy
from pathlib import Path

# Version synchronization
def _extract_version_from_header():
    """Extract version from C++ header file."""
    try:
        # Try to find the header file
        possible_paths = [
            Path(__file__).parent.parent / "include" / "nifty" / "nifty_config.hxx",
            Path(__file__).parent.parent.parent / "include" / "nifty" / "nifty_config.hxx",
            # Fallback for installed package
            Path(__file__).parent / "_version_info.txt"
        ]
        
        for header_path in possible_paths:
            if header_path.exists() and header_path.suffix == ".hxx":
                version_regex = r"#define NIFTY_VERSION_(MAJOR|MINOR|PATCH)\s+(\d+)"
                versions = {}
                
                with open(header_path) as f:
                    for line in f:
                        match = re.match(version_regex, line.strip())
                        if match:
                            versions[match.group(1).lower()] = int(match.group(2))
                
                if len(versions) == 3:
                    return f"{versions['major']}.{versions['minor']}.{versions['patch']}"
            elif header_path.exists() and header_path.suffix == ".txt":
                # Fallback version file for installed packages
                with open(header_path) as f:
                    return f.read().strip()
        
        # If no version found, return a default
        return "1.2.4"
        
    except Exception:
        # Fallback version
        return "1.2.4"

# Set version
__version__ = _extract_version_from_header()

# Import core C++ extension
try:
    from ._nifty import *
    _has_core_extension = True
except ImportError as e:
    _has_core_extension = False
    _import_error = str(e)
    
    # Create a dummy Configuration object for development
    class Configuration:
        WITH_HDF5 = False
        WITH_Z5 = False
        WITH_CPLEX = False
        WITH_GUROBI = False
        WITH_GLPK = False
        WITH_LP_MP = False
        WITH_QPBO = False
        WITH_OPENMP = False
        WITH_FASTFILTERS = False

# Import submodules (with error handling for missing C++ extensions)
try:
    from . import graph
except ImportError as e:
    if _has_core_extension:
        raise
    import warnings
    warnings.warn(f"Could not import graph module: {e}", ImportWarning)

try:
    from . import tools
except ImportError as e:
    if _has_core_extension:
        raise
    import warnings
    warnings.warn(f"Could not import tools module: {e}", ImportWarning)

try:
    from . import ufd
except ImportError as e:
    if _has_core_extension:
        raise
    import warnings
    warnings.warn(f"Could not import ufd module: {e}", ImportWarning)

# Conditional imports based on available features
# Import optional modules based on configuration (if available)
try:
    if _has_core_extension and Configuration.WITH_HDF5:
        from . import hdf5
except (ImportError, AttributeError, NameError):
    pass

try:
    if _has_core_extension and Configuration.WITH_Z5:
        from . import z5
except (ImportError, AttributeError, NameError):
    pass

# Import other modules (with graceful handling)
optional_modules = ['carving', 'cgp', 'distributed', 'filters', 'ground_truth',
                   'segmentation', 'skeletons', 'transformation', 'viewer']

for module_name in optional_modules:
    try:
        exec(f"from . import {module_name}")
    except ImportError:
        if _has_core_extension:
            import warnings
            warnings.warn(f"Could not import optional module: {module_name}", ImportWarning)

else:
    import warnings
    warnings.warn(
        f"NIFTY core C++ extension could not be imported: {_import_error}. "
        "Some functionality will be limited. Make sure the package is properly compiled.",
        ImportWarning
    )


class Timer:
    """Timer class for use with context manager (with statement).
    
    Time pieces of code with a with statement timer.
    
    Examples:
        >>> import nifty
        >>> with nifty.Timer() as t:
        ...     import time
        ...     time.sleep(0.1)
        Timer took 0.100... sec
        
        >>> with nifty.Timer("My operation") as t:
        ...     pass
        My operation took 0.000... sec
    
    Args:
        name: Name to print (default: None)
        verbose: Enable printout (default: True)
    """
    
    def __init__(self, name=None, verbose=True):
        self.name = name
        self.verbose = verbose
        self.start_time = None
        self.end_time = None
        self.elapsed_time = None

    def __enter__(self):
        if self.verbose and self.name is not None:
            print(f"{self.name}...")
        
        # Use time.perf_counter() for better precision (Python 3.3+)
        if hasattr(time, 'perf_counter'):
            self.start_time = time.perf_counter()
        else:
            # Fallback for older Python versions
            self.start_time = time.time()
        
        return self

    def __exit__(self, *args):
        if hasattr(time, 'perf_counter'):
            self.end_time = time.perf_counter()
        else:
            self.end_time = time.time()
            
        self.elapsed_time = self.end_time - self.start_time
        
        if self.verbose:
            if self.name is not None:
                print(f"{self.name} took {self.elapsed_time:.6f} sec")
            else:
                print(f"Timer took {self.elapsed_time:.6f} sec")


def get_version_info():
    """Get detailed version information.
    
    Returns:
        dict: Dictionary containing version information
    """
    info = {
        'version': __version__,
        'has_core_extension': _has_core_extension,
    }
    
    if _has_core_extension:
        # Add feature information
        try:
            features = {}
            for attr in dir(Configuration):
                if attr.startswith('WITH_'):
                    features[attr] = getattr(Configuration, attr)
            info['features'] = features
        except NameError:
            info['features'] = {}
    else:
        info['import_error'] = _import_error
        info['features'] = {}
    
    return info


def print_version_info():
    """Print detailed version information."""
    info = get_version_info()
    
    print(f"NIFTY version: {info['version']}")
    print(f"Core extension available: {info['has_core_extension']}")
    
    if not info['has_core_extension']:
        print(f"Import error: {info.get('import_error', 'Unknown')}")
    
    if info['features']:
        print("\nAvailable features:")
        for feature, available in sorted(info['features'].items()):
            status = "✓" if available else "✗"
            feature_name = feature.replace('WITH_', '').lower()
            print(f"  {status} {feature_name}")
    else:
        print("\nNo feature information available")


# Module metadata
__author__ = "NIFTY Development Team"
__email__ = "nifty-dev@example.com"
__license__ = "MIT"
__url__ = "https://github.com/DerThorsten/nifty"

# Export public API
__all__ = [
    '__version__',
    'Timer',
    'get_version_info',
    'print_version_info',
    'graph',
    'tools',
    'ufd',
]

# Add conditional exports
if _has_core_extension:
    try:
        if Configuration.WITH_HDF5:
            __all__.append('hdf5')
    except (NameError, AttributeError):
        pass
    
    try:
        if Configuration.WITH_Z5:
            __all__.append('z5')
    except (NameError, AttributeError):
        pass

# Add other available modules to __all__
for module_name in ['carving', 'cgp', 'distributed', 'filters', 'ground_truth', 
                   'segmentation', 'skeletons', 'transformation', 'viewer']:
    if module_name in sys.modules.get(__name__, {}).__dict__:
        __all__.append(module_name)
