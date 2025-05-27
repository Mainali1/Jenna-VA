"""Flashcards Feature Implementation"""

import asyncio
import json
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional

from backend.core.config import Settings
from backend.core.logger import get_logger
from backend.utils.exceptions import FeatureManagerException


class Flashcard:
    """Represents a single flashcard with spaced repetition metadata."""
    
    def __init__(self, card_id: str, front: str, back: str, deck_id: str):
        self.card_id = card_id
        self.front = front
        self.back = back
        self.deck_id = deck_id
        
        # Spaced repetition metadata
        self.ease_factor = 2.5  # Initial ease factor
        self.interval = 0       # Days between reviews
        self.repetitions = 0    # Number of successful reviews
        self.last_reviewed = None
        self.next_review = datetime.now()
        self.created_at = datetime.now()
    
    def review(self, quality: int) -> None:
        """Review the card with a quality rating (0-5).
        
        0 = Complete blackout
        1 = Incorrect response; the correct one remembered
        2 = Incorrect response; the correct one seemed familiar
        3 = Correct response, but required significant effort
        4 = Correct response, after some hesitation
        5 = Correct response with perfect recall
        """
        self.last_reviewed = datetime.now()
        
        # Constrain quality between 0 and 5
        quality = max(0, min(5, quality))
        
        # SM-2 algorithm implementation
        if quality < 3:
            # Failed recall, reset repetitions
            self.repetitions = 0
            self.interval = 0
        else:
            # Successful recall
            if self.repetitions == 0:
                self.interval = 1
            elif self.repetitions == 1:
                self.interval = 6
            else:
                self.interval = round(self.interval * self.ease_factor)
            
            self.repetitions += 1
        
        # Update ease factor
        self.ease_factor += 0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)
        self.ease_factor = max(1.3, self.ease_factor)  # Minimum ease factor
        
        # Calculate next review date
        self.next_review = datetime.now() + timedelta(days=self.interval)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "card_id": self.card_id,
            "front": self.front,
            "back": self.back,
            "deck_id": self.deck_id,
            "ease_factor": self.ease_factor,
            "interval": self.interval,
            "repetitions": self.repetitions,
            "last_reviewed": self.last_reviewed.isoformat() if self.last_reviewed else None,
            "next_review": self.next_review.isoformat(),
            "created_at": self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Flashcard':
        """Create a Flashcard from a dictionary."""
        card = cls(data["card_id"], data["front"], data["back"], data["deck_id"])
        card.ease_factor = data.get("ease_factor", 2.5)
        card.interval = data.get("interval", 0)
        card.repetitions = data.get("repetitions", 0)
        
        if data.get("last_reviewed"):
            card.last_reviewed = datetime.fromisoformat(data["last_reviewed"])
        
        card.next_review = datetime.fromisoformat(data["next_review"])
        card.created_at = datetime.fromisoformat(data["created_at"])
        
        return card


class Deck:
    """Represents a deck of flashcards."""
    
    def __init__(self, deck_id: str, name: str, description: str = ""):
        self.deck_id = deck_id
        self.name = name
        self.description = description
        self.cards: Dict[str, Flashcard] = {}
        self.created_at = datetime.now()
        self.last_modified = datetime.now()
    
    def add_card(self, card: Flashcard) -> None:
        """Add a card to the deck."""
        self.cards[card.card_id] = card
        self.last_modified = datetime.now()
    
    def remove_card(self, card_id: str) -> bool:
        """Remove a card from the deck."""
        if card_id in self.cards:
            del self.cards[card_id]
            self.last_modified = datetime.now()
            return True
        return False
    
    def get_card(self, card_id: str) -> Optional[Flashcard]:
        """Get a card by ID."""
        return self.cards.get(card_id)
    
    def get_all_cards(self) -> List[Flashcard]:
        """Get all cards in the deck."""
        return list(self.cards.values())
    
    def get_due_cards(self) -> List[Flashcard]:
        """Get cards due for review."""
        now = datetime.now()
        return [card for card in self.cards.values() if card.next_review <= now]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "deck_id": self.deck_id,
            "name": self.name,
            "description": self.description,
            "cards": [card.to_dict() for card in self.cards.values()],
            "created_at": self.created_at.isoformat(),
            "last_modified": self.last_modified.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Deck':
        """Create a Deck from a dictionary."""
        deck = cls(data["deck_id"], data["name"], data.get("description", ""))
        deck.created_at = datetime.fromisoformat(data["created_at"])
        deck.last_modified = datetime.fromisoformat(data["last_modified"])
        
        for card_data in data.get("cards", []):
            card = Flashcard.from_dict(card_data)
            deck.cards[card.card_id] = card
        
        return deck


