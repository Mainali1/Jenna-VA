"""Fixer Feature Implementation for Currency Exchange"""

import asyncio
import aiohttp
from datetime import datetime
from typing import Dict, Any, Optional, List

from backend.core.config import Settings
from backend.core.feature_manager import Feature
from backend.core.logger import get_logger
from backend.utils.exceptions import FeatureManagerException
from backend.utils.helpers import is_internet_available


class FixerFeature(Feature):
    """Feature for currency exchange rates using Fixer API."""
    
    def __init__(self):
        super().__init__(
            name="fixer",
            description="Currency exchange rates and conversion",
            requires_api=True
        )
        self.api_key = None
        self.api_url = "http://data.fixer.io/api/"
        self.base_currency = "EUR"  # Free plan only supports EUR as base
        self.logger = get_logger("fixer_feature")
        self.cached_rates = {}
        self.last_update = None
    
    def _check_api_requirements(self, settings: Settings) -> bool:
        """Check if Fixer API key is available."""
        return bool(settings.fixer_api_key)
    
    async def _initialize_impl(self, settings: Settings) -> bool:
        """Initialize the Fixer feature."""
        try:
            self.logger.info("Initializing FixerFeature")
            
            # Store API key
            self.api_key = settings.fixer_api_key
            
            # Set preferred base currency if available (premium feature)
            if hasattr(settings, 'preferred_currency'):
                self.preferred_currency = settings.preferred_currency
            
            self.logger.info("FixerFeature initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize FixerFeature: {e}")
            return False
    
    async def _on_enable(self):
        """Called when feature is enabled."""
        # Fetch latest rates when enabled
        if is_internet_available():
            await self.get_latest_rates()
    
    # API methods
    
    async def get_latest_rates(self, base: str = None) -> Dict[str, Any]:
        """Get latest exchange rates.
        
        Args:
            base: Base currency (only works with premium API plan)
        """
        if not self.enabled:
            raise FeatureManagerException("FixerFeature is not enabled")
        
        # Check internet connectivity
        if not is_internet_available():
            self.logger.warning("Internet connection not available for currency exchange rates")
            
            # Return cached rates if available
            if self.cached_rates and self.last_update:
                self.logger.info("Returning cached exchange rates")
                return {
                    **self.cached_rates,
                    "cached": True,
                    "timestamp": self.last_update.isoformat()
                }
            
            return {
                "error": "No internet connection available",
                "timestamp": datetime.now().isoformat()
            }
        
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.api_url}latest?access_key={self.api_key}"
                
                # Add base currency if specified (premium feature)
                if base:
                    url += f"&base={base}"
                
                self.logger.info("Fetching latest exchange rates")
                
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Check for API error
                        if not data.get("success", False):
                            error_info = data.get("error", {}).get("info", "Unknown API error")
                            self.logger.error(f"Fixer API error: {error_info}")
                            return {
                                "error": error_info,
                                "timestamp": datetime.now().isoformat()
                            }
                        
                        # Cache the results
                        self.cached_rates = data
                        self.last_update = datetime.now()
                        
                        # Format the response
                        return {
                            "base": data.get("base", "EUR"),
                            "date": data.get("date"),
                            "rates": data.get("rates", {}),
                            "timestamp": datetime.now().isoformat()
                        }
                    else:
                        self.logger.error(f"Fixer API request failed with status {response.status}")
                        return {
                            "error": f"API request failed with status {response.status}",
                            "timestamp": datetime.now().isoformat()
                        }
        except Exception as e:
            self.logger.error(f"Error getting exchange rates: {e}")
            return {
                "error": f"Failed to get exchange rates: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    async def convert_currency(self, amount: float, from_currency: str, to_currency: str) -> Dict[str, Any]:
        """Convert an amount from one currency to another."""
        if not self.enabled:
            raise FeatureManagerException("FixerFeature is not enabled")
        
        # Get latest rates
        rates_data = await self.get_latest_rates()
        
        # Check for errors
        if "error" in rates_data:
            return rates_data
        
        rates = rates_data.get("rates", {})
        base = rates_data.get("base", "EUR")
        
        # Normalize currencies
        from_currency = from_currency.upper()
        to_currency = to_currency.upper()
        
        try:
            # Direct conversion if base currency is the source
            if from_currency == base:
                if to_currency in rates:
                    converted_amount = amount * rates[to_currency]
                    return {
                        "amount": amount,
                        "from": from_currency,
                        "to": to_currency,
                        "result": converted_amount,
                        "rate": rates[to_currency],
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    return {"error": f"Currency {to_currency} not found in rates"}
            
            # If from_currency is not the base, we need to convert via the base
            elif from_currency in rates and to_currency in rates:
                # Convert from source to base first
                amount_in_base = amount / rates[from_currency]
                # Then convert from base to target
                converted_amount = amount_in_base * rates[to_currency]
                effective_rate = rates[to_currency] / rates[from_currency]
                
                return {
                    "amount": amount,
                    "from": from_currency,
                    "to": to_currency,
                    "result": converted_amount,
                    "rate": effective_rate,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                missing = []
                if from_currency not in rates and from_currency != base:
                    missing.append(from_currency)
                if to_currency not in rates and to_currency != base:
                    missing.append(to_currency)
                    
                return {"error": f"Currency not found in rates: {', '.join(missing)}"}
                
        except Exception as e:
            self.logger.error(f"Error converting currency: {e}")
            return {
                "error": f"Failed to convert currency: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_supported_currencies(self) -> List[str]:
        """Get list of supported currencies."""
        if not self.enabled:
            raise FeatureManagerException("FixerFeature is not enabled")
        
        # Get latest rates to ensure we have current data
        rates_data = await self.get_latest_rates()
        
        # Check for errors
        if "error" in rates_data:
            return []
        
        # Return list of currency codes
        rates = rates_data.get("rates", {})
        currencies = list(rates.keys())
        
        # Add base currency if not in rates
        base = rates_data.get("base", "EUR")
        if base not in currencies:
            currencies.append(base)
        
        return sorted(currencies)