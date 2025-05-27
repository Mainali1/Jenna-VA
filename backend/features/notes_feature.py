"""Notes Feature Implementation"""

import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

from backend.core.config import Settings
from backend.core.feature_manager import Feature
from backend.core.logger import get_logger
from backend.features.notes import NotesManager, Note
from backend.utils.exceptions import FeatureManagerException


class NotesFeature(Feature):
    """Feature for managing notes."""
    
    def __init__(self):
        super().__init__(
            name="notes",
            description="Create and manage notes",
            requires_api=False
        )
        self.logger = get_logger("notes_feature")
        self.manager: Optional[NotesManager] = None
    
    async def _initialize_impl(self, settings: Settings) -> bool:
        """Initialize the notes feature."""
        try:
            self.logger.info("Initializing NotesFeature")
            
            # Create data directory if it doesn't exist
            data_dir = Path(settings.data_dir) / "notes"
            data_dir.mkdir(parents=True, exist_ok=True)
            
            # Initialize the notes manager
            self.manager = NotesManager(Path(settings.data_dir))
            await self.manager.load_data()
            
            self.logger.info("NotesFeature initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize NotesFeature: {e}")
            return False
    
    async def _on_enable(self):
        """Called when feature is enabled."""
        self.logger.info("NotesFeature enabled")
    
    async def _on_disable(self):
        """Called when feature is disabled."""
        self.logger.info("NotesFeature disabled")
    
    async def _cleanup_impl(self):
        """Feature-specific cleanup logic."""
        if self.manager:
            await self.manager.cleanup()
        self.logger.info("NotesFeature cleaned up")
    
    # API methods
    
    async def create_note(self, title: str, content: str, tags: Optional[List[str]] = None, color: str = "#ffffff", pinned: bool = False) -> Dict[str, Any]:
        """Create a new note."""
        if not self.enabled:
            raise FeatureManagerException("NotesFeature is not enabled")
        
        if not self.manager:
            raise FeatureManagerException("NotesFeature not initialized")
        
        note = await self.manager.create_note(title, content, tags, color, pinned)
        return note.to_dict()
    
    async def get_note(self, note_id: str) -> Optional[Dict[str, Any]]:
        """Get a note by ID."""
        if not self.enabled:
            raise FeatureManagerException("NotesFeature is not enabled")
        
        if not self.manager:
            raise FeatureManagerException("NotesFeature not initialized")
        
        note = await self.manager.get_note(note_id)
        return note.to_dict() if note else None
    
    async def get_all_notes(self) -> List[Dict[str, Any]]:
        """Get all notes."""
        if not self.enabled:
            raise FeatureManagerException("NotesFeature is not enabled")
        
        if not self.manager:
            raise FeatureManagerException("NotesFeature not initialized")
        
        notes = await self.manager.get_all_notes()
        return [note.to_dict() for note in notes]
    
    async def get_notes_by_tag(self, tag: str) -> List[Dict[str, Any]]:
        """Get notes by tag."""
        if not self.enabled:
            raise FeatureManagerException("NotesFeature is not enabled")
        
        if not self.manager:
            raise FeatureManagerException("NotesFeature not initialized")
        
        notes = await self.manager.get_notes_by_tag(tag)
        return [note.to_dict() for note in notes]
    
    async def update_note(self, note_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a note."""
        if not self.enabled:
            raise FeatureManagerException("NotesFeature is not enabled")
        
        if not self.manager:
            raise FeatureManagerException("NotesFeature not initialized")
        
        note = await self.manager.update_note(note_id, data)
        return note.to_dict() if note else None
    
    async def delete_note(self, note_id: str) -> bool:
        """Delete a note."""
        if not self.enabled:
            raise FeatureManagerException("NotesFeature is not enabled")
        
        if not self.manager:
            raise FeatureManagerException("NotesFeature not initialized")
        
        return await self.manager.delete_note(note_id)
    
    async def search_notes(self, query: str) -> List[Dict[str, Any]]:
        """Search notes by title and content."""
        if not self.enabled:
            raise FeatureManagerException("NotesFeature is not enabled")
        
        if not self.manager:
            raise FeatureManagerException("NotesFeature not initialized")
        
        notes = await self.manager.search_notes(query)
        return [note.to_dict() for note in notes]
    
    async def get_pinned_notes(self) -> List[Dict[str, Any]]:
        """Get all pinned notes."""
        if not self.enabled:
            raise FeatureManagerException("NotesFeature is not enabled")
        
        if not self.manager:
            raise FeatureManagerException("NotesFeature not initialized")
        
        notes = await self.manager.get_pinned_notes()
        return [note.to_dict() for note in notes]