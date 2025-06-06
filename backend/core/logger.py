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
    """Logger for voice-related activities with sassy personality."""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = get_logger("voice")
        self._voice_log_enabled = settings.debug or settings.dev_verbose_logging
        
        # Sassy messages for different events
        self.wake_messages = [
            "👂 Someone called? I'm all ears!",
            "👋 Hey there! Finally remembered I exist?",
            "💁‍♀️ Yesss? You rang?",
            "✨ Fashionably present and ready to slay!"
        ]
        
        self.listening_messages = [
            "🎧 Listening... make it good!",
            "👂 All ears now, don't waste my time!",
            "🎤 The mic is hot, darling!",
            "🔊 Speak now or forever hold your peace!"
        ]
        
        self.recognition_messages = [
            "💬 Got it! You said: ",
            "🗣️ Heard that loud and clear: ",
            "👂 Ugh, fine. You said: ",
            "💁‍♀️ If I understood correctly (and I always do): "
        ]
        
        self.timeout_messages = [
            "⏱️ Hello? Did you fall asleep or something?",
            "⌛ Waited long enough! Some of us have things to do!",
            "⏰ Time's up! Cat got your tongue?",
            "🙄 No response? I'll just be over here then..."
        ]
        
        self.tts_start_messages = [
            "🔊 Listen up! I'm about to drop some knowledge: ",
            "🎭 Prepare to be dazzled by my response: ",
            "💅 Let me enlighten you with this: ",
            "✨ My brilliant response coming right up: "
        ]
        
        self.tts_end_messages = [
            "🎬 And scene! Was I amazing or what?",
            "💯 Another flawless delivery, if I do say so myself!",
            "🏆 That's how it's done, folks!",
            "💁‍♀️ You're welcome, by the way!"
        ]
        
        self.error_messages = [
            "🙈 Oops! Even I'm not perfect: ",
            "😬 Well this is awkward... Error: ",
            "🤦‍♀️ Someone messed up, and it wasn't me: ",
            "⚠️ Minor technical difficulty, don't panic: "
        ]
        
        self.engine_switch_messages = [
            "🔄 Switching things up! Now using ",
            "🔀 Plot twist! I'm now running on ",
            "⚡ Upgraded myself to ",
            "🚀 Leveling up to "
        ]
        
        import random
        self.random = random
    
    def _get_random_message(self, message_list):
        """Get a random message from a list."""
        return message_list[self.random.randint(0, len(message_list) - 1)]
    
    def log_wake_word(self, confidence: float = None):
        """Log wake word detection with sass."""
        if self._voice_log_enabled:
            msg = self._get_random_message(self.wake_messages)
            if confidence:
                msg += f" (confidence: {confidence:.2f})"
            self.logger.info(msg)
    
    def log_speech_start(self):
        """Log speech recognition start with sass."""
        if self._voice_log_enabled:
            self.logger.debug(self._get_random_message(self.listening_messages))
    
    def log_speech_end(self, text: str, confidence: float = None):
        """Log speech recognition result with sass."""
        if self._voice_log_enabled:
            msg = f"{self._get_random_message(self.recognition_messages)}'{text}'"
            if confidence:
                msg += f" (confidence: {confidence:.2f})"
            self.logger.info(msg)
    
    def log_speech_timeout(self):
        """Log speech recognition timeout with sass."""
        if self._voice_log_enabled:
            self.logger.debug(self._get_random_message(self.timeout_messages))
    
    def log_tts_start(self, text: str):
        """Log TTS start with sass."""
        if self._voice_log_enabled:
            self.logger.debug(f"{self._get_random_message(self.tts_start_messages)}'{text[:50]}{'...' if len(text) > 50 else ''}'") 
    
    def log_tts_end(self):
        """Log TTS completion with sass."""
        if self._voice_log_enabled:
            self.logger.debug(self._get_random_message(self.tts_end_messages))
    
    def log_audio_error(self, error: str):
        """Log audio-related errors with sass."""
        self.logger.error(f"{self._get_random_message(self.error_messages)}{error}")
    
    def log_engine_switch(self, from_engine: str, to_engine: str, reason: str):
        """Log voice engine switching with sass."""
        self.logger.info(f"{self._get_random_message(self.engine_switch_messages)}{from_engine} → {to_engine} ({reason})")


