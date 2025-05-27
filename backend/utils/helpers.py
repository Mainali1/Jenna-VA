"""Helper Utilities for Jenna Voice Assistant"""

import os
import sys
import json
import hashlib
import secrets
import platform
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Callable
from datetime import datetime, timedelta
import asyncio
import threading
from functools import wraps
import time


# File and Path Utilities
def ensure_directory(path: Union[str, Path]) -> Path:
    """Ensure a directory exists, create if it doesn't."""
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_app_data_dir() -> Path:
    """Get the application data directory."""
    if platform.system() == "Windows":
        base_dir = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    elif platform.system() == "Darwin":
        base_dir = Path.home() / "Library" / "Application Support"
    else:
        base_dir = Path.home() / ".local" / "share"
    
    app_dir = base_dir / "Jenna-VA"
    return ensure_directory(app_dir)


def get_temp_dir() -> Path:
    """Get the temporary directory for the application."""
    temp_dir = get_app_data_dir() / "temp"
    return ensure_directory(temp_dir)


def get_logs_dir() -> Path:
    """Get the logs directory."""
    logs_dir = get_app_data_dir() / "logs"
    return ensure_directory(logs_dir)


def get_config_dir() -> Path:
    """Get the configuration directory."""
    config_dir = get_app_data_dir() / "config"
    return ensure_directory(config_dir)


def get_backup_dir() -> Path:
    """Get the backup directory."""
    backup_dir = get_app_data_dir() / "backups"
    return ensure_directory(backup_dir)


def safe_file_name(filename: str) -> str:
    """Create a safe filename by removing/replacing invalid characters."""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename.strip()


def get_file_size_human(size_bytes: int) -> str:
    """Convert file size to human readable format."""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"


def read_json_file(file_path: Union[str, Path]) -> Optional[Dict[str, Any]]:
    """Safely read a JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, PermissionError):
        return None


def write_json_file(file_path: Union[str, Path], data: Dict[str, Any], indent: int = 2) -> bool:
    """Safely write data to a JSON file."""
    try:
        ensure_directory(Path(file_path).parent)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
        return True
    except (PermissionError, OSError):
        return False


# System Utilities
def get_system_info() -> Dict[str, Any]:
    """Get system information."""
    return {
        "platform": platform.system(),
        "platform_version": platform.version(),
        "architecture": platform.architecture()[0],
        "processor": platform.processor(),
        "python_version": platform.python_version(),
        "hostname": platform.node()
    }


def is_admin() -> bool:
    """Check if the application is running with administrator privileges."""
    try:
        if platform.system() == "Windows":
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        else:
            return os.geteuid() == 0
    except:
        return False


def get_available_memory() -> int:
    """Get available system memory in bytes."""
    try:
        import psutil
        return psutil.virtual_memory().available
    except ImportError:
        return 0


def get_cpu_usage() -> float:
    """Get current CPU usage percentage."""
    try:
        import psutil
        return psutil.cpu_percent(interval=1)
    except ImportError:
        return 0.0


def kill_process_by_name(process_name: str) -> bool:
    """Kill a process by name."""
    try:
        if platform.system() == "Windows":
            subprocess.run(["taskkill", "/f", "/im", process_name], 
                         capture_output=True, check=True)
        else:
            subprocess.run(["pkill", "-f", process_name], 
                         capture_output=True, check=True)
        return True
    except subprocess.CalledProcessError:
        return False


def is_process_running(process_name: str) -> bool:
    """Check if a process is running."""
    try:
        import psutil
        for proc in psutil.process_iter(['name']):
            if proc.info['name'] and process_name.lower() in proc.info['name'].lower():
                return True
        return False
    except ImportError:
        # Fallback method
        try:
            if platform.system() == "Windows":
                result = subprocess.run(["tasklist", "/fi", f"imagename eq {process_name}"], 
                                      capture_output=True, text=True)
                return process_name.lower() in result.stdout.lower()
            else:
                result = subprocess.run(["pgrep", "-f", process_name], 
                                      capture_output=True)
                return result.returncode == 0
        except:
            return False


# Security Utilities
def generate_secure_token(length: int = 32) -> str:
    """Generate a secure random token."""
    return secrets.token_urlsafe(length)


def hash_string(text: str, algorithm: str = "sha256") -> str:
    """Hash a string using the specified algorithm."""
    hash_obj = hashlib.new(algorithm)
    hash_obj.update(text.encode('utf-8'))
    return hash_obj.hexdigest()


def verify_hash(text: str, hash_value: str, algorithm: str = "sha256") -> bool:
    """Verify a string against its hash."""
    return hash_string(text, algorithm) == hash_value


def obfuscate_sensitive_data(data: str, show_chars: int = 4) -> str:
    """Obfuscate sensitive data, showing only the last few characters."""
    if len(data) <= show_chars:
        return '*' * len(data)
    return '*' * (len(data) - show_chars) + data[-show_chars:]


# Time and Date Utilities
def get_timestamp() -> str:
    """Get current timestamp in ISO format."""
    return datetime.now().isoformat()


def format_duration(seconds: float) -> str:
    """Format duration in seconds to human readable format."""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"


def parse_duration(duration_str: str) -> Optional[float]:
    """Parse duration string to seconds."""
    try:
        duration_str = duration_str.lower().strip()
        
        if duration_str.endswith('s'):
            return float(duration_str[:-1])
        elif duration_str.endswith('m'):
            return float(duration_str[:-1]) * 60
        elif duration_str.endswith('h'):
            return float(duration_str[:-1]) * 3600
        else:
            return float(duration_str)  # Assume seconds
    except ValueError:
        return None


def is_business_hours(start_hour: int = 9, end_hour: int = 17) -> bool:
    """Check if current time is within business hours."""
    now = datetime.now()
    return start_hour <= now.hour < end_hour and now.weekday() < 5


# Async Utilities
def run_in_thread(func: Callable) -> Callable:
    """Decorator to run a function in a separate thread."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        def run():
            return func(*args, **kwargs)
        
        thread = threading.Thread(target=run)
        thread.daemon = True
        thread.start()
        return thread
    
    return wrapper


