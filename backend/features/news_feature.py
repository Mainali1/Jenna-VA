"""News Feature Implementation for News API"""

import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List

from backend.core.config import Settings
from backend.core.feature_manager import Feature
from backend.core.logger import get_logger
from backend.utils.exceptions import FeatureManagerException
from backend.utils.helpers import is_internet_available


class NewsFeature(Feature):
    """Feature for retrieving news articles using News API."""
    
    def __init__(self):
        super().__init__(
            name="news",
            description="News articles and headlines",
            requires_api=True
        )
        self.api_key = None
        self.api_url = "https://newsapi.org/v2/"
        self.logger = get_logger("news_feature")
        self.cached_headlines = {}
        self.last_update = None
        self.cache_duration = timedelta(minutes=30)  # Cache news for 30 minutes
    
    def _check_api_requirements(self, settings: Settings) -> bool:
        """Check if News API key is available."""
        return bool(settings.news_api_key)
    
    async def _initialize_impl(self, settings: Settings) -> bool:
        """Initialize the News feature."""
        try:
            self.logger.info("Initializing NewsFeature")
            
            # Store API key
            self.api_key = settings.news_api_key
            
            # Store user preferences if available
            self.default_country = getattr(settings, 'news_default_country', 'us')
            self.default_language = getattr(settings, 'news_default_language', 'en')
            self.default_category = getattr(settings, 'news_default_category', 'general')
            
            self.logger.info("NewsFeature initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize NewsFeature: {e}")
            return False
    
    # API methods
    
    async def get_top_headlines(self, country: Optional[str] = None, 
                               category: Optional[str] = None,
                               query: Optional[str] = None,
                               page_size: int = 10,
                               page: int = 1) -> Dict[str, Any]:
        """Get top news headlines.
        
        Args:
            country: 2-letter ISO 3166-1 country code
            category: Category of news (business, entertainment, general, health, science, sports, technology)
            query: Keywords or phrases to search for
            page_size: Number of results to return per page (max 100)
            page: Page number
        """
        if not self.enabled:
            raise FeatureManagerException("NewsFeature is not enabled")
        
        # Check internet connectivity
        if not is_internet_available():
            self.logger.warning("Internet connection not available for news headlines")
            
            # Return cached headlines if available and not expired
            cache_key = f"{country or self.default_country}:{category or self.default_category}:{query or ''}"
            if (cache_key in self.cached_headlines and self.last_update and 
                datetime.now() - self.last_update < self.cache_duration):
                self.logger.info("Returning cached news headlines")
                return {
                    **self.cached_headlines[cache_key],
                    "cached": True,
                    "cache_timestamp": self.last_update.isoformat()
                }
            
            return {
                "error": "No internet connection available",
                "timestamp": datetime.now().isoformat()
            }
        
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.api_url}top-headlines"
                
                # Prepare parameters
                params = {
                    "apiKey": self.api_key,
                    "pageSize": min(page_size, 100),  # API limit
                    "page": page
                }
                
                # Add optional parameters
                if country:
                    params["country"] = country
                elif self.default_country:
                    params["country"] = self.default_country
                    
                if category:
                    params["category"] = category
                elif self.default_category:
                    params["category"] = self.default_category
                    
                if query:
                    params["q"] = query
                
                self.logger.info(f"Fetching top headlines for {params}")
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Check for API error
                        if data.get("status") != "ok":
                            error_info = data.get("message", "Unknown API error")
                            self.logger.error(f"News API error: {error_info}")
                            return {
                                "error": error_info,
                                "timestamp": datetime.now().isoformat()
                            }
                        
                        # Format the response
                        result = {
                            "articles": data.get("articles", []),
                            "total_results": data.get("totalResults", 0),
                            "timestamp": datetime.now().isoformat()
                        }
                        
                        # Cache the results
                        cache_key = f"{country or self.default_country}:{category or self.default_category}:{query or ''}"
                        self.cached_headlines[cache_key] = result
                        self.last_update = datetime.now()
                        
                        return result
                    else:
                        self.logger.error(f"News API request failed with status {response.status}")
                        return {
                            "error": f"API request failed with status {response.status}",
                            "timestamp": datetime.now().isoformat()
                        }
        except Exception as e:
            self.logger.error(f"Error getting news headlines: {e}")
            return {
                "error": f"Failed to get news headlines: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    async def search_news(self, query: str, from_date: Optional[str] = None, 
                        to_date: Optional[str] = None, language: Optional[str] = None,
                        sort_by: str = "publishedAt", page_size: int = 10, 
                        page: int = 1) -> Dict[str, Any]:
        """Search for news articles.
        
        Args:
            query: Keywords or phrases to search for
            from_date: A date in ISO 8601 format (e.g., 2023-12-01)
            to_date: A date in ISO 8601 format (e.g., 2023-12-31)
            language: 2-letter ISO-639-1 language code
            sort_by: Sort order (relevancy, popularity, publishedAt)
            page_size: Number of results to return per page (max 100)
            page: Page number
        """
        if not self.enabled:
            raise FeatureManagerException("NewsFeature is not enabled")
        
        # Check internet connectivity
        if not is_internet_available():
            self.logger.warning("Internet connection not available for news search")
            return {
                "error": "No internet connection available",
                "timestamp": datetime.now().isoformat()
            }
        
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.api_url}everything"
                
                # Prepare parameters
                params = {
                    "apiKey": self.api_key,
                    "q": query,
                    "pageSize": min(page_size, 100),  # API limit
                    "page": page,
                    "sortBy": sort_by
                }
                
                # Add optional parameters
                if from_date:
                    params["from"] = from_date
                    
                if to_date:
                    params["to"] = to_date
                    
                if language:
                    params["language"] = language
                elif self.default_language:
                    params["language"] = self.default_language
                
                self.logger.info(f"Searching news for '{query}'")
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Check for API error
                        if data.get("status") != "ok":
                            error_info = data.get("message", "Unknown API error")
                            self.logger.error(f"News API error: {error_info}")
                            return {
                                "error": error_info,
                                "timestamp": datetime.now().isoformat()
                            }
                        
                        # Format the response
                        return {
                            "articles": data.get("articles", []),
                            "total_results": data.get("totalResults", 0),
                            "timestamp": datetime.now().isoformat()
                        }
                    else:
                        self.logger.error(f"News API request failed with status {response.status}")
                        return {
                            "error": f"API request failed with status {response.status}",
                            "timestamp": datetime.now().isoformat()
                        }
        except Exception as e:
            self.logger.error(f"Error searching news: {e}")
            return {
                "error": f"Failed to search news: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_news_sources(self, category: Optional[str] = None, 
                             language: Optional[str] = None, 
                             country: Optional[str] = None) -> Dict[str, Any]:
        """Get available news sources.
        
        Args:
            category: Category of news source
            language: 2-letter ISO-639-1 language code
            country: 2-letter ISO 3166-1 country code
        """
        if not self.enabled:
            raise FeatureManagerException("NewsFeature is not enabled")
        
        # Check internet connectivity
        if not is_internet_available():
            self.logger.warning("Internet connection not available for news sources")
            return {
                "error": "No internet connection available",
                "timestamp": datetime.now().isoformat()
            }
        
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.api_url}sources"
                
                # Prepare parameters
                params = {"apiKey": self.api_key}
                
                # Add optional parameters
                if category:
                    params["category"] = category
                    
                if language:
                    params["language"] = language
                elif self.default_language:
                    params["language"] = self.default_language
                    
                if country:
                    params["country"] = country
                elif self.default_country:
                    params["country"] = self.default_country
                
                self.logger.info("Fetching news sources")
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Check for API error
                        if data.get("status") != "ok":
                            error_info = data.get("message", "Unknown API error")
                            self.logger.error(f"News API error: {error_info}")
                            return {
                                "error": error_info,
                                "timestamp": datetime.now().isoformat()
                            }
                        
                        # Format the response
                        return {
                            "sources": data.get("sources", []),
                            "timestamp": datetime.now().isoformat()
                        }
                    else:
                        self.logger.error(f"News API request failed with status {response.status}")
                        return {
                            "error": f"API request failed with status {response.status}",
                            "timestamp": datetime.now().isoformat()
                        }
        except Exception as e:
            self.logger.error(f"Error getting news sources: {e}")
            return {
                "error": f"Failed to get news sources: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }