"""Configuration Management for Jenna Voice Assistant"""

import os
from pathlib import Path
from typing import Optional, List, Dict, Any
from pydantic import Field, validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Core Settings
    app_name: str = Field(default="Jenna", description="Application name")
    app_version: str = Field(default="1.0.0", description="Application version")
    debug: bool = Field(default=False, description="Debug mode")
    log_level: str = Field(default="INFO", description="Logging level")
    data_dir: Path = Field(default=Path("./data"), description="Data directory")
    config_dir: Path = Field(default=Path("./config"), description="Config directory")
    
    # Voice Recognition Settings
    wake_phrase: str = Field(default="Jenna Ready", description="Wake phrase")
    voice_recognition_engine: str = Field(default="hybrid", description="Recognition engine")
    offline_model_path: Path = Field(default=Path("./models/vosk"), description="Offline model path")
    pocketsphinx_model_path: Path = Field(default=Path("./models/pocketsphinx"), description="PocketSphinx model path")
    speech_timeout: float = Field(default=5.0, description="Speech timeout in seconds")
    phrase_timeout: float = Field(default=1.0, description="Phrase timeout in seconds")
    energy_threshold: int = Field(default=300, description="Energy threshold for voice detection")
    dynamic_energy_threshold: bool = Field(default=True, description="Dynamic energy threshold")
    preferred_offline_engine: str = Field(default="vosk", description="Preferred offline recognition engine")
    
    # Text-to-Speech Settings
    tts_engine: str = Field(default="pyttsx3", description="TTS engine")
    voice_gender: str = Field(default="female", description="Voice gender")
    speech_rate: int = Field(default=200, description="Speech rate")
    volume: float = Field(default=0.8, description="Speech volume")
    voice_id: Optional[str] = Field(default=None, description="Specific voice ID")
    
    # API Keys
    google_cloud_credentials_path: Optional[str] = Field(default=None, description="Google Cloud credentials")
    google_application_credentials: Optional[str] = Field(default=None, description="Google app credentials")
    weather_api_key: Optional[str] = Field(default=None, description="Weather API key")
    weather_service_url: str = Field(default="https://api.weatherapi.com/v1", description="Weather service URL")
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key")
    openai_model: str = Field(default="gpt-3.5-turbo", description="OpenAI model")
    openai_max_tokens: int = Field(default=150, description="OpenAI max tokens")
    
    # Wikipedia Settings
    wikipedia_language: str = Field(default="en", description="Wikipedia language")
    wikipedia_sentences: int = Field(default=3, description="Wikipedia summary sentences")
    
    # Email Configuration
    email_enabled: bool = Field(default=False, description="Email feature enabled")
    smtp_server: Optional[str] = Field(default=None, description="SMTP server")
    smtp_port: int = Field(default=587, description="SMTP port")
    smtp_username: Optional[str] = Field(default=None, description="SMTP username")
    smtp_password: Optional[str] = Field(default=None, description="SMTP password")
    imap_server: Optional[str] = Field(default=None, description="IMAP server")
    imap_port: int = Field(default=993, description="IMAP port")
    email_address: Optional[str] = Field(default=None, description="Email address")
    
    # Database Settings
    database_url: str = Field(default="sqlite:///./data/jenna.db", description="Database URL")
    database_echo: bool = Field(default=False, description="Database echo SQL")
    
    # Security Settings
    secret_key: str = Field(default="your-secret-key-here-change-this", description="Secret key")
    jwt_algorithm: str = Field(default="HS256", description="JWT algorithm")
    jwt_expiration_hours: int = Field(default=24, description="JWT expiration hours")
    encryption_key: Optional[str] = Field(default=None, description="Encryption key")
    
    # Feature Toggles
    feature_pomodoro: bool = Field(default=True, description="Pomodoro timer feature")
    feature_flashcards: bool = Field(default=True, description="Flashcards feature")
    feature_weather: bool = Field(default=True, description="Weather feature")
    feature_email: bool = Field(default=False, description="Email feature")
    feature_file_operations: bool = Field(default=True, description="File operations feature")
    feature_app_launcher: bool = Field(default=True, description="App launcher feature")
    feature_music_control: bool = Field(default=True, description="Music control feature")
    feature_screen_analysis: bool = Field(default=True, description="Screen analysis feature")
    feature_mood_detection: bool = Field(default=True, description="Mood detection feature")
    feature_backup: bool = Field(default=True, description="Backup feature")
    
    # UI Settings
    ui_theme: str = Field(default="dark", description="UI theme")
    ui_accent_color: str = Field(default="#00ff88", description="UI accent color")
    ui_animation_speed: str = Field(default="normal", description="UI animation speed")
    ui_show_visualizer: bool = Field(default=True, description="Show audio visualizer")
    ui_minimize_to_tray: bool = Field(default=True, description="Minimize to tray")
    ui_start_minimized: bool = Field(default=False, description="Start minimized")
    
    # System Integration
    start_with_windows: bool = Field(default=True, description="Start with Windows")
    system_tray_enabled: bool = Field(default=True, description="System tray enabled")
    hotkey_toggle: str = Field(default="ctrl+shift+j", description="Global hotkey")
    auto_update_check: bool = Field(default=True, description="Auto update check")
    update_channel: str = Field(default="stable", description="Update channel")
    
    # Performance Settings
    audio_chunk_size: int = Field(default=1024, description="Audio chunk size")
    audio_sample_rate: int = Field(default=16000, description="Audio sample rate")
    audio_channels: int = Field(default=1, description="Audio channels")
    processing_threads: int = Field(default=4, description="Processing threads")
    cache_size_mb: int = Field(default=100, description="Cache size in MB")
    max_conversation_history: int = Field(default=50, description="Max conversation history")
    
    # Backup Settings
    backup_enabled: bool = Field(default=True, description="Backup enabled")
    backup_interval_hours: int = Field(default=24, description="Backup interval hours")
    backup_retention_days: int = Field(default=30, description="Backup retention days")
    backup_location: Path = Field(default=Path("./backups"), description="Backup location")
    backup_include_audio: bool = Field(default=False, description="Include audio in backups")
    
    # Development Settings
    dev_mode: bool = Field(default=False, description="Development mode")
    dev_mock_apis: bool = Field(default=False, description="Mock APIs in dev")
    dev_verbose_logging: bool = Field(default=False, description="Verbose logging in dev")
    dev_skip_audio_init: bool = Field(default=False, description="Skip audio init in dev")
    
    @validator('data_dir', 'config_dir', 'offline_model_path', 'backup_location', pre=True)
    def convert_to_path(cls, v):
        """Convert string paths to Path objects."""
        if isinstance(v, str):
            return Path(v)
        return v
    
    @validator('log_level')
    def validate_log_level(cls, v):
        """Validate log level."""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of: {valid_levels}")
        return v.upper()
    
    @validator('voice_recognition_engine')
    def validate_voice_engine(cls, v):
        """Validate voice recognition engine."""
        valid_engines = ['google', 'vosk', 'pocketsphinx', 'hybrid']
        if v not in valid_engines:
            raise ValueError(f"Voice engine must be one of: {valid_engines}")
        return v
        
    @validator('preferred_offline_engine')
    def validate_offline_engine(cls, v):
        """Validate preferred offline engine."""
        valid_engines = ['vosk', 'pocketsphinx']
        if v not in valid_engines:
            raise ValueError(f"Preferred offline engine must be one of: {valid_engines}")
        return v
    
    @validator('tts_engine')
    def validate_tts_engine(cls, v):
        """Validate TTS engine."""
        valid_engines = ['pyttsx3', 'azure', 'google']
        if v not in valid_engines:
            raise ValueError(f"TTS engine must be one of: {valid_engines}")
        return v
    
    @validator('ui_theme')
    def validate_ui_theme(cls, v):
        """Validate UI theme."""
        valid_themes = ['light', 'dark', 'auto']
        if v not in valid_themes:
            raise ValueError(f"UI theme must be one of: {valid_themes}")
        return v
    
    @validator('volume')
    def validate_volume(cls, v):
        """Validate volume range."""
        if not 0.0 <= v <= 1.0:
            raise ValueError("Volume must be between 0.0 and 1.0")
        return v
    
    def get_enabled_features(self) -> List[str]:
        """Get list of enabled features."""
        features = []
        for field_name, field_info in self.__fields__.items():
            if field_name.startswith('feature_') and getattr(self, field_name):
                feature_name = field_name.replace('feature_', '')
                features.append(feature_name)
        return features
    
    def get_missing_api_keys(self) -> Dict[str, str]:
        """Get list of missing API keys and their required features."""
        missing = {}
        
        if self.feature_weather and not self.weather_api_key:
            missing['weather_api_key'] = 'Weather updates'
        
        if not self.openai_api_key:
            missing['openai_api_key'] = 'Enhanced AI responses'
        
        if self.feature_email and not all([self.smtp_server, self.smtp_username, self.smtp_password]):
            missing['email_config'] = 'Email management'
        
        if self.voice_recognition_engine in ['google', 'hybrid'] and not self.google_cloud_credentials_path:
            missing['google_cloud_credentials'] = 'Google Speech Recognition'
        
        return missing
    
    def is_feature_available(self, feature: str) -> bool:
        """Check if a feature is available (enabled and has required API keys)."""
        feature_enabled = getattr(self, f'feature_{feature}', False)
        if not feature_enabled:
            return False
        
        # Check feature-specific requirements
        if feature == 'weather':
            return bool(self.weather_api_key)
        elif feature == 'email':
            return bool(self.smtp_server and self.smtp_username and self.smtp_password)
        
        return True
    
    def get_database_path(self) -> Path:
        """Get the database file path."""
        if self.database_url.startswith('sqlite:///'):
            db_path = self.database_url.replace('sqlite:///', '')
            return Path(db_path)
        return self.data_dir / "jenna.db"
    
    def ensure_directories(self):
        """Ensure all required directories exist."""
        directories = [
            self.data_dir,
            self.config_dir,
            self.backup_location,
            self.offline_model_path.parent if self.offline_model_path else None
        ]
        
        for directory in directories:
            if directory:
                directory.mkdir(parents=True, exist_ok=True)
    
    # Configuration is handled by model_config above