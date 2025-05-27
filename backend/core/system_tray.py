"""System Tray Manager for Background Operation"""

import sys
import threading
from pathlib import Path
from typing import Optional, Callable

try:
    import pystray
    from pystray import MenuItem as item
    from PIL import Image, ImageDraw
except ImportError:
    pystray = None
    item = None
    Image = None
    ImageDraw = None

from .config import Settings
from .logger import get_logger
from ..utils.exceptions import SystemTrayException


class SystemTrayManager:
    """Manages system tray icon and menu for background operation."""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = get_logger(__name__)
        
        # Check if pystray is available
        if pystray is None:
            self.logger.warning("⚠️ pystray not available, system tray disabled")
            self.enabled = False
            return
        
        self.enabled = True
        self.icon = None
        self.running = False
        
        # Callbacks
        self.on_show_ui: Optional[Callable] = None
        self.on_hide_ui: Optional[Callable] = None
        self.on_toggle_listening: Optional[Callable] = None
        self.on_settings: Optional[Callable] = None
        self.on_quit: Optional[Callable] = None
        
        # State
        self.listening_enabled = True
        self.ui_visible = False
        
        # Create icon
        self._create_icon()
    
    def _create_icon_image(self) -> Optional[Image.Image]:
        """Create the system tray icon image."""
        if Image is None or ImageDraw is None:
            return None
        
        try:
            # Create a simple icon (32x32 pixels)
            width = 32
            height = 32
            
            # Create image with transparent background
            image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
            draw = ImageDraw.Draw(image)
            
            # Draw a simple microphone icon
            # Microphone body (rectangle)
            mic_width = 12
            mic_height = 16
            mic_x = (width - mic_width) // 2
            mic_y = 4
            
            # Main microphone body
            draw.rounded_rectangle(
                [mic_x, mic_y, mic_x + mic_width, mic_y + mic_height],
                radius=6,
                fill=(0, 150, 255, 255),  # Blue color
                outline=(255, 255, 255, 255),
                width=1
            )
            
            # Microphone stand
            stand_x = width // 2
            stand_y = mic_y + mic_height
            draw.line(
                [stand_x, stand_y, stand_x, stand_y + 6],
                fill=(255, 255, 255, 255),
                width=2
            )
            
            # Base
            base_width = 8
            base_x = stand_x - base_width // 2
            base_y = stand_y + 6
            draw.line(
                [base_x, base_y, base_x + base_width, base_y],
                fill=(255, 255, 255, 255),
                width=2
            )
            
            # Add status indicator (small dot)
            if self.listening_enabled:
                # Green dot for listening
                dot_color = (0, 255, 0, 255)
            else:
                # Red dot for not listening
                dot_color = (255, 0, 0, 255)
            
            draw.ellipse(
                [width - 8, 2, width - 2, 8],
                fill=dot_color
            )
            
            return image
            
        except Exception as e:
            self.logger.error(f"Failed to create icon image: {e}")
            return None
    
    def _create_icon(self):
        """Create the system tray icon."""
        if not self.enabled:
            return
        
        try:
            # Try to load custom icon first
            icon_path = Path(__file__).parent.parent.parent / "assets" / "icon.ico"
            if icon_path.exists():
                image = Image.open(icon_path)
            else:
                # Create default icon
                image = self._create_icon_image()
                if image is None:
                    self.logger.error("Failed to create icon image")
                    self.enabled = False
                    return
            
            # Create menu
            menu = pystray.Menu(
                item(
                    "Show Jenna",
                    self._show_ui,
                    default=True,
                    visible=lambda item: not self.ui_visible
                ),
                item(
                    "Hide Jenna",
                    self._hide_ui,
                    visible=lambda item: self.ui_visible
                ),
                pystray.Menu.SEPARATOR,
                item(
                    "Enable Listening",
                    self._toggle_listening,
                    checked=lambda item: self.listening_enabled,
                    visible=lambda item: not self.listening_enabled
                ),
                item(
                    "Disable Listening",
                    self._toggle_listening,
                    checked=lambda item: self.listening_enabled,
                    visible=lambda item: self.listening_enabled
                ),
                pystray.Menu.SEPARATOR,
                item("Settings", self._open_settings),
                item("About", self._show_about),
                pystray.Menu.SEPARATOR,
                item("Quit", self._quit_application)
            )
            
            # Create icon
            self.icon = pystray.Icon(
                "Jenna Voice Assistant",
                image,
                "Jenna Voice Assistant",
                menu
            )
            
            self.logger.info("✅ System tray icon created")
            
        except Exception as e:
            self.logger.error(f"Failed to create system tray icon: {e}")
            self.enabled = False
    
    def _show_ui(self, icon=None, item=None):
        """Show the UI."""
        try:
            if self.on_show_ui:
                self.on_show_ui()
            self.ui_visible = True
            self._update_icon()
            self.logger.info("📱 UI show requested from system tray")
        except Exception as e:
            self.logger.error(f"Error showing UI: {e}")
    
    def _hide_ui(self, icon=None, item=None):
        """Hide the UI."""
        try:
            if self.on_hide_ui:
                self.on_hide_ui()
            self.ui_visible = False
            self._update_icon()
            self.logger.info("🙈 UI hide requested from system tray")
        except Exception as e:
            self.logger.error(f"Error hiding UI: {e}")
    
    def _toggle_listening(self, icon=None, item=None):
        """Toggle listening state."""
        try:
            self.listening_enabled = not self.listening_enabled
            if self.on_toggle_listening:
                self.on_toggle_listening(self.listening_enabled)
            self._update_icon()
            
            status = "enabled" if self.listening_enabled else "disabled"
            self.logger.info(f"🎤 Listening {status} from system tray")
            
        except Exception as e:
            self.logger.error(f"Error toggling listening: {e}")
    
    def _open_settings(self, icon=None, item=None):
        """Open settings."""
        try:
            if self.on_settings:
                self.on_settings()
            self.logger.info("⚙️ Settings requested from system tray")
        except Exception as e:
            self.logger.error(f"Error opening settings: {e}")
    
    def _show_about(self, icon=None, item=None):
        """Show about dialog."""
        try:
            # For now, just log. In a full implementation, this could show a dialog
            self.logger.info("ℹ️ About dialog requested from system tray")
            
            # Could implement a simple message box here
            if sys.platform == "win32":
                try:
                    import ctypes
                    ctypes.windll.user32.MessageBoxW(
                        0,
                        "Jenna Voice Assistant v1.0.0\n\nA commercial-grade desktop voice assistant\nBuilt with Python and modern web technologies.",
                        "About Jenna",
                        0x40  # MB_ICONINFORMATION
                    )
                except:
                    pass
            
        except Exception as e:
            self.logger.error(f"Error showing about: {e}")
    
    def _quit_application(self, icon=None, item=None):
        """Quit the application."""
        try:
            if self.on_quit:
                self.on_quit()
            self.logger.info("🚪 Application quit requested from system tray")
        except Exception as e:
            self.logger.error(f"Error quitting application: {e}")
    
    def _update_icon(self):
        """Update the icon image to reflect current state."""
        if not self.enabled or not self.icon:
            return
        
        try:
            new_image = self._create_icon_image()
            if new_image:
                self.icon.icon = new_image
        except Exception as e:
            self.logger.error(f"Error updating icon: {e}")
    
    def start(self):
        """Start the system tray icon."""
        if not self.enabled:
            self.logger.warning("⚠️ System tray not enabled, skipping start")
            return
        
        try:
            self.logger.info("🚀 Starting system tray...")
            
            # Run icon in a separate thread
            def run_icon():
                try:
                    self.running = True
                    self.icon.run()
                except Exception as e:
                    self.logger.error(f"System tray error: {e}")
                finally:
                    self.running = False
            
            self.tray_thread = threading.Thread(target=run_icon, daemon=True)
            self.tray_thread.start()
            
            self.logger.info("✅ System tray started")
            
        except Exception as e:
            self.logger.error(f"Failed to start system tray: {e}")
            raise SystemTrayException(f"System tray startup failed: {e}")
    
    def stop(self):
        """Stop the system tray icon."""
        if not self.enabled or not self.running:
            return
        
        try:
            self.logger.info("🛑 Stopping system tray...")
            
            if self.icon:
                self.icon.stop()
            
            self.running = False
            self.logger.info("✅ System tray stopped")
            
        except Exception as e:
            self.logger.error(f"Error stopping system tray: {e}")
    
    def update_listening_state(self, enabled: bool):
        """Update the listening state."""
        self.listening_enabled = enabled
        self._update_icon()
    
    def update_ui_state(self, visible: bool):
        """Update the UI visibility state."""
        self.ui_visible = visible
        self._update_icon()
    
    def show_notification(self, title: str, message: str, timeout: int = 5):
        """Show a system notification."""
        if not self.enabled or not self.icon:
            return
        
        try:
            self.icon.notify(message, title)
            self.logger.info(f"📢 Notification shown: {title} - {message}")
        except Exception as e:
            self.logger.error(f"Error showing notification: {e}")
    
    def is_enabled(self) -> bool:
        """Check if system tray is enabled."""
        return self.enabled
    
    def is_running(self) -> bool:
        """Check if system tray is running."""
        return self.running