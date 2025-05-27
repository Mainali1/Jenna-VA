"""Screen Analysis Feature Implementation"""

import asyncio
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import tempfile

import numpy as np
from PIL import Image, ImageGrab
import pytesseract

from backend.core.config import Settings
from backend.core.logger import get_logger
from backend.utils.exceptions import FeatureManagerException


class ScreenCapture:
    """Captures and processes screenshots."""
    
    def __init__(self, tesseract_path: Optional[str] = None):
        self.logger = get_logger("screen_capture")
        
        # Set Tesseract path if provided
        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
        
        # Create a temporary directory for screenshots
        self.temp_dir = tempfile.mkdtemp(prefix="jenna_screen_")
        self.logger.info(f"Created temporary directory for screenshots: {self.temp_dir}")
    
    def capture_screen(self) -> Optional[Image.Image]:
        """Capture the entire screen."""
        try:
            screenshot = ImageGrab.grab()
            self.logger.info(f"Captured screenshot: {screenshot.size[0]}x{screenshot.size[1]}")
            return screenshot
        except Exception as e:
            self.logger.error(f"Error capturing screenshot: {e}")
            return None
    
    def capture_region(self, bbox: Tuple[int, int, int, int]) -> Optional[Image.Image]:
        """Capture a specific region of the screen.
        
        Args:
            bbox: The region to capture (left, top, right, bottom)
        """
        try:
            screenshot = ImageGrab.grab(bbox=bbox)
            self.logger.info(f"Captured region: {bbox}, size: {screenshot.size[0]}x{screenshot.size[1]}")
            return screenshot
        except Exception as e:
            self.logger.error(f"Error capturing region: {e}")
            return None
    
    def save_screenshot(self, image: Image.Image, filename: Optional[str] = None) -> Optional[str]:
        """Save a screenshot to a file.
        
        Args:
            image: The image to save
            filename: The filename to use (if None, a timestamp will be used)
        
        Returns:
            The path to the saved file, or None if saving failed
        """
        if not image:
            return None
        
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"screenshot_{timestamp}.png"
            
            filepath = os.path.join(self.temp_dir, filename)
            image.save(filepath)
            self.logger.info(f"Saved screenshot to {filepath}")
            return filepath
        except Exception as e:
            self.logger.error(f"Error saving screenshot: {e}")
            return None
    
    def extract_text(self, image: Image.Image) -> str:
        """Extract text from an image using OCR."""
        if not image:
            return ""
        
        try:
            text = pytesseract.image_to_string(image)
            self.logger.info(f"Extracted {len(text)} characters of text from image")
            return text
        except Exception as e:
            self.logger.error(f"Error extracting text from image: {e}")
            return ""
    
    def cleanup(self) -> None:
        """Clean up temporary files."""
        try:
            # Remove all files in the temporary directory
            for file in os.listdir(self.temp_dir):
                file_path = os.path.join(self.temp_dir, file)
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            
            # Remove the directory itself
            os.rmdir(self.temp_dir)
            self.logger.info(f"Cleaned up temporary directory: {self.temp_dir}")
        except Exception as e:
            self.logger.error(f"Error cleaning up temporary directory: {e}")


class WindowDetector:
    """Detects and analyzes windows on the screen."""
    
    def __init__(self):
        self.logger = get_logger("window_detector")
    
    def get_active_window_title(self) -> str:
        """Get the title of the currently active window."""
        try:
            import win32gui
            window = win32gui.GetForegroundWindow()
            title = win32gui.GetWindowText(window)
            self.logger.info(f"Active window: {title}")
            return title
        except ImportError:
            self.logger.error("win32gui module not available")
            return ""
        except Exception as e:
            self.logger.error(f"Error getting active window title: {e}")
            return ""
    
    def get_window_position(self, window_title: Optional[str] = None) -> Optional[Tuple[int, int, int, int]]:
        """Get the position of a window by title.
        
        Args:
            window_title: The title of the window to find (if None, the active window is used)
        
        Returns:
            The window position as (left, top, right, bottom), or None if the window was not found
        """
        try:
            import win32gui
            
            if window_title is None:
                # Get the active window
                window = win32gui.GetForegroundWindow()
            else:
                # Find the window by title
                window = win32gui.FindWindow(None, window_title)
                if not window:
                    self.logger.warning(f"Window not found: {window_title}")
                    return None
            
            # Get the window position
            left, top, right, bottom = win32gui.GetWindowRect(window)
            self.logger.info(f"Window position: ({left}, {top}, {right}, {bottom})")
            return (left, top, right, bottom)
        except ImportError:
            self.logger.error("win32gui module not available")
            return None
        except Exception as e:
            self.logger.error(f"Error getting window position: {e}")
            return None
    
    def list_visible_windows(self) -> List[Dict[str, Any]]:
        """List all visible windows on the screen."""
        windows = []
        
        try:
            import win32gui
            
            def callback(hwnd, windows):
                if win32gui.IsWindowVisible(hwnd):
                    title = win32gui.GetWindowText(hwnd)
                    if title:
                        rect = win32gui.GetWindowRect(hwnd)
                        windows.append({
                            "title": title,
                            "handle": hwnd,
                            "position": rect
                        })
                return True
            
            win32gui.EnumWindows(callback, windows)
            self.logger.info(f"Found {len(windows)} visible windows")
            return windows
        except ImportError:
            self.logger.error("win32gui module not available")
            return []
        except Exception as e:
            self.logger.error(f"Error listing visible windows: {e}")
            return []


