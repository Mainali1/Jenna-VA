"""Service Manager for External Services and Integrations"""

import asyncio
import aiohttp
import json
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime, timedelta
from pathlib import Path

from .config import Settings
from .logger import get_logger
from ..utils.exceptions import ServiceManagerException


class ServiceHealth:
    """Represents the health status of a service."""
    
    def __init__(self, name: str):
        self.name = name
        self.is_healthy = False
        self.last_check = None
        self.error_count = 0
        self.last_error = None
        self.response_time = None
    
    def update_health(self, healthy: bool, response_time: Optional[float] = None, error: Optional[str] = None):
        """Update health status."""
        self.is_healthy = healthy
        self.last_check = datetime.now()
        self.response_time = response_time
        
        if not healthy:
            self.error_count += 1
            self.last_error = error
        else:
            self.error_count = 0
            self.last_error = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "healthy": self.is_healthy,
            "last_check": self.last_check.isoformat() if self.last_check else None,
            "error_count": self.error_count,
            "last_error": self.last_error,
            "response_time_ms": round(self.response_time * 1000) if self.response_time else None
        }


class BaseService:
    """Base class for all external services."""
    
    def __init__(self, name: str, base_url: Optional[str] = None):
        self.name = name
        self.base_url = base_url
        self.logger = get_logger(f"service.{name}")
        self.health = ServiceHealth(name)
        self.session: Optional[aiohttp.ClientSession] = None
        self.enabled = False
    
    async def initialize(self, settings: Settings) -> bool:
        """Initialize the service."""
        try:
            self.logger.info(f"🔧 Initializing service: {self.name}")
            
            # Create HTTP session
            timeout = aiohttp.ClientTimeout(total=30)
            self.session = aiohttp.ClientSession(timeout=timeout)
            
            # Service-specific initialization
            success = await self._initialize_impl(settings)
            
            if success:
                self.enabled = True
                self.logger.info(f"✅ Service {self.name} initialized")
            else:
                self.logger.error(f"❌ Failed to initialize service {self.name}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error initializing service {self.name}: {e}")
            return False
    
    async def _initialize_impl(self, settings: Settings) -> bool:
        """Service-specific initialization. Override in subclasses."""
        return True
    
    async def health_check(self) -> bool:
        """Perform health check."""
        try:
            start_time = datetime.now()
            success = await self._health_check_impl()
            response_time = (datetime.now() - start_time).total_seconds()
            
            self.health.update_health(success, response_time)
            return success
            
        except Exception as e:
            self.health.update_health(False, error=str(e))
            self.logger.warning(f"Health check failed for {self.name}: {e}")
            return False
    
    async def _health_check_impl(self) -> bool:
        """Service-specific health check. Override in subclasses."""
        return True
    
    async def cleanup(self):
        """Cleanup service resources."""
        try:
            if self.session:
                await self.session.close()
            
            await self._cleanup_impl()
            self.enabled = False
            self.logger.info(f"🧹 Service {self.name} cleaned up")
            
        except Exception as e:
            self.logger.error(f"Error cleaning up service {self.name}: {e}")
    
    async def _cleanup_impl(self):
        """Service-specific cleanup. Override in subclasses."""
        pass


