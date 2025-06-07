"""Configuration settings for Jenna"""

import os
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Set

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import validator, Field


class Settings(BaseSettings):
    """Application settings using pydantic-settings."""
    
    # Core settings
    app_name: str = "Jenna Voice Assistant"
    app_version: str = "0.1.0"
    debug: bool = False
    log_level: str = "INFO"
    data_dir: str = "./data"
    temp_dir: str = "./temp"
    log_dir: str = "./logs"
    plugins_dir: str = "./plugins"
    external_plugins_dir: str = "./external_plugins"
    
    # Voice recognition settings
    voice_recognition_enabled: bool = True
    voice_recognition_engine: str = "vosk"  # vosk, google, azure, whisper
    preferred_offline_engine: str = "vosk"
    wake_word: str = "jenna"
    wake_word_sensitivity: float = 0.5
    voice_activation_timeout: int = 10  # seconds
    voice_command_timeout: int = 5  # seconds
    
    # Text-to-speech settings
    tts_enabled: bool = True
    tts_engine: str = "pyttsx3"  # pyttsx3, google, azure, elevenlabs
    tts_voice: str = "default"
    tts_rate: int = 150
    tts_volume: float = 1.0
    
    # API keys
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-3.5-turbo"
    openai_max_tokens: int = 150
    
    google_api_key: Optional[str] = None
    azure_speech_key: Optional[str] = None
    azure_speech_region: Optional[str] = None
    elevenlabs_api_key: Optional[str] = None
    
    # Weather API
    openweathermap_api_key: Optional[str] = None
    weather_units: str = "metric"  # metric, imperial
    default_city: Optional[str] = None
    
    # News API
    newsapi_key: Optional[str] = None
    news_sources: str = "bbc-news,cnn,the-verge,wired,ars-technica"
    news_categories: str = "technology,science,business,health"
    news_language: str = "en"
    news_country: str = "us"
    news_max_results: int = 5
    
    # Wikipedia settings
    wikipedia_language: str = "en"
    wikipedia_max_results: int = 3
    
    # Email settings
    email_enabled: bool = False
    email_provider: Optional[str] = None  # gmail, outlook
    email_address: Optional[str] = None
    email_password: Optional[str] = None
    email_imap_server: Optional[str] = None
    email_smtp_server: Optional[str] = None
    
    # Database settings
    database_type: str = "sqlite"  # sqlite, mysql, postgres
    database_path: str = "./data/jenna.db"
    database_host: Optional[str] = None
    database_port: Optional[int] = None
    database_name: Optional[str] = None
    database_user: Optional[str] = None
    database_password: Optional[str] = None
    
    # Security settings
    encryption_key: Optional[str] = None
    require_authentication: bool = False
    session_timeout: int = 3600  # seconds
    max_login_attempts: int = 5
    
    # Plugin settings
    plugins_enabled: bool = True
    auto_load_plugins: bool = True
    plugin_sandboxing: bool = True
    allow_network_access: bool = False
    allow_file_access: bool = False
    trusted_plugin_sources: List[str] = []
    plugin_timeout: int = 10  # seconds
    
    # Feature toggles
    feature_app_launcher: bool = True
    feature_music_control: bool = True
    feature_screen_analysis: bool = False
    feature_mood_detection: bool = False
    feature_ip_geolocation: bool = True
    feature_currency_exchange: bool = True
    feature_news: bool = True
    feature_dictionary: bool = True
    feature_translation: bool = True
    feature_recipe: bool = True
    feature_nutrition: bool = True
    feature_health_fitness: bool = True
    feature_financial_management: bool = False
    feature_music_media: bool = True
    feature_voice_personality: bool = True
    
    # UI settings
    ui_theme: str = "dark"  # dark, light, system
    ui_accent_color: str = "blue"  # blue, green, purple, orange, red
    ui_animation_speed: str = "normal"  # slow, normal, fast, none
    ui_visualizer: bool = True
    ui_minimize_to_tray: bool = True
    ui_start_minimized: bool = False
    ui_desktop_window: bool = True
    
    # System integration
    start_with_windows: bool = False
    system_tray_enabled: bool = True
    hotkey_enabled: bool = True
    hotkey_combination: str = "ctrl+alt+j"
    auto_update: bool = True
    
    # Performance settings
    audio_chunk_size: int = 1024
    audio_sample_rate: int = 16000
    audio_channels: int = 1
    processing_threads: int = 4
    cache_size: int = 100  # MB
    max_conversation_history: int = 50
    # Model management settings
    performance_model_cache_size: int = 5  # Number of models to keep in memory
    performance_memory_limit_mb: int = 1024  # Memory limit for models in MB
    performance_use_quantized_models: bool = True  # Whether to use quantized models by default
    performance_optimize_models: bool = True  # Whether to optimize models on load
    performance_model_pruning: bool = False  # Whether to prune models (experimental)
    
    # Backup settings
    backup_enabled: bool = True
    backup_interval: int = 7  # days
    backup_retention: int = 30  # days
    backup_location: str = "./backups"
    backup_include_audio: bool = False
    
    # Development settings
    dev_mode: bool = False
    mock_apis: bool = False
    verbose_logging: bool = False
    skip_audio_init: bool = False
    
    # Environment variables configuration
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="JENNA_",
        extra="ignore"
    )
    
    # Validators
    @validator("log_level")
    def validate_log_level(cls, v):
        allowed_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in allowed_levels:
            raise ValueError(f"Log level must be one of {allowed_levels}")
        return v.upper()
    
    @validator("voice_recognition_engine")
    def validate_voice_engine(cls, v):
        allowed_engines = ["vosk", "google", "azure", "whisper"]
        if v.lower() not in allowed_engines:
            raise ValueError(f"Voice recognition engine must be one of {allowed_engines}")
        return v.lower()
    
    @validator("preferred_offline_engine")
    def validate_offline_engine(cls, v):
        allowed_engines = ["vosk", "whisper"]
        if v.lower() not in allowed_engines:
            raise ValueError(f"Offline engine must be one of {allowed_engines}")
        return v.lower()
    
    @validator("tts_engine")
    def validate_tts_engine(cls, v):
        allowed_engines = ["pyttsx3", "google", "azure", "elevenlabs"]
        if v.lower() not in allowed_engines:
            raise ValueError(f"TTS engine must be one of {allowed_engines}")
        return v.lower()
    
    @validator("ui_theme")
    def validate_ui_theme(cls, v):
        allowed_themes = ["dark", "light", "system"]
        if v.lower() not in allowed_themes:
            raise ValueError(f"UI theme must be one of {allowed_themes}")
        return v.lower()
    
    @validator("tts_volume")
    def validate_volume(cls, v):
        if v < 0 or v > 1:
            raise ValueError("Volume must be between 0 and 1")
        return v
    
    def get_enabled_features(self) -> List[str]:
        """Get a list of enabled features."""
        enabled_features = []
        for key, value in self.__dict__.items():
            if key.startswith("feature_") and value is True:
                feature_name = key.replace("feature_", "")
                enabled_features.append(feature_name)
        return enabled_features
    
    def get_missing_api_keys(self) -> Dict[str, List[str]]:
        """Get a dictionary of missing API keys and their associated features."""
        missing_keys = {}
        
        # Map API keys to features
        api_feature_map = {
            "openai_api_key": ["voice_personality", "text_analysis"],
            "google_api_key": ["speech_recognition", "translation"],
            "azure_speech_key": ["speech_recognition", "text_to_speech"],
            "elevenlabs_api_key": ["voice_personality"],
            "openweathermap_api_key": ["weather"],
            "newsapi_key": ["news"]
        }
        
        # Check for missing keys
        for key, features in api_feature_map.items():
            if not getattr(self, key, None):
                missing_keys[key] = features
        
        return missing_keys
    
    def is_feature_available(self, feature_name: str) -> bool:
        """Check if a feature is available based on being enabled and having required API keys."""
        # Check if feature is enabled
        feature_toggle = f"feature_{feature_name}"
        if not getattr(self, feature_toggle, False):
            return False
        
        # Check for required API keys
        missing_keys = self.get_missing_api_keys()
        for key, features in missing_keys.items():
            if feature_name in features:
                return False
        
        return True
    
    def get_database_path(self) -> Path:
        """Get the database path as a Path object."""
        if self.database_type == "sqlite":
            return Path(self.database_path).expanduser().absolute()
        return None
    
    def ensure_directories(self):
        """Ensure that necessary directories exist."""
        for dir_name in [self.data_dir, self.temp_dir, self.log_dir, 
                         self.plugins_dir, self.external_plugins_dir, 
                         self.backup_location]:
            Path(dir_name).expanduser().absolute().mkdir(parents=True, exist_ok=True)