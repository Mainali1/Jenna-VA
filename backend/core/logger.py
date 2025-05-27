"""Logging Configuration for Jenna Voice Assistant"""

import sys
import logging
from pathlib import Path
from typing import Optional
from loguru import logger
from rich.console import Console
from rich.logging import RichHandler
from rich.traceback import install

from .config import Settings


class InterceptHandler(logging.Handler):
    """Intercept standard logging and redirect to loguru."""
    
    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno
        
        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1
        
        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def setup_logger(settings: Settings) -> logger:
    """Setup logging configuration."""
    
    # Remove default loguru handler
    logger.remove()
    
    # Install rich traceback handler
    install(show_locals=settings.debug)
    
    # Create console for rich output
    console = Console()
    
    # Determine log level
    log_level = settings.log_level.upper()
    
    # Setup console logging with rich
    if settings.debug or settings.dev_verbose_logging:
        # Detailed format for development
        log_format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        )
    else:
        # Simple format for production
        log_format = (
            "<green>{time:HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<level>{message}</level>"
        )
    
    # Add console handler
    logger.add(
        sys.stdout,
        format=log_format,
        level=log_level,
        colorize=True,
        backtrace=settings.debug,
        diagnose=settings.debug
    )
    
    # Setup file logging
    log_dir = settings.data_dir / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Main log file
    logger.add(
        log_dir / "jenna.log",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} | {message}",
        level=log_level,
        rotation="10 MB",
        retention="30 days",
        compression="zip",
        backtrace=True,
        diagnose=settings.debug
    )
    
    # Error log file
    logger.add(
        log_dir / "errors.log",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} | {message}",
        level="ERROR",
        rotation="5 MB",
        retention="60 days",
        compression="zip",
        backtrace=True,
        diagnose=True
    )
    
    # Voice activity log (if enabled)
    if settings.dev_verbose_logging:
        logger.add(
            log_dir / "voice.log",
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {message}",
            filter=lambda record: "voice" in record["name"].lower(),
            level="DEBUG",
            rotation="5 MB",
            retention="7 days"
        )
    
    # Intercept standard logging
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
    
    # Set levels for noisy libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    logging.getLogger("websockets").setLevel(logging.WARNING)
    
    if not settings.debug:
        logging.getLogger("uvicorn").setLevel(logging.WARNING)
        logging.getLogger("fastapi").setLevel(logging.WARNING)
    
    # Log startup information
    logger.info(f"🚀 Jenna Voice Assistant v{settings.app_version}")
    logger.info(f"📊 Log level: {log_level}")
    logger.info(f"📁 Log directory: {log_dir}")
    logger.info(f"🔧 Debug mode: {settings.debug}")
    
    return logger


def get_logger(name: str) -> logger:
    """Get a logger instance for a specific module."""
    return logger.bind(name=name)


class VoiceLogger:
    """Specialized logger for voice-related activities."""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = get_logger("voice")
        self._voice_log_enabled = settings.dev_verbose_logging
    
    def log_wake_word(self, confidence: float = None):
        """Log wake word detection."""
        if self._voice_log_enabled:
            msg = "👂 Wake word detected"
            if confidence:
                msg += f" (confidence: {confidence:.2f})"
            self.logger.info(msg)
    
    def log_speech_start(self):
        """Log speech recognition start."""
        if self._voice_log_enabled:
            self.logger.debug("🎤 Speech recognition started")
    
    def log_speech_end(self, text: str, confidence: float = None):
        """Log speech recognition result."""
        if self._voice_log_enabled:
            msg = f"🗣️ Speech recognized: '{text}'"
            if confidence:
                msg += f" (confidence: {confidence:.2f})"
            self.logger.info(msg)
    
    def log_speech_timeout(self):
        """Log speech recognition timeout."""
        if self._voice_log_enabled:
            self.logger.debug("⏰ Speech recognition timeout")
    
    def log_tts_start(self, text: str):
        """Log TTS start."""
        if self._voice_log_enabled:
            self.logger.debug(f"🔊 TTS started: '{text[:50]}{'...' if len(text) > 50 else ''}'")
    
    def log_tts_end(self):
        """Log TTS completion."""
        if self._voice_log_enabled:
            self.logger.debug("🔊 TTS completed")
    
    def log_audio_error(self, error: str):
        """Log audio-related errors."""
        self.logger.error(f"🎵 Audio error: {error}")
    
    def log_engine_switch(self, from_engine: str, to_engine: str, reason: str):
        """Log voice engine switching."""
        self.logger.info(f"🔄 Voice engine switched: {from_engine} → {to_engine} ({reason})")


class PerformanceLogger:
    """Logger for performance metrics."""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = get_logger("performance")
        self._perf_log_enabled = settings.debug or settings.dev_verbose_logging
    
    def log_response_time(self, operation: str, duration: float):
        """Log operation response time."""
        if self._perf_log_enabled:
            self.logger.info(f"⏱️ {operation}: {duration:.3f}s")
    
    def log_memory_usage(self, operation: str, memory_mb: float):
        """Log memory usage."""
        if self._perf_log_enabled:
            self.logger.info(f"💾 {operation}: {memory_mb:.1f}MB")
    
    def log_api_call(self, service: str, endpoint: str, duration: float, status: str):
        """Log API call metrics."""
        if self._perf_log_enabled:
            self.logger.info(f"🌐 {service}/{endpoint}: {duration:.3f}s ({status})")


class SecurityLogger:
    """Logger for security-related events."""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = get_logger("security")
    
    def log_auth_attempt(self, success: bool, method: str, details: str = None):
        """Log authentication attempts."""
        status = "✅ SUCCESS" if success else "❌ FAILED"
        msg = f"🔐 Auth {status}: {method}"
        if details:
            msg += f" - {details}"
        
        if success:
            self.logger.info(msg)
        else:
            self.logger.warning(msg)
    
    def log_api_key_usage(self, service: str, key_present: bool):
        """Log API key usage."""
        status = "present" if key_present else "missing"
        self.logger.info(f"🔑 API key for {service}: {status}")
    
    def log_file_access(self, operation: str, path: str, success: bool):
        """Log file access attempts."""
        status = "✅" if success else "❌"
        self.logger.info(f"📁 {status} File {operation}: {path}")
    
    def log_security_event(self, event: str, severity: str = "info"):
        """Log general security events."""
        emoji = {"info": "ℹ️", "warning": "⚠️", "error": "🚨"}.get(severity, "ℹ️")
        msg = f"🛡️ {emoji} Security: {event}"
        
        if severity == "error":
            self.logger.error(msg)
        elif severity == "warning":
            self.logger.warning(msg)
        else:
            self.logger.info(msg)