class ScreenAnalysisHistory:
    """Manages the history of screen analysis results."""
    
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir / "screen_analysis"
        self.history: List[Dict[str, Any]] = []
        self.logger = get_logger("screen_analysis_history")
        
        # Create data directory if it doesn't exist
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    async def load_history(self) -> None:
        """Load screen analysis history from disk."""
        history_file = self.data_dir / "history.json"
        
        if history_file.exists():
            try:
                with open(history_file, "r", encoding="utf-8") as f:
                    self.history = json.load(f)
                self.logger.info(f"Loaded {len(self.history)} screen analysis entries from history")
            except Exception as e:
                self.logger.error(f"Error loading screen analysis history: {e}")
    
    async def save_history(self) -> None:
        """Save screen analysis history to disk."""
        history_file = self.data_dir / "history.json"
        
        try:
            # Keep only the most recent 50 entries to prevent the file from growing too large
            recent_history = self.history[-50:] if len(self.history) > 50 else self.history
            
            with open(history_file, "w", encoding="utf-8") as f:
                json.dump(recent_history, f, indent=2)
            self.logger.info(f"Saved {len(recent_history)} screen analysis entries to history")
        except Exception as e:
            self.logger.error(f"Error saving screen analysis history: {e}")
    
    def add_entry(self, analysis_type: str, result: Dict[str, Any]) -> None:
        """Add a new entry to the screen analysis history."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "type": analysis_type,
            "result": result
        }
        
        self.history.append(entry)
        asyncio.create_task(self.save_history())
    
    def get_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get the most recent entries from the screen analysis history."""
        return self.history[-limit:] if len(self.history) > limit else self.history
    
    def clear_history(self) -> None:
        """Clear the screen analysis history."""
        self.history = []
        asyncio.create_task(self.save_history())


