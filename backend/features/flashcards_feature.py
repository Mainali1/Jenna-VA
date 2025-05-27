"""Flashcards Feature Implementation"""

import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional

from backend.core.config import Settings
from backend.core.feature_manager import Feature
from backend.core.logger import get_logger
from backend.features.flashcards import FlashcardsManager, Deck, Flashcard
from backend.utils.exceptions import FeatureManagerException


class FlashcardsFeature(Feature):
    """Feature for managing flashcards with spaced repetition."""
    
    def __init__(self):
        super().__init__(
            name="flashcards",
            description="Flashcards with spaced repetition for learning",
            requires_api=False
        )
        self.manager: Optional[FlashcardsManager] = None
    
    async def _initialize_impl(self, settings: Settings) -> bool:
        """Initialize the flashcards feature."""
        try:
            self.logger.info("Initializing FlashcardsFeature")
            
            # Create data directory if it doesn't exist
            data_dir = Path(settings.data_dir) / "flashcards"
            data_dir.mkdir(parents=True, exist_ok=True)
            
            # Initialize the flashcards manager
            self.manager = FlashcardsManager(data_dir)
            await self.manager.load_decks()
            
            self.logger.info("FlashcardsFeature initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize FlashcardsFeature: {e}")
            return False
    
    # API methods
    
    async def create_deck(self, name: str, description: str = "") -> Dict[str, Any]:
        """Create a new deck."""
        if not self.enabled:
            raise FeatureManagerException("FlashcardsFeature is not enabled")
        
        deck = self.manager.create_deck(name, description)
        await self.manager.save_deck(deck.deck_id)
        return deck.to_dict()
    
    async def delete_deck(self, deck_id: str) -> bool:
        """Delete a deck."""
        if not self.enabled:
            raise FeatureManagerException("FlashcardsFeature is not enabled")
        
        return self.manager.delete_deck(deck_id)
    
    async def get_deck(self, deck_id: str) -> Optional[Dict[str, Any]]:
        """Get a deck by ID."""
        if not self.enabled:
            raise FeatureManagerException("FlashcardsFeature is not enabled")
        
        deck = self.manager.get_deck(deck_id)
        return deck.to_dict() if deck else None
    
    async def get_all_decks(self) -> List[Dict[str, Any]]:
        """Get all decks."""
        if not self.enabled:
            raise FeatureManagerException("FlashcardsFeature is not enabled")
        
        decks = self.manager.get_all_decks()
        return [deck.to_dict() for deck in decks]
    
    async def add_card(self, deck_id: str, front: str, back: str) -> Optional[Dict[str, Any]]:
        """Add a card to a deck."""
        if not self.enabled:
            raise FeatureManagerException("FlashcardsFeature is not enabled")
        
        card = self.manager.add_card_to_deck(deck_id, front, back)
        if card:
            await self.manager.save_deck(deck_id)
            return card.to_dict()
        return None
    
    async def remove_card(self, deck_id: str, card_id: str) -> bool:
        """Remove a card from a deck."""
        if not self.enabled:
            raise FeatureManagerException("FlashcardsFeature is not enabled")
        
        result = self.manager.remove_card_from_deck(deck_id, card_id)
        if result:
            await self.manager.save_deck(deck_id)
        return result
    
    async def get_due_cards(self, deck_id: str) -> List[Dict[str, Any]]:
        """Get cards due for review in a deck."""
        if not self.enabled:
            raise FeatureManagerException("FlashcardsFeature is not enabled")
        
        cards = self.manager.get_due_cards(deck_id)
        return [card.to_dict() for card in cards]
    
    async def get_all_due_cards(self) -> List[Dict[str, Any]]:
        """Get all cards due for review across all decks."""
        if not self.enabled:
            raise FeatureManagerException("FlashcardsFeature is not enabled")
        
        cards = self.manager.get_all_due_cards()
        return [card.to_dict() for card in cards]
    
    async def review_card(self, card_id: str, quality: int) -> bool:
        """Review a card with a quality rating."""
        if not self.enabled:
            raise FeatureManagerException("FlashcardsFeature is not enabled")
        
        result = self.manager.review_card(card_id, quality)
        if result:
            # Find the deck that contains this card and save it
            for deck in self.manager.get_all_decks():
                if deck.get_card(card_id):
                    await self.manager.save_deck(deck.deck_id)
                    break
        return result
    
    async def get_study_stats(self) -> Dict[str, Any]:
        """Get study statistics."""
        if not self.enabled:
            raise FeatureManagerException("FlashcardsFeature is not enabled")
        
        return self.manager.get_study_stats()