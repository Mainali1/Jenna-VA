"""Calendar Integration Feature Implementation"""

import asyncio
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Union

import aiohttp
from icalendar import Calendar, Event

from backend.core.config import Settings
from backend.core.logger import get_logger
from backend.utils.exceptions import FeatureManagerException


class CalendarEvent:
    """Represents a calendar event with standardized properties."""
    
    def __init__(
        self,
        event_id: str,
        title: str,
        start_time: datetime,
        end_time: Optional[datetime] = None,
        description: Optional[str] = None,
        location: Optional[str] = None,
        calendar_id: Optional[str] = None,
        attendees: Optional[List[str]] = None,
        is_all_day: bool = False,
        recurrence: Optional[str] = None,
        source: str = "unknown"
    ):
        self.event_id = event_id
        self.title = title
        self.start_time = start_time
        self.end_time = end_time or (start_time + timedelta(hours=1))
        self.description = description or ""
        self.location = location or ""
        self.calendar_id = calendar_id
        self.attendees = attendees or []
        self.is_all_day = is_all_day
        self.recurrence = recurrence
        self.source = source  # e.g., "google", "outlook", "local"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the event to a dictionary."""
        return {
            "event_id": self.event_id,
            "title": self.title,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "description": self.description,
            "location": self.location,
            "calendar_id": self.calendar_id,
            "attendees": self.attendees,
            "is_all_day": self.is_all_day,
            "recurrence": self.recurrence,
            "source": self.source
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CalendarEvent':
        """Create an event from a dictionary."""
        start_time = datetime.fromisoformat(data["start_time"])
        end_time = datetime.fromisoformat(data["end_time"]) if data.get("end_time") else None
        
        return cls(
            event_id=data["event_id"],
            title=data["title"],
            start_time=start_time,
            end_time=end_time,
            description=data.get("description", ""),
            location=data.get("location", ""),
            calendar_id=data.get("calendar_id"),
            attendees=data.get("attendees", []),
            is_all_day=data.get("is_all_day", False),
            recurrence=data.get("recurrence"),
            source=data.get("source", "unknown")
        )


class LocalCalendarProvider:
    """Manages a local calendar stored as JSON."""
    
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir / "calendar"
        self.events_file = self.data_dir / "local_events.json"
        self.logger = get_logger("local_calendar")
        
        # Create data directory if it doesn't exist
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize events list
        self.events: List[CalendarEvent] = []
    
    async def load_events(self) -> None:
        """Load events from the local storage."""
        if not self.events_file.exists():
            self.logger.info("Local events file does not exist, creating empty file")
            await self.save_events()
            return
        
        try:
            with open(self.events_file, "r", encoding="utf-8") as f:
                events_data = json.load(f)
            
            self.events = [CalendarEvent.from_dict(event) for event in events_data]
            self.logger.info(f"Loaded {len(self.events)} events from local storage")
        except Exception as e:
            self.logger.error(f"Error loading local events: {e}")
            self.events = []
    
    async def save_events(self) -> None:
        """Save events to the local storage."""
        try:
            events_data = [event.to_dict() for event in self.events]
            
            with open(self.events_file, "w", encoding="utf-8") as f:
                json.dump(events_data, f, indent=2)
            
            self.logger.info(f"Saved {len(self.events)} events to local storage")
        except Exception as e:
            self.logger.error(f"Error saving local events: {e}")
    
    async def get_events(self, start_date: datetime, end_date: datetime) -> List[CalendarEvent]:
        """Get events within the specified date range."""
        return [
            event for event in self.events
            if (event.start_time <= end_date and 
                (event.end_time >= start_date if event.end_time else event.start_time >= start_date))
        ]
    
    async def add_event(self, event: CalendarEvent) -> CalendarEvent:
        """Add a new event to the local calendar."""
        # Set source to local
        event.source = "local"
        
        # Add the event to the list
        self.events.append(event)
        
        # Save the events
        await self.save_events()
        
        return event
    
    async def update_event(self, event_id: str, updated_event: CalendarEvent) -> Optional[CalendarEvent]:
        """Update an existing event in the local calendar."""
        # Find the event
        for i, event in enumerate(self.events):
            if event.event_id == event_id:
                # Update the event
                self.events[i] = updated_event
                
                # Save the events
                await self.save_events()
                
                return updated_event
        
        return None
    
    async def delete_event(self, event_id: str) -> bool:
        """Delete an event from the local calendar."""
        # Find the event
        for i, event in enumerate(self.events):
            if event.event_id == event_id:
                # Remove the event
                self.events.pop(i)
                
                # Save the events
                await self.save_events()
                
                return True
        
        return False


class GoogleCalendarProvider:
    """Provides integration with Google Calendar API."""
    
    def __init__(self, api_key: Optional[str] = None, client_id: Optional[str] = None, client_secret: Optional[str] = None):
        self.api_key = api_key
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.token_expiry: Optional[datetime] = None
        self.logger = get_logger("google_calendar")
        
        self.base_url = "https://www.googleapis.com/calendar/v3"
    
    async def authenticate(self) -> bool:
        """Authenticate with Google Calendar API."""
        # This is a placeholder for actual OAuth2 authentication
        # In a real implementation, this would handle the OAuth2 flow
        if not self.api_key and not (self.client_id and self.client_secret):
            self.logger.error("No API key or OAuth credentials provided for Google Calendar")
            return False
        
        self.logger.info("Authenticated with Google Calendar API")
        return True
    
    async def get_events(self, start_date: datetime, end_date: datetime, calendar_id: str = "primary") -> List[CalendarEvent]:
        """Get events from Google Calendar within the specified date range."""
        if not self.api_key and not self.access_token:
            self.logger.error("Not authenticated with Google Calendar API")
            return []
        
        try:
            # Format dates for API
            start_date_str = start_date.isoformat() + "Z"  # UTC format
            end_date_str = end_date.isoformat() + "Z"  # UTC format
            
            # Build URL
            url = f"{self.base_url}/calendars/{calendar_id}/events"
            params = {
                "timeMin": start_date_str,
                "timeMax": end_date_str,
                "singleEvents": "true",
                "orderBy": "startTime"
            }
            
            # Add authentication
            if self.access_token:
                headers = {"Authorization": f"Bearer {self.access_token}"}
            else:
                params["key"] = self.api_key
                headers = {}
            
            # Make request
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, headers=headers) as response:
                    if response.status != 200:
                        self.logger.error(f"Error getting Google Calendar events: {response.status}")
                        return []
                    
                    data = await response.json()
            
            # Parse events
            events = []
            for item in data.get("items", []):
                # Parse start and end times
                start = item.get("start", {})
                end = item.get("end", {})
                
                start_time = None
                end_time = None
                is_all_day = False
                
                if "dateTime" in start:
                    start_time = datetime.fromisoformat(start["dateTime"].replace("Z", "+00:00"))
                elif "date" in start:
                    start_time = datetime.fromisoformat(start["date"])
                    is_all_day = True
                
                if "dateTime" in end:
                    end_time = datetime.fromisoformat(end["dateTime"].replace("Z", "+00:00"))
                elif "date" in end:
                    end_time = datetime.fromisoformat(end["date"])
                
                if not start_time:
                    continue
                
                # Create event
                event = CalendarEvent(
                    event_id=item.get("id", ""),
                    title=item.get("summary", "Untitled Event"),
                    start_time=start_time,
                    end_time=end_time,
                    description=item.get("description", ""),
                    location=item.get("location", ""),
                    calendar_id=calendar_id,
                    attendees=[attendee.get("email", "") for attendee in item.get("attendees", [])],
                    is_all_day=is_all_day,
                    recurrence=item.get("recurrence"),
                    source="google"
                )
                
                events.append(event)
            
            self.logger.info(f"Retrieved {len(events)} events from Google Calendar")
            return events
        except Exception as e:
            self.logger.error(f"Error getting Google Calendar events: {e}")
            return []
    
    # Additional methods for adding, updating, and deleting events would be implemented here


