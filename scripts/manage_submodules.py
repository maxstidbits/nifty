#!/usr/bin/env python3
"""
Git submodule management script for NIFTY project.

This script provides utilities to initialize, update, and manage git submodules
required for the NIFTY project, specifically LP_MP and QPBO.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
from typing import Dict, List, Optional


class SubmoduleManager:
    """Manage git submodules for NIFTY project."""
    
    def __init__(self, project_root: Optional[Path] = None):
        """Initialize submodule manager.
        
        Args:
            project_root: Path to project root. If None, uses current directory.
        """
        self.project_root = project_root or Path.cwd()
        self.submodules = {
            "externals/LP_MP": {
                "url": "https://github.com/pawelswoboda/LP_MP.git",
                "description": "LP_MP - Linear Programming Message Passing solver",
            },
            "externals/qpbo": {
                "url": "https://github.com/DerThorsten/qpbo",
                "description": "QPBO - Quadratic Pseudo-Boolean Optimization",
            },
        }
    
    def check_git_repository(self) -> bool:
        """Check if we're in a git repository."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                cwd=self.project_root,
                capture_output=True,
                check=True
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def get_submodule_status(self) -> Dict[str, Dict[str, str]]:
        """Get status of all submodules."""
        status = {}
        
        for submodule_path in self.submodules:
            full_path = self.project_root / submodule_path
            config = self.submodules[submodule_path]
            
            if not full_path.exists():
                status[submodule_path] = {
                    "status": "missing",
                    "description": config["description"],
                    "url": config["url"]
                }
            elif not (full_path / ".git").exists():
                status[submodule_path] = {
                    "status": "not_initialized",
                    "description": config["description"],
                    "url": config["url"]
                }
            else:
                # Check if it's up to date
                try:
                    result = subprocess.run(
                        ["git", "submodule", "status", submodule_path],
                        cwd=self.project_root,
                        capture_output=True,
                        text=True,
                        check=True
                    )
                    output = result.stdout.strip()
                    if output.startswith("-"):
                        status[submodule_path] = {
                            "status": "not_initialized",
                            "description": config["description"],
                            "url": config["url"]
                        }
                    elif output.startswith("+"):
                        status[submodule_path] = {
                            "status": "modified",
                            "description": config["description"],
                            "url": config["url"]
                        }
                    else:
                        status[submodule_path] = {
                            "status": "up_to_date",
                            "description": config["description"],
                            "url": config["url"]
                        }
                except subprocess.CalledProcessError:
                    status[submodule_path] = {
                        "status": "error",
                        "description": config["description"],
                        "url": config["url"]
                    }
        
        return status
    
    def initialize_submodule(self, submodule_path: str, force: bool = False) -> bool:
        """Initialize a specific submodule.
        
        Args:
            submodule_path: Path to the submodule
            force: Force re-initialization if already exists
            
        Returns:
            True if successful, False otherwise
        """
        if submodule_path not in self.submodules:
            print(f"Error: Unknown submodule '{submodule_path}'")
            return False
        
        config = self.submodules[submodule_path]
        full_path = self.project_root / submodule_path
        
        print(f"Initializing submodule: {submodule_path}")
        print(f"Description: {config['description']}")
        print(f"URL: {config['url']}")
        
        # Remove existing directory if force is True
        if force and full_path.exists():
            import shutil
            print(f"Removing existing directory: {full_path}")
            shutil.rmtree(full_path)
        
        try:
            # Try git submodule update first
            result = subprocess.run(
                ["git", "submodule", "update", "--init", "--recursive", submodule_path],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=True
            )
            print(f"✓ Successfully initialized submodule: {submodule_path}")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"Git submodule command failed: {e}")
            print("Falling back to direct clone...")
            
            # Fallback: clone directly
            try:
                # Ensure parent directory exists
                full_path.parent.mkdir(parents=True, exist_ok=True)
                
                result = subprocess.run(
                    ["git", "clone", config["url"], str(full_path)],
                    capture_output=True,
                    text=True,
                    check=True
                )
                print(f"✓ Successfully cloned submodule: {submodule_path}")
                return True
                
            except subprocess.CalledProcessError as e:
                print(f"✗ Failed to clone submodule: {e}")
                if e.stderr:
                    print(f"Error output: {e.stderr}")
                return False
    
    def initialize_all_submodules(self, force: bool = False) -> bool:
        """Initialize all submodules.
        
        Args:
            force: Force re-initialization of existing submodules
            
        Returns:
            True if all successful, False if any failed
        """
        print("Initializing all submodules...")
        success = True
        
        for submodule_path in self.submodules:
            if not self.initialize_submodule(submodule_path, force):
                success = False
        
        return success
    
    def update_submodule(self, submodule_path: str) -> bool:
        """Update a specific submodule to latest commit.
        
        Args:
            submodule_path: Path to the submodule
            
        Returns:
            True if successful, False otherwise
        """
        if submodule_path not in self.submodules:
            print(f"Error: Unknown submodule '{submodule_path}'")
            return False
        
        full_path = self.project_root / submodule_path
        if not full_path.exists():
            print(f"Submodule not initialized: {submodule_path}")
            return self.initialize_submodule(submodule_path)
        
        print(f"Updating submodule: {submodule_path}")
        
        try:
            result = subprocess.run(
                ["git", "submodule", "update", "--remote", submodule_path],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=True
            )
            print(f"✓ Successfully updated submodule: {submodule_path}")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to update submodule: {e}")
            if e.stderr:
                print(f"Error output: {e.stderr}")
            return False
    
    def update_all_submodules(self) -> bool:
        """Update all submodules.
        
        Returns:
            True if all successful, False if any failed
        """
        print("Updating all submodules...")
        success = True
        
        for submodule_path in self.submodules:
            if not self.update_submodule(submodule_path):
                success = False
        
        return success
    
    def print_status(self):
        """Print status of all submodules."""
        print("Submodule Status:")
        print("=" * 60)
        
        status = self.get_submodule_status()
        
        for submodule_path, info in status.items():
            status_symbol = {
                "up_to_date": "✓",
                "missing": "✗",
                "not_initialized": "⚠",
                "modified": "~",
                "error": "✗"
            }.get(info["status"], "?")
            
            status_text = {
                "up_to_date": "Up to date",
                "missing": "Missing",
                "not_initialized": "Not initialized",
                "modified": "Modified",
                "error": "Error"
            }.get(info["status"], "Unknown")
            
            print(f"{status_symbol} {submodule_path}")
            print(f"  Status: {status_text}")
            print(f"  Description: {info['description']}")
            print(f"  URL: {info['url']}")
            print()
    
    def verify_submodules(self) -> bool:
        """Verify that all submodules are properly initialized and contain expected files.
        
        Returns:
            True if all submodules are valid, False otherwise
        """
        print("Verifying submodules...")
        all_valid = True
        
        # LP_MP verification
        lp_mp_path = self.project_root / "externals/LP_MP"
        if lp_mp_path.exists():
            if not (lp_mp_path / "include").exists():
                print("✗ LP_MP: Missing include directory")
                all_valid = False
            else:
                print("✓ LP_MP: Include directory found")
        else:
            print("✗ LP_MP: Directory not found")
            all_valid = False
        
        # QPBO verification
        qpbo_path = self.project_root / "externals/qpbo"
        if qpbo_path.exists():
            header_files = list(qpbo_path.glob("*.h"))
            if not header_files:
                print("✗ QPBO: No header files found")
                all_valid = False
            else:
                print(f"✓ QPBO: Found {len(header_files)} header files")
        else:
            print("✗ QPBO: Directory not found")
            all_valid = False
        
        return all_valid


