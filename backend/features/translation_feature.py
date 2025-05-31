"""Translation Feature Implementation using LinguaTools API"""

import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List

from backend.core.config import Settings
from backend.core.feature_manager import Feature
from backend.core.logger import get_logger
from backend.utils.exceptions import FeatureManagerException
from backend.utils.helpers import is_internet_available


class TranslationFeature(Feature):
    """Feature for translating text between languages using LinguaTools API."""
    
    def __init__(self, settings: Settings):
        super().__init__(
            name="translation",
            description="Text translation between languages",
            requires_api=True
        )
        self.api_key = None
        self.api_url = "https://lt-translate-test.herokuapp.com/"
        self.logger = get_logger("translation_feature")
        self.cached_translations = {}
        self.last_update = None
        self.cache_duration = timedelta(minutes=60)  # Cache translations for 60 minutes
        self.supported_language_pairs = [
            "de-en", "de-es", "de-nl", "de-pl", "de-it", "de-cs",
            "en-de", "es-de", "nl-de", "pl-de", "it-de", "cs-de"
        ]
    
    def _check_api_requirements(self, settings: Settings) -> bool:
        """Check if LinguaTools API key is available."""
        return bool(settings.linguatools_api_key)
    
    async def _initialize_impl(self, settings: Settings) -> bool:
        """Initialize the Translation feature."""
        try:
            self.logger.info("Initializing TranslationFeature")
            
            # Store API key
            self.api_key = settings.linguatools_api_key
            
            self.logger.info("TranslationFeature initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize TranslationFeature: {e}")
            return False
    
    # API methods
    
    async def translate(self, text: str, source_lang: str, target_lang: str, word_class: Optional[str] = None) -> Dict[str, Any]:
        """Translate text from source language to target language.
        
        Args:
            text: The text to translate
            source_lang: Source language code (e.g., 'en', 'de')
            target_lang: Target language code (e.g., 'de', 'en')
            word_class: Optional word class filter (NOMEN, ADJ, VERB, ADVERB)
        """
        if not self.enabled:
            raise FeatureManagerException("TranslationFeature is not enabled")
        
        # Check internet connectivity
        if not is_internet_available():
            self.logger.warning("Internet connection not available for translation")
            return {
                "error": "No internet connection available",
                "timestamp": datetime.now().isoformat()
            }
        
        # Validate language pair
        lang_pair = f"{source_lang}-{target_lang}"
        if lang_pair not in self.supported_language_pairs:
            return {
                "error": f"Unsupported language pair: {lang_pair}",
                "supported_pairs": self.supported_language_pairs,
                "timestamp": datetime.now().isoformat()
            }
        
        # Check cache first
        cache_key = f"{text}_{lang_pair}_{word_class}"
        if cache_key in self.cached_translations and self.last_update and \
           datetime.now() - self.last_update < self.cache_duration:
            self.logger.info(f"Returning cached translation for {text}")
            return self.cached_translations[cache_key]
        
        try:
            async with aiohttp.ClientSession() as session:
                url = self.api_url
                
                params = {
                    "langpair": lang_pair,
                    "query": text,
                    "min_freq": 1  # Only return translations that have occurred at least once
                }
                
                # Add word class filter if provided
                if word_class and word_class in ["NOMEN", "ADJ", "VERB", "ADVERB"]:
                    params["wortart"] = word_class
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Format the response
                        result = {
                            "original_text": text,
                            "source_language": source_lang,
                            "target_language": target_lang,
                            "translations": []
                        }
                        
                        for translation in data:
                            result["translations"].append({
                                "text": translation.get("l1_text") if source_lang == "de" else translation.get("l2_text"),
                                "word_class": translation.get("wortart", ""),
                                "frequency": translation.get("freq", 0),
                                "synonyms": translation.get("synonyme1", "").split(", ") if translation.get("synonyme1") else []
                            })
                        
                        # Cache the result
                        self.cached_translations[cache_key] = result
                        self.last_update = datetime.now()
                        
                        return result
                    else:
                        self.logger.error(f"Error fetching translation: {response.status}")
                        return {
                            "original_text": text,
                            "error": f"API error: {response.status}",
                            "timestamp": datetime.now().isoformat()
                        }
        except Exception as e:
            self.logger.error(f"Error translating {text}: {e}")
            return {
                "original_text": text,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def get_supported_language_pairs(self) -> Dict[str, Any]:
        """Get list of supported language pairs."""
        return {
            "supported_language_pairs": self.supported_language_pairs,
            "language_codes": {
                "de": "German",
                "en": "English",
                "es": "Spanish",
                "nl": "Dutch",
                "pl": "Polish",
                "it": "Italian",
                "cs": "Czech"
            }
        }
    
    def get_supported_word_classes(self) -> Dict[str, Any]:
        """Get list of supported word classes for filtering."""
        return {
            "supported_word_classes": [
                "NOMEN",  # Noun
                "ADJ",    # Adjective
                "VERB",   # Verb
                "ADVERB"  # Adverb
            ]
        }