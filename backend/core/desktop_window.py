"""Desktop Window Manager for Native UI"""

import sys
import threading
from pathlib import Path
from typing import Optional, Callable

try:
    from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
    from PyQt5.QtCore import QUrl, Qt, QSize
    from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
    from PyQt5.QtGui import QIcon
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False

from .config import Settings
from .logger import get_logger
from ..utils.exceptions import DesktopWindowException


class DesktopWindowManager:
    """Manages a native desktop window using PyQt5 to display the web UI."""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = get_logger(__name__)
        
        # Check if PyQt5 is available
        if not PYQT_AVAILABLE:
            self.logger.warning("⚠️ PyQt5 not available, desktop window disabled")
            self.enabled = False
            return
        
        self.enabled = True
        self.app = None
        self.window = None
        self.web_view = None
        self.window_thread = None
        self.running = False
        
        # Window state
        self.is_visible = False
        
        # Server URL
        self.host = "127.0.0.1"
        self.port = 8080
    
    def initialize(self):
        """Initialize the desktop window manager."""
        if not self.enabled:
            return
        
        try:
            self.logger.info("🖥️ Initializing desktop window manager...")
            
            # Set server configuration from settings
            if hasattr(self.settings, 'ui_host'):
                self.host = self.settings.ui_host
            if hasattr(self.settings, 'ui_port'):
                self.port = self.settings.ui_port
            
            self.logger.info("✅ Desktop window manager initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize desktop window manager: {e}")
            self.enabled = False
            raise DesktopWindowException(f"Desktop window initialization failed: {e}")
    
    def _create_window(self):
        """Create the desktop window with QWebEngineView."""
        try:
            # Create QApplication if it doesn't exist
            if QApplication.instance() is None:
                self.app = QApplication(sys.argv)
            else:
                self.app = QApplication.instance()
            
            # Create main window
            self.window = QMainWindow()
            self.window.setWindowTitle("Jenna Voice Assistant")
            self.window.resize(1000, 700)
            self.window.setMinimumSize(800, 600)
            
            # Try to load icon
            icon_path = Path(__file__).parent.parent.parent / "assets" / "icon.ico"
            if icon_path.exists():
                self.window.setWindowIcon(QIcon(str(icon_path)))
            
            # Create central widget and layout
            central_widget = QWidget()
            layout = QVBoxLayout(central_widget)
            layout.setContentsMargins(0, 0, 0, 0)
            
            # Create web view
            self.web_view = QWebEngineView()
            layout.addWidget(self.web_view)
            
            # Set central widget
            self.window.setCentralWidget(central_widget)
            
            # Connect close event to hide instead of close
            self.window.closeEvent = self._handle_close_event
            
            self.logger.info("✅ Desktop window created successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to create desktop window: {e}")
            raise DesktopWindowException(f"Desktop window creation failed: {e}")
    
    def _handle_close_event(self, event):
        """Handle window close event to hide instead of close."""
        event.ignore()
        self.hide_window()
    
    def load_url(self):
        """Load the FastAPI server URL in the web view."""
        if not self.enabled or not self.web_view:
            return
        
        try:
            url = f"http://{self.host}:{self.port}"
            self.web_view.load(QUrl(url))
            self.logger.info(f"🌐 Loading URL in desktop window: {url}")
        except Exception as e:
            self.logger.error(f"Failed to load URL in desktop window: {e}")
    
    def show_window(self):
        """Show the desktop window."""
        if not self.enabled:
            self.logger.warning("⚠️ Desktop window not enabled, cannot show")
            return
        
        try:
            # Create window if it doesn't exist
            if not self.window:
                self._create_window()
                self.load_url()
            
            # Show window
            self.window.show()
            self.window.activateWindow()
            self.window.raise_()
            self.is_visible = True
            self.logger.info("🖥️ Desktop window shown")
            
        except Exception as e:
            self.logger.error(f"Failed to show desktop window: {e}")
    
    def hide_window(self):
        """Hide the desktop window."""
        if not self.enabled or not self.window:
            return
        
        try:
            self.window.hide()
            self.is_visible = False
            self.logger.info("🙈 Desktop window hidden")
        except Exception as e:
            self.logger.error(f"Failed to hide desktop window: {e}")
    
    def toggle_window(self):
        """Toggle the desktop window visibility."""
        if self.is_visible:
            self.hide_window()
        else:
            self.show_window()
    
    def start(self):
        """Start the desktop window in a separate thread."""
        if not self.enabled:
            self.logger.warning("⚠️ Desktop window not enabled, skipping start")
            return
        
        try:
            self.logger.info("🚀 Starting desktop window...")
            
            # Run window in a separate thread
            def run_window():
                try:
                    self._create_window()
                    self.load_url()
                    self.running = True
                    self.app.exec_()
                except Exception as e:
                    self.logger.error(f"Desktop window error: {e}")
                finally:
                    self.running = False
            
            self.window_thread = threading.Thread(target=run_window, daemon=True)
            self.window_thread.start()
            
            self.logger.info("✅ Desktop window started")
            
        except Exception as e:
            self.logger.error(f"Failed to start desktop window: {e}")
            raise DesktopWindowException(f"Desktop window start failed: {e}")
    
    def stop(self):
        """Stop the desktop window."""
        if not self.enabled or not self.running:
            return
        
        try:
            # Quit the application
            if self.app:
                self.app.quit()
            
            # Wait for thread to finish
            if self.window_thread and self.window_thread.is_alive():
                self.window_thread.join(timeout=1.0)
            
            self.running = False
            self.logger.info("✅ Desktop window stopped")
            
        except Exception as e:
            self.logger.error(f"Failed to stop desktop window: {e}")
    
    def cleanup(self):
        """Clean up resources."""
        self.stop()