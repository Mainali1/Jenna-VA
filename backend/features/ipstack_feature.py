"""IPstack Feature Implementation for IP Geolocation"""

import asyncio
import aiohttp
from datetime import datetime
from typing import Dict, Any, Optional

from backend.core.config import Settings
from backend.core.feature_manager import Feature
from backend.core.logger import get_logger
from backend.utils.exceptions import FeatureManagerException
from backend.utils.helpers import is_internet_available


class IPstackFeature(Feature):
    """Feature for IP geolocation using IPstack API."""
    
    def __init__(self):
        super().__init__(
            name="ipstack",
            description="IP geolocation and location data",
            requires_api=True
        )
        self.api_key = None
        self.api_url = "http://api.ipstack.com/"
        self.logger = get_logger("ipstack_feature")
    
    def _check_api_requirements(self, settings: Settings) -> bool:
        """Check if IPstack API key is available."""
        return bool(settings.ipstack_api_key)
    
    async def _initialize_impl(self, settings: Settings) -> bool:
        """Initialize the IPstack feature."""
        try:
            self.logger.info("Initializing IPstackFeature")
            
            # Store API key
            self.api_key = settings.ipstack_api_key
            
            self.logger.info("IPstackFeature initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize IPstackFeature: {e}")
            return False
    
    # API methods
    
    async def get_location_by_ip(self, ip_address: Optional[str] = None) -> Dict[str, Any]:
        """Get location information for an IP address.
        
        If no IP address is provided, the user's current IP will be used.
        """
        if not self.enabled:
            raise FeatureManagerException("IPstackFeature is not enabled")
        
        # Check internet connectivity
        if not is_internet_available():
            self.logger.warning("Internet connection not available for IP geolocation")
            return {
                "error": "No internet connection available",
                "timestamp": datetime.now().isoformat()
            }
        
        try:
            # If no IP is provided, use "check" endpoint to get current IP info
            endpoint = "check" if not ip_address else ip_address
            
            async with aiohttp.ClientSession() as session:
                url = f"{self.api_url}{endpoint}?access_key={self.api_key}"
                self.logger.info(f"Fetching IP geolocation data for {endpoint}")
                
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Check for API error
                        if "error" in data:
                            self.logger.error(f"IPstack API error: {data['error']['info']}")
                            return {
                                "error": data['error']['info'],
                                "timestamp": datetime.now().isoformat()
                            }
                        
                        # Format the response
                        return {
                            "ip": data.get("ip"),
                            "continent": data.get("continent_name"),
                            "country": data.get("country_name"),
                            "region": data.get("region_name"),
                            "city": data.get("city"),
                            "latitude": data.get("latitude"),
                            "longitude": data.get("longitude"),
                            "timezone": data.get("time_zone", {}).get("id"),
                            "currency": data.get("currency", {}).get("code"),
                            "connection": {
                                "asn": data.get("connection", {}).get("asn"),
                                "isp": data.get("connection", {}).get("isp")
                            },
                            "timestamp": datetime.now().isoformat()
                        }
                    else:
                        self.logger.error(f"IPstack API request failed with status {response.status}")
                        return {
                            "error": f"API request failed with status {response.status}",
                            "timestamp": datetime.now().isoformat()
                        }
        except Exception as e:
            self.logger.error(f"Error getting IP geolocation: {e}")
            return {
                "error": f"Failed to get IP geolocation: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_current_location(self) -> Dict[str, Any]:
        """Get the current location based on the user's IP address."""
        return await self.get_location_by_ip()