class PerformanceLogger:
    """Logger for performance metrics with sassy personality."""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = get_logger("performance")
        self._perf_log_enabled = settings.debug or settings.dev_verbose_logging
        
        # Sassy performance messages
        self.fast_response_messages = [
            "⚡ Speed demon! ",
            "🏎️ Zoom zoom! ",
            "⏱️ That was quick! ",
            "🚀 Lightning fast! "
        ]
        
        self.slow_response_messages = [
            "🐢 Taking my sweet time... ",
            "⏳ Good things come to those who wait... ",
            "🧠 Thinking deep thoughts here... ",
            "🐌 Rome wasn't built in a day, honey! "
        ]
        
        self.memory_low_messages = [
            "🧠 Barely breaking a sweat! ",
            "💪 Memory game strong! ",
            "🤏 Just a tiny bit of memory for ",
            "✨ Efficiency queen! "
        ]
        
        self.memory_high_messages = [
            "💾 Whew, that was a workout! ",
            "🧠 My brain cells are on fire! ",
            "🐘 Never forget... how much memory I just used! ",
            "🤯 That's a lot to remember! "
        ]
        
        self.api_success_messages = [
            "🌐 Nailed that API call! ",
            "✨ API whisperer at your service! ",
            "🔌 Connected and conquered! ",
            "🌟 API call? More like API slay! "
        ]
        
        self.api_failure_messages = [
            "😬 Awkward API moment... ",
            "🙄 The API is being dramatic again... ",
            "🤦‍♀️ Someone else's API, someone else's problem! ",
            "💔 API relationship status: It's complicated. "
        ]
        
        import random
        self.random = random
    
    def _get_random_message(self, message_list):
        """Get a random message from a list."""
        return message_list[self.random.randint(0, len(message_list) - 1)]
    
    def log_response_time(self, operation: str, duration: float):
        """Log operation response time with sass."""
        if self._perf_log_enabled:
            # Choose message based on speed
            if duration < 1.0:
                prefix = self._get_random_message(self.fast_response_messages)
            else:
                prefix = self._get_random_message(self.slow_response_messages)
            
            self.logger.info(f"{prefix}{operation}: {duration:.3f}s")
    
    def log_memory_usage(self, operation: str, memory_mb: float):
        """Log memory usage with sass."""
        if self._perf_log_enabled:
            # Choose message based on memory usage
            if memory_mb < 50:
                prefix = self._get_random_message(self.memory_low_messages)
            else:
                prefix = self._get_random_message(self.memory_high_messages)
            
            self.logger.info(f"{prefix}{operation}: {memory_mb:.1f}MB")
    
    def log_api_call(self, service: str, endpoint: str, duration: float, status: str):
        """Log API call metrics with sass."""
        if self._perf_log_enabled:
            # Choose message based on status
            if "success" in status.lower() or "200" in status:
                prefix = self._get_random_message(self.api_success_messages)
            else:
                prefix = self._get_random_message(self.api_failure_messages)
            
            self.logger.info(f"{prefix}{service}/{endpoint}: {duration:.3f}s ({status})")


class SecurityLogger:
    """Logger for security-related events with sassy personality."""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = get_logger("security")
        
        # Sassy security messages
        self.auth_success_messages = [
            "🔐 Access granted, VIP coming through! ",
            "✅ Identity confirmed! I know a real one when I see one. ",
            "🎯 Authentication nailed it! Welcome back, bestie. ",
            "🔓 Door's open! I've been expecting you. "
        ]
        
        self.auth_fail_messages = [
            "🚫 Nice try, but I don't think so! ",
            "🕵️‍♀️ Suspicious much? I'm keeping my eye on you. ",
            "🔒 Access denied! Did you forget who you're dealing with? ",
            "❌ That's gonna be a no from me. Try harder next time! "
        ]
        
        self.api_key_present_messages = [
            "🔑 Found the key! We're in business for ",
            "💎 Treasure found! Got the API key for ",
            "🔐 VIP access confirmed for ",
            "✨ API key looking fabulous for "
        ]
        
        self.api_key_missing_messages = [
            "🤷‍♀️ Where's the key? Can't find it for ",
            "🔍 Looked everywhere but no API key for ",
            "😬 Awkward... missing the API key for ",
            "🚪 Locked out! No key found for "
        ]
        
        self.file_access_success_messages = [
            "📂 File access? Consider it handled! ",
            "✅ File operation complete! Was there ever any doubt? ",
            "💅 Just worked some file magic on ",
            "📄 File whisperer strikes again! "
        ]
        
        self.file_access_fail_messages = [
            "📁 File is playing hard to get! ",
            "❌ File operation failed. Don't blame me! ",
            "🙄 This file is being so difficult right now. ",
            "💔 File breakup! It's not me, it's the "
        ]
        
        self.security_info_messages = [
            "ℹ️ Security tea to spill: ",
            "🛡️ Just keeping you in the loop: ",
            "🔍 Security observation, darling: ",
            "💭 Security thought bubble: "
        ]
        
        self.security_warning_messages = [
            "⚠️ Hmm, this looks suspicious: ",
            "👀 Eyes on this security situation: ",
            "🧐 Something's fishy here: ",
            "💅 Not to be dramatic, but you should know: "
        ]
        
        self.security_error_messages = [
            "🚨 RED ALERT! Security breach: ",
            "🔥 We've got a situation here: ",
            "⛔ Major security drama unfolding: ",
            "😱 Sound the alarms! Security issue: "
        ]
        
        import random
        self.random = random
    
    def _get_random_message(self, message_list):
        """Get a random message from a list."""
        return message_list[self.random.randint(0, len(message_list) - 1)]
    
    def log_auth_attempt(self, success: bool, method: str, details: str = None):
        """Log authentication attempts with sass."""
        if success:
            prefix = self._get_random_message(self.auth_success_messages)
        else:
            prefix = self._get_random_message(self.auth_fail_messages)
        
        msg = f"{prefix}{method}"
        if details:
            msg += f" - {details}"
        
        if success:
            self.logger.info(msg)
        else:
            self.logger.warning(msg)
    
    def log_api_key_usage(self, service: str, key_present: bool):
        """Log API key usage with sass."""
        if key_present:
            prefix = self._get_random_message(self.api_key_present_messages)
        else:
            prefix = self._get_random_message(self.api_key_missing_messages)
        
        status = "present" if key_present else "missing"
        self.logger.info(f"{prefix}{service}")
    
    def log_file_access(self, operation: str, path: str, success: bool):
        """Log file access attempts with sass."""
        if success:
            prefix = self._get_random_message(self.file_access_success_messages)
        else:
            prefix = self._get_random_message(self.file_access_fail_messages)
        
        self.logger.info(f"{prefix}{operation}: {path}")
    
    def log_security_event(self, event: str, severity: str = "info"):
        """Log general security events with sass."""
        if severity == "error":
            prefix = self._get_random_message(self.security_error_messages)
            self.logger.error(f"{prefix}{event}")
        elif severity == "warning":
            prefix = self._get_random_message(self.security_warning_messages)
            self.logger.warning(f"{prefix}{event}")
        else:
            prefix = self._get_random_message(self.security_info_messages)
            self.logger.info(f"{prefix}{event}")