"""System Utilities for Jenna Voice Assistant"""

import os
import sys
import platform
import shutil
from pathlib import Path
from typing import Dict, Any, Optional

import psutil

from backend.core.config import Settings
from backend.core.logger import get_logger
from backend.utils.helpers import ensure_directory
from backend.utils.exceptions import JennaException


logger = get_logger(__name__)


def check_system_requirements() -> bool:
    """Check if the system meets the requirements to run Jenna.
    
    Returns:
        bool: True if all requirements are met, False otherwise.
    """
    logger.info("Checking system requirements...")
    
    # Check Python version
    python_version = sys.version_info
    if python_version < (3, 10):
        logger.error(f"Python 3.10 or higher is required. Current version: {sys.version}")
        return False
    
    # Check available memory (at least 2GB recommended)
    available_memory = psutil.virtual_memory().available
    if available_memory < 2 * 1024 * 1024 * 1024:  # 2GB in bytes
        logger.warning(f"Low memory available: {available_memory / (1024 * 1024 * 1024):.2f} GB")
        # Warning only, don't fail
    
    # Check disk space (at least 1GB free space recommended)
    disk_usage = psutil.disk_usage(os.getcwd())
    if disk_usage.free < 1 * 1024 * 1024 * 1024:  # 1GB in bytes
        logger.warning(f"Low disk space: {disk_usage.free / (1024 * 1024 * 1024):.2f} GB free")
        # Warning only, don't fail
    
    # Check for required external dependencies
    if platform.system() == "Windows":
        # Check for Microsoft Visual C++ Redistributable
        # This is a simplified check and might not be accurate in all cases
        if not os.path.exists("C:\\Windows\\System32\\msvcp140.dll"):
            logger.warning("Microsoft Visual C++ Redistributable might not be installed")
            # Warning only, don't fail
    
    # All critical requirements met
    logger.info("✅ System requirements check passed")
    return True


def setup_directories(settings: Settings) -> None:
    """Set up the required directories for Jenna.
    
    Args:
        settings: Application settings
    """
    logger.info("Setting up application directories...")
    
    # Create data directory
    data_dir = Path(settings.data_dir)
    ensure_directory(data_dir)
    logger.debug(f"Data directory: {data_dir}")
    
    # Create config directory
    config_dir = Path(settings.config_dir)
    ensure_directory(config_dir)
    logger.debug(f"Config directory: {config_dir}")
    
    # Create logs directory
    logs_dir = data_dir / "logs"
    ensure_directory(logs_dir)
    logger.debug(f"Logs directory: {logs_dir}")
    
    # Create temp directory
    temp_dir = data_dir / "temp"
    ensure_directory(temp_dir)
    logger.debug(f"Temp directory: {temp_dir}")
    
    # Create cache directory
    cache_dir = data_dir / "cache"
    ensure_directory(cache_dir)
    logger.debug(f"Cache directory: {cache_dir}")
    
    # Create feature-specific directories
    features_dir = data_dir / "features"
    ensure_directory(features_dir)
    
    # Create directories for specific features
    feature_dirs = [
        "tasks",
        "calendar",
        "flashcards",
        "pomodoro",
        "research",
        "screen_analysis"
    ]
    
    for feature_dir in feature_dirs:
        ensure_directory(features_dir / feature_dir)
        logger.debug(f"Feature directory: {features_dir / feature_dir}")
    
    # Create voice model directory if using offline recognition
    if settings.voice_recognition_engine == "vosk":
        voice_models_dir = data_dir / "voice_models"
        ensure_directory(voice_models_dir)
        logger.debug(f"Voice models directory: {voice_models_dir}")
        
        # Check if model exists, if not create a placeholder
        model_path = Path(settings.voice_recognition_model_path)
        if not model_path.exists():
            model_placeholder = voice_models_dir / "model"
            ensure_directory(model_placeholder)
            logger.warning(f"Voice model not found at {model_path}. Created placeholder at {model_placeholder}")
    
    logger.info("✅ Application directories setup complete")


def get_system_info() -> Dict[str, Any]:
    """Get detailed system information.
    
    Returns:
        Dict[str, Any]: System information
    """
    # Get memory information
    memory = psutil.virtual_memory()
    memory_info = {
        "total": memory.total,
        "available": memory.available,
        "percent": memory.percent,
        "used": memory.used,
        "free": memory.free
    }
    
    # Get CPU information
    cpu_info = {
        "physical_cores": psutil.cpu_count(logical=False),
        "logical_cores": psutil.cpu_count(logical=True),
        "percent": psutil.cpu_percent(interval=1),
        "frequency": psutil.cpu_freq().current if psutil.cpu_freq() else None
    }
    
    # Get disk information
    disk = psutil.disk_usage('/')
    disk_info = {
        "total": disk.total,
        "used": disk.used,
        "free": disk.free,
        "percent": disk.percent
    }
    
    # Get network information
    network_info = {
        "interfaces": list(psutil.net_if_addrs().keys())
    }
    
    return {
        "platform": platform.system(),
        "version": platform.version(),
        "architecture": platform.architecture()[0],
        "memory": memory_info,
        "cpu": cpu_info,
        "disk": disk_info,
        "network": network_info
    }


def cleanup_temp_files(temp_dir: Optional[Path] = None) -> None:
    """Clean up temporary files.
    
    Args:
        temp_dir: Directory containing temporary files. If None, use default temp directory.
    """
    if temp_dir is None:
        from backend.utils.helpers import get_temp_dir
        temp_dir = get_temp_dir()
    
    logger.info(f"Cleaning up temporary files in {temp_dir}")
    
    try:
        # Remove all files in the temp directory
        for item in temp_dir.iterdir():
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                shutil.rmtree(item)
        
        logger.info("✅ Temporary files cleanup complete")
    except Exception as e:
        logger.error(f"Error cleaning up temporary files: {e}")