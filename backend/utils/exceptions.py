"""Custom Exceptions for Jenna Voice Assistant"""


class JennaException(Exception):
    """Base exception for all Jenna-related errors."""
    
    def __init__(self, message: str, error_code: str = None, details: dict = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or "JENNA_ERROR"
        self.details = details or {}
    
    def to_dict(self) -> dict:
        """Convert exception to dictionary format."""
        return {
            "error": self.__class__.__name__,
            "message": self.message,
            "error_code": self.error_code,
            "details": self.details
        }


# Core Application Exceptions
class ApplicationException(JennaException):
    """Exception raised for application-level errors."""
    pass


class ConfigurationException(JennaException):
    """Exception raised for configuration-related errors."""
    pass


class InitializationException(JennaException):
    """Exception raised during application initialization."""
    pass


# Voice Engine Exceptions
class VoiceEngineException(JennaException):
    """Exception raised for voice engine errors."""
    pass


class SpeechRecognitionException(VoiceEngineException):
    """Exception raised for speech recognition errors."""
    pass


class TextToSpeechException(VoiceEngineException):
    """Exception raised for text-to-speech errors."""
    pass


class MicrophoneException(VoiceEngineException):
    """Exception raised for microphone-related errors."""
    pass


class WakeWordException(VoiceEngineException):
    """Exception raised for wake word detection errors."""
    pass


# AI Engine Exceptions
class AIEngineException(JennaException):
    """Exception raised for AI engine errors."""
    pass


class IntentRecognitionException(AIEngineException):
    """Exception raised for intent recognition errors."""
    pass


class EntityExtractionException(AIEngineException):
    """Exception raised for entity extraction errors."""
    pass


class ResponseGenerationException(AIEngineException):
    """Exception raised for response generation errors."""
    pass


# UI Manager Exceptions
class UIManagerException(JennaException):
    """Exception raised for UI manager errors."""
    pass


class WebServerException(UIManagerException):
    """Exception raised for web server errors."""
    pass


class WebSocketException(UIManagerException):
    """Exception raised for WebSocket errors."""
    pass


# System Tray Exceptions
class SystemTrayException(JennaException):
    """Exception raised for system tray errors."""
    pass


# Feature Manager Exceptions
class FeatureManagerException(JennaException):
    """Exception raised for feature manager errors."""
    pass


class FeatureInitializationException(FeatureManagerException):
    """Exception raised for feature initialization errors."""
    pass


class FeatureNotAvailableException(FeatureManagerException):
    """Exception raised when a feature is not available."""
    pass


class FeatureConfigurationException(FeatureManagerException):
    """Exception raised for feature configuration errors."""
    pass


# Service Manager Exceptions
class ServiceManagerException(JennaException):
    """Exception raised for service manager errors."""
    pass


class ServiceInitializationException(ServiceManagerException):
    """Exception raised for service initialization errors."""
    pass


class ServiceUnavailableException(ServiceManagerException):
    """Exception raised when a service is unavailable."""
    pass


class APIException(ServiceManagerException):
    """Exception raised for external API errors."""
    pass


class APIKeyException(APIException):
    """Exception raised for API key related errors."""
    pass


class APIRateLimitException(APIException):
    """Exception raised when API rate limit is exceeded."""
    pass


# File System Exceptions
class FileSystemException(JennaException):
    """Exception raised for file system errors."""
    pass


class FileNotFoundError(FileSystemException):
    """Exception raised when a file is not found."""
    pass


class FilePermissionException(FileSystemException):
    """Exception raised for file permission errors."""
    pass


class DirectoryException(FileSystemException):
    """Exception raised for directory-related errors."""
    pass


# Security Exceptions
class SecurityException(JennaException):
    """Exception raised for security-related errors."""
    pass


class AuthenticationException(SecurityException):
    """Exception raised for authentication errors."""
    pass


class AuthorizationException(SecurityException):
    """Exception raised for authorization errors."""
    pass


class EncryptionException(SecurityException):
    """Exception raised for encryption/decryption errors."""
    pass


# Database Exceptions
class DatabaseException(JennaException):
    """Exception raised for database errors."""
    pass


class DatabaseConnectionException(DatabaseException):
    """Exception raised for database connection errors."""
    pass


class DatabaseQueryException(DatabaseException):
    """Exception raised for database query errors."""
    pass


# Network Exceptions
class NetworkException(JennaException):
    """Exception raised for network-related errors."""
    pass


class ConnectionException(NetworkException):
    """Exception raised for connection errors."""
    pass


class TimeoutException(NetworkException):
    """Exception raised for timeout errors."""
    pass


# Validation Exceptions
class ValidationException(JennaException):
    """Exception raised for validation errors."""
    pass


class InvalidInputException(ValidationException):
    """Exception raised for invalid input."""
    pass


class InvalidConfigurationException(ValidationException):
    """Exception raised for invalid configuration."""
    pass


# Resource Exceptions
class ResourceException(JennaException):
    """Exception raised for resource-related errors."""
    pass


class ResourceNotAvailableException(ResourceException):
    """Exception raised when a resource is not available."""
    pass


class ResourceExhaustedException(ResourceException):
    """Exception raised when resources are exhausted."""
    pass


class MemoryException(ResourceException):
    """Exception raised for memory-related errors."""
    pass


# Plugin Exceptions
class PluginException(JennaException):
    """Exception raised for plugin-related errors."""
    pass


class PluginLoadException(PluginException):
    """Exception raised when a plugin fails to load."""
    pass


class PluginNotFoundError(PluginException):
    """Exception raised when a plugin is not found."""
    pass


# Backup Exceptions
class BackupException(JennaException):
    """Exception raised for backup-related errors."""
    pass


class BackupCreationException(BackupException):
    """Exception raised when backup creation fails."""
    pass


class BackupRestoreException(BackupException):
    """Exception raised when backup restoration fails."""
    pass


# Update Exceptions
class UpdateException(JennaException):
    """Exception raised for update-related errors."""
    pass


class UpdateCheckException(UpdateException):
    """Exception raised when update check fails."""
    pass


class UpdateDownloadException(UpdateException):
    """Exception raised when update download fails."""
    pass


class UpdateInstallException(UpdateException):
    """Exception raised when update installation fails."""
    pass


# Utility Functions
def handle_exception(exception: Exception, logger=None) -> dict:
    """Handle and format exceptions consistently."""
    if isinstance(exception, JennaException):
        error_dict = exception.to_dict()
    else:
        error_dict = {
            "error": exception.__class__.__name__,
            "message": str(exception),
            "error_code": "UNKNOWN_ERROR",
            "details": {}
        }
    
    if logger:
        logger.error(f"Exception occurred: {error_dict}")
    
    return error_dict


def create_error_response(exception: Exception, include_details: bool = False) -> dict:
    """Create a standardized error response."""
    error_dict = handle_exception(exception)
    
    response = {
        "success": False,
        "error": error_dict["error"],
        "message": error_dict["message"]
    }
    
    if include_details:
        response["error_code"] = error_dict["error_code"]
        response["details"] = error_dict["details"]
    
    return response


def is_critical_error(exception: Exception) -> bool:
    """Determine if an exception is critical and requires application shutdown."""
    critical_exceptions = (
        InitializationException,
        ConfigurationException,
        SecurityException,
        MemoryException,
        ResourceExhaustedException
    )
    
    return isinstance(exception, critical_exceptions)


def get_error_category(exception: Exception) -> str:
    """Get the category of an error for classification purposes."""
    if isinstance(exception, (VoiceEngineException, SpeechRecognitionException, TextToSpeechException)):
        return "voice"
    elif isinstance(exception, (AIEngineException, IntentRecognitionException, ResponseGenerationException)):
        return "ai"
    elif isinstance(exception, (UIManagerException, WebServerException, WebSocketException)):
        return "ui"
    elif isinstance(exception, (ServiceManagerException, APIException, NetworkException)):
        return "service"
    elif isinstance(exception, (FeatureManagerException, FeatureInitializationException)):
        return "feature"
    elif isinstance(exception, (FileSystemException, DatabaseException)):
        return "storage"
    elif isinstance(exception, (SecurityException, AuthenticationException)):
        return "security"
    elif isinstance(exception, (ValidationException, InvalidInputException)):
        return "validation"
    elif isinstance(exception, (ResourceException, MemoryException)):
        return "resource"
    else:
        return "general"