class FlashcardsManager:
    """Manages flashcard decks and study sessions."""
    
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir / "flashcards"
        self.decks: Dict[str, Deck] = {}
        self.logger = get_logger("flashcards")
        
        # Create data directory if it doesn't exist
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    async def load_decks(self) -> None:
        """Load all decks from disk."""
        try:
            for deck_file in self.data_dir.glob("*.json"):
                try:
                    with open(deck_file, "r", encoding="utf-8") as f:
                        deck_data = json.load(f)
                        deck = Deck.from_dict(deck_data)
                        self.decks[deck.deck_id] = deck
                        self.logger.info(f"Loaded deck: {deck.name} ({len(deck.cards)} cards)")
                except Exception as e:
                    self.logger.error(f"Error loading deck {deck_file}: {e}")
        except Exception as e:
            self.logger.error(f"Error loading decks: {e}")
    
    async def save_deck(self, deck_id: str) -> bool:
        """Save a deck to disk."""
        if deck_id not in self.decks:
            return False
        
        try:
            deck = self.decks[deck_id]
            deck_file = self.data_dir / f"{deck_id}.json"
            
            with open(deck_file, "w", encoding="utf-8") as f:
                json.dump(deck.to_dict(), f, indent=2)
            
            self.logger.info(f"Saved deck: {deck.name}")
            return True
        except Exception as e:
            self.logger.error(f"Error saving deck {deck_id}: {e}")
            return False
    
    async def save_all_decks(self) -> None:
        """Save all decks to disk."""
        for deck_id in self.decks:
            await self.save_deck(deck_id)
    
    def create_deck(self, name: str, description: str = "") -> Deck:
        """Create a new deck."""
        import uuid
        deck_id = str(uuid.uuid4())
        deck = Deck(deck_id, name, description)
        self.decks[deck_id] = deck
        self.logger.info(f"Created new deck: {name} ({deck_id})")
        return deck
    
    def delete_deck(self, deck_id: str) -> bool:
        """Delete a deck."""
        if deck_id not in self.decks:
            return False
        
        try:
            deck_file = self.data_dir / f"{deck_id}.json"
            if deck_file.exists():
                deck_file.unlink()
            
            del self.decks[deck_id]
            self.logger.info(f"Deleted deck: {deck_id}")
            return True
        except Exception as e:
            self.logger.error(f"Error deleting deck {deck_id}: {e}")
            return False
    
    def get_deck(self, deck_id: str) -> Optional[Deck]:
        """Get a deck by ID."""
        return self.decks.get(deck_id)
    
    def get_all_decks(self) -> List[Deck]:
        """Get all decks."""
        return list(self.decks.values())
    
    def add_card_to_deck(self, deck_id: str, front: str, back: str) -> Optional[Flashcard]:
        """Add a card to a deck."""
        if deck_id not in self.decks:
            return None
        
        import uuid
        card_id = str(uuid.uuid4())
        card = Flashcard(card_id, front, back, deck_id)
        
        self.decks[deck_id].add_card(card)
        self.logger.info(f"Added card to deck {deck_id}: {front[:20]}...")
        return card
    
    def remove_card_from_deck(self, deck_id: str, card_id: str) -> bool:
        """Remove a card from a deck."""
        if deck_id not in self.decks:
            return False
        
        return self.decks[deck_id].remove_card(card_id)
    
    def get_due_cards(self, deck_id: str) -> List[Flashcard]:
        """Get cards due for review in a deck."""
        if deck_id not in self.decks:
            return []
        
        return self.decks[deck_id].get_due_cards()
    
    def get_all_due_cards(self) -> List[Flashcard]:
        """Get all cards due for review across all decks."""
        due_cards = []
        for deck in self.decks.values():
            due_cards.extend(deck.get_due_cards())
        return due_cards
    
    def review_card(self, card_id: str, quality: int) -> bool:
        """Review a card with a quality rating."""
        for deck in self.decks.values():
            card = deck.get_card(card_id)
            if card:
                card.review(quality)
                self.logger.info(f"Reviewed card {card_id} with quality {quality}")
                return True
        return False
    
    def get_study_stats(self) -> Dict[str, Any]:
        """Get study statistics."""
        total_cards = 0
        total_due = 0
        total_decks = len(self.decks)
        deck_stats = []
        
        for deck in self.decks.values():
            cards = deck.get_all_cards()
            due_cards = deck.get_due_cards()
            
            total_cards += len(cards)
            total_due += len(due_cards)
            
            deck_stats.append({
                "deck_id": deck.deck_id,
                "name": deck.name,
                "total_cards": len(cards),
                "due_cards": len(due_cards)
            })
        
        return {
            "total_cards": total_cards,
            "total_due": total_due,
            "total_decks": total_decks,
            "deck_stats": deck_stats
        }