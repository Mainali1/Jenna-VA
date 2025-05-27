"""Feature Manager for Toggleable Features"""

import asyncio
from typing import Dict, Any, Optional, Callable, List
from datetime import datetime
from pathlib import Path

from .config import Settings
from .logger import get_logger
from ..utils.exceptions import FeatureManagerException

# Import features
try:
    from ..features.pomodoro_feature import PomodoroFeature
    from ..features.weather_feature import WeatherFeature
    from ..features.flashcards_feature import FlashcardsFeature
    from ..features.text_summarization_feature import TextSummarizationFeature
    from ..features.research_feature import ResearchFeature
    from ..features.mood_detection_feature import MoodDetectionFeature
    from ..features.screen_analysis_feature import ScreenAnalysisFeature
    from ..features.calendar_integration_feature import CalendarIntegrationFeature
    from ..features.task_management_feature import TaskManagementFeature
    from ..features.notes_feature import NotesFeature
    from ..features.reminders_feature import RemindersFeature
except ImportError as e:
    print(f"Warning: Some features could not be imported: {e}")
    # Create placeholder classes for missing features
    class PomodoroFeature:
        pass
    class WeatherFeature:
        pass
    class FlashcardsFeature:
        pass
    class TextSummarizationFeature:
        pass
    class ResearchFeature:
        pass
    class MoodDetectionFeature:
        pass
    class ScreenAnalysisFeature:
        pass
    class CalendarIntegrationFeature:
        pass
    class TaskManagementFeature:
        pass
    class NotesFeature:
        pass
    class RemindersFeature:
        pass


class Feature:
    """Base class for all features."""
    
    def __init__(self, name: str, description: str, requires_api: bool = False):
        self.name = name
        self.description = description
        self.requires_api = requires_api
        self.enabled = False
        self.initialized = False
        self.logger = get_logger(f"feature.{name}")
    
    async def initialize(self, settings: Settings) -> bool:
        """Initialize the feature. Return True if successful."""
        try:
            self.logger.info(f"🔧 Initializing feature: {self.name}")
            
            # Check API requirements
            if self.requires_api and not self._check_api_requirements(settings):
                self.logger.warning(f"⚠️ API requirements not met for {self.name}")
                return False
            
            # Perform feature-specific initialization
            success = await self._initialize_impl(settings)
            
            if success:
                self.initialized = True
                self.logger.info(f"✅ Feature {self.name} initialized successfully")
            else:
                self.logger.error(f"❌ Failed to initialize feature {self.name}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error initializing feature {self.name}: {e}")
            return False
    
    async def _initialize_impl(self, settings: Settings) -> bool:
        """Feature-specific initialization logic. Override in subclasses."""
        return True
    
    def _check_api_requirements(self, settings: Settings) -> bool:
        """Check if API requirements are met. Override in subclasses."""
        return True
    
    async def enable(self):
        """Enable the feature."""
        if not self.initialized:
            self.logger.warning(f"Cannot enable {self.name}: not initialized")
            return False
        
        self.enabled = True
        await self._on_enable()
        self.logger.info(f"🟢 Feature {self.name} enabled")
        return True
    
    async def disable(self):
        """Disable the feature."""
        self.enabled = False
        await self._on_disable()
        self.logger.info(f"🔴 Feature {self.name} disabled")
    
    async def _on_enable(self):
        """Called when feature is enabled. Override in subclasses."""
        pass
    
    async def _on_disable(self):
        """Called when feature is disabled. Override in subclasses."""
        pass
    
    async def cleanup(self):
        """Cleanup feature resources."""
        try:
            await self._cleanup_impl()
            self.enabled = False
            self.initialized = False
            self.logger.info(f"🧹 Feature {self.name} cleaned up")
        except Exception as e:
            self.logger.error(f"Error cleaning up feature {self.name}: {e}")
    
    async def _cleanup_impl(self):
        """Feature-specific cleanup logic. Override in subclasses."""
        pass
    
    def get_status(self) -> Dict[str, Any]:
        """Get feature status information."""
        return {
            "name": self.name,
            "description": self.description,
            "enabled": self.enabled,
            "initialized": self.initialized,
            "requires_api": self.requires_api
        }