class ScreenAnalysisManager:
    """Manages screen analysis operations and history."""
    
    def __init__(self, data_dir: Path, settings: Settings):
        self.data_dir = data_dir
        self.settings = settings
        self.screen_capture = ScreenCapture(tesseract_path=settings.feature_screen_analysis_tesseract_path)
        self.window_detector = WindowDetector()
        self.history = ScreenAnalysisHistory(data_dir)
        self.logger = get_logger("screen_analysis")
    
    async def initialize(self) -> None:
        """Initialize the screen analysis manager."""
        try:
            # Load screen analysis history
            await self.history.load_history()
            self.logger.info("Initialized ScreenAnalysisManager")
        except Exception as e:
            self.logger.error(f"Error initializing ScreenAnalysisManager: {e}")
            raise FeatureManagerException(f"Failed to initialize ScreenAnalysisManager: {e}")
    
    async def capture_and_analyze_screen(self) -> Dict[str, Any]:
        """Capture and analyze the entire screen."""
        try:
            # Capture the screen
            screenshot = self.screen_capture.capture_screen()
            if not screenshot:
                raise FeatureManagerException("Failed to capture screenshot")
            
            # Save the screenshot
            filepath = self.screen_capture.save_screenshot(screenshot)
            
            # Extract text from the screenshot
            text = self.screen_capture.extract_text(screenshot)
            
            # Get the active window title
            active_window = self.window_detector.get_active_window_title()
            
            # Create the analysis result
            result = {
                "screenshot_path": filepath,
                "resolution": screenshot.size,
                "active_window": active_window,
                "text_length": len(text),
                "text_preview": text[:200] + "..." if len(text) > 200 else text
            }
            
            # Add to history
            self.history.add_entry("full_screen", result)
            
            return result
        except Exception as e:
            self.logger.error(f"Error analyzing screen: {e}")
            raise FeatureManagerException(f"Failed to analyze screen: {e}")
    
    async def capture_and_analyze_active_window(self) -> Dict[str, Any]:
        """Capture and analyze the active window."""
        try:
            # Get the active window position
            window_pos = self.window_detector.get_window_position()
            if not window_pos:
                raise FeatureManagerException("Failed to get active window position")
            
            # Capture the window region
            screenshot = self.screen_capture.capture_region(window_pos)
            if not screenshot:
                raise FeatureManagerException("Failed to capture window screenshot")
            
            # Save the screenshot
            filepath = self.screen_capture.save_screenshot(screenshot)
            
            # Extract text from the screenshot
            text = self.screen_capture.extract_text(screenshot)
            
            # Get the active window title
            active_window = self.window_detector.get_active_window_title()
            
            # Create the analysis result
            result = {
                "screenshot_path": filepath,
                "window_title": active_window,
                "window_position": window_pos,
                "resolution": screenshot.size,
                "text_length": len(text),
                "text_preview": text[:200] + "..." if len(text) > 200 else text
            }
            
            # Add to history
            self.history.add_entry("active_window", result)
            
            return result
        except Exception as e:
            self.logger.error(f"Error analyzing active window: {e}")
            raise FeatureManagerException(f"Failed to analyze active window: {e}")
    
    async def extract_text_from_screen(self) -> str:
        """Extract text from the entire screen."""
        try:
            # Capture the screen
            screenshot = self.screen_capture.capture_screen()
            if not screenshot:
                raise FeatureManagerException("Failed to capture screenshot")
            
            # Extract text from the screenshot
            text = self.screen_capture.extract_text(screenshot)
            
            # Add to history
            self.history.add_entry("text_extraction", {
                "text_length": len(text),
                "text_preview": text[:200] + "..." if len(text) > 200 else text
            })
            
            return text
        except Exception as e:
            self.logger.error(f"Error extracting text from screen: {e}")
            raise FeatureManagerException(f"Failed to extract text from screen: {e}")
    
    async def extract_text_from_active_window(self) -> str:
        """Extract text from the active window."""
        try:
            # Get the active window position
            window_pos = self.window_detector.get_window_position()
            if not window_pos:
                raise FeatureManagerException("Failed to get active window position")
            
            # Capture the window region
            screenshot = self.screen_capture.capture_region(window_pos)
            if not screenshot:
                raise FeatureManagerException("Failed to capture window screenshot")
            
            # Extract text from the screenshot
            text = self.screen_capture.extract_text(screenshot)
            
            # Add to history
            self.history.add_entry("window_text_extraction", {
                "window_title": self.window_detector.get_active_window_title(),
                "text_length": len(text),
                "text_preview": text[:200] + "..." if len(text) > 200 else text
            })
            
            return text
        except Exception as e:
            self.logger.error(f"Error extracting text from active window: {e}")
            raise FeatureManagerException(f"Failed to extract text from active window: {e}")
    
    async def list_visible_windows(self) -> List[Dict[str, Any]]:
        """List all visible windows on the screen."""
        try:
            windows = self.window_detector.list_visible_windows()
            
            # Add to history
            self.history.add_entry("window_list", {
                "window_count": len(windows),
                "windows": [w["title"] for w in windows]
            })
            
            return windows
        except Exception as e:
            self.logger.error(f"Error listing visible windows: {e}")
            raise FeatureManagerException(f"Failed to list visible windows: {e}")
    
    def get_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get the screen analysis history."""
        return self.history.get_history(limit)
    
    def clear_history(self) -> None:
        """Clear the screen analysis history."""
        self.history.clear_history()
        self.logger.info("Cleared screen analysis history")
    
    async def cleanup(self) -> None:
        """Clean up resources."""
        self.screen_capture.cleanup()
        await self.history.save_history()
        self.logger.info("Cleaned up ScreenAnalysisManager")