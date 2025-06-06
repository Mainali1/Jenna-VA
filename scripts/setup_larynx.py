#!/usr/bin/env python3
"""
Larynx Model Setup Script for Jenna Voice Assistant.

This script downloads and sets up the Larynx model for offline text-to-speech.
It supports different voices and languages based on user preferences.
"""

import os
import sys
import argparse
import logging
import zipfile
import shutil
import tarfile
from pathlib import Path
from typing import Optional, Dict, List, Tuple, Any

import requests
from tqdm import tqdm

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Define available voices
# Format: voice_name: (url, size_mb, language, description)
AVAILABLE_VOICES: Dict[str, Tuple[str, int, str, str]] = {
    "larynx-cmu-arctic-slt-1.0": (
        "https://github.com/rhasspy/larynx/releases/download/v1.0/larynx-cmu-arctic-slt-1.0.tar.gz",
        70,
        "en-us",
        "Female English voice (SLT from CMU Arctic)"
    ),
    "larynx-cmu-arctic-bdl-1.0": (
        "https://github.com/rhasspy/larynx/releases/download/v1.0/larynx-cmu-arctic-bdl-1.0.tar.gz",
        70,
        "en-us",
        "Male English voice (BDL from CMU Arctic)"
    ),
    "larynx-cmu-arctic-clb-1.0": (
        "https://github.com/rhasspy/larynx/releases/download/v1.0/larynx-cmu-arctic-clb-1.0.tar.gz",
        70,
        "en-us",
        "Female English voice (CLB from CMU Arctic)"
    ),
    "larynx-cmu-arctic-rms-1.0": (
        "https://github.com/rhasspy/larynx/releases/download/v1.0/larynx-cmu-arctic-rms-1.0.tar.gz",
        70,
        "en-us",
        "Male English voice (RMS from CMU Arctic)"
    ),
    "larynx-glow-tts-en-ljspeech-1.0": (
        "https://github.com/rhasspy/larynx/releases/download/v1.0/larynx-glow-tts-en-ljspeech-1.0.tar.gz",
        120,
        "en-us",
        "Female English voice (LJSpeech)"
    ),
}

# Define available vocoder models
# Format: model_name: (url, size_mb, description)
AVAILABLE_VOCODERS: Dict[str, Tuple[str, int, str]] = {
    "larynx-hifi-gan-universal-1.0": (
        "https://github.com/rhasspy/larynx/releases/download/v1.0/larynx-hifi-gan-universal-1.0.tar.gz",
        60,
        "Universal vocoder that works with all voices"
    ),
}


def download_file(url: str, destination: Path, desc: Optional[str] = None) -> bool:
    """Download a file with progress bar.
    
    Args:
        url: URL to download
        destination: Destination path
        desc: Description for the progress bar
        
    Returns:
        True if download was successful, False otherwise
    """
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get("content-length", 0))
        block_size = 8192  # 8 KB
        
        with open(destination, "wb") as f, tqdm(
            desc=desc,
            total=total_size,
            unit="B",
            unit_scale=True,
            unit_divisor=1024,
        ) as progress_bar:
            for chunk in response.iter_content(chunk_size=block_size):
                if chunk:  # filter out keep-alive chunks
                    f.write(chunk)
                    progress_bar.update(len(chunk))
        
        return True
    except Exception as e:
        logger.error(f"Error downloading file: {e}")
        return False


def extract_tar_gz(tar_path: Path, extract_to: Path) -> bool:
    """Extract a tar.gz file.
    
    Args:
        tar_path: Path to the tar.gz file
        extract_to: Path to extract to
        
    Returns:
        True if extraction was successful, False otherwise
    """
    try:
        with tarfile.open(tar_path, "r:gz") as tar_ref:
            # Get the total size for progress bar
            total_size = sum(member.size for member in tar_ref.getmembers() if member.isreg())
            extracted_size = 0
            
            # Create progress bar
            with tqdm(
                desc="Extracting",
                total=total_size,
                unit="B",
                unit_scale=True,
                unit_divisor=1024,
            ) as progress_bar:
                for member in tar_ref.getmembers():
                    tar_ref.extract(member, extract_to)
                    if member.isreg():
                        extracted_size += member.size
                        progress_bar.update(member.size)
        
        return True
    except Exception as e:
        logger.error(f"Error extracting tar.gz file: {e}")
        return False


