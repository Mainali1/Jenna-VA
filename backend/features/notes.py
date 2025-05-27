"""Notes Feature Implementation"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

from backend.core.logger import get_logger
from backend.utils.exceptions import FeatureManagerException


class Note:
    """Represents a single note."""
    
    def __init__(
        self,
        note_id: str,
        title: str,
        content: str,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        tags: List[str] = None,
        color: str = "#ffffff",  # Default white color
        pinned: bool = False
    ):
        self.note_id = note_id
        self.title = title
        self.content = content
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
        self.tags = tags or []
        self.color = color
        self.pinned = pinned
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert note to dictionary."""
        return {
            "note_id": self.note_id,
            "title": self.title,
            "content": self.content,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "tags": self.tags,
            "color": self.color,
            "pinned": self.pinned
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Note':
        """Create a note from dictionary."""
        return cls(
            note_id=data["note_id"],
            title=data["title"],
            content=data["content"],
            created_at=datetime.fromisoformat(data["created_at"]) if isinstance(data["created_at"], str) else data["created_at"],
            updated_at=datetime.fromisoformat(data["updated_at"]) if isinstance(data["updated_at"], str) else data["updated_at"],
            tags=data.get("tags", []),
            color=data.get("color", "#ffffff"),
            pinned=data.get("pinned", False)
        )
    
    def update(self, data: Dict[str, Any]) -> None:
        """Update note properties from a dictionary."""
        if "title" in data:
            self.title = data["title"]
        
        if "content" in data:
            self.content = data["content"]
        
        if "tags" in data:
            self.tags = data["tags"]
        
        if "color" in data:
            self.color = data["color"]
        
        if "pinned" in data:
            self.pinned = data["pinned"]
        
        # Update the updated_at timestamp
        self.updated_at = datetime.now()


class NotesManager:
    """Manages notes."""
    
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir / "notes"
        self.notes_file = self.data_dir / "notes.json"
        self.logger = get_logger("notes_manager")
        
        # Create data directory if it doesn't exist
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize notes
        self.notes: Dict[str, Note] = {}
    
    async def load_data(self) -> None:
        """Load notes from disk."""
        # Load notes
        if self.notes_file.exists():
            try:
                with open(self.notes_file, "r", encoding="utf-8") as f:
                    notes_data = json.load(f)
                
                for note_data in notes_data:
                    note = Note.from_dict(note_data)
                    self.notes[note.note_id] = note
                
                self.logger.info(f"Loaded {len(self.notes)} notes from disk")
            except Exception as e:
                self.logger.error(f"Error loading notes: {e}")
        else:
            self.logger.info("Notes file does not exist, creating empty file")
            await self.save_notes()
    
    async def save_notes(self) -> None:
        """Save notes to disk."""
        try:
            notes_data = [note.to_dict() for note in self.notes.values()]
            
            with open(self.notes_file, "w", encoding="utf-8") as f:
                json.dump(notes_data, f, indent=2)
            
            self.logger.info(f"Saved {len(self.notes)} notes to disk")
        except Exception as e:
            self.logger.error(f"Error saving notes: {e}")
    
    async def create_note(self, title: str, content: str, tags: List[str] = None, color: str = "#ffffff", pinned: bool = False) -> Note:
        """Create a new note."""
        note_id = str(uuid.uuid4())
        
        note = Note(
            note_id=note_id,
            title=title,
            content=content,
            tags=tags or [],
            color=color,
            pinned=pinned
        )
        
        self.notes[note_id] = note
        await self.save_notes()
        
        return note
    
    async def get_note(self, note_id: str) -> Optional[Note]:
        """Get a note by ID."""
        return self.notes.get(note_id)
    
    async def get_all_notes(self) -> List[Note]:
        """Get all notes."""
        return list(self.notes.values())
    
    async def get_notes_by_tag(self, tag: str) -> List[Note]:
        """Get notes by tag."""
        return [note for note in self.notes.values() if tag in note.tags]
    
    async def update_note(self, note_id: str, data: Dict[str, Any]) -> Optional[Note]:
        """Update a note."""
        note = self.notes.get(note_id)
        if not note:
            return None
        
        note.update(data)
        await self.save_notes()
        
        return note
    
    async def delete_note(self, note_id: str) -> bool:
        """Delete a note."""
        if note_id not in self.notes:
            return False
        
        del self.notes[note_id]
        await self.save_notes()
        
        return True
    
    async def search_notes(self, query: str) -> List[Note]:
        """Search notes by title and content."""
        query = query.lower()
        return [
            note for note in self.notes.values()
            if query in note.title.lower() or query in note.content.lower()
        ]
    
    async def get_pinned_notes(self) -> List[Note]:
        """Get all pinned notes."""
        return [note for note in self.notes.values() if note.pinned]
    
    async def cleanup(self) -> None:
        """Clean up resources."""
        await self.save_notes()
        self.logger.info("Cleaned up NotesManager")