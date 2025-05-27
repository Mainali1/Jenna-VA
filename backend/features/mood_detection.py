"""Mood Detection Feature Implementation"""

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import re

import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.tokenize import word_tokenize, sent_tokenize

from backend.core.config import Settings
from backend.core.logger import get_logger
from backend.utils.exceptions import FeatureManagerException


class MoodAnalyzer:
    """Analyzes text to determine the user's mood using sentiment analysis."""
    
    def __init__(self):
        self.logger = get_logger("mood_analyzer")
        self.ensure_nltk_resources()
        self.sia = SentimentIntensityAnalyzer()
        
        # Define mood categories and their score ranges
        self.mood_categories = {
            "very_negative": (-1.0, -0.6),
            "negative": (-0.6, -0.2),
            "neutral": (-0.2, 0.2),
            "positive": (0.2, 0.6),
            "very_positive": (0.6, 1.0)
        }
        
        # Define mood responses for each category
        self.mood_responses = {
            "very_negative": [
                "I'm sorry to hear that you're feeling down. Is there anything I can do to help?",
                "It sounds like you're having a tough time. Would you like to talk about it?",
                "I'm here for you during this difficult moment. How can I support you?"
            ],
            "negative": [
                "I notice you seem a bit upset. Is everything okay?",
                "You sound a little frustrated. Would you like me to help with something?",
                "I'm sensing some negativity. Would a different topic help lift your spirits?"
            ],
            "neutral": [
                "How else can I assist you today?",
                "I'm ready to help with whatever you need.",
                "What would you like to do next?"
            ],
            "positive": [
                "You seem to be in a good mood! That's great to hear.",
                "I'm glad things are going well for you today.",
                "Your positive energy is contagious! How else can I help maintain this good mood?"
            ],
            "very_positive": [
                "Wow, you're really enthusiastic! I'm happy to see you so excited.",
                "Your excellent mood brightens my day too! What's got you so happy?",
                "It's wonderful to hear you so upbeat! Let's keep this positive momentum going."
            ]
        }
    
    def ensure_nltk_resources(self) -> None:
        """Ensure that required NLTK resources are downloaded."""
        try:
            resources = [
                'punkt',
                'vader_lexicon'
            ]
            
            for resource in resources:
                try:
                    nltk.data.find(f'tokenizers/{resource}')
                except LookupError:
                    self.logger.info(f"Downloading NLTK resource: {resource}")
                    nltk.download(resource, quiet=True)
        except Exception as e:
            self.logger.error(f"Error ensuring NLTK resources: {e}")
            raise FeatureManagerException(f"Failed to initialize NLTK resources: {e}")
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze the sentiment of the given text."""
        if not text or len(text.strip()) == 0:
            return {
                "compound": 0.0,
                "positive": 0.0,
                "negative": 0.0,
                "neutral": 0.0,
                "mood": "neutral"
            }
        
        # Get sentiment scores
        scores = self.sia.polarity_scores(text)
        
        # Determine mood category based on compound score
        mood = "neutral"
        for category, (min_score, max_score) in self.mood_categories.items():
            if min_score <= scores["compound"] < max_score:
                mood = category
                break
        
        # Add mood to scores
        scores["mood"] = mood
        
        return scores
    
    def analyze_text_mood(self, text: str) -> Dict[str, Any]:
        """Analyze the mood of the given text with detailed metrics."""
        # Tokenize text into sentences
        sentences = sent_tokenize(text)
        
        # Analyze each sentence
        sentence_scores = []
        for sentence in sentences:
            scores = self.analyze_sentiment(sentence)
            sentence_scores.append({
                "text": sentence,
                "scores": scores
            })
        
        # Calculate overall scores
        if sentence_scores:
            compound_scores = [s["scores"]["compound"] for s in sentence_scores]
            positive_scores = [s["scores"]["positive"] for s in sentence_scores]
            negative_scores = [s["scores"]["negative"] for s in sentence_scores]
            neutral_scores = [s["scores"]["neutral"] for s in sentence_scores]
            
            avg_compound = sum(compound_scores) / len(compound_scores)
            avg_positive = sum(positive_scores) / len(positive_scores)
            avg_negative = sum(negative_scores) / len(negative_scores)
            avg_neutral = sum(neutral_scores) / len(neutral_scores)
            
            # Determine overall mood
            overall_mood = "neutral"
            for category, (min_score, max_score) in self.mood_categories.items():
                if min_score <= avg_compound < max_score:
                    overall_mood = category
                    break
        else:
            avg_compound = 0.0
            avg_positive = 0.0
            avg_negative = 0.0
            avg_neutral = 0.0
            overall_mood = "neutral"
        
        # Get mood response
        import random
        mood_response = random.choice(self.mood_responses[overall_mood])
        
        return {
            "overall_mood": overall_mood,
            "mood_response": mood_response,
            "overall_scores": {
                "compound": avg_compound,
                "positive": avg_positive,
                "negative": avg_negative,
                "neutral": avg_neutral
            },
            "sentence_analysis": sentence_scores,
            "sentence_count": len(sentence_scores)
        }
    
    def get_mood_response(self, mood: str) -> str:
        """Get a response appropriate for the given mood."""
        import random
        return random.choice(self.mood_responses.get(mood, self.mood_responses["neutral"]))


class MoodHistory:
    """Manages the history of mood analysis results."""
    
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir / "mood"
        self.history: List[Dict[str, Any]] = []
        self.logger = get_logger("mood_history")
        
        # Create data directory if it doesn't exist
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    async def load_history(self) -> None:
        """Load mood history from disk."""
        history_file = self.data_dir / "history.json"
        
        if history_file.exists():
            try:
                with open(history_file, "r", encoding="utf-8") as f:
                    self.history = json.load(f)
                self.logger.info(f"Loaded {len(self.history)} mood entries from history")
            except Exception as e:
                self.logger.error(f"Error loading mood history: {e}")
    
    async def save_history(self) -> None:
        """Save mood history to disk."""
        history_file = self.data_dir / "history.json"
        
        try:
            # Keep only the most recent 100 entries to prevent the file from growing too large
            recent_history = self.history[-100:] if len(self.history) > 100 else self.history
            
            with open(history_file, "w", encoding="utf-8") as f:
                json.dump(recent_history, f, indent=2)
            self.logger.info(f"Saved {len(recent_history)} mood entries to history")
        except Exception as e:
            self.logger.error(f"Error saving mood history: {e}")
    
    def add_entry(self, text: str, analysis: Dict[str, Any]) -> None:
        """Add a new entry to the mood history."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "text": text[:100] + "..." if len(text) > 100 else text,  # Truncate long text
            "mood": analysis["overall_mood"],
            "compound_score": analysis["overall_scores"]["compound"],
            "positive_score": analysis["overall_scores"]["positive"],
            "negative_score": analysis["overall_scores"]["negative"],
            "neutral_score": analysis["overall_scores"]["neutral"]
        }
        
        self.history.append(entry)
        asyncio.create_task(self.save_history())
    
    def get_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get the most recent entries from the mood history."""
        return self.history[-limit:] if len(self.history) > limit else self.history
    
    def get_mood_trends(self) -> Dict[str, Any]:
        """Get mood trends over time."""
        if not self.history:
            return {
                "average_compound": 0.0,
                "mood_distribution": {
                    "very_negative": 0,
                    "negative": 0,
                    "neutral": 0,
                    "positive": 0,
                    "very_positive": 0
                },
                "trend": "neutral"
            }
        
        # Calculate average compound score
        compound_scores = [entry["compound_score"] for entry in self.history]
        avg_compound = sum(compound_scores) / len(compound_scores)
        
        # Calculate mood distribution
        mood_distribution = {
            "very_negative": 0,
            "negative": 0,
            "neutral": 0,
            "positive": 0,
            "very_positive": 0
        }
        
        for entry in self.history:
            mood_distribution[entry["mood"]] += 1
        
        # Determine overall trend
        if len(self.history) >= 5:
            recent_scores = [entry["compound_score"] for entry in self.history[-5:]]
            older_scores = [entry["compound_score"] for entry in self.history[-10:-5]] if len(self.history) >= 10 else [0.0] * 5
            
            avg_recent = sum(recent_scores) / len(recent_scores)
            avg_older = sum(older_scores) / len(older_scores)
            
            if avg_recent > avg_older + 0.2:
                trend = "improving"
            elif avg_recent < avg_older - 0.2:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "neutral"
        
        return {
            "average_compound": avg_compound,
            "mood_distribution": mood_distribution,
            "trend": trend
        }
    
    def clear_history(self) -> None:
        """Clear the mood history."""
        self.history = []
        asyncio.create_task(self.save_history())


class MoodDetectionManager:
    """Manages mood detection operations and history."""
    
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.analyzer = MoodAnalyzer()
        self.history = MoodHistory(data_dir)
        self.logger = get_logger("mood_detection")
        
        # Current conversation context for continuous mood tracking
        self.conversation_buffer: List[str] = []
        self.buffer_max_size = 10  # Maximum number of recent messages to keep
    
    async def initialize(self) -> None:
        """Initialize the mood detection manager."""
        try:
            # Load mood history
            await self.history.load_history()
            self.logger.info("Initialized MoodDetectionManager")
        except Exception as e:
            self.logger.error(f"Error initializing MoodDetectionManager: {e}")
            raise FeatureManagerException(f"Failed to initialize MoodDetectionManager: {e}")
    
    async def analyze_text(self, text: str, save_to_history: bool = True) -> Dict[str, Any]:
        """Analyze the mood of the given text."""
        try:
            # Add to conversation buffer
            self.add_to_conversation(text)
            
            # Analyze the text
            analysis = self.analyzer.analyze_text_mood(text)
            
            # Save to history if requested
            if save_to_history:
                self.history.add_entry(text, analysis)
            
            return analysis
        except Exception as e:
            self.logger.error(f"Error analyzing text mood: {e}")
            raise FeatureManagerException(f"Failed to analyze text mood: {e}")
    
    async def analyze_conversation(self) -> Dict[str, Any]:
        """Analyze the mood of the current conversation context."""
        if not self.conversation_buffer:
            return {
                "overall_mood": "neutral",
                "mood_response": "How can I help you today?",
                "overall_scores": {
                    "compound": 0.0,
                    "positive": 0.0,
                    "negative": 0.0,
                    "neutral": 1.0
                }
            }
        
        # Combine conversation buffer into a single text
        conversation_text = " ".join(self.conversation_buffer)
        
        # Analyze the combined text but don't save to history
        return await self.analyze_text(conversation_text, save_to_history=False)
    
    def add_to_conversation(self, text: str) -> None:
        """Add a message to the conversation buffer."""
        self.conversation_buffer.append(text)
        
        # Keep buffer size limited
        if len(self.conversation_buffer) > self.buffer_max_size:
            self.conversation_buffer = self.conversation_buffer[-self.buffer_max_size:]
    
    def clear_conversation(self) -> None:
        """Clear the conversation buffer."""
        self.conversation_buffer = []
    
    def get_appropriate_response(self, text: str) -> str:
        """Get a response appropriate for the mood of the given text."""
        analysis = self.analyzer.analyze_sentiment(text)
        return self.analyzer.get_mood_response(analysis["mood"])
    
    def get_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get the mood history."""
        return self.history.get_history(limit)
    
    def get_mood_trends(self) -> Dict[str, Any]:
        """Get mood trends over time."""
        return self.history.get_mood_trends()
    
    def clear_history(self) -> None:
        """Clear the mood history."""
        self.history.clear_history()
        self.logger.info("Cleared mood history")
    
    async def cleanup(self) -> None:
        """Clean up resources."""
        await self.history.save_history()
        self.logger.info("Cleaned up MoodDetectionManager")