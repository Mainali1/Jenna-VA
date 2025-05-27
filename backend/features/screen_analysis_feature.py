"""Screen Analysis Feature Implementation"""

import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional

from backend.core.config import Settings
from backend.core.feature_manager import Feature
from backend.core.logger import get_logger
from backend.features.screen_analysis import ScreenAnalysisManager
from backend.utils.exceptions import FeatureManagerException


class ScreenAnalysisFeature(Feature):
    """Feature for analyzing screen content and providing context-aware assistance."""
    
    def __init__(self, settings: Settings, data_dir: Path):
        super().__init__(settings, data_dir)
        self.logger = get_logger("screen_analysis_feature")
        self.manager: Optional[ScreenAnalysisManager] = None
    
    async def initialize(self) -> None:
        """Initialize the screen analysis feature."""
        try:
            self.logger.info("Initializing ScreenAnalysisFeature")
            
            # Check if Tesseract path is configured
            if not self.settings.feature_screen_analysis_tesseract_path:
                self.logger.warning("Tesseract path not configured. OCR functionality will be limited.")
            
            # Initialize the screen analysis manager
            self.manager = ScreenAnalysisManager(self.data_dir, self.settings)
            await self.manager.initialize()
            
            self.logger.info("ScreenAnalysisFeature initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize ScreenAnalysisFeature: {e}")
            raise FeatureManagerException(f"Failed to initialize ScreenAnalysisFeature: {e}")
    
    async def enable(self) -> None:
        """Enable the screen analysis feature."""
        if not self.manager:
            await self.initialize()
        
        self.logger.info("ScreenAnalysisFeature enabled")
    
    async def disable(self) -> None:
        """Disable the screen analysis feature."""
        self.logger.info("ScreenAnalysisFeature disabled")
    
    async def cleanup(self) -> None:
        """Clean up resources used by the screen analysis feature."""
        if self.manager:
            await self.manager.cleanup()
        self.logger.info("ScreenAnalysisFeature cleaned up")
    
    # API methods
    
    async def capture_screen(self) -> Dict[str, Any]:
        """Capture and analyze the entire screen."""
        if not self.manager:
            raise FeatureManagerException("ScreenAnalysisFeature not initialized")
        
        return await self.manager.capture_and_analyze_screen()
    
    async def capture_active_window(self) -> Dict[str, Any]:
        """Capture and analyze the active window."""
        if not self.manager:
            raise FeatureManagerException("ScreenAnalysisFeature not initialized")
        
        return await self.manager.capture_and_analyze_active_window()
    
    async def extract_text_from_screen(self) -> str:
        """Extract text from the entire screen."""
        if not self.manager:
            raise FeatureManagerException("ScreenAnalysisFeature not initialized")
        
        return await self.manager.extract_text_from_screen()
    
    async def extract_text_from_active_window(self) -> str:
        """Extract text from the active window."""
        if not self.manager:
            raise FeatureManagerException("ScreenAnalysisFeature not initialized")
        
        return await self.manager.extract_text_from_active_window()
    
    async def list_visible_windows(self) -> List[Dict[str, Any]]:
        """List all visible windows on the screen."""
        if not self.manager:
            raise FeatureManagerException("ScreenAnalysisFeature not initialized")
        
        return await self.manager.list_visible_windows()
    
    async def get_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get the screen analysis history."""
        if not self.manager:
            raise FeatureManagerException("ScreenAnalysisFeature not initialized")
        
        return self.manager.get_history(limit)
    
    async def clear_history(self) -> None:
        """Clear the screen analysis history."""
        if not self.manager:
            raise FeatureManagerException("ScreenAnalysisFeature not initialized")
        
        self.manager.clear_history()