class OutlookCalendarProvider:
    """Provides integration with Microsoft Outlook Calendar API."""
    
    def __init__(self, client_id: Optional[str] = None, client_secret: Optional[str] = None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.token_expiry: Optional[datetime] = None
        self.logger = get_logger("outlook_calendar")
        
        self.base_url = "https://graph.microsoft.com/v1.0"
    
    async def authenticate(self) -> bool:
        """Authenticate with Microsoft Graph API."""
        # This is a placeholder for actual OAuth2 authentication
        # In a real implementation, this would handle the OAuth2 flow
        if not self.client_id or not self.client_secret:
            self.logger.error("No OAuth credentials provided for Outlook Calendar")
            return False
        
        self.logger.info("Authenticated with Outlook Calendar API")
        return True
    
    async def get_events(self, start_date: datetime, end_date: datetime) -> List[CalendarEvent]:
        """Get events from Outlook Calendar within the specified date range."""
        if not self.access_token:
            self.logger.error("Not authenticated with Outlook Calendar API")
            return []
        
        try:
            # Format dates for API
            start_date_str = start_date.isoformat()
            end_date_str = end_date.isoformat()
            
            # Build URL
            url = f"{self.base_url}/me/calendarView"
            params = {
                "startDateTime": start_date_str,
                "endDateTime": end_date_str,
                "$select": "id,subject,bodyPreview,start,end,location,attendees,isAllDay,recurrence"
            }
            
            # Add authentication
            headers = {"Authorization": f"Bearer {self.access_token}"}
            
            # Make request
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, headers=headers) as response:
                    if response.status != 200:
                        self.logger.error(f"Error getting Outlook Calendar events: {response.status}")
                        return []
                    
                    data = await response.json()
            
            # Parse events
            events = []
            for item in data.get("value", []):
                # Parse start and end times
                start = item.get("start", {})
                end = item.get("end", {})
                
                start_time = datetime.fromisoformat(start.get("dateTime", "").replace("Z", "+00:00"))
                end_time = datetime.fromisoformat(end.get("dateTime", "").replace("Z", "+00:00"))
                
                # Create event
                event = CalendarEvent(
                    event_id=item.get("id", ""),
                    title=item.get("subject", "Untitled Event"),
                    start_time=start_time,
                    end_time=end_time,
                    description=item.get("bodyPreview", ""),
                    location=item.get("location", {}).get("displayName", ""),
                    attendees=[attendee.get("emailAddress", {}).get("address", "") for attendee in item.get("attendees", [])],
                    is_all_day=item.get("isAllDay", False),
                    recurrence=item.get("recurrence"),
                    source="outlook"
                )
                
                events.append(event)
            
            self.logger.info(f"Retrieved {len(events)} events from Outlook Calendar")
            return events
        except Exception as e:
            self.logger.error(f"Error getting Outlook Calendar events: {e}")
            return []
    
    # Additional methods for adding, updating, and deleting events would be implemented here


class ICalendarProvider:
    """Provides integration with iCalendar files and URLs."""
    
    def __init__(self):
        self.logger = get_logger("ical_calendar")
    
    async def get_events_from_url(self, url: str, start_date: datetime, end_date: datetime) -> List[CalendarEvent]:
        """Get events from an iCalendar URL within the specified date range."""
        try:
            # Fetch the iCalendar data
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        self.logger.error(f"Error fetching iCalendar data: {response.status}")
                        return []
                    
                    ical_data = await response.text()
            
            # Parse the iCalendar data
            return self._parse_ical(ical_data, start_date, end_date, source=url)
        except Exception as e:
            self.logger.error(f"Error getting events from iCalendar URL: {e}")
            return []
    
    async def get_events_from_file(self, file_path: str, start_date: datetime, end_date: datetime) -> List[CalendarEvent]:
        """Get events from an iCalendar file within the specified date range."""
        try:
            # Read the iCalendar file
            with open(file_path, "r", encoding="utf-8") as f:
                ical_data = f.read()
            
            # Parse the iCalendar data
            return self._parse_ical(ical_data, start_date, end_date, source=file_path)
        except Exception as e:
            self.logger.error(f"Error getting events from iCalendar file: {e}")
            return []
    
    def _parse_ical(self, ical_data: str, start_date: datetime, end_date: datetime, source: str) -> List[CalendarEvent]:
        """Parse iCalendar data and extract events within the specified date range."""
        try:
            # Parse the iCalendar data
            cal = Calendar.from_ical(ical_data)
            
            # Extract events
            events = []
            for component in cal.walk():
                if component.name != "VEVENT":
                    continue
                
                # Get event properties
                event_id = str(component.get("UID", ""))
                title = str(component.get("SUMMARY", "Untitled Event"))
                description = str(component.get("DESCRIPTION", ""))
                location = str(component.get("LOCATION", ""))
                
                # Get start and end times
                dtstart = component.get("DTSTART")
                dtend = component.get("DTEND")
                
                if not dtstart:
                    continue
                
                start_time = dtstart.dt
                end_time = dtend.dt if dtend else None
                
                # Check if it's an all-day event
                is_all_day = isinstance(start_time, datetime.date) and not isinstance(start_time, datetime.datetime)
                
                # Convert date to datetime if needed
                if is_all_day:
                    start_time = datetime.combine(start_time, datetime.min.time())
                    if end_time:
                        end_time = datetime.combine(end_time, datetime.min.time())
                
                # Check if the event is within the specified date range
                if end_time and end_time < start_date:
                    continue
                if start_time > end_date:
                    continue
                
                # Create event
                event = CalendarEvent(
                    event_id=event_id,
                    title=title,
                    start_time=start_time,
                    end_time=end_time,
                    description=description,
                    location=location,
                    is_all_day=is_all_day,
                    source="ical"
                )
                
                events.append(event)
            
            self.logger.info(f"Parsed {len(events)} events from iCalendar data")
            return events
        except Exception as e:
            self.logger.error(f"Error parsing iCalendar data: {e}")
            return []


