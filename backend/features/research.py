"""Research Feature Implementation"""

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import re
import urllib.parse

import aiohttp
from bs4 import BeautifulSoup

from backend.core.config import Settings
from backend.core.logger import get_logger
from backend.utils.exceptions import FeatureManagerException


class WikipediaClient:
    """Client for interacting with the Wikipedia API."""
    
    def __init__(self):
        self.base_url = "https://en.wikipedia.org/w/api.php"
        self.logger = get_logger("wikipedia_client")
    
    async def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search Wikipedia for articles matching the query."""
        params = {
            "action": "query",
            "format": "json",
            "list": "search",
            "srsearch": query,
            "srlimit": limit,
            "srprop": "snippet|titlesnippet"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("query", {}).get("search", [])
                    else:
                        self.logger.error(f"Wikipedia search failed with status {response.status}")
                        return []
        except Exception as e:
            self.logger.error(f"Error searching Wikipedia: {e}")
            return []
    
    async def get_article_summary(self, title: str) -> Optional[Dict[str, Any]]:
        """Get a summary of a Wikipedia article."""
        params = {
            "action": "query",
            "format": "json",
            "titles": title,
            "prop": "extracts|info|pageimages",
            "exintro": True,
            "explaintext": True,
            "inprop": "url",
            "pithumbsize": 300
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        pages = data.get("query", {}).get("pages", {})
                        
                        # The API returns a dict with page IDs as keys
                        if pages:
                            page_id = next(iter(pages))
                            page = pages[page_id]
                            
                            # Check if the page exists
                            if "missing" in page:
                                return None
                            
                            return {
                                "pageid": page.get("pageid"),
                                "title": page.get("title"),
                                "extract": page.get("extract"),
                                "url": page.get("fullurl"),
                                "thumbnail": page.get("thumbnail", {}).get("source")
                            }
                    else:
                        self.logger.error(f"Wikipedia article fetch failed with status {response.status}")
                        return None
        except Exception as e:
            self.logger.error(f"Error fetching Wikipedia article: {e}")
            return None
    
    async def get_article_sections(self, title: str) -> Optional[Dict[str, Any]]:
        """Get the sections of a Wikipedia article."""
        params = {
            "action": "parse",
            "format": "json",
            "page": title,
            "prop": "sections"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("parse", {})
                    else:
                        self.logger.error(f"Wikipedia sections fetch failed with status {response.status}")
                        return None
        except Exception as e:
            self.logger.error(f"Error fetching Wikipedia article sections: {e}")
            return None
    
    async def get_section_content(self, title: str, section_index: int) -> Optional[Dict[str, Any]]:
        """Get the content of a specific section in a Wikipedia article."""
        params = {
            "action": "parse",
            "format": "json",
            "page": title,
            "section": section_index,
            "prop": "text",
            "contentformat": "text/plain"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("parse", {})
                    else:
                        self.logger.error(f"Wikipedia section content fetch failed with status {response.status}")
                        return None
        except Exception as e:
            self.logger.error(f"Error fetching Wikipedia section content: {e}")
            return None
    
    async def get_related_articles(self, title: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get articles related to the given title."""
        params = {
            "action": "query",
            "format": "json",
            "titles": title,
            "prop": "links",
            "pllimit": limit
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        pages = data.get("query", {}).get("pages", {})
                        
                        if pages:
                            page_id = next(iter(pages))
                            page = pages[page_id]
                            links = page.get("links", [])
                            
                            return [{
                                "title": link.get("title")
                            } for link in links]
                        return []
                    else:
                        self.logger.error(f"Wikipedia related articles fetch failed with status {response.status}")
                        return []
        except Exception as e:
            self.logger.error(f"Error fetching related Wikipedia articles: {e}")
            return []


class WebSearchClient:
    """Client for performing web searches using a search engine API."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.logger = get_logger("web_search_client")
    
    async def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search the web for results matching the query."""
        if not self.api_key:
            self.logger.warning("Web search API key not provided")
            return []
        
        # This is a placeholder for a real search API implementation
        # In a real implementation, you would use a service like Google Custom Search API,
        # Bing Search API, or another search provider
        
        # For now, we'll return a message indicating that the API key is missing
        return [{
            "title": "API Key Required",
            "link": "#",
            "snippet": "To use web search, please provide a valid API key in the settings."
        }]


class ResearchHistory:
    """Manages the history of research queries and results."""
    
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir / "research"
        self.history: List[Dict[str, Any]] = []
        self.logger = get_logger("research_history")
        
        # Create data directory if it doesn't exist
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    async def load_history(self) -> None:
        """Load research history from disk."""
        history_file = self.data_dir / "history.json"
        
        if history_file.exists():
            try:
                with open(history_file, "r", encoding="utf-8") as f:
                    self.history = json.load(f)
                self.logger.info(f"Loaded {len(self.history)} research entries from history")
            except Exception as e:
                self.logger.error(f"Error loading research history: {e}")
    
    async def save_history(self) -> None:
        """Save research history to disk."""
        history_file = self.data_dir / "history.json"
        
        try:
            # Keep only the most recent 100 entries to prevent the file from growing too large
            recent_history = self.history[-100:] if len(self.history) > 100 else self.history
            
            with open(history_file, "w", encoding="utf-8") as f:
                json.dump(recent_history, f, indent=2)
            self.logger.info(f"Saved {len(recent_history)} research entries to history")
        except Exception as e:
            self.logger.error(f"Error saving research history: {e}")
    
    def add_entry(self, query: str, source: str, results: List[Dict[str, Any]]) -> None:
        """Add a new entry to the research history."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "source": source,
            "results_count": len(results),
            "results": results
        }
        
        self.history.append(entry)
        asyncio.create_task(self.save_history())
    
    def get_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get the most recent entries from the research history."""
        return self.history[-limit:] if len(self.history) > limit else self.history
    
    def search_history(self, query: str) -> List[Dict[str, Any]]:
        """Search the history for entries matching the query."""
        query = query.lower()
        matches = []
        
        for entry in self.history:
            if query in entry["query"].lower():
                matches.append(entry)
        
        return matches
    
    def clear_history(self) -> None:
        """Clear the research history."""
        self.history = []
        asyncio.create_task(self.save_history())


class ResearchManager:
    """Manages research operations and history."""
    
    def __init__(self, data_dir: Path, settings: Settings):
        self.data_dir = data_dir
        self.settings = settings
        self.wikipedia_client = WikipediaClient()
        self.web_search_client = WebSearchClient(api_key=settings.feature_research_api_key)
        self.history = ResearchHistory(data_dir)
        self.logger = get_logger("research_manager")
    
    async def initialize(self) -> None:
        """Initialize the research manager."""
        try:
            # Load research history
            await self.history.load_history()
            self.logger.info("Initialized ResearchManager")
        except Exception as e:
            self.logger.error(f"Error initializing ResearchManager: {e}")
            raise FeatureManagerException(f"Failed to initialize ResearchManager: {e}")
    
    async def search_wikipedia(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search Wikipedia for articles matching the query."""
        try:
            results = await self.wikipedia_client.search(query, limit)
            
            # Clean up HTML in snippets
            for result in results:
                if "snippet" in result:
                    result["snippet"] = self._clean_html(result["snippet"])
                if "titlesnippet" in result:
                    result["titlesnippet"] = self._clean_html(result["titlesnippet"])
            
            # Add to history
            self.history.add_entry(query, "wikipedia", results)
            
            return results
        except Exception as e:
            self.logger.error(f"Error searching Wikipedia: {e}")
            raise FeatureManagerException(f"Failed to search Wikipedia: {e}")
    
    async def get_wikipedia_article(self, title: str) -> Optional[Dict[str, Any]]:
        """Get a Wikipedia article by title."""
        try:
            article = await self.wikipedia_client.get_article_summary(title)
            
            if article:
                # Add to history
                self.history.add_entry(f"Article: {title}", "wikipedia_article", [article])
            
            return article
        except Exception as e:
            self.logger.error(f"Error getting Wikipedia article: {e}")
            raise FeatureManagerException(f"Failed to get Wikipedia article: {e}")
    
    async def search_web(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search the web for results matching the query."""
        try:
            results = await self.web_search_client.search(query, limit)
            
            # Add to history
            self.history.add_entry(query, "web", results)
            
            return results
        except Exception as e:
            self.logger.error(f"Error searching the web: {e}")
            raise FeatureManagerException(f"Failed to search the web: {e}")
    
    async def get_related_articles(self, title: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get articles related to the given title."""
        try:
            results = await self.wikipedia_client.get_related_articles(title, limit)
            return results
        except Exception as e:
            self.logger.error(f"Error getting related articles: {e}")
            raise FeatureManagerException(f"Failed to get related articles: {e}")
    
    def get_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get the research history."""
        return self.history.get_history(limit)
    
    def search_history(self, query: str) -> List[Dict[str, Any]]:
        """Search the history for entries matching the query."""
        return self.history.search_history(query)
    
    def clear_history(self) -> None:
        """Clear the research history."""
        self.history.clear_history()
        self.logger.info("Cleared research history")
    
    async def cleanup(self) -> None:
        """Clean up resources."""
        await self.history.save_history()
        self.logger.info("Cleaned up ResearchManager")
    
    def _clean_html(self, html: str) -> str:
        """Clean HTML tags and entities from a string."""
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', html)
        
        # Replace HTML entities
        text = text.replace('&quot;', '"')
        text = text.replace('&amp;', '&')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&nbsp;', ' ')
        
        return text