"""Reminders Feature Implementation"""

import json
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional, Union

from backend.core.logger import get_logger
from backend.utils.exceptions import FeatureManagerException


class Reminder:
    """Represents a single reminder."""
    
    def __init__(
        self,
        reminder_id: str,
        title: str,
        description: str,
        due_date: datetime,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        completed: bool = False,
        priority: str = "medium",  # low, medium, high
        repeat: Optional[str] = None,  # daily, weekly, monthly, yearly
        notify_before: Optional[int] = None,  # minutes before due date
        tags: List[str] = None
    ):
        self.reminder_id = reminder_id
        self.title = title
        self.description = description
        self.due_date = due_date
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
        self.completed = completed
        self.priority = priority
        self.repeat = repeat
        self.notify_before = notify_before
        self.tags = tags or []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert reminder to dictionary."""
        return {
            "reminder_id": self.reminder_id,
            "title": self.title,
            "description": self.description,
            "due_date": self.due_date.isoformat(),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "completed": self.completed,
            "priority": self.priority,
            "repeat": self.repeat,
            "notify_before": self.notify_before,
            "tags": self.tags
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Reminder':
        """Create a reminder from dictionary."""
        return cls(
            reminder_id=data["reminder_id"],
            title=data["title"],
            description=data["description"],
            due_date=datetime.fromisoformat(data["due_date"]) if isinstance(data["due_date"], str) else data["due_date"],
            created_at=datetime.fromisoformat(data["created_at"]) if isinstance(data["created_at"], str) else data["created_at"],
            updated_at=datetime.fromisoformat(data["updated_at"]) if isinstance(data["updated_at"], str) else data["updated_at"],
            completed=data.get("completed", False),
            priority=data.get("priority", "medium"),
            repeat=data.get("repeat"),
            notify_before=data.get("notify_before"),
            tags=data.get("tags", [])
        )
    
    def update(self, data: Dict[str, Any]) -> None:
        """Update reminder properties from a dictionary."""
        if "title" in data:
            self.title = data["title"]
        
        if "description" in data:
            self.description = data["description"]
        
        if "due_date" in data:
            self.due_date = data["due_date"]
        
        if "completed" in data:
            self.completed = data["completed"]
        
        if "priority" in data:
            self.priority = data["priority"]
        
        if "repeat" in data:
            self.repeat = data["repeat"]
        
        if "notify_before" in data:
            self.notify_before = data["notify_before"]
        
        if "tags" in data:
            self.tags = data["tags"]
        
        # Update the updated_at timestamp
        self.updated_at = datetime.now()


class RemindersManager:
    """Manages reminders."""
    
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir / "reminders"
        self.reminders_file = self.data_dir / "reminders.json"
        self.logger = get_logger("reminders_manager")
        
        # Create data directory if it doesn't exist
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize reminders
        self.reminders: Dict[str, Reminder] = {}
    
    async def load_data(self) -> None:
        """Load reminders from disk."""
        # Load reminders
        if self.reminders_file.exists():
            try:
                with open(self.reminders_file, "r", encoding="utf-8") as f:
                    reminders_data = json.load(f)
                
                for reminder_data in reminders_data:
                    reminder = Reminder.from_dict(reminder_data)
                    self.reminders[reminder.reminder_id] = reminder
                
                self.logger.info(f"Loaded {len(self.reminders)} reminders from disk")
            except Exception as e:
                self.logger.error(f"Error loading reminders: {e}")
        else:
            self.logger.info("Reminders file does not exist, creating empty file")
            await self.save_reminders()
    
    async def save_reminders(self) -> None:
        """Save reminders to disk."""
        try:
            reminders_data = [reminder.to_dict() for reminder in self.reminders.values()]
            
            with open(self.reminders_file, "w", encoding="utf-8") as f:
                json.dump(reminders_data, f, indent=2)
            
            self.logger.info(f"Saved {len(self.reminders)} reminders to disk")
        except Exception as e:
            self.logger.error(f"Error saving reminders: {e}")
    
    async def create_reminder(
        self,
        title: str,
        description: str,
        due_date: Union[datetime, str],
        priority: str = "medium",
        repeat: Optional[str] = None,
        notify_before: Optional[int] = None,
        tags: List[str] = None
    ) -> Reminder:
        """Create a new reminder."""
        reminder_id = str(uuid.uuid4())
        
        # Convert string due_date to datetime if needed
        if isinstance(due_date, str):
            due_date = datetime.fromisoformat(due_date)
        
        reminder = Reminder(
            reminder_id=reminder_id,
            title=title,
            description=description,
            due_date=due_date,
            priority=priority,
            repeat=repeat,
            notify_before=notify_before,
            tags=tags or []
        )
        
        self.reminders[reminder_id] = reminder
        await self.save_reminders()
        
        return reminder
    
    async def get_reminder(self, reminder_id: str) -> Optional[Reminder]:
        """Get a reminder by ID."""
        return self.reminders.get(reminder_id)
    
    async def get_all_reminders(self) -> List[Reminder]:
        """Get all reminders."""
        return list(self.reminders.values())
    
    async def get_reminders_by_tag(self, tag: str) -> List[Reminder]:
        """Get reminders by tag."""
        return [reminder for reminder in self.reminders.values() if tag in reminder.tags]
    
    async def get_upcoming_reminders(self, days: int = 7) -> List[Reminder]:
        """Get upcoming reminders within the specified number of days."""
        now = datetime.now()
        end_date = now + timedelta(days=days)
        
        return [
            reminder for reminder in self.reminders.values()
            if not reminder.completed and now <= reminder.due_date <= end_date
        ]
    
    async def get_overdue_reminders(self) -> List[Reminder]:
        """Get overdue reminders."""
        now = datetime.now()
        
        return [
            reminder for reminder in self.reminders.values()
            if not reminder.completed and reminder.due_date < now
        ]
    
    async def get_reminders_by_priority(self, priority: str) -> List[Reminder]:
        """Get reminders by priority."""
        return [
            reminder for reminder in self.reminders.values()
            if reminder.priority == priority
        ]
    
    async def update_reminder(self, reminder_id: str, data: Dict[str, Any]) -> Optional[Reminder]:
        """Update a reminder."""
        reminder = self.reminders.get(reminder_id)
        if not reminder:
            return None
        
        reminder.update(data)
        await self.save_reminders()
        
        return reminder
    
    async def mark_as_completed(self, reminder_id: str) -> Optional[Reminder]:
        """Mark a reminder as completed."""
        reminder = self.reminders.get(reminder_id)
        if not reminder:
            return None
        
        reminder.completed = True
        reminder.updated_at = datetime.now()
        await self.save_reminders()
        
        return reminder
    
    async def delete_reminder(self, reminder_id: str) -> bool:
        """Delete a reminder."""
        if reminder_id not in self.reminders:
            return False
        
        del self.reminders[reminder_id]
        await self.save_reminders()
        
        return True
    
    async def search_reminders(self, query: str) -> List[Reminder]:
        """Search reminders by title and description."""
        query = query.lower()
        return [
            reminder for reminder in self.reminders.values()
            if query in reminder.title.lower() or query in reminder.description.lower()
        ]
    
    async def cleanup(self) -> None:
        """Clean up resources."""
        await self.save_reminders()
        self.logger.info("Cleaned up RemindersManager")