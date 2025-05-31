"""Dictionary Feature Implementation using Wordnik API"""

import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List

from backend.core.config import Settings
from backend.core.feature_manager import Feature
from backend.core.logger import get_logger
from backend.utils.exceptions import FeatureManagerException
from backend.utils.helpers import is_internet_available


class DictionaryFeature(Feature):
    """Feature for retrieving word definitions, synonyms, and other word information using Wordnik API."""
    
    def __init__(self, settings: Settings):
        super().__init__(
            name="dictionary",
            description="Word definitions, synonyms, and other word information",
            requires_api=True
        )
        self.api_key = None
        self.api_url = "https://api.wordnik.com/v4/"
        self.logger = get_logger("dictionary_feature")
        self.cached_definitions = {}
        self.last_update = None
        self.cache_duration = timedelta(minutes=60)  # Cache definitions for 60 minutes
    
    def _check_api_requirements(self, settings: Settings) -> bool:
        """Check if Wordnik API key is available."""
        return bool(settings.wordnik_api_key)
    
    async def _initialize_impl(self, settings: Settings) -> bool:
        """Initialize the Dictionary feature."""
        try:
            self.logger.info("Initializing DictionaryFeature")
            
            # Store API key
            self.api_key = settings.wordnik_api_key
            
            self.logger.info("DictionaryFeature initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize DictionaryFeature: {e}")
            return False
    
    # API methods
    
    async def get_definition(self, word: str, limit: int = 5) -> Dict[str, Any]:
        """Get definitions for a word.
        
        Args:
            word: The word to look up
            limit: Maximum number of definitions to return
        """
        if not self.enabled:
            raise FeatureManagerException("DictionaryFeature is not enabled")
        
        # Check internet connectivity
        if not is_internet_available():
            self.logger.warning("Internet connection not available for dictionary lookup")
            return {
                "error": "No internet connection available",
                "timestamp": datetime.now().isoformat()
            }
        
        # Check cache first
        cache_key = f"{word}_{limit}"
        if cache_key in self.cached_definitions and self.last_update and \
           datetime.now() - self.last_update < self.cache_duration:
            self.logger.info(f"Returning cached definition for {word}")
            return self.cached_definitions[cache_key]
        
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.api_url}word.json/{word}/definitions"
                
                params = {
                    "api_key": self.api_key,
                    "limit": limit,
                    "sourceDictionaries": "all",
                    "useCanonical": "true"
                }
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Format the response
                        result = {
                            "word": word,
                            "definitions": []
                        }
                        
                        for definition in data:
                            result["definitions"].append({
                                "text": definition.get("text", ""),
                                "part_of_speech": definition.get("partOfSpeech", ""),
                                "source_dictionary": definition.get("sourceDictionary", ""),
                                "attribution": definition.get("attributionText", "")
                            })
                        
                        # Cache the result
                        self.cached_definitions[cache_key] = result
                        self.last_update = datetime.now()
                        
                        return result
                    elif response.status == 404:
                        return {
                            "word": word,
                            "error": "Word not found",
                            "timestamp": datetime.now().isoformat()
                        }
                    else:
                        self.logger.error(f"Error fetching definition: {response.status}")
                        return {
                            "word": word,
                            "error": f"API error: {response.status}",
                            "timestamp": datetime.now().isoformat()
                        }
        except Exception as e:
            self.logger.error(f"Error fetching definition for {word}: {e}")
            return {
                "word": word,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_synonyms(self, word: str, limit: int = 10) -> Dict[str, Any]:
        """Get synonyms for a word.
        
        Args:
            word: The word to look up
            limit: Maximum number of synonyms to return
        """
        if not self.enabled:
            raise FeatureManagerException("DictionaryFeature is not enabled")
        
        # Check internet connectivity
        if not is_internet_available():
            self.logger.warning("Internet connection not available for synonym lookup")
            return {
                "error": "No internet connection available",
                "timestamp": datetime.now().isoformat()
            }
        
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.api_url}word.json/{word}/relatedWords"
                
                params = {
                    "api_key": self.api_key,
                    "relationshipTypes": "synonym",
                    "limitPerRelationshipType": limit,
                    "useCanonical": "true"
                }
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Format the response
                        result = {
                            "word": word,
                            "synonyms": []
                        }
                        
                        for related_word in data:
                            if related_word.get("relationshipType") == "synonym":
                                result["synonyms"] = related_word.get("words", [])
                        
                        return result
                    elif response.status == 404:
                        return {
                            "word": word,
                            "error": "Word not found",
                            "timestamp": datetime.now().isoformat()
                        }
                    else:
                        self.logger.error(f"Error fetching synonyms: {response.status}")
                        return {
                            "word": word,
                            "error": f"API error: {response.status}",
                            "timestamp": datetime.now().isoformat()
                        }
        except Exception as e:
            self.logger.error(f"Error fetching synonyms for {word}: {e}")
            return {
                "word": word,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_examples(self, word: str, limit: int = 5) -> Dict[str, Any]:
        """Get example sentences for a word.
        
        Args:
            word: The word to look up
            limit: Maximum number of examples to return
        """
        if not self.enabled:
            raise FeatureManagerException("DictionaryFeature is not enabled")
        
        # Check internet connectivity
        if not is_internet_available():
            self.logger.warning("Internet connection not available for examples lookup")
            return {
                "error": "No internet connection available",
                "timestamp": datetime.now().isoformat()
            }
        
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.api_url}word.json/{word}/examples"
                
                params = {
                    "api_key": self.api_key,
                    "limit": limit
                }
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Format the response
                        result = {
                            "word": word,
                            "examples": []
                        }
                        
                        for example in data.get("examples", []):
                            result["examples"].append({
                                "text": example.get("text", ""),
                                "title": example.get("title", ""),
                                "url": example.get("url", "")
                            })
                        
                        return result
                    elif response.status == 404:
                        return {
                            "word": word,
                            "error": "Word not found",
                            "timestamp": datetime.now().isoformat()
                        }
                    else:
                        self.logger.error(f"Error fetching examples: {response.status}")
                        return {
                            "word": word,
                            "error": f"API error: {response.status}",
                            "timestamp": datetime.now().isoformat()
                        }
        except Exception as e:
            self.logger.error(f"Error fetching examples for {word}: {e}")
            return {
                "word": word,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_random_word(self) -> Dict[str, Any]:
        """Get a random word."""
        if not self.enabled:
            raise FeatureManagerException("DictionaryFeature is not enabled")
        
        # Check internet connectivity
        if not is_internet_available():
            self.logger.warning("Internet connection not available for random word lookup")
            return {
                "error": "No internet connection available",
                "timestamp": datetime.now().isoformat()
            }
        
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.api_url}words.json/randomWord"
                
                params = {
                    "api_key": self.api_key,
                    "hasDictionaryDef": "true",
                    "minCorpusCount": 1000,  # Common words only
                    "minLength": 3
                }
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Format the response
                        result = {
                            "word": data.get("word", ""),
                            "id": data.get("id", 0)
                        }
                        
                        return result
                    else:
                        self.logger.error(f"Error fetching random word: {response.status}")
                        return {
                            "error": f"API error: {response.status}",
                            "timestamp": datetime.now().isoformat()
                        }
        except Exception as e:
            self.logger.error(f"Error fetching random word: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_word_of_the_day(self) -> Dict[str, Any]:
        """Get the word of the day."""
        if not self.enabled:
            raise FeatureManagerException("DictionaryFeature is not enabled")
        
        # Check internet connectivity
        if not is_internet_available():
            self.logger.warning("Internet connection not available for word of the day lookup")
            return {
                "error": "No internet connection available",
                "timestamp": datetime.now().isoformat()
            }
        
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.api_url}words.json/wordOfTheDay"
                
                params = {
                    "api_key": self.api_key
                }
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Format the response
                        result = {
                            "word": data.get("word", ""),
                            "note": data.get("note", ""),
                            "definitions": []
                        }
                        
                        for definition in data.get("definitions", []):
                            result["definitions"].append({
                                "text": definition.get("text", ""),
                                "part_of_speech": definition.get("partOfSpeech", ""),
                                "source": definition.get("source", "")
                            })
                        
                        return result
                    else:
                        self.logger.error(f"Error fetching word of the day: {response.status}")
                        return {
                            "error": f"API error: {response.status}",
                            "timestamp": datetime.now().isoformat()
                        }
        except Exception as e:
            self.logger.error(f"Error fetching word of the day: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }