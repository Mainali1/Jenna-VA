#!/usr/bin/env python3
"""
Vosk Model Setup Script for Jenna Voice Assistant.

This script downloads and sets up the Vosk model for offline speech recognition.
It supports different languages and model sizes based on user preferences.
"""

import os
import sys
import argparse
import logging
import zipfile
import shutil
from pathlib import Path
from typing import Optional, Dict, List, Tuple

import requests
from tqdm import tqdm

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Define available models
# Format: model_name: (url, size_mb, description)
AVAILABLE_MODELS: Dict[str, Tuple[str, int, str]] = {
    "vosk-model-small-en-us-0.15": (
        "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip",
        40,
        "Small English model (40MB) - Good for constrained environments"
    ),
    "vosk-model-en-us-0.22": (
        "https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip",
        1800,
        "Large English model (1.8GB) - High accuracy"
    ),
    "vosk-model-en-us-0.22-lgraph": (
        "https://alphacephei.com/vosk/models/vosk-model-en-us-0.22-lgraph.zip",
        128,
        "English model with small language model (128MB) - Good balance of size and accuracy"
    ),
    "vosk-model-small-en-us-zamia-0.5": (
        "https://alphacephei.com/vosk/models/vosk-model-small-en-us-zamia-0.5.zip",
        50,
        "Small English Zamia model (50MB) - Alternative to the standard small model"
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


def extract_zip(zip_path: Path, extract_to: Path) -> bool:
    """Extract a zip file.
    
    Args:
        zip_path: Path to the zip file
        extract_to: Path to extract to
        
    Returns:
        True if extraction was successful, False otherwise
    """
    try:
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            # Get the total size for progress bar
            total_size = sum(info.file_size for info in zip_ref.infolist())
            extracted_size = 0
            
            # Create progress bar
            with tqdm(
                desc="Extracting",
                total=total_size,
                unit="B",
                unit_scale=True,
                unit_divisor=1024,
            ) as progress_bar:
                for info in zip_ref.infolist():
                    zip_ref.extract(info, extract_to)
                    extracted_size += info.file_size
                    progress_bar.update(info.file_size)
        
        return True
    except Exception as e:
        logger.error(f"Error extracting zip file: {e}")
        return False


def setup_vosk_model(model_name: str, models_dir: Path, force: bool = False) -> bool:
    """Download and setup a Vosk model.
    
    Args:
        model_name: Name of the model to download
        models_dir: Directory to store models
        force: Force download even if model already exists
        
    Returns:
        True if setup was successful, False otherwise
    """
    if model_name not in AVAILABLE_MODELS:
        logger.error(f"Unknown model: {model_name}")
        logger.info("Available models:")
        for name, (_, size, desc) in AVAILABLE_MODELS.items():
            logger.info(f"  - {name} ({size} MB): {desc}")
        return False
    
    # Create models directory if it doesn't exist
    vosk_dir = models_dir / "vosk"
    vosk_dir.mkdir(parents=True, exist_ok=True)
    
    # Check if model already exists
    model_dir = vosk_dir / model_name
    if model_dir.exists() and not force:
        logger.info(f"Model {model_name} already exists at {model_dir}")
        return True
    
    # Download model
    url, size, _ = AVAILABLE_MODELS[model_name]
    zip_path = vosk_dir / f"{model_name}.zip"
    
    logger.info(f"Downloading {model_name} ({size} MB)...")
    if not download_file(url, zip_path, desc=f"Downloading {model_name}"):
        return False
    
    # Extract model
    logger.info(f"Extracting {model_name}...")
    if not extract_zip(zip_path, vosk_dir):
        return False
    
    # Remove zip file
    zip_path.unlink()
    
    # Rename extracted directory if needed
    extracted_dir = next((d for d in vosk_dir.iterdir() if d.is_dir() and model_name in d.name), None)
    if extracted_dir and extracted_dir != model_dir:
        shutil.move(str(extracted_dir), str(model_dir))
    
    logger.info(f"Model {model_name} setup complete at {model_dir}")
    return True


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Setup Vosk model for Jenna Voice Assistant")
    parser.add_argument(
        "--model",
        choices=list(AVAILABLE_MODELS.keys()),
        default="vosk-model-small-en-us-0.15",
        help="Model to download"
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
        help="Force download even if model already exists"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available models"
    )
    
    args = parser.parse_args()
    
    if args.list:
        print("Available models:")
        for name, (_, size, desc) in AVAILABLE_MODELS.items():
            print(f"  - {name} ({size} MB): {desc}")
        return 0
    
    if not setup_vosk_model(args.model, args.models_dir, args.force):
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())