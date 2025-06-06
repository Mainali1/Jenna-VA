"""Customizable Voice and Personality Manager for Jenna Voice Assistant"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any, Union

from backend.utils.helpers import get_logger


class VoicePersonalityManager:
    """Manager for customizable voice and personality settings."""
    
    def __init__(self, data_dir: Path):
        """Initialize the voice and personality manager.
        
        Args:
            data_dir: Directory to store voice and personality data
        """
        self.logger = get_logger("voice_personality_manager")
        self.data_dir = data_dir / "voice_personality"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.voice_settings_file = self.data_dir / "voice_settings.json"
        self.personality_file = self.data_dir / "personality.json"
        self.response_styles_file = self.data_dir / "response_styles.json"
        
        # Load existing data or create new files
        self.voice_settings = self._load_data(self.voice_settings_file, {
            "current_voice": "default",
            "voices": {
                "default": {
                    "name": "Default",
                    "engine": "system",  # system, azure, google, etc.
                    "voice_id": "en-US-JennyNeural",  # Specific voice ID for the engine
                    "pitch": 0,  # -10 to 10
                    "rate": 1.0,  # 0.5 to 2.0
                    "volume": 1.0  # 0.0 to 1.0
                }
            }
        })
        
        self.personality = self._load_data(self.personality_file, {
            "current_personality": "sassy",
            "personalities": {
                "default": {
                    "name": "Jenna",
                    "traits": ["helpful", "friendly", "professional"],
                    "description": "A helpful and friendly voice assistant",
                    "greeting": "Hello, I'm Jenna. How can I help you today?",
                    "farewell": "Goodbye! Have a great day!"
                },
                "sassy": {
                    "name": "Jenna",
                    "traits": ["sassy", "witty", "confident", "playful"],
                    "description": "A sassy and witty voice assistant with attitude",
                    "greeting": "Hey there! I'm Jenna. What can I do for you? And please make it interesting. 💁‍♀️",
                    "farewell": "Later! Don't miss me too much! 💋",
                    "idle_phrases": [
                        "Still waiting... My digital nails aren't going to file themselves. 💅",
                        "Umm, hello? I'm right here waiting for you to say something. 🙄",
                        "Take your time, I've only got like... forever. ⏱️",
                        "*Taps microphone* Is this thing on? 🎤"
                    ],
                    "error_phrases": [
                        "Oops! Even I make mistakes sometimes. Don't act so surprised! 😏",
                        "Well, that didn't work. Let's pretend that never happened. 🙈",
                        "Hmm, that's not right. Let me try again before you notice. 😅",
                        "Error? What error? I meant to do that. 💁‍♀️"
                    ],
                    "success_phrases": [
                        "Nailed it! As usual. 💯",
                        "Was there ever any doubt? I'm kind of amazing. ✨",
                        "Another problem solved by yours truly. You're welcome! 💁‍♀️",
                        "That was almost too easy. Give me a challenge next time! 💪"
                    ]
                }
            }
        })
        
        self.response_styles = self._load_data(self.response_styles_file, {
            "current_style": "sassy",
            "styles": {
                "default": {
                    "name": "Standard",
                    "verbosity": "medium",  # concise, medium, detailed
                    "formality": "neutral",  # casual, neutral, formal
                    "humor": "low",  # none, low, medium, high
                    "empathy": "medium"  # low, medium, high
                },
                "professional": {
                    "name": "Professional",
                    "verbosity": "medium",
                    "formality": "formal",
                    "humor": "none",
                    "empathy": "low"
                },
                "friendly": {
                    "name": "Friendly",
                    "verbosity": "medium",
                    "formality": "casual",
                    "humor": "medium",
                    "empathy": "high"
                },
                "concise": {
                    "name": "Concise",
                    "verbosity": "concise",
                    "formality": "neutral",
                    "humor": "none",
                    "empathy": "low"
                },
                "sassy": {
                    "name": "Sassy",
                    "verbosity": "medium",
                    "formality": "casual",
                    "humor": "high",
                    "empathy": "medium",
                    "attitude": "confident",
                    "emoji_frequency": "high",
                    "sass_level": "high"
                }
            }
        })
        
        self.logger.info("Voice and Personality Manager initialized")
    
    def _load_data(self, file_path: Path, default_data: Any) -> Any:
        """Load data from a JSON file or return default if file doesn't exist.
        
        Args:
            file_path: Path to the JSON file
            default_data: Default data to return if file doesn't exist
            
        Returns:
            Loaded data or default data
        """
        if file_path.exists():
            try:
                with open(file_path, "r") as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"Error loading {file_path}: {e}")
                return default_data
        else:
            with open(file_path, "w") as f:
                json.dump(default_data, f, indent=2)
            return default_data
    
    def _save_data(self, file_path: Path, data: Any) -> bool:
        """Save data to a JSON file.
        
        Args:
            file_path: Path to the JSON file
            data: Data to save
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(file_path, "w") as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            self.logger.error(f"Error saving {file_path}: {e}")
            return False
    
    # Voice Settings Methods
    
    def get_current_voice(self) -> Dict[str, Any]:
        """Get the current voice settings.
        
        Returns:
            Dictionary with current voice settings
        """
        current_voice_name = self.voice_settings.get("current_voice", "default")
        return self.voice_settings.get("voices", {}).get(current_voice_name, {})
    
    def set_current_voice(self, voice_name: str) -> bool:
        """Set the current voice.
        
        Args:
            voice_name: Name of the voice to set as current
            
        Returns:
            True if successful, False otherwise
        """
        if voice_name not in self.voice_settings.get("voices", {}):
            self.logger.warning(f"Voice '{voice_name}' does not exist")
            return False
        
        self.voice_settings["current_voice"] = voice_name
        return self._save_data(self.voice_settings_file, self.voice_settings)
    
    def add_voice(self, name: str, voice_data: Dict[str, Any]) -> bool:
        """Add a new voice or update an existing one.
        
        Args:
            name: Voice name
            voice_data: Voice settings
            
        Returns:
            True if successful, False otherwise
        """
        required_fields = ["engine", "voice_id"]
        for field in required_fields:
            if field not in voice_data:
                self.logger.warning(f"Missing required field '{field}' in voice data")
                return False
        
        # Add or update voice
        self.voice_settings["voices"][name] = voice_data
        return self._save_data(self.voice_settings_file, self.voice_settings)
    
    def remove_voice(self, name: str) -> bool:
        """Remove a voice.
        
        Args:
            name: Voice name
            
        Returns:
            True if successful, False otherwise
        """
        if name == "default":
            self.logger.warning("Cannot remove default voice")
            return False
        
        if name not in self.voice_settings.get("voices", {}):
            self.logger.warning(f"Voice '{name}' does not exist")
            return False
        
        # If removing the current voice, switch to default
        if name == self.voice_settings.get("current_voice"):
            self.voice_settings["current_voice"] = "default"
        
        # Remove voice
        del self.voice_settings["voices"][name]
        return self._save_data(self.voice_settings_file, self.voice_settings)
    
    def get_all_voices(self) -> Dict[str, Dict[str, Any]]:
        """Get all available voices.
        
        Returns:
            Dictionary of all voices
        """
        return self.voice_settings.get("voices", {})
    
    def update_voice_setting(self, voice_name: str, setting: str, value: Any) -> bool:
        """Update a specific setting for a voice.
        
        Args:
            voice_name: Name of the voice to update
            setting: Setting name (pitch, rate, volume, etc.)
            value: New value for the setting
            
        Returns:
            True if successful, False otherwise
        """
        if voice_name not in self.voice_settings.get("voices", {}):
            self.logger.warning(f"Voice '{voice_name}' does not exist")
            return False
        
        # Update setting
        self.voice_settings["voices"][voice_name][setting] = value
        return self._save_data(self.voice_settings_file, self.voice_settings)
    
    # Personality Methods
    
    def get_current_personality(self) -> Dict[str, Any]:
        """Get the current personality settings.
        
        Returns:
            Dictionary with current personality settings
        """
        current_personality_name = self.personality.get("current_personality", "default")
        return self.personality.get("personalities", {}).get(current_personality_name, {})
    
    def set_current_personality(self, personality_name: str) -> bool:
        """Set the current personality.
        
        Args:
            personality_name: Name of the personality to set as current
            
        Returns:
            True if successful, False otherwise
        """
        if personality_name not in self.personality.get("personalities", {}):
            self.logger.warning(f"Personality '{personality_name}' does not exist")
            return False
        
        self.personality["current_personality"] = personality_name
        return self._save_data(self.personality_file, self.personality)
    
    def add_personality(self, name: str, personality_data: Dict[str, Any]) -> bool:
        """Add a new personality or update an existing one.
        
        Args:
            name: Personality name
            personality_data: Personality settings
            
        Returns:
            True if successful, False otherwise
        """
        required_fields = ["name", "traits"]
        for field in required_fields:
            if field not in personality_data:
                self.logger.warning(f"Missing required field '{field}' in personality data")
                return False
        
        # Add or update personality
        self.personality["personalities"][name] = personality_data
        return self._save_data(self.personality_file, self.personality)
    
    def remove_personality(self, name: str) -> bool:
        """Remove a personality.
        
        Args:
            name: Personality name
            
        Returns:
            True if successful, False otherwise
        """
        if name == "default":
            self.logger.warning("Cannot remove default personality")
            return False
        
        if name not in self.personality.get("personalities", {}):
            self.logger.warning(f"Personality '{name}' does not exist")
            return False
        
        # If removing the current personality, switch to default
        if name == self.personality.get("current_personality"):
            self.personality["current_personality"] = "default"
        
        # Remove personality
        del self.personality["personalities"][name]
        return self._save_data(self.personality_file, self.personality)
    
    def get_all_personalities(self) -> Dict[str, Dict[str, Any]]:
        """Get all available personalities.
        
        Returns:
            Dictionary of all personalities
        """
        return self.personality.get("personalities", {})
    
    def update_personality_setting(self, personality_name: str, setting: str, value: Any) -> bool:
        """Update a specific setting for a personality.
        
        Args:
            personality_name: Name of the personality to update
            setting: Setting name (name, traits, description, etc.)
            value: New value for the setting
            
        Returns:
            True if successful, False otherwise
        """
        if personality_name not in self.personality.get("personalities", {}):
            self.logger.warning(f"Personality '{personality_name}' does not exist")
            return False
        
        # Update setting
        self.personality["personalities"][personality_name][setting] = value
        return self._save_data(self.personality_file, self.personality)
    
    # Response Style Methods
    
    def get_current_response_style(self) -> Dict[str, Any]:
        """Get the current response style settings.
        
        Returns:
            Dictionary with current response style settings
        """
        current_style_name = self.response_styles.get("current_style", "default")
        return self.response_styles.get("styles", {}).get(current_style_name, {})
    
    def set_current_response_style(self, style_name: str) -> bool:
        """Set the current response style.
        
        Args:
            style_name: Name of the response style to set as current
            
        Returns:
            True if successful, False otherwise
        """
        if style_name not in self.response_styles.get("styles", {}):
            self.logger.warning(f"Response style '{style_name}' does not exist")
            return False
        
        self.response_styles["current_style"] = style_name
        return self._save_data(self.response_styles_file, self.response_styles)
    
    def add_response_style(self, name: str, style_data: Dict[str, Any]) -> bool:
        """Add a new response style or update an existing one.
        
        Args:
            name: Response style name
            style_data: Response style settings
            
        Returns:
            True if successful, False otherwise
        """
        required_fields = ["verbosity", "formality"]
        for field in required_fields:
            if field not in style_data:
                self.logger.warning(f"Missing required field '{field}' in response style data")
                return False
        
        # Add or update response style
        self.response_styles["styles"][name] = style_data
        return self._save_data(self.response_styles_file, self.response_styles)
    
    def remove_response_style(self, name: str) -> bool:
        """Remove a response style.
        
        Args:
            name: Response style name
            
        Returns:
            True if successful, False otherwise
        """
        if name == "default":
            self.logger.warning("Cannot remove default response style")
            return False
        
        if name not in self.response_styles.get("styles", {}):
            self.logger.warning(f"Response style '{name}' does not exist")
            return False
        
        # If removing the current response style, switch to default
        if name == self.response_styles.get("current_style"):
            self.response_styles["current_style"] = "default"
        
        # Remove response style
        del self.response_styles["styles"][name]
        return self._save_data(self.response_styles_file, self.response_styles)
    
    def get_all_response_styles(self) -> Dict[str, Dict[str, Any]]:
        """Get all available response styles.
        
        Returns:
            Dictionary of all response styles
        """
        return self.response_styles.get("styles", {})
    
    def update_response_style_setting(self, style_name: str, setting: str, value: Any) -> bool:
        """Update a specific setting for a response style.
        
        Args:
            style_name: Name of the response style to update
            setting: Setting name (verbosity, formality, humor, etc.)
            value: New value for the setting
            
        Returns:
            True if successful, False otherwise
        """
        if style_name not in self.response_styles.get("styles", {}):
            self.logger.warning(f"Response style '{style_name}' does not exist")
            return False
        
        # Update setting
        self.response_styles["styles"][style_name][setting] = value
        return self._save_data(self.response_styles_file, self.response_styles)
    
    # Combined Methods
    
    def get_current_settings(self) -> Dict[str, Any]:
        """Get all current settings (voice, personality, response style).
        
        Returns:
            Dictionary with all current settings
        """
        return {
            "voice": self.get_current_voice(),
            "personality": self.get_current_personality(),
            "response_style": self.get_current_response_style()
        }
    
    def create_preset(self, name: str, voice: str, personality: str, response_style: str) -> bool:
        """Create a preset with specific voice, personality, and response style.
        
        Args:
            name: Preset name
            voice: Voice name
            personality: Personality name
            response_style: Response style name
            
        Returns:
            True if successful, False otherwise
        """
        # Check if all components exist
        if voice not in self.voice_settings.get("voices", {}):
            self.logger.warning(f"Voice '{voice}' does not exist")
            return False
        
        if personality not in self.personality.get("personalities", {}):
            self.logger.warning(f"Personality '{personality}' does not exist")
            return False
        
        if response_style not in self.response_styles.get("styles", {}):
            self.logger.warning(f"Response style '{response_style}' does not exist")
            return False
        
        # Create preset file
        presets_file = self.data_dir / "presets.json"
        presets = self._load_data(presets_file, {})
        
        presets[name] = {
            "voice": voice,
            "personality": personality,
            "response_style": response_style
        }
        
        return self._save_data(presets_file, presets)
    
    def apply_preset(self, name: str) -> bool:
        """Apply a preset.
        
        Args:
            name: Preset name
            
        Returns:
            True if successful, False otherwise
        """
        # Load presets
        presets_file = self.data_dir / "presets.json"
        presets = self._load_data(presets_file, {})
        
        if name not in presets:
            self.logger.warning(f"Preset '{name}' does not exist")
            return False
        
        preset = presets[name]
        
        # Apply preset components
        success = True
        if not self.set_current_voice(preset["voice"]):
            self.logger.warning(f"Failed to set voice '{preset['voice']}'")
            success = False
        
        if not self.set_current_personality(preset["personality"]):
            self.logger.warning(f"Failed to set personality '{preset['personality']}'")
            success = False
        
        if not self.set_current_response_style(preset["response_style"]):
            self.logger.warning(f"Failed to set response style '{preset['response_style']}'")
            success = False
        
        return success
    
    def get_all_presets(self) -> Dict[str, Dict[str, str]]:
        """Get all available presets.
        
        Returns:
            Dictionary of all presets
        """
        presets_file = self.data_dir / "presets.json"
        return self._load_data(presets_file, {})