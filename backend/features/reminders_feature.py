"""Reminders Feature Implementation"""

import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional, Union

from backend.core.config import Settings
from backend.core.feature_manager import Feature
from backend.core.logger import get_logger
from backend.features.reminders import RemindersManager, Reminder
from backend.utils.exceptions import FeatureManagerException


class RemindersFeature(Feature):
    """Feature for managing reminders."""
    
    def __init__(self):
        super().__init__(
            name="reminders",
            description="Create and manage reminders and notifications",
            requires_api=False
        )
        self.logger = get_logger("reminders_feature")
        self.manager: Optional[RemindersManager] = None
    
    async def _initialize_impl(self, settings: Settings) -> bool:
        """Initialize the reminders feature."""
        try:
            self.logger.info("Initializing RemindersFeature")
            
            # Create data directory if it doesn't exist
            data_dir = Path(settings.data_dir) / "reminders"
            data_dir.mkdir(parents=True, exist_ok=True)
            
            # Initialize the reminders manager
            self.manager = RemindersManager(Path(settings.data_dir))
            await self.manager.load_data()
            
            self.logger.info("RemindersFeature initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize RemindersFeature: {e}")
            return False
    
    async def _on_enable(self):
        """Called when feature is enabled."""
        self.logger.info("RemindersFeature enabled")
    
    async def _on_disable(self):
        """Called when feature is disabled."""
        self.logger.info("RemindersFeature disabled")
    
    async def _cleanup_impl(self):
        """Feature-specific cleanup logic."""
        if self.manager:
            await self.manager.cleanup()
        self.logger.info("RemindersFeature cleaned up")
    
    # API methods
    
    async def create_reminder(
        self,
        title: str,
        description: str,
        due_date: Union[datetime, str],
        priority: str = "medium",
        repeat: Optional[str] = None,
        notify_before: Optional[int] = None,
        tags: List[str] = None
    ) -> Dict[str, Any]:
        """Create a new reminder."""
        if not self.enabled:
            raise FeatureManagerException("RemindersFeature is not enabled")
        
        if not self.manager:
            raise FeatureManagerException("RemindersFeature not initialized")
        
        reminder = await self.manager.create_reminder(
            title=title,
            description=description,
            due_date=due_date,
            priority=priority,
            repeat=repeat,
            notify_before=notify_before,
            tags=tags
        )
        return reminder.to_dict()
    
    async def get_reminder(self, reminder_id: str) -> Optional[Dict[str, Any]]:
        """Get a reminder by ID."""
        if not self.enabled:
            raise FeatureManagerException("RemindersFeature is not enabled")
        
        if not self.manager:
            raise FeatureManagerException("RemindersFeature not initialized")
        
        reminder = await self.manager.get_reminder(reminder_id)
        return reminder.to_dict() if reminder else None
    
    async def get_all_reminders(self) -> List[Dict[str, Any]]:
        """Get all reminders."""
        if not self.enabled:
            raise FeatureManagerException("RemindersFeature is not enabled")
        
        if not self.manager:
            raise FeatureManagerException("RemindersFeature not initialized")
        
        reminders = await self.manager.get_all_reminders()
        return [reminder.to_dict() for reminder in reminders]
    
    async def get_reminders_by_tag(self, tag: str) -> List[Dict[str, Any]]:
        """Get reminders by tag."""
        if not self.enabled:
            raise FeatureManagerException("RemindersFeature is not enabled")
        
        if not self.manager:
            raise FeatureManagerException("RemindersFeature not initialized")
        
        reminders = await self.manager.get_reminders_by_tag(tag)
        return [reminder.to_dict() for reminder in reminders]
    
    async def get_upcoming_reminders(self, days: int = 7) -> List[Dict[str, Any]]:
        """Get upcoming reminders within the specified number of days."""
        if not self.enabled:
            raise FeatureManagerException("RemindersFeature is not enabled")
        
        if not self.manager:
            raise FeatureManagerException("RemindersFeature not initialized")
        
        reminders = await self.manager.get_upcoming_reminders(days)
        return [reminder.to_dict() for reminder in reminders]
    
    async def get_overdue_reminders(self) -> List[Dict[str, Any]]:
        """Get overdue reminders."""
        if not self.enabled:
            raise FeatureManagerException("RemindersFeature is not enabled")
        
        if not self.manager:
            raise FeatureManagerException("RemindersFeature not initialized")
        
        reminders = await self.manager.get_overdue_reminders()
        return [reminder.to_dict() for reminder in reminders]
    
    async def get_reminders_by_priority(self, priority: str) -> List[Dict[str, Any]]:
        """Get reminders by priority."""
        if not self.enabled:
            raise FeatureManagerException("RemindersFeature is not enabled")
        
        if not self.manager:
            raise FeatureManagerException("RemindersFeature not initialized")
        
        reminders = await self.manager.get_reminders_by_priority(priority)
        return [reminder.to_dict() for reminder in reminders]
    
    async def update_reminder(self, reminder_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a reminder."""
        if not self.enabled:
            raise FeatureManagerException("RemindersFeature is not enabled")
        
        if not self.manager:
            raise FeatureManagerException("RemindersFeature not initialized")
        
        reminder = await self.manager.update_reminder(reminder_id, data)
        return reminder.to_dict() if reminder else None
    
    async def mark_as_completed(self, reminder_id: str) -> Optional[Dict[str, Any]]:
        """Mark a reminder as completed."""
        if not self.enabled:
            raise FeatureManagerException("RemindersFeature is not enabled")
        
        if not self.manager:
            raise FeatureManagerException("RemindersFeature not initialized")
        
        reminder = await self.manager.mark_as_completed(reminder_id)
        return reminder.to_dict() if reminder else None
    
    async def delete_reminder(self, reminder_id: str) -> bool:
        """Delete a reminder."""
        if not self.enabled:
            raise FeatureManagerException("RemindersFeature is not enabled")
        
        if not self.manager:
            raise FeatureManagerException("RemindersFeature not initialized")
        
        return await self.manager.delete_reminder(reminder_id)
    
    async def search_reminders(self, query: str) -> List[Dict[str, Any]]:
        """Search reminders by title and description."""
        if not self.enabled:
            raise FeatureManagerException("RemindersFeature is not enabled")
        
        if not self.manager:
            raise FeatureManagerException("RemindersFeature not initialized")
        
        reminders = await self.manager.search_reminders(query)
        return [reminder.to_dict() for reminder in reminders]