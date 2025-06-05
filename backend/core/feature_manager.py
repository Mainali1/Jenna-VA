"""Feature Manager for Jenna Voice Assistant"""

import asyncio
import importlib
import inspect
import logging
from typing import Dict, List, Optional, Any, Callable, Type, Tuple, Set

from backend.core.config import Settings
from backend.utils.exceptions import FeatureManagerException
from backend.utils.helpers import get_logger
from backend.utils.helpers import is_internet_available


class Feature:
    """Base class for all features."""
    
    def __init__(self, settings: Settings):
        self.name = self.__class__.__name__.replace('Feature', '')
        self.settings = settings
        self.logger = get_logger(f"feature.{self.name.lower()}")
        self.initialized = False
        self.enabled = False
        
        # Feature metadata
        self.requires_api = False  # Set to True if feature requires API keys
        self.requires_internet = False  # Set to True if feature requires internet
        self.description = ""  # Feature description
        self.version = "1.0.0"  # Feature version
        self.author = "Jenna Team"  # Feature author
        
    async def initialize(self) -> bool:
        """Initialize the feature."""
        if self.initialized:
            self.logger.debug(f"Feature {self.name} already initialized")
            return True
        
        # Check if feature is enabled in settings
        feature_toggle = getattr(self.settings, f"feature_{self.name.lower()}", None)
        if feature_toggle is not None and not feature_toggle:
            self.logger.info(f"Feature {self.name} disabled in settings")
            return False
        
        # Check API requirements
        if self.requires_api and not await self._check_api_requirements():
            self.logger.warning(f"Feature {self.name} missing API requirements")
            return False
        
        # Check internet requirements
        if self.requires_internet and not is_internet_available():
            self.logger.warning(f"Feature {self.name} requires internet, but it's not available")
            return False
        
        # Initialize implementation
        try:
            await self._initialize_impl()
            self.initialized = True
            self.logger.info(f"✅ Feature {self.name} initialized")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize feature {self.name}: {e}")
            return False
    
    async def _check_api_requirements(self) -> bool:
        """Check if all required API keys are available."""
        # Override in subclasses to check specific API requirements
        return True
    
    async def _initialize_impl(self):
        """Implementation of feature initialization."""
        # Override in subclasses
        pass
    
    async def enable(self):
        """Enable the feature."""
        if not self.initialized:
            self.logger.warning(f"Cannot enable {self.name}: not initialized")
            return False
        
        self.enabled = True
        await self._on_enable()
        self.logger.info(f"🟢 Feature {self.name} enabled")
        return True
    
    async def _on_enable(self):
        """Called when feature is enabled."""
        # Override in subclasses
        pass
    
    async def disable(self):
        """Disable the feature."""
        if not self.enabled:
            return
        
        self.enabled = False
        await self._on_disable()
        self.logger.info(f"🔴 Feature {self.name} disabled")
    
    async def _on_disable(self):
        """Called when feature is disabled."""
        # Override in subclasses
        pass
    
    async def cleanup(self):
        """Cleanup resources used by the feature."""
        # Override in subclasses
        pass
    
    def get_status(self) -> Dict[str, Any]:
        """Get feature status."""
        return {
            "name": self.name,
            "initialized": self.initialized,
            "enabled": self.enabled,
            "requires_api": self.requires_api,
            "requires_internet": self.requires_internet,
            "description": self.description,
            "version": self.version,
            "author": self.author
        }


