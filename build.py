#!/usr/bin/env python3
"""
Jenna Voice Assistant - Build Script

This script builds the Jenna Voice Assistant application into a standalone executable
using PyInstaller. It handles frontend compilation, resource collection, and packaging.

Usage:
    python build.py [--release] [--clean] [--no-frontend] [--spec-only]
"""

import os
import sys
import shutil
import argparse
import subprocess
import platform
from pathlib import Path
from typing import List, Dict, Any, Optional

# Ensure we're in the project root directory
project_root = Path(__file__).resolve().parent
os.chdir(project_root)

# Configuration
APP_NAME = "Jenna Voice Assistant"
APP_VERSION = "1.0.0"
AUTHOR = "Jenna Development Team"

# Directories
DIST_DIR = project_root / "dist"
BUILD_DIR = project_root / "build"
FRONTEND_DIR = project_root / "frontend"
FRONTEND_DIST = FRONTEND_DIR / "dist"
RESOURCE_DIR = project_root / "resources"
MODELS_DIR = project_root / "models"

# PyInstaller options
PYINSTALLER_OPTS = [
    "--name=Jenna-VA",
    "--windowed",  # No console window in Windows
    "--icon=resources/icon.ico",
    "--add-data=frontend/dist;frontend/dist",
    "--add-data=resources;resources",
    "--add-data=models;models",  # Include models directory
    "--add-data=.env.template;.",
    "--add-data=LICENSE;.",
    "--add-data=README.md;.",
    "--hidden-import=pyttsx3.drivers",
    "--hidden-import=pyttsx3.drivers.sapi5",
    "--hidden-import=nltk",
    "--hidden-import=vosk",
    "--hidden-import=pocketsphinx",
    "--hidden-import=fastapi",
    "--hidden-import=uvicorn",
    "--collect-all=vosk",
    "--collect-all=nltk_data",
    "--collect-all=pocketsphinx",
]

# Ensure cross-platform path separators
def fix_path_separator(path_str: str) -> str:
    """Fix path separators for the current OS."""
    if platform.system() == "Windows":
        # Windows uses semicolons as path separators
        return path_str.replace("/", "\\").replace(";", ";")
    else:
        # Unix-like systems (Linux, macOS) use colons as path separators
        return path_str.replace("\\", "/").replace(";", ":")


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Build Jenna Voice Assistant")
    parser.add_argument("--release", action="store_true", help="Build in release mode")
    parser.add_argument("--clean", action="store_true", help="Clean build directories first")
    parser.add_argument("--no-frontend", action="store_true", help="Skip frontend build")
    parser.add_argument("--spec-only", action="store_true", help="Generate spec file only")
    return parser.parse_args()


def clean_build_dirs():
    """Clean build and dist directories."""
    print("🧹 Cleaning build directories...")
    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)
    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)
    print("✅ Build directories cleaned")


def build_frontend():
    """Build the frontend application."""
    print("🏗️ Building frontend...")
    os.chdir(FRONTEND_DIR)
    
    # Install dependencies if needed
    if not (FRONTEND_DIR / "node_modules").exists():
        subprocess.run(["npm", "install"], check=True)
    
    # Build the frontend
    subprocess.run(["npm", "run", "build"], check=True)
    
    os.chdir(project_root)
    print("✅ Frontend built successfully")


def prepare_nltk_data():
    """Download and prepare NLTK data."""
    print("📥 Preparing NLTK data...")
    import nltk
    
    # Download essential NLTK resources
    resources = [
        'punkt',
        'stopwords',
        'averaged_perceptron_tagger',
        'vader_lexicon'
    ]
    
    for resource in resources:
        try:
            nltk.data.find(f'tokenizers/{resource}')
            print(f"  ✓ {resource} already downloaded")
        except LookupError:
            print(f"  ↓ Downloading {resource}...")
            nltk.download(resource, quiet=True)
    
    print("✅ NLTK data prepared")