class WeatherService(BaseService):
    """Weather API service."""
    
    def __init__(self):
        super().__init__("weather", "https://api.openweathermap.org/data/2.5")
        self.api_key = None
    
    async def _initialize_impl(self, settings: Settings) -> bool:
        """Initialize weather service."""
        self.api_key = settings.weather_api_key
        return bool(self.api_key)
    
    async def _health_check_impl(self) -> bool:
        """Check weather API health."""
        if not self.api_key or not self.session:
            return False
        
        try:
            url = f"{self.base_url}/weather"
            params = {
                "q": "London",
                "appid": self.api_key,
                "units": "metric"
            }
            
            async with self.session.get(url, params=params) as response:
                return response.status == 200
                
        except Exception:
            return False
    
    async def get_weather(self, location: str) -> Optional[Dict[str, Any]]:
        """Get weather for a location."""
        if not self.enabled or not self.session:
            return None
        
        try:
            url = f"{self.base_url}/weather"
            params = {
                "q": location,
                "appid": self.api_key,
                "units": "metric"
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "location": data["name"],
                        "temperature": f"{data['main']['temp']:.1f}°C",
                        "condition": data["weather"][0]["description"].title(),
                        "humidity": f"{data['main']['humidity']}%",
                        "wind_speed": f"{data['wind']['speed']} m/s",
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    self.logger.error(f"Weather API error: {response.status}")
                    return None
                    
        except Exception as e:
            self.logger.error(f"Error getting weather: {e}")
            return None


class WikipediaService(BaseService):
    """Wikipedia API service."""
    
    def __init__(self):
        super().__init__("wikipedia", "https://en.wikipedia.org/api/rest_v1")
    
    async def _health_check_impl(self) -> bool:
        """Check Wikipedia API health."""
        if not self.session:
            return False
        
        try:
            url = f"{self.base_url}/page/summary/Python_(programming_language)"
            async with self.session.get(url) as response:
                return response.status == 200
        except Exception:
            return False
    
    async def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search Wikipedia articles."""
        if not self.enabled or not self.session:
            return []
        
        try:
            url = "https://en.wikipedia.org/w/api.php"
            params = {
                "action": "query",
                "format": "json",
                "list": "search",
                "srsearch": query,
                "srlimit": limit
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    results = []
                    
                    for item in data.get("query", {}).get("search", []):
                        results.append({
                            "title": item["title"],
                            "snippet": item["snippet"],
                            "url": f"https://en.wikipedia.org/wiki/{item['title'].replace(' ', '_')}"
                        })
                    
                    return results
                else:
                    self.logger.error(f"Wikipedia search error: {response.status}")
                    return []
                    
        except Exception as e:
            self.logger.error(f"Error searching Wikipedia: {e}")
            return []
    
    async def get_summary(self, title: str) -> Optional[Dict[str, Any]]:
        """Get article summary."""
        if not self.enabled or not self.session:
            return None
        
        try:
            url = f"{self.base_url}/page/summary/{title.replace(' ', '_')}"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "title": data.get("title"),
                        "extract": data.get("extract"),
                        "url": data.get("content_urls", {}).get("desktop", {}).get("page"),
                        "thumbnail": data.get("thumbnail", {}).get("source") if "thumbnail" in data else None
                    }
                else:
                    self.logger.error(f"Wikipedia summary error: {response.status}")
                    return None
                    
        except Exception as e:
            self.logger.error(f"Error getting Wikipedia summary: {e}")
            return None


class OpenAIService(BaseService):
    """OpenAI API service."""
    
    def __init__(self):
        super().__init__("openai", "https://api.openai.com/v1")
        self.api_key = None
        self.model = "gpt-3.5-turbo"
    
    async def _initialize_impl(self, settings: Settings) -> bool:
        """Initialize OpenAI service."""
        self.api_key = settings.openai_api_key
        if hasattr(settings, 'openai_model'):
            self.model = settings.openai_model
        return bool(self.api_key)
    
    async def _health_check_impl(self) -> bool:
        """Check OpenAI API health."""
        if not self.api_key or not self.session:
            return False
        
        try:
            url = f"{self.base_url}/models"
            headers = {"Authorization": f"Bearer {self.api_key}"}
            
            async with self.session.get(url, headers=headers) as response:
                return response.status == 200
        except Exception:
            return False
    
    async def generate_response(self, messages: List[Dict[str, str]], max_tokens: int = 150) -> Optional[str]:
        """Generate AI response."""
        if not self.enabled or not self.session:
            return None
        
        try:
            url = f"{self.base_url}/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": 0.7
            }
            
            async with self.session.post(url, headers=headers, json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    return result["choices"][0]["message"]["content"].strip()
                else:
                    self.logger.error(f"OpenAI API error: {response.status}")
                    return None
                    
        except Exception as e:
            self.logger.error(f"Error generating AI response: {e}")
            return None


class ServiceManager:
    """Manages all external services."""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = get_logger(__name__)
        
        # Service registry
        self.services: Dict[str, BaseService] = {}
        
        # Health monitoring
        self.health_check_interval = 300  # 5 minutes
        self.health_check_task = None
        
        # Callbacks
        self.on_service_health_changed: Optional[Callable] = None
        
        # Initialize services
        self._register_services()
    
    def _register_services(self):
        """Register all available services."""
        services = [
            WeatherService(),
            WikipediaService(),
            OpenAIService(),
        ]
        
        for service in services:
            self.services[service.name] = service
            self.logger.info(f"📋 Registered service: {service.name}")
    
    async def initialize_all(self):
        """Initialize all services."""
        self.logger.info("🔧 Initializing services...")
        
        initialization_tasks = [
            service.initialize(self.settings)
            for service in self.services.values()
        ]
        
        results = await asyncio.gather(*initialization_tasks, return_exceptions=True)
        
        success_count = sum(1 for result in results if result is True)
        self.logger.info(f"✅ Initialized {success_count}/{len(self.services)} services")
        
        # Start health monitoring
        await self._start_health_monitoring()
        
        self.logger.info("🎯 Service initialization completed")
    
    async def _start_health_monitoring(self):
        """Start periodic health checks."""
        if self.health_check_task:
            return
        
        async def health_monitor():
            while True:
                try:
                    await self._perform_health_checks()
                    await asyncio.sleep(self.health_check_interval)
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    self.logger.error(f"Health monitoring error: {e}")
                    await asyncio.sleep(60)  # Wait before retrying
        
        self.health_check_task = asyncio.create_task(health_monitor())
        self.logger.info("💓 Started service health monitoring")
    
    async def _perform_health_checks(self):
        """Perform health checks on all services."""
        health_tasks = [
            service.health_check()
            for service in self.services.values()
            if service.enabled
        ]
        
        if health_tasks:
            await asyncio.gather(*health_tasks, return_exceptions=True)
            
            # Notify about health changes if callback is set
            if self.on_service_health_changed:
                await self.on_service_health_changed(self.get_health_status())
    
    def get_service(self, name: str) -> Optional[BaseService]:
        """Get a service by name."""
        return self.services.get(name)
    
    def get_health_status(self) -> Dict[str, Dict[str, Any]]:
        """Get health status of all services."""
        return {
            name: service.health.to_dict()
            for name, service in self.services.items()
        }
    
    def get_enabled_services(self) -> List[str]:
        """Get list of enabled service names."""
        return [
            name for name, service in self.services.items()
            if service.enabled
        ]
    
    def get_healthy_services(self) -> List[str]:
        """Get list of healthy service names."""
        return [
            name for name, service in self.services.items()
            if service.enabled and service.health.is_healthy
        ]
    
    async def get_weather(self, location: str) -> Optional[Dict[str, Any]]:
        """Get weather information."""
        weather_service = self.get_service("weather")
        if isinstance(weather_service, WeatherService):
            return await weather_service.get_weather(location)
        return None
    
    async def search_wikipedia(self, query: str) -> List[Dict[str, Any]]:
        """Search Wikipedia."""
        wiki_service = self.get_service("wikipedia")
        if isinstance(wiki_service, WikipediaService):
            return await wiki_service.search(query)
        return []
    
    async def get_wikipedia_summary(self, title: str) -> Optional[Dict[str, Any]]:
        """Get Wikipedia article summary."""
        wiki_service = self.get_service("wikipedia")
        if isinstance(wiki_service, WikipediaService):
            return await wiki_service.get_summary(title)
        return None
    
    async def generate_ai_response(self, messages: List[Dict[str, str]]) -> Optional[str]:
        """Generate AI response."""
        openai_service = self.get_service("openai")
        if isinstance(openai_service, OpenAIService):
            return await openai_service.generate_response(messages)
        return None
    
    async def cleanup_all(self):
        """Cleanup all services."""
        self.logger.info("🧹 Cleaning up services...")
        
        # Stop health monitoring
        if self.health_check_task:
            self.health_check_task.cancel()
            try:
                await self.health_check_task
            except asyncio.CancelledError:
                pass
        
        # Cleanup all services
        cleanup_tasks = [
            service.cleanup()
            for service in self.services.values()
            if service.enabled
        ]
        
        if cleanup_tasks:
            await asyncio.gather(*cleanup_tasks, return_exceptions=True)
        
        self.logger.info("✅ Service cleanup completed")