def main():
    """Main entry point for the submodule management script."""
    parser = argparse.ArgumentParser(
        description="Manage git submodules for NIFTY project",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s status                    # Show status of all submodules
  %(prog)s init                      # Initialize all submodules
  %(prog)s init --force              # Force re-initialize all submodules
  %(prog)s init externals/LP_MP      # Initialize specific submodule
  %(prog)s update                    # Update all submodules
  %(prog)s update externals/qpbo     # Update specific submodule
  %(prog)s verify                    # Verify submodules are properly set up
        """
    )
    
    parser.add_argument(
        "command",
        choices=["status", "init", "update", "verify"],
        help="Command to execute"
    )
    
    parser.add_argument(
        "submodule",
        nargs="?",
        help="Specific submodule to operate on (optional)"
    )
    
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force operation (e.g., re-initialize existing submodules)"
    )
    
    parser.add_argument(
        "--project-root",
        type=Path,
        help="Path to project root (default: current directory)"
    )
    
    args = parser.parse_args()
    
    # Initialize manager
    manager = SubmoduleManager(args.project_root)
    
    # Check if we're in a git repository
    if not manager.check_git_repository():
        print("Error: Not in a git repository")
        sys.exit(1)
    
    # Execute command
    success = True
    
    if args.command == "status":
        manager.print_status()
    
    elif args.command == "init":
        if args.submodule:
            success = manager.initialize_submodule(args.submodule, args.force)
        else:
            success = manager.initialize_all_submodules(args.force)
    
    elif args.command == "update":
        if args.submodule:
            success = manager.update_submodule(args.submodule)
        else:
            success = manager.update_all_submodules()
    
    elif args.command == "verify":
        success = manager.verify_submodules()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()