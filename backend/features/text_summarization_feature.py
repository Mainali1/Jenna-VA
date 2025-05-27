"""Text Summarization Feature Implementation"""

import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional

from backend.core.config import Settings
from backend.core.feature_manager import Feature
from backend.core.logger import get_logger
from backend.features.text_summarization import TextSummarizationManager
from backend.utils.exceptions import FeatureManagerException


class TextSummarizationFeature(Feature):
    """Feature for summarizing text using various algorithms."""
    
    def __init__(self):
        super().__init__(
            name="text_summarization",
            description="Text summarization using various algorithms",
            requires_api=False
        )
        self.manager: Optional[TextSummarizationManager] = None
    
    async def _initialize_impl(self, settings: Settings) -> bool:
        """Initialize the text summarization feature."""
        try:
            self.logger.info("Initializing TextSummarizationFeature")
            
            # Create data directory if it doesn't exist
            data_dir = Path(settings.data_dir) / "text_summarization"
            data_dir.mkdir(parents=True, exist_ok=True)
            
            # Initialize the text summarization manager
            self.manager = TextSummarizationManager(data_dir)
            await self.manager.initialize()
            
            self.logger.info("TextSummarizationFeature initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize TextSummarizationFeature: {e}")
            return False
    
    async def cleanup(self) -> None:
        """Clean up resources used by the text summarization feature."""
        if self.manager:
            await self.manager.cleanup()
        self.logger.info("TextSummarizationFeature cleaned up")
    
    # API methods
    
    async def summarize(self, text: str, method: str = "hybrid", ratio: float = 0.3, max_sentences: int = 5) -> str:
        """Summarize the given text."""
        if not self.enabled:
            raise FeatureManagerException("TextSummarizationFeature is not enabled")
        
        if not self.manager:
            raise FeatureManagerException("TextSummarizationFeature not initialized")
        
        return self.manager.summarize(text, method, ratio, max_sentences)
    
    async def get_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get the summarization history."""
        if not self.enabled:
            raise FeatureManagerException("TextSummarizationFeature is not enabled")
        
        if not self.manager:
            raise FeatureManagerException("TextSummarizationFeature not initialized")
        
        return self.manager.get_history(limit)
    
    async def clear_history(self) -> None:
        """Clear the summarization history."""
        if not self.enabled:
            raise FeatureManagerException("TextSummarizationFeature is not enabled")
        
        if not self.manager:
            raise FeatureManagerException("TextSummarizationFeature not initialized")
        
        self.manager.clear_history()