class CalendarManager:
    """Manages calendar providers and events."""
    
    def __init__(self, data_dir: Path, settings: Settings):
        self.data_dir = data_dir
        self.settings = settings
        self.logger = get_logger("calendar_manager")
        
        # Initialize providers
        self.local_provider = LocalCalendarProvider(data_dir)
        self.google_provider: Optional[GoogleCalendarProvider] = None
        self.outlook_provider: Optional[OutlookCalendarProvider] = None
        self.ical_provider = ICalendarProvider()
        
        # Initialize providers based on settings
        if settings.feature_calendar_google_enabled:
            self.google_provider = GoogleCalendarProvider(
                api_key=settings.feature_calendar_google_api_key,
                client_id=settings.feature_calendar_google_client_id,
                client_secret=settings.feature_calendar_google_client_secret
            )
        
        if settings.feature_calendar_outlook_enabled:
            self.outlook_provider = OutlookCalendarProvider(
                client_id=settings.feature_calendar_outlook_client_id,
                client_secret=settings.feature_calendar_outlook_client_secret
            )
    
    async def initialize(self) -> None:
        """Initialize the calendar manager."""
        try:
            # Load local events
            await self.local_provider.load_events()
            
            # Authenticate with external providers
            if self.google_provider:
                await self.google_provider.authenticate()
            
            if self.outlook_provider:
                await self.outlook_provider.authenticate()
            
            self.logger.info("Initialized CalendarManager")
        except Exception as e:
            self.logger.error(f"Error initializing CalendarManager: {e}")
            raise FeatureManagerException(f"Failed to initialize CalendarManager: {e}")
    
    async def get_events(self, start_date: datetime, end_date: datetime, sources: Optional[List[str]] = None) -> List[CalendarEvent]:
        """Get events from all enabled providers within the specified date range."""
        all_events: List[CalendarEvent] = []
        tasks = []
        
        # Determine which sources to query
        sources = sources or ["local", "google", "outlook", "ical"]
        
        # Query local provider
        if "local" in sources:
            tasks.append(self.local_provider.get_events(start_date, end_date))
        
        # Query Google provider
        if "google" in sources and self.google_provider:
            tasks.append(self.google_provider.get_events(start_date, end_date))
        
        # Query Outlook provider
        if "outlook" in sources and self.outlook_provider:
            tasks.append(self.outlook_provider.get_events(start_date, end_date))
        
        # Query iCalendar URLs
        if "ical" in sources and self.settings.feature_calendar_ical_urls:
            for url in self.settings.feature_calendar_ical_urls:
                tasks.append(self.ical_provider.get_events_from_url(url, start_date, end_date))
        
        # Wait for all tasks to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        for result in results:
            if isinstance(result, Exception):
                self.logger.error(f"Error getting events: {result}")
            else:
                all_events.extend(result)
        
        # Sort events by start time
        all_events.sort(key=lambda e: e.start_time)
        
        self.logger.info(f"Retrieved {len(all_events)} events from all providers")
        return all_events
    
    async def get_events_for_day(self, date: datetime, sources: Optional[List[str]] = None) -> List[CalendarEvent]:
        """Get events for a specific day."""
        start_date = datetime(date.year, date.month, date.day, 0, 0, 0)
        end_date = datetime(date.year, date.month, date.day, 23, 59, 59)
        
        return await self.get_events(start_date, end_date, sources)
    
    async def get_events_for_week(self, date: datetime, sources: Optional[List[str]] = None) -> List[CalendarEvent]:
        """Get events for a specific week."""
        # Calculate the start of the week (Monday)
        start_date = date - timedelta(days=date.weekday())
        start_date = datetime(start_date.year, start_date.month, start_date.day, 0, 0, 0)
        
        # Calculate the end of the week (Sunday)
        end_date = start_date + timedelta(days=6)
        end_date = datetime(end_date.year, end_date.month, end_date.day, 23, 59, 59)
        
        return await self.get_events(start_date, end_date, sources)
    
    async def get_events_for_month(self, date: datetime, sources: Optional[List[str]] = None) -> List[CalendarEvent]:
        """Get events for a specific month."""
        # Calculate the start of the month
        start_date = datetime(date.year, date.month, 1, 0, 0, 0)
        
        # Calculate the end of the month
        if date.month == 12:
            end_date = datetime(date.year + 1, 1, 1, 0, 0, 0) - timedelta(seconds=1)
        else:
            end_date = datetime(date.year, date.month + 1, 1, 0, 0, 0) - timedelta(seconds=1)
        
        return await self.get_events(start_date, end_date, sources)
    
    async def add_event(self, event: CalendarEvent) -> CalendarEvent:
        """Add a new event to the local calendar."""
        return await self.local_provider.add_event(event)
    
    async def update_event(self, event_id: str, updated_event: CalendarEvent) -> Optional[CalendarEvent]:
        """Update an existing event in the local calendar."""
        return await self.local_provider.update_event(event_id, updated_event)
    
    async def delete_event(self, event_id: str) -> bool:
        """Delete an event from the local calendar."""
        return await self.local_provider.delete_event(event_id)
    
    async def get_upcoming_events(self, days: int = 7, limit: int = 10, sources: Optional[List[str]] = None) -> List[CalendarEvent]:
        """Get upcoming events for the next N days."""
        start_date = datetime.now()
        end_date = start_date + timedelta(days=days)
        
        events = await self.get_events(start_date, end_date, sources)
        
        # Limit the number of events
        return events[:limit] if len(events) > limit else events
    
    async def cleanup(self) -> None:
        """Clean up resources."""
        await self.local_provider.save_events()
        self.logger.info("Cleaned up CalendarManager")