"""File Operations Feature Implementation"""

import asyncio
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

from backend.core.config import Settings
from backend.core.feature_manager import Feature
from backend.core.logger import get_logger
from backend.utils.exceptions import FeatureManagerException


class FileOperationsFeature(Feature):
    """Feature for file system operations and management."""
    
    def __init__(self):
        super().__init__(
            name="file_operations",
            description="File system operations and management",
            requires_api=False
        )
        self.logger = get_logger("file_operations_feature")
    
    async def _initialize_impl(self, settings: Settings) -> bool:
        """Initialize the file operations feature."""
        try:
            self.logger.info("Initializing FileOperationsFeature")
            self.logger.info("FileOperationsFeature initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize FileOperationsFeature: {e}")
            return False
    
    # API methods
    
    async def search_files(self, query: str, directory: Optional[str] = None, max_results: int = 50) -> List[Dict[str, Any]]:
        """Search for files matching the query."""
        if not self.enabled:
            raise FeatureManagerException("FileOperationsFeature is not enabled")
        
        try:
            search_dir = Path(directory) if directory else Path.home()
            self.logger.info(f"Searching for files matching '{query}' in {search_dir}")
            
            results = []
            for file_path in search_dir.rglob(f"*{query}*"):
                if file_path.is_file():
                    results.append({
                        "name": file_path.name,
                        "path": str(file_path),
                        "size": file_path.stat().st_size,
                        "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                    })
                    
                    # Limit results
                    if len(results) >= max_results:
                        break
            
            return results
        except Exception as e:
            self.logger.error(f"Error searching files: {e}")
            return []
    
    async def open_file(self, file_path: str) -> bool:
        """Open a file with the default application."""
        if not self.enabled:
            raise FeatureManagerException("FileOperationsFeature is not enabled")
        
        try:
            self.logger.info(f"Opening file: {file_path}")
            
            if sys.platform == "win32":
                os.startfile(file_path)
            elif sys.platform == "darwin":
                subprocess.call(["open", file_path])
            else:
                subprocess.call(["xdg-open", file_path])
            
            return True
        except Exception as e:
            self.logger.error(f"Error opening file {file_path}: {e}")
            return False
    
    async def list_directory(self, directory: Optional[str] = None) -> List[Dict[str, Any]]:
        """List the contents of a directory."""
        if not self.enabled:
            raise FeatureManagerException("FileOperationsFeature is not enabled")
        
        try:
            dir_path = Path(directory) if directory else Path.cwd()
            self.logger.info(f"Listing directory: {dir_path}")
            
            results = []
            for item in dir_path.iterdir():
                item_type = "directory" if item.is_dir() else "file"
                results.append({
                    "name": item.name,
                    "path": str(item),
                    "type": item_type,
                    "size": item.stat().st_size if item.is_file() else None,
                    "modified": datetime.fromtimestamp(item.stat().st_mtime).isoformat()
                })
            
            return results
        except Exception as e:
            self.logger.error(f"Error listing directory {directory}: {e}")
            return []
    
    async def create_directory(self, directory: str) -> bool:
        """Create a new directory."""
        if not self.enabled:
            raise FeatureManagerException("FileOperationsFeature is not enabled")
        
        try:
            dir_path = Path(directory)
            self.logger.info(f"Creating directory: {dir_path}")
            
            dir_path.mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            self.logger.error(f"Error creating directory {directory}: {e}")
            return False
    
    async def copy_file(self, source: str, destination: str) -> bool:
        """Copy a file from source to destination."""
        if not self.enabled:
            raise FeatureManagerException("FileOperationsFeature is not enabled")
        
        try:
            import shutil
            self.logger.info(f"Copying file from {source} to {destination}")
            
            shutil.copy2(source, destination)
            return True
        except Exception as e:
            self.logger.error(f"Error copying file from {source} to {destination}: {e}")
            return False
    
    async def move_file(self, source: str, destination: str) -> bool:
        """Move a file from source to destination."""
        if not self.enabled:
            raise FeatureManagerException("FileOperationsFeature is not enabled")
        
        try:
            import shutil
            self.logger.info(f"Moving file from {source} to {destination}")
            
            shutil.move(source, destination)
            return True
        except Exception as e:
            self.logger.error(f"Error moving file from {source} to {destination}: {e}")
            return False
    
    async def delete_file(self, file_path: str) -> bool:
        """Delete a file."""
        if not self.enabled:
            raise FeatureManagerException("FileOperationsFeature is not enabled")
        
        try:
            path = Path(file_path)
            self.logger.info(f"Deleting file: {path}")
            
            if path.is_file():
                path.unlink()
                return True
            else:
                self.logger.warning(f"Not a file: {path}")
                return False
        except Exception as e:
            self.logger.error(f"Error deleting file {file_path}: {e}")
            return False