"""Customizable Voice and Personality Feature for Jenna Voice Assistant"""

import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Any, Union

from backend.feature_manager import Feature
from backend.features.voice_personality import VoicePersonalityManager
from backend.utils.helpers import get_logger


class VoicePersonalityFeature(Feature):
    """Feature for customizing voice and personality settings."""
    
    def __init__(self, settings):
        """Initialize the voice and personality feature.
        
        Args:
            settings: Application settings
        """
        super().__init__(
            name="Voice and Personality",
            description="Customize voice settings, personality traits, and response styles",
            settings=settings,
            requires_internet=False,  # Basic functionality works without internet
            requires_api_key=False,   # No API key required for basic functionality
        )
        self.logger = get_logger("voice_personality_feature")
        self.manager = None
    
    async def _initialize_impl(self) -> bool:
        """Initialize the voice and personality feature.
        
        Returns:
            True if initialization was successful, False otherwise
        """
        try:
            data_dir = Path(self.settings.data_directory)
            self.manager = VoicePersonalityManager(data_dir)
            self.logger.info("Voice and Personality feature initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize Voice and Personality feature: {e}")
            return False
    
    async def _on_enable(self) -> bool:
        """Actions to perform when the feature is enabled.
        
        Returns:
            True if successful, False otherwise
        """
        self.logger.info("Voice and Personality feature enabled")
        return True
    
    async def _on_disable(self) -> bool:
        """Actions to perform when the feature is disabled.
        
        Returns:
            True if successful, False otherwise
        """
        self.logger.info("Voice and Personality feature disabled")
        return True
    
    async def cleanup(self) -> None:
        """Clean up resources used by the feature."""
        self.logger.info("Cleaning up Voice and Personality feature")
        # No specific cleanup needed for this feature
    
    # Voice Settings Methods
    
    async def get_current_voice(self) -> Dict[str, Any]:
        """Get the current voice settings.
        
        Returns:
            Dictionary with current voice settings
        """
        if not self.is_enabled():
            self.logger.warning("Cannot get current voice: feature is disabled")
            return {}
        
        return self.manager.get_current_voice()
    
    async def set_current_voice(self, voice_name: str) -> bool:
        """Set the current voice.
        
        Args:
            voice_name: Name of the voice to set as current
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_enabled():
            self.logger.warning("Cannot set current voice: feature is disabled")
            return False
        
        return self.manager.set_current_voice(voice_name)
    
    async def add_voice(self, name: str, voice_data: Dict[str, Any]) -> bool:
        """Add a new voice or update an existing one.
        
        Args:
            name: Voice name
            voice_data: Voice settings
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_enabled():
            self.logger.warning("Cannot add voice: feature is disabled")
            return False
        
        return self.manager.add_voice(name, voice_data)
    
    async def remove_voice(self, name: str) -> bool:
        """Remove a voice.
        
        Args:
            name: Voice name
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_enabled():
            self.logger.warning("Cannot remove voice: feature is disabled")
            return False
        
        return self.manager.remove_voice(name)
    
    async def get_all_voices(self) -> Dict[str, Dict[str, Any]]:
        """Get all available voices.
        
        Returns:
            Dictionary of all voices
        """
        if not self.is_enabled():
            self.logger.warning("Cannot get all voices: feature is disabled")
            return {}
        
        return self.manager.get_all_voices()
    
    async def update_voice_setting(self, voice_name: str, setting: str, value: Any) -> bool:
        """Update a specific setting for a voice.
        
        Args:
            voice_name: Name of the voice to update
            setting: Setting name (pitch, rate, volume, etc.)
            value: New value for the setting
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_enabled():
            self.logger.warning("Cannot update voice setting: feature is disabled")
            return False
        
        return self.manager.update_voice_setting(voice_name, setting, value)
    
    # Personality Methods
    
    async def get_current_personality(self) -> Dict[str, Any]:
        """Get the current personality settings.
        
        Returns:
            Dictionary with current personality settings
        """
        if not self.is_enabled():
            self.logger.warning("Cannot get current personality: feature is disabled")
            return {}
        
        return self.manager.get_current_personality()
    
    async def set_current_personality(self, personality_name: str) -> bool:
        """Set the current personality.
        
        Args:
            personality_name: Name of the personality to set as current
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_enabled():
            self.logger.warning("Cannot set current personality: feature is disabled")
            return False
        
        return self.manager.set_current_personality(personality_name)
    
    async def add_personality(self, name: str, personality_data: Dict[str, Any]) -> bool:
        """Add a new personality or update an existing one.
        
        Args:
            name: Personality name
            personality_data: Personality settings
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_enabled():
            self.logger.warning("Cannot add personality: feature is disabled")
            return False
        
        return self.manager.add_personality(name, personality_data)
    
    async def remove_personality(self, name: str) -> bool:
        """Remove a personality.
        
        Args:
            name: Personality name
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_enabled():
            self.logger.warning("Cannot remove personality: feature is disabled")
            return False
        
        return self.manager.remove_personality(name)
    
    async def get_all_personalities(self) -> Dict[str, Dict[str, Any]]:
        """Get all available personalities.
        
        Returns:
            Dictionary of all personalities
        """
        if not self.is_enabled():
            self.logger.warning("Cannot get all personalities: feature is disabled")
            return {}
        
        return self.manager.get_all_personalities()
    
    async def update_personality_setting(self, personality_name: str, setting: str, value: Any) -> bool:
        """Update a specific setting for a personality.
        
        Args:
            personality_name: Name of the personality to update
            setting: Setting name (name, traits, description, etc.)
            value: New value for the setting
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_enabled():
            self.logger.warning("Cannot update personality setting: feature is disabled")
            return False
        
        return self.manager.update_personality_setting(personality_name, setting, value)
    
    # Response Style Methods
    
    async def get_current_response_style(self) -> Dict[str, Any]:
        """Get the current response style settings.
        
        Returns:
            Dictionary with current response style settings
        """
        if not self.is_enabled():
            self.logger.warning("Cannot get current response style: feature is disabled")
            return {}
        
        return self.manager.get_current_response_style()
    
    async def set_current_response_style(self, style_name: str) -> bool:
        """Set the current response style.
        
        Args:
            style_name: Name of the response style to set as current
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_enabled():
            self.logger.warning("Cannot set current response style: feature is disabled")
            return False
        
        return self.manager.set_current_response_style(style_name)
    
    async def add_response_style(self, name: str, style_data: Dict[str, Any]) -> bool:
        """Add a new response style or update an existing one.
        
        Args:
            name: Response style name
            style_data: Response style settings
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_enabled():
            self.logger.warning("Cannot add response style: feature is disabled")
            return False
        
        return self.manager.add_response_style(name, style_data)
    
    async def remove_response_style(self, name: str) -> bool:
        """Remove a response style.
        
        Args:
            name: Response style name
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_enabled():
            self.logger.warning("Cannot remove response style: feature is disabled")
            return False
        
        return self.manager.remove_response_style(name)
    
    async def get_all_response_styles(self) -> Dict[str, Dict[str, Any]]:
        """Get all available response styles.
        
        Returns:
            Dictionary of all response styles
        """
        if not self.is_enabled():
            self.logger.warning("Cannot get all response styles: feature is disabled")
            return {}
        
        return self.manager.get_all_response_styles()
    
    async def update_response_style_setting(self, style_name: str, setting: str, value: Any) -> bool:
        """Update a specific setting for a response style.
        
        Args:
            style_name: Name of the response style to update
            setting: Setting name (verbosity, formality, humor, etc.)
            value: New value for the setting
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_enabled():
            self.logger.warning("Cannot update response style setting: feature is disabled")
            return False
        
        return self.manager.update_response_style_setting(style_name, setting, value)
    
    # Combined Methods
    
    async def get_current_settings(self) -> Dict[str, Any]:
        """Get all current settings (voice, personality, response style).
        
        Returns:
            Dictionary with all current settings
        """
        if not self.is_enabled():
            self.logger.warning("Cannot get current settings: feature is disabled")
            return {}
        
        return self.manager.get_current_settings()
    
    async def create_preset(self, name: str, voice: str, personality: str, response_style: str) -> bool:
        """Create a preset with specific voice, personality, and response style.
        
        Args:
            name: Preset name
            voice: Voice name
            personality: Personality name
            response_style: Response style name
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_enabled():
            self.logger.warning("Cannot create preset: feature is disabled")
            return False
        
        return self.manager.create_preset(name, voice, personality, response_style)
    
    async def apply_preset(self, name: str) -> bool:
        """Apply a preset.
        
        Args:
            name: Preset name
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_enabled():
            self.logger.warning("Cannot apply preset: feature is disabled")
            return False
        
        return self.manager.apply_preset(name)
    
    async def get_all_presets(self) -> Dict[str, Dict[str, str]]:
        """Get all available presets.
        
        Returns:
            Dictionary of all presets
        """
        if not self.is_enabled():
            self.logger.warning("Cannot get all presets: feature is disabled")
            return {}
        
        return self.manager.get_all_presets()