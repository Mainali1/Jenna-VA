"""Music and Media Control Manager for Jenna Voice Assistant"""

import json
import os
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple

import pyautogui

from backend.utils.helpers import get_logger


class MusicMediaManager:
    """Manager for music and media control functionality."""
    
    def __init__(self, data_dir: Path):
        """Initialize the music and media manager.
        
        Args:
            data_dir: Directory to store music and media data
        """
        self.logger = get_logger("music_media_manager")
        self.data_dir = data_dir / "music_media"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.playlists_file = self.data_dir / "playlists.json"
        self.preferences_file = self.data_dir / "preferences.json"
        
        # Load existing data or create new files
        self.playlists = self._load_data(self.playlists_file, {})
        self.preferences = self._load_data(self.preferences_file, {
            "default_player": "system",  # system, spotify, vlc, etc.
            "volume": 50,
            "last_played": None
        })
        
        # Initialize media keys handler
        self._init_media_keys()
        
        self.logger.info("Music and Media Manager initialized")
    
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
                json.dump(default_data, f)
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
    
    def _init_media_keys(self):
        """Initialize media keys handler."""
        # No specific initialization needed for pyautogui
        pass
    
    # Media Control Methods
    
    def play_pause(self) -> bool:
        """Toggle play/pause for the current media.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            pyautogui.press('playpause')
            self.logger.info("Toggled play/pause")
            return True
        except Exception as e:
            self.logger.error(f"Error toggling play/pause: {e}")
            return False
    
    def next_track(self) -> bool:
        """Skip to the next track.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            pyautogui.press('nexttrack')
            self.logger.info("Skipped to next track")
            return True
        except Exception as e:
            self.logger.error(f"Error skipping to next track: {e}")
            return False
    
    def previous_track(self) -> bool:
        """Go back to the previous track.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            pyautogui.press('prevtrack')
            self.logger.info("Went back to previous track")
            return True
        except Exception as e:
            self.logger.error(f"Error going back to previous track: {e}")
            return False
    
    def stop(self) -> bool:
        """Stop media playback.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Some systems don't have a dedicated stop key, so we'll use play/pause
            pyautogui.press('playpause')
            self.logger.info("Stopped media playback")
            return True
        except Exception as e:
            self.logger.error(f"Error stopping media playback: {e}")
            return False
    
    def set_volume(self, level: int) -> bool:
        """Set the system volume level.
        
        Args:
            level: Volume level (0-100)
            
        Returns:
            True if successful, False otherwise
        """
        if level < 0 or level > 100:
            self.logger.warning(f"Invalid volume level: {level}. Must be between 0 and 100.")
            return False
        
        try:
            # Calculate how many times to press volume up/down
            current_volume = self.preferences.get("volume", 50)
            volume_diff = level - current_volume
            
            if volume_diff > 0:
                # Increase volume
                for _ in range(abs(volume_diff) // 2):  # Each press typically changes ~2%
                    pyautogui.press('volumeup')
            elif volume_diff < 0:
                # Decrease volume
                for _ in range(abs(volume_diff) // 2):  # Each press typically changes ~2%
                    pyautogui.press('volumedown')
            
            # Update stored volume preference
            self.preferences["volume"] = level
            self._save_data(self.preferences_file, self.preferences)
            
            self.logger.info(f"Set volume to {level}%")
            return True
        except Exception as e:
            self.logger.error(f"Error setting volume: {e}")
            return False
    
    def mute_unmute(self) -> bool:
        """Toggle mute/unmute.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            pyautogui.press('volumemute')
            self.logger.info("Toggled mute/unmute")
            return True
        except Exception as e:
            self.logger.error(f"Error toggling mute/unmute: {e}")
            return False
    
    # Application-specific Methods
    
    def launch_player(self, player_name: Optional[str] = None) -> bool:
        """Launch a media player application.
        
        Args:
            player_name: Name of the player to launch (spotify, vlc, etc.)
                         If None, uses the default player from preferences
            
        Returns:
            True if successful, False otherwise
        """
        if player_name is None:
            player_name = self.preferences.get("default_player", "system")
        
        try:
            if player_name.lower() == "spotify":
                # Launch Spotify
                subprocess.Popen(["spotify"])
            elif player_name.lower() == "vlc":
                # Launch VLC
                subprocess.Popen(["vlc"])
            elif player_name.lower() == "windows media player":
                # Launch Windows Media Player
                subprocess.Popen(["wmplayer"])
            else:
                self.logger.warning(f"Unknown player: {player_name}")
                return False
            
            # Update default player preference
            self.preferences["default_player"] = player_name.lower()
            self._save_data(self.preferences_file, self.preferences)
            
            self.logger.info(f"Launched {player_name}")
            return True
        except Exception as e:
            self.logger.error(f"Error launching {player_name}: {e}")
            return False
    
    # Playlist Management Methods
    
    def create_playlist(self, name: str, description: Optional[str] = None) -> bool:
        """Create a new playlist.
        
        Args:
            name: Playlist name
            description: Playlist description
            
        Returns:
            True if successful, False otherwise
        """
        if name in self.playlists:
            self.logger.warning(f"Playlist '{name}' already exists")
            return False
        
        self.playlists[name] = {
            "description": description,
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "tracks": []
        }
        
        return self._save_data(self.playlists_file, self.playlists)
    
    def add_to_playlist(self, playlist_name: str, track_info: Dict[str, Any]) -> bool:
        """Add a track to a playlist.
        
        Args:
            playlist_name: Name of the playlist
            track_info: Dictionary with track information (title, artist, etc.)
            
        Returns:
            True if successful, False otherwise
        """
        if playlist_name not in self.playlists:
            self.logger.warning(f"Playlist '{playlist_name}' does not exist")
            return False
        
        # Add track to playlist
        self.playlists[playlist_name]["tracks"].append(track_info)
        
        return self._save_data(self.playlists_file, self.playlists)
    
    def remove_from_playlist(self, playlist_name: str, track_index: int) -> bool:
        """Remove a track from a playlist.
        
        Args:
            playlist_name: Name of the playlist
            track_index: Index of the track to remove
            
        Returns:
            True if successful, False otherwise
        """
        if playlist_name not in self.playlists:
            self.logger.warning(f"Playlist '{playlist_name}' does not exist")
            return False
        
        tracks = self.playlists[playlist_name]["tracks"]
        if track_index < 0 or track_index >= len(tracks):
            self.logger.warning(f"Invalid track index: {track_index}")
            return False
        
        # Remove track from playlist
        del tracks[track_index]
        
        return self._save_data(self.playlists_file, self.playlists)
    
    def get_playlists(self) -> Dict[str, Any]:
        """Get all playlists.
        
        Returns:
            Dictionary of playlists
        """
        return self.playlists
    
    def get_playlist(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a specific playlist.
        
        Args:
            name: Playlist name
            
        Returns:
            Playlist information or None if not found
        """
        return self.playlists.get(name)
    
    def delete_playlist(self, name: str) -> bool:
        """Delete a playlist.
        
        Args:
            name: Playlist name
            
        Returns:
            True if successful, False otherwise
        """
        if name not in self.playlists:
            self.logger.warning(f"Playlist '{name}' does not exist")
            return False
        
        del self.playlists[name]
        return self._save_data(self.playlists_file, self.playlists)
    
    # Preference Management Methods
    
    def set_preference(self, key: str, value: Any) -> bool:
        """Set a preference value.
        
        Args:
            key: Preference key
            value: Preference value
            
        Returns:
            True if successful, False otherwise
        """
        self.preferences[key] = value
        return self._save_data(self.preferences_file, self.preferences)
    
    def get_preference(self, key: str, default: Any = None) -> Any:
        """Get a preference value.
        
        Args:
            key: Preference key
            default: Default value if key doesn't exist
            
        Returns:
            Preference value or default
        """
        return self.preferences.get(key, default)
    
    def get_all_preferences(self) -> Dict[str, Any]:
        """Get all preferences.
        
        Returns:
            Dictionary of preferences
        """
        return self.preferences