def prepare_vosk_model():
    """Check for Vosk model and provide instructions if missing."""
    print("🔍 Checking for Vosk model...")
    model_path = project_root / "models" / "vosk"
    
    if not model_path.exists() or not any(model_path.iterdir()):
        print("⚠️ Vosk model not found!")
        print("📋 Please download a model from https://alphacephei.com/vosk/models")
        print("   and extract it to the 'models/vosk' directory.")
        return False
    
    print("✅ Vosk model found")
    return True


def prepare_pocketsphinx():
    """Prepare PocketSphinx for offline speech recognition."""
    print("🔧 Setting up PocketSphinx...")
    
    # Create models directory if it doesn't exist
    pocketsphinx_dir = project_root / "models" / "pocketsphinx"
    pocketsphinx_dir.mkdir(parents=True, exist_ok=True)
    
    # Check if model files exist
    model_files = list(pocketsphinx_dir.glob("*.dict")) + list(pocketsphinx_dir.glob("*.lm"))
    
    if not model_files:
        print("⚠️ PocketSphinx model files not found!")
        print("📥 Copying default PocketSphinx model files...")
        
        try:
            # Get default model path from pocketsphinx
            from pocketsphinx import get_model_path
            default_model_path = Path(get_model_path())
            
            # Create subdirectories
            en_us_dir = pocketsphinx_dir / "en-us"
            en_us_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy essential model files
            import shutil
            
            # Copy dictionary file
            dict_file = default_model_path / "cmudict-en-us.dict"
            if dict_file.exists():
                shutil.copy2(dict_file, pocketsphinx_dir)
                print(f"  ✓ Copied {dict_file.name}")
            
            # Copy language model file
            lm_file = default_model_path / "en-us.lm.bin"
            if lm_file.exists():
                shutil.copy2(lm_file, pocketsphinx_dir)
                print(f"  ✓ Copied {lm_file.name}")
            
            # Copy acoustic model files
            acoustic_model_dir = default_model_path / "en-us"
            if acoustic_model_dir.exists() and acoustic_model_dir.is_dir():
                # Copy entire directory
                shutil.copytree(acoustic_model_dir, en_us_dir, dirs_exist_ok=True)
                print(f"  ✓ Copied acoustic model files")
            
            print("✅ Default PocketSphinx model files copied successfully")
        except Exception as e:
            print(f"⚠️ Error copying default PocketSphinx models: {e}")
            print("📋 Basic model will be included in the package.")
            print("   For better accuracy, consider adding custom models to 'models/pocketsphinx'.")
    else:
        print("✅ PocketSphinx models found")
    
    return True


def check_requirements():
    """Check if all required packages are installed."""
    print("🔍 Checking requirements...")
    
    # Add PyInstaller to requirements if not already there
    required_packages = [
        "pyinstaller",
        "pocketsphinx",  # Add PocketSphinx for offline recognition
    ]
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"  ✓ {package} is installed")
        except ImportError:
            print(f"  ✗ {package} is not installed. Installing...")
            subprocess.run([sys.executable, "-m", "pip", "install", package], check=True)
    
    print("✅ All build requirements satisfied")


def generate_spec_file():
    """Generate a PyInstaller spec file."""
    print("📝 Generating spec file...")
    
    # Fix path separators for the current OS
    fixed_opts = [fix_path_separator(opt) for opt in PYINSTALLER_OPTS]
    
    # Generate the spec file
    cmd = ["pyinstaller", "--specpath", str(project_root)] + fixed_opts + ["main.py"]
    subprocess.run(cmd, check=True)
    
    print("✅ Spec file generated")


def build_executable(release_mode=False):
    """Build the executable using PyInstaller."""
    print("🚀 Building executable...")
    
    # Use the spec file
    cmd = ["pyinstaller", "Jenna-VA.spec"]
    if release_mode:
        cmd.append("--clean")
    
    subprocess.run(cmd, check=True)
    
    print("✅ Executable built successfully")


