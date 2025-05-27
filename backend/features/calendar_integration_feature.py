"""Calendar Integration Feature Implementation"""

import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional

from backend.core.config import Settings
from backend.core.feature_manager import Feature
from backend.core.logger import get_logger
from backend.features.calendar_integration import CalendarManager, CalendarEvent
from backend.utils.exceptions import FeatureManagerException


class CalendarIntegrationFeature(Feature):
    """Feature for integrating with various calendar providers and managing events."""
    
    def __init__(self, settings: Settings, data_dir: Path):
        super().__init__(settings, data_dir)
        self.logger = get_logger("calendar_integration_feature")
        self.manager: Optional[CalendarManager] = None
    
    async def initialize(self) -> None:
        """Initialize the calendar integration feature."""
        try:
            self.logger.info("Initializing CalendarIntegrationFeature")
            
            # Initialize the calendar manager
            self.manager = CalendarManager(self.data_dir, self.settings)
            await self.manager.initialize()
            
            self.logger.info("CalendarIntegrationFeature initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize CalendarIntegrationFeature: {e}")
            raise FeatureManagerException(f"Failed to initialize CalendarIntegrationFeature: {e}")
    
    async def enable(self) -> None:
        """Enable the calendar integration feature."""
        if not self.manager:
            await self.initialize()
        
        self.logger.info("CalendarIntegrationFeature enabled")
    
    async def disable(self) -> None:
        """Disable the calendar integration feature."""
        self.logger.info("CalendarIntegrationFeature disabled")
    
    async def cleanup(self) -> None:
        """Clean up resources used by the calendar integration feature."""
        if self.manager:
            await self.manager.cleanup()
        self.logger.info("CalendarIntegrationFeature cleaned up")
    
    # API methods
    
    async def get_events(self, start_date: datetime, end_date: datetime, sources: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Get events from all enabled providers within the specified date range."""
        if not self.manager:
            raise FeatureManagerException("CalendarIntegrationFeature not initialized")
        
        events = await self.manager.get_events(start_date, end_date, sources)
        return [event.to_dict() for event in events]
    
    async def get_events_for_day(self, date: datetime, sources: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Get events for a specific day."""
        if not self.manager:
            raise FeatureManagerException("CalendarIntegrationFeature not initialized")
        
        events = await self.manager.get_events_for_day(date, sources)
        return [event.to_dict() for event in events]
    
    async def get_events_for_week(self, date: datetime, sources: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Get events for a specific week."""
        if not self.manager:
            raise FeatureManagerException("CalendarIntegrationFeature not initialized")
        
        events = await self.manager.get_events_for_week(date, sources)
        return [event.to_dict() for event in events]
    
    async def get_events_for_month(self, date: datetime, sources: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Get events for a specific month."""
        if not self.manager:
            raise FeatureManagerException("CalendarIntegrationFeature not initialized")
        
        events = await self.manager.get_events_for_month(date, sources)
        return [event.to_dict() for event in events]
    
    async def add_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add a new event to the local calendar."""
        if not self.manager:
            raise FeatureManagerException("CalendarIntegrationFeature not initialized")
        
        # Generate a unique ID if not provided
        if "event_id" not in event_data:
            event_data["event_id"] = f"local-{datetime.now().timestamp()}"
        
        # Create a CalendarEvent object
        event = CalendarEvent(
            event_id=event_data["event_id"],
            title=event_data["title"],
            start_time=datetime.fromisoformat(event_data["start_time"]) if isinstance(event_data["start_time"], str) else event_data["start_time"],
            end_time=datetime.fromisoformat(event_data["end_time"]) if isinstance(event_data["end_time"], str) and event_data.get("end_time") else None,
            description=event_data.get("description"),
            location=event_data.get("location"),
            calendar_id=event_data.get("calendar_id"),
            attendees=event_data.get("attendees"),
            is_all_day=event_data.get("is_all_day", False),
            recurrence=event_data.get("recurrence"),
            source=event_data.get("source", "local")
        )
        
        # Add the event
        added_event = await self.manager.add_event(event)
        return added_event.to_dict()
    
    async def update_event(self, event_id: str, event_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an existing event in the local calendar."""
        if not self.manager:
            raise FeatureManagerException("CalendarIntegrationFeature not initialized")
        
        # Create a CalendarEvent object
        event = CalendarEvent(
            event_id=event_id,
            title=event_data["title"],
            start_time=datetime.fromisoformat(event_data["start_time"]) if isinstance(event_data["start_time"], str) else event_data["start_time"],
            end_time=datetime.fromisoformat(event_data["end_time"]) if isinstance(event_data["end_time"], str) and event_data.get("end_time") else None,
            description=event_data.get("description"),
            location=event_data.get("location"),
            calendar_id=event_data.get("calendar_id"),
            attendees=event_data.get("attendees"),
            is_all_day=event_data.get("is_all_day", False),
            recurrence=event_data.get("recurrence"),
            source=event_data.get("source", "local")
        )
        
        # Update the event
        updated_event = await self.manager.update_event(event_id, event)
        return updated_event.to_dict() if updated_event else None
    
    async def delete_event(self, event_id: str) -> bool:
        """Delete an event from the local calendar."""
        if not self.manager:
            raise FeatureManagerException("CalendarIntegrationFeature not initialized")
        
        return await self.manager.delete_event(event_id)
    
    async def get_upcoming_events(self, days: int = 7, limit: int = 10, sources: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Get upcoming events for the next N days."""
        if not self.manager:
            raise FeatureManagerException("CalendarIntegrationFeature not initialized")
        
        events = await self.manager.get_upcoming_events(days, limit, sources)
        return [event.to_dict() for event in events]