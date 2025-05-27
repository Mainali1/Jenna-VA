"""Pomodoro Feature Implementation"""

import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional

from backend.core.config import Settings
from backend.core.feature_manager import Feature
from backend.core.logger import get_logger
from backend.features.pomodoro import PomodoroManager, PomodoroState
from backend.utils.exceptions import FeatureManagerException


class PomodoroFeature(Feature):
    """Feature for managing pomodoro sessions for productivity."""
    
    def __init__(self):
        super().__init__(
            name="pomodoro",
            description="Pomodoro technique for productivity",
            requires_api=False
        )
        self.manager: Optional[PomodoroManager] = None
    
    async def _initialize_impl(self, settings: Settings) -> bool:
        """Initialize the pomodoro feature."""
        try:
            self.logger.info("Initializing PomodoroFeature")
            
            # Create data directory if it doesn't exist
            data_dir = Path(settings.data_dir) / "pomodoro"
            data_dir.mkdir(parents=True, exist_ok=True)
            
            # Initialize the pomodoro manager with settings
            self.manager = PomodoroManager(data_dir, settings)
            await self.manager.initialize()
            
            self.logger.info("PomodoroFeature initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize PomodoroFeature: {e}")
            return False
    
    async def cleanup(self) -> None:
        """Clean up resources used by the pomodoro feature."""
        if self.manager:
            await self.manager.cleanup()
        self.logger.info("PomodoroFeature cleaned up")
    
    # API methods
    
    async def start_session(self, task_name: str = "", custom_duration: Optional[int] = None) -> Dict[str, Any]:
        """Start a new pomodoro session."""
        if not self.enabled:
            raise FeatureManagerException("PomodoroFeature is not enabled")
        
        if not self.manager:
            raise FeatureManagerException("PomodoroFeature not initialized")
        
        session = await self.manager.start_session(task_name, custom_duration)
        return session.to_dict()
    
    async def pause_session(self) -> Dict[str, Any]:
        """Pause the current pomodoro session."""
        if not self.enabled:
            raise FeatureManagerException("PomodoroFeature is not enabled")
        
        if not self.manager:
            raise FeatureManagerException("PomodoroFeature not initialized")
        
        session = await self.manager.pause_session()
        return session.to_dict()
    
    async def resume_session(self) -> Dict[str, Any]:
        """Resume the paused pomodoro session."""
        if not self.enabled:
            raise FeatureManagerException("PomodoroFeature is not enabled")
        
        if not self.manager:
            raise FeatureManagerException("PomodoroFeature not initialized")
        
        session = await self.manager.resume_session()
        return session.to_dict()
    
    async def stop_session(self) -> Dict[str, Any]:
        """Stop the current pomodoro session."""
        if not self.enabled:
            raise FeatureManagerException("PomodoroFeature is not enabled")
        
        if not self.manager:
            raise FeatureManagerException("PomodoroFeature not initialized")
        
        session = await self.manager.stop_session()
        return session.to_dict()
    
    async def skip_break(self) -> Dict[str, Any]:
        """Skip the current break."""
        if not self.enabled:
            raise FeatureManagerException("PomodoroFeature is not enabled")
        
        if not self.manager:
            raise FeatureManagerException("PomodoroFeature not initialized")
        
        session = await self.manager.skip_break()
        return session.to_dict()
    
    async def get_current_session(self) -> Optional[Dict[str, Any]]:
        """Get the current pomodoro session."""
        if not self.enabled:
            raise FeatureManagerException("PomodoroFeature is not enabled")
        
        if not self.manager:
            raise FeatureManagerException("PomodoroFeature not initialized")
        
        session = self.manager.get_current_session()
        return session.to_dict() if session else None
    
    async def get_session_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get the pomodoro session history."""
        if not self.enabled:
            raise FeatureManagerException("PomodoroFeature is not enabled")
        
        if not self.manager:
            raise FeatureManagerException("PomodoroFeature not initialized")
        
        history = self.manager.get_session_history(limit)
        return [session.to_dict() for session in history]
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get pomodoro statistics."""
        if not self.enabled:
            raise FeatureManagerException("PomodoroFeature is not enabled")
        
        if not self.manager:
            raise FeatureManagerException("PomodoroFeature not initialized")
        
        return self.manager.get_statistics()
    
    async def update_settings(self, settings: Dict[str, Any]) -> None:
        """Update pomodoro settings."""
        if not self.enabled:
            raise FeatureManagerException("PomodoroFeature is not enabled")
        
        if not self.manager:
            raise FeatureManagerException("PomodoroFeature not initialized")
        
        await self.manager.update_settings(settings)