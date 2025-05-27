"""Research Feature Implementation"""

import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional

from backend.core.config import Settings
from backend.core.feature_manager import Feature
from backend.core.logger import get_logger
from backend.features.research import ResearchManager
from backend.utils.exceptions import FeatureManagerException


class ResearchFeature(Feature):
    """Feature for conducting research using various sources."""
    
    def __init__(self):
        super().__init__(
            name="research",
            description="Research using Wikipedia and web search",
            requires_api=False
        )
        self.manager: Optional[ResearchManager] = None
    
    async def _initialize_impl(self, settings: Settings) -> bool:
        """Initialize the research feature."""
        try:
            self.logger.info("Initializing ResearchFeature")
            
            # Create data directory if it doesn't exist
            data_dir = Path(settings.data_dir) / "research"
            data_dir.mkdir(parents=True, exist_ok=True)
            
            # Check if web search API keys are available
            has_web_search = bool(settings.feature_research_web_search_api_key)
            
            # Initialize the research manager
            self.manager = ResearchManager(data_dir, settings, has_web_search)
            await self.manager.initialize()
            
            self.logger.info("ResearchFeature initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize ResearchFeature: {e}")
            return False
    
    async def cleanup(self) -> None:
        """Clean up resources used by the research feature."""
        if self.manager:
            await self.manager.cleanup()
        self.logger.info("ResearchFeature cleaned up")
    
    # API methods
    
    async def search_wikipedia(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search Wikipedia for the given query."""
        if not self.enabled:
            raise FeatureManagerException("ResearchFeature is not enabled")
        
        if not self.manager:
            raise FeatureManagerException("ResearchFeature not initialized")
        
        return await self.manager.search_wikipedia(query, limit)
    
    async def get_wikipedia_summary(self, title: str) -> Dict[str, Any]:
        """Get a summary of a Wikipedia article."""
        if not self.enabled:
            raise FeatureManagerException("ResearchFeature is not enabled")
        
        if not self.manager:
            raise FeatureManagerException("ResearchFeature not initialized")
        
        return await self.manager.get_wikipedia_summary(title)
    
    async def get_wikipedia_sections(self, title: str) -> List[Dict[str, Any]]:
        """Get the sections of a Wikipedia article."""
        if not self.enabled:
            raise FeatureManagerException("ResearchFeature is not enabled")
        
        if not self.manager:
            raise FeatureManagerException("ResearchFeature not initialized")
        
        return await self.manager.get_wikipedia_sections(title)
    
    async def get_wikipedia_section_content(self, title: str, section: str) -> str:
        """Get the content of a specific section in a Wikipedia article."""
        if not self.enabled:
            raise FeatureManagerException("ResearchFeature is not enabled")
        
        if not self.manager:
            raise FeatureManagerException("ResearchFeature not initialized")
        
        return await self.manager.get_wikipedia_section_content(title, section)
    
    async def search_web(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search the web for the given query."""
        if not self.enabled:
            raise FeatureManagerException("ResearchFeature is not enabled")
        
        if not self.manager:
            raise FeatureManagerException("ResearchFeature not initialized")
        
        return await self.manager.search_web(query, limit)
    
    async def get_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get the research history."""
        if not self.enabled:
            raise FeatureManagerException("ResearchFeature is not enabled")
        
        if not self.manager:
            raise FeatureManagerException("ResearchFeature not initialized")
        
        return self.manager.get_history(limit)
    
    async def clear_history(self) -> None:
        """Clear the research history."""
        if not self.enabled:
            raise FeatureManagerException("ResearchFeature is not enabled")
        
        if not self.manager:
            raise FeatureManagerException("ResearchFeature not initialized")
        
        self.manager.clear_history()