class FeatureManager:
    """Manages all toggleable features."""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = get_logger(__name__)
        
        # Feature registry
        self.features: Dict[str, Feature] = {}
        
        # Feature change callbacks
        self.on_feature_enabled: Optional[Callable] = None
        self.on_feature_disabled: Optional[Callable] = None
        
        # Initialize features
        self._register_features()
    
    def _register_features(self):
        """Register all available features."""
        features = [
            PomodoroFeature(),
            WeatherFeature(),
            EmailFeature(),
            FileOperationsFeature(),
            # New features
            FlashcardsFeature(),
            TextSummarizationFeature(),
            ResearchFeature(),
            MoodDetectionFeature(),
            ScreenAnalysisFeature(),
            CalendarIntegrationFeature(),
            TaskManagementFeature(),
            NotesFeature(),
            RemindersFeature(),
        ]
        
        for feature in features:
            self.features[feature.name] = feature
            self.logger.info(f"📋 Registered feature: {feature.name}")
    
    async def initialize_all(self):
        """Initialize all features based on settings."""
        self.logger.info("🔧 Initializing features...")
        
        initialization_tasks = []
        
        for name, feature in self.features.items():
            # Check if feature is enabled in settings
            setting_name = f"feature_{name}"
            if hasattr(self.settings, setting_name) and getattr(self.settings, setting_name):
                initialization_tasks.append(self._initialize_feature(feature))
        
        # Initialize features concurrently
        if initialization_tasks:
            results = await asyncio.gather(*initialization_tasks, return_exceptions=True)
            
            success_count = sum(1 for result in results if result is True)
            self.logger.info(f"✅ Initialized {success_count}/{len(initialization_tasks)} features")
        
        self.logger.info("🎯 Feature initialization completed")
    
    async def _initialize_feature(self, feature: Feature) -> bool:
        """Initialize a single feature."""
        try:
            success = await feature.initialize(self.settings)
            if success:
                await feature.enable()
            return success
        except Exception as e:
            self.logger.error(f"Error initializing feature {feature.name}: {e}")
            return False
    
    async def enable_feature(self, name: str) -> bool:
        """Enable a specific feature."""
        if name not in self.features:
            self.logger.warning(f"Unknown feature: {name}")
            return False
        
        feature = self.features[name]
        
        if not feature.initialized:
            success = await feature.initialize(self.settings)
            if not success:
                return False
        
        success = await feature.enable()
        
        if success and self.on_feature_enabled:
            await self.on_feature_enabled(name)
        
        return success
    
    async def disable_feature(self, name: str) -> bool:
        """Disable a specific feature."""
        if name not in self.features:
            self.logger.warning(f"Unknown feature: {name}")
            return False
        
        feature = self.features[name]
        await feature.disable()
        
        if self.on_feature_disabled:
            await self.on_feature_disabled(name)
        
        return True
    
    async def toggle_feature(self, name: str) -> bool:
        """Toggle a feature on/off."""
        if name not in self.features:
            return False
        
        feature = self.features[name]
        
        if feature.enabled:
            return await self.disable_feature(name)
        else:
            return await self.enable_feature(name)
    
    def is_feature_enabled(self, name: str) -> bool:
        """Check if a feature is enabled."""
        if name not in self.features:
            return False
        return self.features[name].enabled
    
    def is_feature_available(self, name: str) -> bool:
        """Check if a feature is available (initialized)."""
        if name not in self.features:
            return False
        return self.features[name].initialized
    
    def get_feature(self, name: str) -> Optional[Feature]:
        """Get a feature instance."""
        return self.features.get(name)
    
    def get_all_features(self) -> Dict[str, Feature]:
        """Get all features."""
        return self.features.copy()
    
    def get_feature_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all features."""
        return {
            name: feature.get_status()
            for name, feature in self.features.items()
        }
    
    def get_enabled_features(self) -> List[str]:
        """Get list of enabled feature names."""
        return [
            name for name, feature in self.features.items()
            if feature.enabled
        ]
    
    def get_available_features(self) -> List[str]:
        """Get list of available feature names."""
        return [
            name for name, feature in self.features.items()
            if feature.initialized
        ]
    
    async def update_settings(self, new_settings: Dict[str, Any]):
        """Update feature settings."""
        self.logger.info("⚙️ Updating feature settings...")
        
        for setting_name, value in new_settings.items():
            if setting_name.startswith("feature_"):
                feature_name = setting_name[8:]  # Remove "feature_" prefix
                
                if feature_name in self.features:
                    if value and not self.is_feature_enabled(feature_name):
                        await self.enable_feature(feature_name)
                    elif not value and self.is_feature_enabled(feature_name):
                        await self.disable_feature(feature_name)
    
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