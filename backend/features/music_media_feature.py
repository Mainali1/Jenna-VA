"""Music and Media Control Feature for Jenna Voice Assistant"""

import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Any, Union

from backend.feature_manager import Feature
from backend.features.music_media import MusicMediaManager
from backend.utils.helpers import get_logger


class MusicMediaFeature(Feature):
    """Feature for controlling music and media playback."""
    
    def __init__(self, settings):
        """Initialize the music and media control feature.
        
        Args:
            settings: Application settings
        """
        super().__init__(
            name="Music and Media Control",
            description="Control music playback, manage playlists, and control media applications",
            settings=settings,
            requires_internet=False,  # Basic controls work without internet
            requires_api_key=False,   # No API key required for basic functionality
        )
        self.logger = get_logger("music_media_feature")
        self.manager = None
    
    async def _initialize_impl(self) -> bool:
        """Initialize the music and media control feature.
        
        Returns:
            True if initialization was successful, False otherwise
        """
        try:
            data_dir = Path(self.settings.data_directory)
            self.manager = MusicMediaManager(data_dir)
            self.logger.info("Music and Media Control feature initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize Music and Media Control feature: {e}")
            return False
    
    async def _on_enable(self) -> bool:
        """Actions to perform when the feature is enabled.
        
        Returns:
            True if successful, False otherwise
        """
        self.logger.info("Music and Media Control feature enabled")
        return True
    
    async def _on_disable(self) -> bool:
        """Actions to perform when the feature is disabled.
        
        Returns:
            True if successful, False otherwise
        """
        self.logger.info("Music and Media Control feature disabled")
        return True
    
    async def cleanup(self) -> None:
        """Clean up resources used by the feature."""
        self.logger.info("Cleaning up Music and Media Control feature")
        # No specific cleanup needed for this feature
    
    # Media Control Methods
    
    async def play_pause(self) -> bool:
        """Toggle play/pause for the current media.
        
        Returns:
            True if successful, False otherwise
        """
        if not self.is_enabled():
            self.logger.warning("Cannot play/pause: feature is disabled")
            return False
        
        return self.manager.play_pause()
    
    async def next_track(self) -> bool:
        """Skip to the next track.
        
        Returns:
            True if successful, False otherwise
        """
        if not self.is_enabled():
            self.logger.warning("Cannot skip to next track: feature is disabled")
            return False
        
        return self.manager.next_track()
    
    async def previous_track(self) -> bool:
        """Go back to the previous track.
        
        Returns:
            True if successful, False otherwise
        """
        if not self.is_enabled():
            self.logger.warning("Cannot go to previous track: feature is disabled")
            return False
        
        return self.manager.previous_track()
    
    async def stop(self) -> bool:
        """Stop media playback.
        
        Returns:
            True if successful, False otherwise
        """
        if not self.is_enabled():
            self.logger.warning("Cannot stop playback: feature is disabled")
            return False
        
        return self.manager.stop()
    
    async def set_volume(self, level: int) -> bool:
        """Set the system volume level.
        
        Args:
            level: Volume level (0-100)
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_enabled():
            self.logger.warning("Cannot set volume: feature is disabled")
            return False
        
        return self.manager.set_volume(level)
    
    async def mute_unmute(self) -> bool:
        """Toggle mute/unmute.
        
        Returns:
            True if successful, False otherwise
        """
        if not self.is_enabled():
            self.logger.warning("Cannot mute/unmute: feature is disabled")
            return False
        
        return self.manager.mute_unmute()
    
    # Application-specific Methods
    
    async def launch_player(self, player_name: Optional[str] = None) -> bool:
        """Launch a media player application.
        
        Args:
            player_name: Name of the player to launch (spotify, vlc, etc.)
                         If None, uses the default player from preferences
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_enabled():
            self.logger.warning(f"Cannot launch player {player_name}: feature is disabled")
            return False
        
        return self.manager.launch_player(player_name)
    
    # Playlist Management Methods
    
    async def create_playlist(self, name: str, description: Optional[str] = None) -> bool:
        """Create a new playlist.
        
        Args:
            name: Playlist name
            description: Playlist description
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_enabled():
            self.logger.warning("Cannot create playlist: feature is disabled")
            return False
        
        return self.manager.create_playlist(name, description)
    
    async def add_to_playlist(self, playlist_name: str, track_info: Dict[str, Any]) -> bool:
        """Add a track to a playlist.
        
        Args:
            playlist_name: Name of the playlist
            track_info: Dictionary with track information (title, artist, etc.)
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_enabled():
            self.logger.warning("Cannot add to playlist: feature is disabled")
            return False
        
        return self.manager.add_to_playlist(playlist_name, track_info)
    
    async def remove_from_playlist(self, playlist_name: str, track_index: int) -> bool:
        """Remove a track from a playlist.
        
        Args:
            playlist_name: Name of the playlist
            track_index: Index of the track to remove
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_enabled():
            self.logger.warning("Cannot remove from playlist: feature is disabled")
            return False
        
        return self.manager.remove_from_playlist(playlist_name, track_index)
    
    async def get_playlists(self) -> Dict[str, Any]:
        """Get all playlists.
        
        Returns:
            Dictionary of playlists
        """
        if not self.is_enabled():
            self.logger.warning("Cannot get playlists: feature is disabled")
            return {}
        
        return self.manager.get_playlists()
    
    async def get_playlist(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a specific playlist.
        
        Args:
            name: Playlist name
            
        Returns:
            Playlist information or None if not found
        """
        if not self.is_enabled():
            self.logger.warning("Cannot get playlist: feature is disabled")
            return None
        
        return self.manager.get_playlist(name)
    
    async def delete_playlist(self, name: str) -> bool:
        """Delete a playlist.
        
        Args:
            name: Playlist name
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_enabled():
            self.logger.warning("Cannot delete playlist: feature is disabled")
            return False
        
        return self.manager.delete_playlist(name)
    
    # Preference Management Methods
    
    async def set_preference(self, key: str, value: Any) -> bool:
        """Set a preference value.
        
        Args:
            key: Preference key
            value: Preference value
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_enabled():
            self.logger.warning("Cannot set preference: feature is disabled")
            return False
        
        return self.manager.set_preference(key, value)
    
    async def get_preference(self, key: str, default: Any = None) -> Any:
        """Get a preference value.
        
        Args:
            key: Preference key
            default: Default value if key doesn't exist
            
        Returns:
            Preference value or default
        """
        if not self.is_enabled():
            self.logger.warning("Cannot get preference: feature is disabled")
            return default
        
        return self.manager.get_preference(key, default)
    
    async def get_all_preferences(self) -> Dict[str, Any]:
        """Get all preferences.
        
        Returns:
            Dictionary of preferences
        """
        if not self.is_enabled():
            self.logger.warning("Cannot get all preferences: feature is disabled")
            return {}
        
        return self.manager.get_all_preferences()