class FeatureManager:
    """Manages features for the voice assistant."""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = get_logger(__name__)
        self.features: Dict[str, Feature] = {}
        self._register_features()
    
    def _register_features(self):
        """Register all available features."""
        from backend.features.pomodoro_feature import PomodoroFeature
        from backend.features.weather_feature import WeatherFeature
        from backend.features.email_feature import EmailFeature
        from backend.features.ipstack_feature import IPstackFeature
        from backend.features.fixer_feature import FixerFeature
        from backend.features.news_feature import NewsFeature
        from backend.features.dictionary_feature import DictionaryFeature
        from backend.features.translation_feature import TranslationFeature
        from backend.features.recipe_feature import RecipeFeature
        from backend.features.nutrition_feature import NutritionFeature
        
        # Import new features
        from backend.features.health_fitness_feature import HealthFitnessFeature
        from backend.features.financial_management_feature import FinancialManagementFeature
        from backend.features.music_media_feature import MusicMediaFeature
        from backend.features.voice_personality_feature import VoicePersonalityFeature
        
        # Register core features
        self.register_feature(PomodoroFeature(self.settings))
        self.register_feature(WeatherFeature(self.settings))
        self.register_feature(EmailFeature(self.settings))
        self.register_feature(IPstackFeature(self.settings))
        self.register_feature(FixerFeature(self.settings))
        self.register_feature(NewsFeature(self.settings))
        
        # Register new features
        self.register_feature(DictionaryFeature(self.settings))
        self.register_feature(TranslationFeature(self.settings))
        self.register_feature(RecipeFeature(self.settings))
        self.register_feature(NutritionFeature(self.settings))
        
        # Register additional features
        self.register_feature(HealthFitnessFeature(self.settings))
        self.register_feature(FinancialManagementFeature(self.settings))
        self.register_feature(MusicMediaFeature(self.settings))
        self.register_feature(VoicePersonalityFeature(self.settings))
        
        # Log registered features
        self.logger.info(f"Registered {len(self.features)} features")
    
    def register_feature(self, feature: Feature):
        """Register a feature."""
        self.features[feature.name.lower()] = feature
    
    async def initialize_all(self):
        """Initialize all features."""
        self.logger.info("Initializing features...")
        
        # Initialize features in parallel
        init_tasks = [self._initialize_feature(feature) for feature in self.features.values()]
        await asyncio.gather(*init_tasks)
        
        # Count initialized features
        initialized_count = sum(1 for feature in self.features.values() if feature.initialized)
        self.logger.info(f"✅ Initialized {initialized_count}/{len(self.features)} features")
    
    async def _initialize_feature(self, feature: Feature):
        """Initialize a feature and enable it if successful."""
        try:
            if await feature.initialize():
                # Auto-enable feature if initialization was successful
                await feature.enable()
        except Exception as e:
            self.logger.error(f"Error initializing feature {feature.name}: {e}")
    
    async def enable_feature(self, feature_name: str) -> bool:
        """Enable a feature by name."""
        feature = self.get_feature(feature_name)
        if not feature:
            return False
        
        # Check internet requirement
        if feature.requires_internet and not is_internet_available():
            self.logger.warning(f"Cannot enable {feature_name}: requires internet connection")
            return False
        
        # Initialize if not already initialized
        if not feature.initialized and not await feature.initialize():
            return False
        
        return await feature.enable()
    
    async def disable_feature(self, feature_name: str) -> bool:
        """Disable a feature by name."""
        feature = self.get_feature(feature_name)
        if not feature:
            return False
        
        await feature.disable()
        return True
    
    async def toggle_feature(self, feature_name: str) -> bool:
        """Toggle a feature by name."""
        feature = self.get_feature(feature_name)
        if not feature:
            return False
        
        if feature.enabled:
            await feature.disable()
            return False
        else:
            return await self.enable_feature(feature_name)
    
    def get_feature(self, feature_name: str) -> Optional[Feature]:
        """Get a feature by name."""
        return self.features.get(feature_name.lower())
    
    def is_feature_enabled(self, feature_name: str) -> bool:
        """Check if a feature is enabled."""
        feature = self.get_feature(feature_name)
        return feature is not None and feature.enabled
    
    def is_feature_available(self, feature_name: str) -> bool:
        """Check if a feature is available (initialized)."""
        feature = self.get_feature(feature_name)
        return feature is not None and feature.initialized
    
    def get_feature_status(self, feature_name: str = None) -> Dict[str, Any]:
        """Get status of a specific feature or all features."""
        if feature_name:
            feature = self.get_feature(feature_name)
            if not feature:
                raise FeatureManagerException(f"Feature {feature_name} not found")
            return feature.get_status()
        
        # Return status of all features
        return {
            name: feature.get_status()
            for name, feature in self.features.items()
        }
    
    async def update_settings(self, settings: Settings):
        """Update settings for all features."""
        self.settings = settings
        
        # Update settings for each feature
        for feature in self.features.values():
            feature.settings = settings
            
            # Check if feature should be enabled/disabled based on settings
            feature_toggle = getattr(settings, f"feature_{feature.name.lower()}", None)
            if feature_toggle is not None:
                if feature_toggle and not feature.enabled and feature.initialized:
                    await feature.enable()
                elif not feature_toggle and feature.enabled:
                    await feature.disable()
    
    async def cleanup_all(self):
        """Cleanup all features."""
        self.logger.info("🧹 Cleaning up features...")
        
        cleanup_tasks = [
            feature.cleanup()
            for feature in self.features.values()
            if feature.initialized
        ]
        
        if cleanup_tasks:
            await asyncio.gather(*cleanup_tasks, return_exceptions=True)
        
        self.logger.info("✅ Feature cleanup completed")