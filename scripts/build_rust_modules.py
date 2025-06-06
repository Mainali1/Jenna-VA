#!/usr/bin/env python3
"""
Build Rust Modules Script for Jenna Voice Assistant.

This script builds the Rust modules for integration with the Python codebase.
It handles the build process for different platforms and configurations.
"""

import os
import sys
import argparse
import logging
import subprocess
import shutil
from pathlib import Path
from typing import Optional, Dict, List, Tuple, Any

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def check_rust_installed() -> bool:
    """Check if Rust is installed.
    
    Returns:
        True if Rust is installed, False otherwise
    """
    try:
        subprocess.run(
            ["rustc", "--version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            text=True,
        )
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        return False


def check_cargo_installed() -> bool:
    """Check if Cargo is installed.
    
    Returns:
        True if Cargo is installed, False otherwise
    """
    try:
        subprocess.run(
            ["cargo", "--version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            text=True,
        )
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        return False


def install_rust() -> bool:
    """Install Rust using rustup.
    
    Returns:
        True if installation was successful, False otherwise
    """
    try:
        logger.info("Installing Rust...")
        
        # Check if we're on Windows
        if os.name == "nt":
            # On Windows, we need to download and run the rustup-init.exe
            import tempfile
            import urllib.request
            
            # Create a temporary directory
            with tempfile.TemporaryDirectory() as temp_dir:
                # Download rustup-init.exe
                rustup_init = Path(temp_dir) / "rustup-init.exe"
                urllib.request.urlretrieve(
                    "https://win.rustup.rs/x86_64",
                    rustup_init
                )
                
                # Run rustup-init.exe with -y to accept defaults
                subprocess.run(
                    [rustup_init, "-y"],
                    check=True,
                    text=True,
                )
        else:
            # On Unix-like systems, we can use the curl | sh method
            subprocess.run(
                ["curl", "--proto", "'=https'", "--tlsv1.2", "-sSf", "https://sh.rustup.rs", "-o", "rustup-init.sh"],
                check=True,
                text=True,
            )
            subprocess.run(
                ["sh", "rustup-init.sh", "-y"],
                check=True,
                text=True,
            )
            os.unlink("rustup-init.sh")
        
        logger.info("Rust installed successfully")
        
        # Update PATH to include cargo
        if os.name == "nt":
            cargo_path = Path.home() / ".cargo" / "bin"
            os.environ["PATH"] = f"{cargo_path};{os.environ['PATH']}"
        else:
            cargo_path = Path.home() / ".cargo" / "bin"
            os.environ["PATH"] = f"{cargo_path}:{os.environ['PATH']}"
        
        return True
    except Exception as e:
        logger.error(f"Failed to install Rust: {e}")
        return False


def install_maturin() -> bool:
    """Install maturin using pip.
    
    Returns:
        True if installation was successful, False otherwise
    """
    try:
        logger.info("Installing maturin...")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "maturin"],
            check=True,
            text=True,
        )
        return True
    except subprocess.SubprocessError as e:
        logger.error(f"Failed to install maturin: {e}")
        return False


def build_rust_modules(rust_modules_dir: Path, release: bool = False, force: bool = False) -> bool:
    """Build Rust modules using maturin.
    
    Args:
        rust_modules_dir: Directory containing the Rust modules
        release: Whether to build in release mode
        force: Whether to force a rebuild
        
    Returns:
        True if build was successful, False otherwise
    """
    try:
        # Check if Cargo.toml exists
        cargo_toml = rust_modules_dir / "Cargo.toml"
        if not cargo_toml.exists():
            logger.error(f"Cargo.toml not found at {cargo_toml}")
            return False
        
        # Clean if force is True
        if force:
            logger.info("Cleaning previous build...")
            subprocess.run(
                ["cargo", "clean"],
                cwd=rust_modules_dir,
                check=True,
                text=True,
            )
        
        # Build using maturin
        logger.info(f"Building Rust modules in {'release' if release else 'debug'} mode...")
        cmd = ["maturin", "build"]
        if release:
            cmd.append("--release")
        
        subprocess.run(
            cmd,
            cwd=rust_modules_dir,
            check=True,
            text=True,
        )
        
        # Check if wheel was created
        target_dir = rust_modules_dir / "target" / ("release" if release else "debug")
        if not target_dir.exists():
            logger.error(f"Target directory not found at {target_dir}")
            return False
        
        logger.info(f"Rust modules built successfully")
        return True
    except subprocess.SubprocessError as e:
        logger.error(f"Failed to build Rust modules: {e}")
        return False


def install_rust_modules(rust_modules_dir: Path, release: bool = False) -> bool:
    """Install Rust modules using pip.
    
    Args:
        rust_modules_dir: Directory containing the Rust modules
        release: Whether to install the release build
        
    Returns:
        True if installation was successful, False otherwise
    """
    try:
        # Find the wheel file
        wheel_dir = rust_modules_dir / "target" / "wheels"
        if not wheel_dir.exists():
            logger.error(f"Wheel directory not found at {wheel_dir}")
            return False
        
        wheel_files = list(wheel_dir.glob("*.whl"))
        if not wheel_files:
            logger.error(f"No wheel files found in {wheel_dir}")
            return False
        
        # Sort by modification time to get the latest wheel
        wheel_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        wheel_file = wheel_files[0]
        
        # Install the wheel
        logger.info(f"Installing Rust modules from {wheel_file}...")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "--force-reinstall", wheel_file],
            check=True,
            text=True,
        )
        
        logger.info(f"Rust modules installed successfully")
        return True
    except subprocess.SubprocessError as e:
        logger.error(f"Failed to install Rust modules: {e}")
        return False


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Build Rust modules for Jenna Voice Assistant")
    parser.add_argument(
        "--rust-modules-dir",
        type=Path,
        default=Path(__file__).parent.parent / "rust_modules",
        help="Directory containing the Rust modules"
    )
    parser.add_argument(
        "--release",
        action="store_true",
        help="Build in release mode"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force a rebuild"
    )
    parser.add_argument(
        "--install",
        action="store_true",
        help="Install the built modules"
    )
    
    args = parser.parse_args()
    
    # Check if Rust is installed
    if not check_rust_installed() or not check_cargo_installed():
        logger.info("Rust or Cargo is not installed")
        if not install_rust():
            logger.error("Failed to install Rust")
            return 1
    
    # Check if maturin is installed
    try:
        subprocess.run(
            ["maturin", "--version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            text=True,
        )
    except (subprocess.SubprocessError, FileNotFoundError):
        logger.info("maturin is not installed")
        if not install_maturin():
            logger.error("Failed to install maturin")
            return 1
    
    # Build Rust modules
    if not build_rust_modules(args.rust_modules_dir, args.release, args.force):
        return 1
    
    # Install Rust modules if requested
    if args.install:
        if not install_rust_modules(args.rust_modules_dir, args.release):
            return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())