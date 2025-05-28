"""Custom exceptions for Jenna Voice Assistant"""


class JennaException(Exception):
    """Base exception for all Jenna-related errors."""
    pass


class ConfigException(JennaException):
    """Exception raised for configuration errors."""
    pass


class VoiceEngineException(JennaException):
    """Exception raised for voice engine errors."""
    pass


class AIEngineException(JennaException):
    """Exception raised for AI engine errors."""
    pass


class UIManagerException(JennaException):
    """Exception raised for UI manager errors."""
    pass


class SystemTrayException(JennaException):
    """Exception raised for system tray errors."""
    pass


class FeatureManagerException(JennaException):
    """Exception raised for feature manager errors."""
    pass


class ServiceManagerException(JennaException):
    """Exception raised for service manager errors."""
    pass


class DesktopWindowException(JennaException):
    """Exception raised for desktop window errors."""
    pass