def setup_larynx_voice(voice_name: str, models_dir: Path, force: bool = False) -> bool:
    """Download and setup a Larynx voice.
    
    Args:
        voice_name: Name of the voice to download
        models_dir: Directory to store models
        force: Force download even if voice already exists
        
    Returns:
        True if setup was successful, False otherwise
    """
    if voice_name not in AVAILABLE_VOICES:
        logger.error(f"Unknown voice: {voice_name}")
        logger.info("Available voices:")
        for name, (_, size, lang, desc) in AVAILABLE_VOICES.items():
            logger.info(f"  - {name} ({size} MB, {lang}): {desc}")
        return False
    
    # Create models directory if it doesn't exist
    larynx_dir = models_dir / "larynx"
    larynx_dir.mkdir(parents=True, exist_ok=True)
    
    # Check if voice already exists
    voice_dir = larynx_dir / voice_name
    if voice_dir.exists() and not force:
        logger.info(f"Voice {voice_name} already exists at {voice_dir}")
        return True
    
    # Download voice
    url, size, lang, _ = AVAILABLE_VOICES[voice_name]
    tar_path = larynx_dir / f"{voice_name}.tar.gz"
    
    logger.info(f"Downloading {voice_name} ({size} MB)...")
    if not download_file(url, tar_path, desc=f"Downloading {voice_name}"):
        return False
    
    # Extract voice
    logger.info(f"Extracting {voice_name}...")
    if not extract_tar_gz(tar_path, larynx_dir):
        return False
    
    # Remove tar.gz file
    tar_path.unlink()
    
    # Rename extracted directory if needed
    extracted_dir = next((d for d in larynx_dir.iterdir() if d.is_dir() and voice_name in d.name), None)
    if extracted_dir and extracted_dir != voice_dir:
        shutil.move(str(extracted_dir), str(voice_dir))
    
    logger.info(f"Voice {voice_name} setup complete at {voice_dir}")
    return True


def setup_larynx_vocoder(vocoder_name: str, models_dir: Path, force: bool = False) -> bool:
    """Download and setup a Larynx vocoder.
    
    Args:
        vocoder_name: Name of the vocoder to download
        models_dir: Directory to store models
        force: Force download even if vocoder already exists
        
    Returns:
        True if setup was successful, False otherwise
    """
    if vocoder_name not in AVAILABLE_VOCODERS:
        logger.error(f"Unknown vocoder: {vocoder_name}")
        logger.info("Available vocoders:")
        for name, (_, size, desc) in AVAILABLE_VOCODERS.items():
            logger.info(f"  - {name} ({size} MB): {desc}")
        return False
    
    # Create models directory if it doesn't exist
    larynx_dir = models_dir / "larynx"
    larynx_dir.mkdir(parents=True, exist_ok=True)
    
    # Check if vocoder already exists
    vocoder_dir = larynx_dir / vocoder_name
    if vocoder_dir.exists() and not force:
        logger.info(f"Vocoder {vocoder_name} already exists at {vocoder_dir}")
        return True
    
    # Download vocoder
    url, size, _ = AVAILABLE_VOCODERS[vocoder_name]
    tar_path = larynx_dir / f"{vocoder_name}.tar.gz"
    
    logger.info(f"Downloading {vocoder_name} ({size} MB)...")
    if not download_file(url, tar_path, desc=f"Downloading {vocoder_name}"):
        return False
    
    # Extract vocoder
    logger.info(f"Extracting {vocoder_name}...")
    if not extract_tar_gz(tar_path, larynx_dir):
        return False
    
    # Remove tar.gz file
    tar_path.unlink()
    
    # Rename extracted directory if needed
    extracted_dir = next((d for d in larynx_dir.iterdir() if d.is_dir() and vocoder_name in d.name), None)
    if extracted_dir and extracted_dir != vocoder_dir:
        shutil.move(str(extracted_dir), str(vocoder_dir))
    
    logger.info(f"Vocoder {vocoder_name} setup complete at {vocoder_dir}")
    return True


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Setup Larynx model for Jenna Voice Assistant")
    parser.add_argument(
        "--voice",
        choices=list(AVAILABLE_VOICES.keys()),
        default="larynx-cmu-arctic-slt-1.0",
        help="Voice to download"
    )
    parser.add_argument(
        "--vocoder",
        choices=list(AVAILABLE_VOCODERS.keys()),
        default="larynx-hifi-gan-universal-1.0",
        help="Vocoder to download"
    )
    parser.add_argument(
        "--models-dir",
        type=Path,
        default=Path(__file__).parent.parent / "models",
        help="Directory to store models"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force download even if models already exist"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available voices and vocoders"
    )
    
    args = parser.parse_args()
    
    if args.list:
        print("Available voices:")
        for name, (_, size, lang, desc) in AVAILABLE_VOICES.items():
            print(f"  - {name} ({size} MB, {lang}): {desc}")
        
        print("\nAvailable vocoders:")
        for name, (_, size, desc) in AVAILABLE_VOCODERS.items():
            print(f"  - {name} ({size} MB): {desc}")
        return 0
    
    # Setup voice
    if not setup_larynx_voice(args.voice, args.models_dir, args.force):
        return 1
    
    # Setup vocoder
    if not setup_larynx_vocoder(args.vocoder, args.models_dir, args.force):
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())