async def run_in_executor(func: Callable, *args, **kwargs) -> Any:
    """Run a blocking function in an executor."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, func, *args, **kwargs)


def retry_async(max_attempts: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """Decorator for retrying async functions."""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            attempt = 1
            current_delay = delay
            
            while attempt <= max_attempts:
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts:
                        raise e
                    
                    await asyncio.sleep(current_delay)
                    current_delay *= backoff
                    attempt += 1
            
            return None
        
        return wrapper
    return decorator


def timeout_async(seconds: float):
    """Decorator to add timeout to async functions."""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await asyncio.wait_for(func(*args, **kwargs), timeout=seconds)
        return wrapper
    return decorator


# Performance Utilities
class Timer:
    """Context manager for timing operations."""
    
    def __init__(self, name: str = "Operation"):
        self.name = name
        self.start_time = None
        self.end_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
    
    @property
    def elapsed(self) -> float:
        """Get elapsed time in seconds."""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return 0.0
    
    def __str__(self) -> str:
        return f"{self.name}: {format_duration(self.elapsed)}"


def measure_performance(func: Callable) -> Callable:
    """Decorator to measure function performance."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        with Timer(func.__name__) as timer:
            result = func(*args, **kwargs)
        print(f"Performance: {timer}")
        return result
    
    return wrapper


# Data Utilities
def deep_merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """Deep merge two dictionaries."""
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge_dicts(result[key], value)
        else:
            result[key] = value
    
    return result


def flatten_dict(d: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
    """Flatten a nested dictionary."""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """Split a list into chunks of specified size."""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def remove_duplicates(lst: List[Any], key: Optional[Callable] = None) -> List[Any]:
    """Remove duplicates from a list while preserving order."""
    if key is None:
        seen = set()
        return [x for x in lst if not (x in seen or seen.add(x))]
    else:
        seen = set()
        return [x for x in lst if not (key(x) in seen or seen.add(key(x)))]


# Validation Utilities
def is_valid_email(email: str) -> bool:
    """Validate email address format."""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def is_valid_url(url: str) -> bool:
    """Validate URL format."""
    import re
    pattern = r'^https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:\w*))?)?$'
    return re.match(pattern, url) is not None


def sanitize_input(text: str, max_length: int = 1000) -> str:
    """Sanitize user input."""
    # Remove control characters
    sanitized = ''.join(char for char in text if ord(char) >= 32 or char in '\n\r\t')
    
    # Limit length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    return sanitized.strip()


# Network Utilities
def is_internet_available() -> bool:
    """Check if internet connection is available."""
    try:
        import socket
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        return False


def get_local_ip() -> Optional[str]:
    """Get local IP address."""
    try:
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except:
        return None


# Logging Utilities
def setup_basic_logging(level: str = "INFO", log_file: Optional[str] = None):
    """Setup basic logging configuration."""
    import logging
    
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    handlers = [logging.StreamHandler()]
    if log_file:
        ensure_directory(Path(log_file).parent)
        handlers.append(logging.FileHandler(log_file))
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=handlers
    )


# Environment Utilities
def get_env_bool(key: str, default: bool = False) -> bool:
    """Get boolean value from environment variable."""
    value = os.environ.get(key, '').lower()
    return value in ('true', '1', 'yes', 'on')


def get_env_int(key: str, default: int = 0) -> int:
    """Get integer value from environment variable."""
    try:
        return int(os.environ.get(key, default))
    except ValueError:
        return default


def get_env_float(key: str, default: float = 0.0) -> float:
    """Get float value from environment variable."""
    try:
        return float(os.environ.get(key, default))
    except ValueError:
        return default


# Application Utilities
def get_app_version() -> str:
    """Get application version."""
    try:
        version_file = Path(__file__).parent.parent.parent / "VERSION"
        if version_file.exists():
            return version_file.read_text().strip()
    except:
        pass
    return "1.0.0"


def is_development_mode() -> bool:
    """Check if application is running in development mode."""
    return get_env_bool("JENNA_DEV_MODE", False) or "pytest" in sys.modules


def get_build_info() -> Dict[str, Any]:
    """Get build information."""
    return {
        "version": get_app_version(),
        "python_version": platform.python_version(),
        "platform": platform.system(),
        "architecture": platform.architecture()[0],
        "build_date": get_timestamp(),
        "development_mode": is_development_mode()
    }