def create_installer(release_mode=False):
    """Create an installer using Inno Setup (Windows only)."""
    if platform.system() != "Windows":
        print("⚠️ Installer creation is only supported on Windows")
        return
    
    print("📦 Creating installer...")
    
    # Check if Inno Setup is installed
    inno_compiler = "C:\\Program Files (x86)\\Inno Setup 6\\ISCC.exe"
    if not os.path.exists(inno_compiler):
        print("⚠️ Inno Setup not found. Please install it to create an installer.")
        print("   Download from: https://jrsoftware.org/isdl.php")
        return
    
    # Create Inno Setup script
    iss_file = project_root / "installer.iss"
    with open(iss_file, "w") as f:
        f.write(f"""
[Setup]
#define MyAppName "{APP_NAME}"
#define MyAppVersion "{APP_VERSION}"
#define MyAppPublisher "{AUTHOR}"
#define MyAppExeName "Jenna-VA.exe"

AppId={{{{8A7D8AE1-9F0D-4B8B-B154-0CB78F47F1A9}}}}
AppName={{#MyAppName}}
AppVersion={{#MyAppVersion}}
AppPublisher={{#MyAppPublisher}}
DefaultDirName={{autopf}}\\{{#MyAppName}}
DisableProgramGroupPage=yes
LicenseFile={project_root}\\LICENSE
OutputDir={DIST_DIR}
OutputBaseFilename=Jenna-VA-Setup
SetupIconFile={project_root}\\resources\\icon.ico
UninstallDisplayIcon={{app}}\\{{#MyAppExeName}}
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{{cm:CreateDesktopIcon}}"; GroupDescription: "{{cm:AdditionalIcons}}"

[Files]
Source: "{DIST_DIR}\\Jenna-VA\\*"; DestDir: "{{app}}"; Flags: ignoreversion recursesubdirs

[Icons]
Name: "{{autoprograms}}\\{{#MyAppName}}"; Filename: "{{app}}\\{{#MyAppExeName}}"
Name: "{{autodesktop}}\\{{#MyAppName}}"; Filename: "{{app}}\\{{#MyAppExeName}}"; Tasks: desktopicon

[Run]
Filename: "{{app}}\\{{#MyAppExeName}}"; Description: "{{cm:LaunchProgram,{{#StringChange(MyAppName, '&', '&&')}}}}"; Flags: nowait postinstall skipifsilent
        """)
    
    # Run Inno Setup compiler
    subprocess.run([inno_compiler, str(iss_file)], check=True)
    
    print("✅ Installer created successfully")


def copy_license_file():
    """Create a license file if it doesn't exist."""
    license_file = project_root / "LICENSE"
    if not license_file.exists():
        print("📝 Creating MIT license file...")
        with open(license_file, "w") as f:
            f.write(f"""
MIT License

Copyright (c) {2023} {AUTHOR}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
            """)
        print("✅ License file created")
    else:
        print("✓ License file exists")


def main():
    """Main build function."""
    args = parse_args()
    
    print(f"🚀 Building {APP_NAME} v{APP_VERSION}")
    
    # Create resource directory if it doesn't exist
    RESOURCE_DIR.mkdir(exist_ok=True)
    MODELS_DIR.mkdir(exist_ok=True)
    
    # Clean build directories if requested
    if args.clean:
        clean_build_dirs()
    
    # Check requirements
    check_requirements()
    
    # Copy license file
    copy_license_file()
    
    # Build frontend if not skipped
    if not args.no_frontend:
        build_frontend()
    
    # Prepare NLTK data
    prepare_nltk_data()
    
    # Check for Vosk model
    prepare_vosk_model()
    
    # Prepare PocketSphinx
    prepare_pocketsphinx()
    
    # Generate spec file
    generate_spec_file()
    
    # Stop if only spec file was requested
    if args.spec_only:
        print("✅ Spec file generated. Exiting as requested.")
        return
    
    # Build the executable
    build_executable(args.release)
    
    # Create installer in release mode
    if args.release:
        create_installer(True)
    
    print(f"✅ Build completed successfully!")
    if args.release and platform.system() == "Windows":
        print(f"📦 Installer available at: {DIST_DIR / 'Jenna-VA-Setup.exe'}")
    else:
        print(f"📦 Executable available at: {DIST_DIR / 'Jenna-VA'}")


if __name__ == "__main__":
    main()