"""NLU Engine Module for Jenna Voice Assistant.

This module provides natural language understanding capabilities
using both online and offline engines.
"""

import os
import sys
import json
import logging
import threading
from pathlib import Path
from typing import Optional, Dict, List, Tuple, Any, Callable, Union

# Setup logging
logger = logging.getLogger(__name__)


class NLUEngine:
    """NLU Engine for Jenna Voice Assistant.
    
    This class provides natural language understanding capabilities
    using both online and offline engines.
    """
    
    def __init__(self, config):
        """Initialize the NLU engine.
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.rasa_available = False
        self.rasa_model = None
        self.fallback_threshold = config.get_float("NLU", "fallback_threshold", fallback=0.3)
        
        # Initialize Rasa if available
        self._initialize_rasa()
    
    def _initialize_rasa(self):
        """Initialize Rasa NLU engine if available."""
        try:
            # Try to import Rasa components
            from rasa.core.agent import Agent
            from rasa.shared.utils.io import json_to_string
            
            # Get model path from config
            models_dir = Path(self.config.get("NLU", "models_dir", fallback="models"))
            rasa_dir = models_dir / "rasa"
            
            # Find the latest model file
            if rasa_dir.exists():
                model_files = list(rasa_dir.glob("*.tar.gz"))
                if model_files:
                    # Sort by modification time (newest first)
                    model_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
                    model_path = model_files[0]
                    
                    # Load the model
                    self.rasa_model = Agent.load(str(model_path))
                    self.rasa_available = True
                    logger.info(f"Rasa NLU model loaded from {model_path}")
                else:
                    logger.warning("No Rasa model found in models/rasa directory")
            else:
                logger.warning("Rasa models directory not found")
        
        except ImportError:
            logger.warning("Rasa not installed. Offline NLU will not be available.")
        except Exception as e:
            logger.error(f"Error initializing Rasa NLU: {e}")
    
    async def process(self, text: str) -> Dict[str, Any]:
        """Process text input and extract intent and entities.
        
        Args:
            text: Input text to process
            
        Returns:
            Dictionary containing intent and entities
        """
        # Default response structure
        result = {
            "text": text,
            "intent": {
                "name": "nlu_fallback",
                "confidence": 0.0
            },
            "entities": [],
            "intent_ranking": [],
            "engine": "fallback"
        }
        
        # Try Rasa first if available
        if self.rasa_available and self.rasa_model:
            try:
                # Process with Rasa
                rasa_result = await self.rasa_model.parse_message(text)
                
                # Check confidence threshold
                if rasa_result["intent"]["confidence"] >= self.fallback_threshold:
                    result = rasa_result
                    result["engine"] = "rasa"
                    return result
                
                # Store intent ranking for later use
                result["intent_ranking"] = rasa_result["intent_ranking"]
                
            except Exception as e:
                logger.error(f"Error processing with Rasa: {e}")
        
        # If Rasa is not available or confidence is low, try online NLU
        try:
            # Here we would integrate with an online NLU service
            # For now, we'll just use a simple keyword-based approach
            online_result = self._simple_keyword_nlu(text)
            
            if online_result["intent"]["confidence"] > result["intent"]["confidence"]:
                result = online_result
        
        except Exception as e:
            logger.error(f"Error processing with online NLU: {e}")
        
        return result
    
    def _simple_keyword_nlu(self, text: str) -> Dict[str, Any]:
        """Simple keyword-based NLU for fallback.
        
        Args:
            text: Input text to process
            
        Returns:
            Dictionary containing intent and entities
        """
        text_lower = text.lower()
        
        # Define some simple intent patterns
        patterns = {
            "greeting": ["hello", "hi", "hey", "greetings", "good morning", "good afternoon", "good evening"],
            "farewell": ["goodbye", "bye", "see you", "later", "good night"],
            "thanks": ["thank", "thanks", "appreciate", "grateful"],
            "help": ["help", "assist", "support", "guide"],
            "weather": ["weather", "temperature", "forecast", "rain", "snow", "sunny", "cloudy"],
            "time": ["time", "clock", "hour", "minute"],
            "date": ["date", "day", "month", "year", "calendar"],
            "music": ["play", "music", "song", "track", "album", "artist"],
            "volume": ["volume", "louder", "quieter", "mute", "unmute"],
            "search": ["search", "find", "look up", "google"],
            "joke": ["joke", "funny", "humor", "laugh"],
            "news": ["news", "headlines", "current events"],
            "reminder": ["remind", "reminder", "remember", "forget"],
            "alarm": ["alarm", "wake", "timer"],
            "email": ["email", "mail", "message", "send"],
            "translate": ["translate", "translation", "language"],
            "calculator": ["calculate", "math", "sum", "add", "subtract", "multiply", "divide"],
            "system": ["system", "computer", "restart", "shutdown", "sleep", "hibernate"],
            "repeat": ["repeat", "say again", "what did you say"],
            "stop": ["stop", "cancel", "end", "terminate"],
        }
        
        # Check for matches
        matches = {}
        for intent, keywords in patterns.items():
            count = 0
            for keyword in keywords:
                if keyword in text_lower:
                    count += 1
            if count > 0:
                matches[intent] = count / len(text_lower.split())
        
        # Find the best match
        best_intent = "nlu_fallback"
        best_confidence = 0.0
        
        for intent, confidence in matches.items():
            if confidence > best_confidence:
                best_intent = intent
                best_confidence = confidence
        
        # Adjust confidence to be between 0 and 1
        if best_confidence > 1.0:
            best_confidence = 1.0
        
        # Extract simple entities (very basic implementation)
        entities = []
        
        # Example: Extract time-related entities
        if "time" in matches or "date" in matches:
            import re
            # Look for time patterns like "10:30" or "10 PM"
            time_matches = re.findall(r'\d{1,2}:\d{2}|\d{1,2}\s?[ap]m', text_lower)
            for match in time_matches:
                entities.append({
                    "entity": "time",
                    "value": match,
                    "start": text_lower.find(match),
                    "end": text_lower.find(match) + len(match),
                    "confidence": 0.8
                })
        
        # Create intent ranking
        intent_ranking = []
        for intent, confidence in sorted(matches.items(), key=lambda x: x[1], reverse=True):
            intent_ranking.append({
                "name": intent,
                "confidence": confidence
            })
        
        # Add fallback intent if no matches found
        if not intent_ranking:
            intent_ranking.append({
                "name": "nlu_fallback",
                "confidence": 1.0
            })
        
        return {
            "text": text,
            "intent": {
                "name": best_intent,
                "confidence": best_confidence
            },
            "entities": entities,
            "intent_ranking": intent_ranking,
            "engine": "keyword"
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the NLU engine.
        
        Returns:
            Dictionary containing status information
        """
        return {
            "rasa_available": self.rasa_available,
            "fallback_threshold": self.fallback_threshold,
            "engines": ["rasa", "keyword"] if self.rasa_available else ["keyword"]
        }