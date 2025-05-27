"""Mood Detection Feature Implementation"""

import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional

from backend.core.config import Settings
from backend.core.feature_manager import Feature
from backend.core.logger import get_logger
from backend.features.mood_detection import MoodDetectionManager
from backend.utils.exceptions import FeatureManagerException


class MoodDetectionFeature(Feature):
    """Feature for detecting user mood from text input."""
    
    def __init__(self):
        super().__init__(
            name="mood_detection",
            description="Detect user mood from text input",
            requires_api=False
        )
        self.manager: Optional[MoodDetectionManager] = None
    
    async def _initialize_impl(self, settings: Settings) -> bool:
        """Initialize the mood detection feature."""
        try:
            self.logger.info("Initializing MoodDetectionFeature")
            
            # Create data directory if it doesn't exist
            data_dir = Path(settings.data_dir) / "mood_detection"
            data_dir.mkdir(parents=True, exist_ok=True)
            
            # Initialize the mood detection manager
            self.manager = MoodDetectionManager(data_dir)
            await self.manager.initialize()
            
            self.logger.info("MoodDetectionFeature initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize MoodDetectionFeature: {e}")
            return False
    
    async def cleanup(self) -> None:
        """Clean up resources used by the mood detection feature."""
        if self.manager:
            await self.manager.cleanup()
        self.logger.info("MoodDetectionFeature cleaned up")
    
    # API methods
    
    async def analyze_mood(self, text: str) -> Dict[str, Any]:
        """Analyze the mood of the given text."""
        if not self.enabled:
            raise FeatureManagerException("MoodDetectionFeature is not enabled")
        
        if not self.manager:
            raise FeatureManagerException("MoodDetectionFeature not initialized")
        
        return self.manager.analyze_mood(text)
    
    async def get_response_for_mood(self, mood: str) -> str:
        """Get an appropriate response for the detected mood."""
        if not self.enabled:
            raise FeatureManagerException("MoodDetectionFeature is not enabled")
        
        if not self.manager:
            raise FeatureManagerException("MoodDetectionFeature not initialized")
        
        return self.manager.get_response_for_mood(mood)
    
    async def analyze_conversation(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze the mood trend in a conversation."""
        if not self.enabled:
            raise FeatureManagerException("MoodDetectionFeature is not enabled")
        
        if not self.manager:
            raise FeatureManagerException("MoodDetectionFeature not initialized")
        
        return self.manager.analyze_conversation(messages)
    
    async def get_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get the mood analysis history."""
        if not self.enabled:
            raise FeatureManagerException("MoodDetectionFeature is not enabled")
        
        if not self.manager:
            raise FeatureManagerException("MoodDetectionFeature not initialized")
        
        return self.manager.get_history(limit)
    
    async def clear_history(self) -> None:
        """Clear the mood analysis history."""
        if not self.enabled:
            raise FeatureManagerException("MoodDetectionFeature is not enabled")
        
        if not self.manager:
            raise FeatureManagerException("MoodDetectionFeature not initialized")
        
        self.manager.clear_history()