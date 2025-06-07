"""Main Jenna Application Class"""

import asyncio
import threading
from typing import Optional, Dict, Any
from pathlib import Path

from .config import Settings
from .logger import get_logger
from .voice_engine import VoiceEngine
from .ai_engine import AIEngine
from .ui_manager import UIManager
from .system_tray import SystemTrayManager
from .feature_manager import FeatureManager
from .plugin_manager import PluginManager
from .service_manager import ServiceManager
from ..utils.exceptions import JennaException


class JennaApplication:
    """Main application class that coordinates all components."""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = get_logger(__name__)
        self.running = False
        self._shutdown_event = asyncio.Event()
        
        # Core components
        self.voice_engine: Optional[VoiceEngine] = None
        self.ai_engine: Optional[AIEngine] = None
        self.ui_manager: Optional[UIManager] = None
        self.system_tray: Optional[SystemTrayManager] = None
        self.feature_manager: Optional[FeatureManager] = None
        self.plugin_manager: Optional[PluginManager] = None
        self.service_manager: Optional[ServiceManager] = None
        
        # State management
        self.is_listening = False
        self.conversation_context = []
        self.current_session = None
    
    async def initialize(self):
        """Initialize all application components."""
        try:
            self.logger.info("Initializing Jenna application components...")
            
            # Initialize service manager first
            self.service_manager = ServiceManager(self.settings)
            await self.service_manager.initialize()
            
            # Initialize AI engine
            self.ai_engine = AIEngine(self.settings)
            await self.ai_engine.initialize()
            
            # Initialize voice engine
            self.voice_engine = VoiceEngine(self.settings)
            await self.voice_engine.initialize()
            
            # Initialize feature manager
            self.feature_manager = FeatureManager(self.settings, self.service_manager)
            await self.feature_manager.initialize()
            
            # Initialize plugin manager
            self.plugin_manager = PluginManager(self.settings, self.feature_manager)
            await self.plugin_manager.initialize()
            
            # Initialize UI manager
            self.ui_manager = UIManager(self.settings)
            await self.ui_manager.initialize()
            
            # Initialize system tray
            if self.settings.system_tray_enabled:
                self.system_tray = SystemTrayManager(self.settings, self)
                self.system_tray.initialize()
            
            # Setup event handlers
            self._setup_event_handlers()
            
            self.logger.info("✅ All components initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize application: {e}")
            raise JennaException(f"Initialization failed: {e}")
    
    def _setup_event_handlers(self):
        """Setup event handlers between components."""
        if self.voice_engine:
            self.voice_engine.on_wake_word_detected = self._on_wake_word_detected
            self.voice_engine.on_speech_recognized = self._on_speech_recognized
            self.voice_engine.on_speech_timeout = self._on_speech_timeout
        
        if self.ui_manager:
            self.ui_manager.on_command_received = self._on_text_command_received
            self.ui_manager.on_settings_changed = self._on_settings_changed
    
    async def run(self):
        """Main application loop."""
        try:
            self.running = True
            self.logger.info("🎯 Jenna is now active and listening...")
            
            # Start voice listening in background
            if self.voice_engine:
                voice_task = asyncio.create_task(self.voice_engine.start_listening())
            
            # Start UI server
            if self.ui_manager:
                ui_task = asyncio.create_task(self.ui_manager.start_server())
            
            # Wait for shutdown signal
            await self._shutdown_event.wait()
            
        except Exception as e:
            self.logger.error(f"Error in main loop: {e}")
            raise
        finally:
            self.running = False
    
    async def _on_wake_word_detected(self):
        """Handle wake word detection."""
        self.logger.info("👂 Wake word detected - Jenna is listening...")
        self.is_listening = True
        
        # Notify UI
        if self.ui_manager:
            await self.ui_manager.update_status("listening")
        
        # Play activation sound
        if self.voice_engine:
            await self.voice_engine.play_activation_sound()
    
    async def _on_speech_recognized(self, text: str):
        """Handle recognized speech."""
        self.logger.info(f"🗣️ Speech recognized: {text}")
        await self._process_command(text, source="voice")
    
    async def _on_speech_timeout(self):
        """Handle speech recognition timeout."""
        self.logger.debug("⏰ Speech recognition timeout")
        self.is_listening = False
        
        if self.ui_manager:
            await self.ui_manager.update_status("idle")
    
    async def _on_text_command_received(self, text: str):
        """Handle text command from UI."""
        self.logger.info(f"💬 Text command received: {text}")
        await self._process_command(text, source="text")
    
    async def _process_command(self, command: str, source: str = "voice"):
        """Process a command from voice or text input."""
        try:
            # Update UI status
            if self.ui_manager:
                await self.ui_manager.update_status("processing")
            
            # Add to conversation context
            self.conversation_context.append({
                "type": "user",
                "content": command,
                "source": source,
                "timestamp": asyncio.get_event_loop().time()
            })
            
            # Process with AI engine
            response = await self.ai_engine.process_command(
                command, 
                context=self.conversation_context,
                features=self.feature_manager,
                plugins=self.plugin_manager
            )
            
            # Add response to context
            self.conversation_context.append({
                "type": "assistant",
                "content": response.text,
                "timestamp": asyncio.get_event_loop().time()
            })
            
            # Limit context size
            if len(self.conversation_context) > self.settings.max_conversation_history:
                self.conversation_context = self.conversation_context[-self.settings.max_conversation_history:]
            
            # Speak response if from voice
            if source == "voice" and self.voice_engine:
                await self.voice_engine.speak(response.text)
            
            # Update UI
            if self.ui_manager:
                await self.ui_manager.add_message("user", command)
                await self.ui_manager.add_message("assistant", response.text)
                await self.ui_manager.update_status("idle")
            
            # Execute any actions
            if response.actions:
                await self._execute_actions(response.actions)
            
        except Exception as e:
            self.logger.error(f"Error processing command: {e}")
            error_message = "I'm sorry, I encountered an error processing your request."
            
            if source == "voice" and self.voice_engine:
                await self.voice_engine.speak(error_message)
            
            if self.ui_manager:
                await self.ui_manager.add_message("assistant", error_message)
                await self.ui_manager.update_status("error")
    
    async def _execute_actions(self, actions: list):
        """Execute a list of actions."""
        for action in actions:
            try:
                if self.feature_manager:
                    await self.feature_manager.execute_action(action)
                    
                # Check if action is for a plugin
                if self.plugin_manager and action.get('type') == 'plugin':
                    plugin_name = action.get('plugin_name')
                    method_name = action.get('method')
                    args = action.get('args', [])
                    kwargs = action.get('kwargs', {})
                    
                    if plugin_name and method_name:
                        await self.plugin_manager.call_plugin_method(
                            plugin_name, method_name, *args, **kwargs
                        )
            except Exception as e:
                self.logger.error(f"Error executing action {action}: {e}")
    
    async def _on_settings_changed(self, settings: Dict[str, Any]):
        """Handle settings changes from UI."""
        self.logger.info("⚙️ Settings updated")
        
        # Update settings
        for key, value in settings.items():
            if hasattr(self.settings, key):
                setattr(self.settings, key, value)
        
        # Notify components of settings changes
        if self.voice_engine:
            await self.voice_engine.update_settings(self.settings)
        
        if self.ai_engine:
            await self.ai_engine.update_settings(self.settings)
    
    def toggle_listening(self):
        """Toggle voice listening on/off."""
        if self.voice_engine:
            if self.is_listening:
                self.voice_engine.stop_listening()
                self.is_listening = False
            else:
                asyncio.create_task(self.voice_engine.start_listening())
                self.is_listening = True
    
    def show_ui(self):
        """Show the main UI window."""
        if self.ui_manager:
            self.ui_manager.show_window()
    
    def hide_ui(self):
        """Hide the main UI window."""
        if self.ui_manager:
            self.ui_manager.hide_window()
    
    async def shutdown(self):
        """Gracefully shutdown the application."""
        self.logger.info("🛑 Shutting down Jenna...")
        self._shutdown_event.set()
    
    async def cleanup(self):
        """Cleanup all resources."""
        try:
            self.logger.info("🧹 Cleaning up resources...")
            
            # Cleanup components in reverse order
            if self.system_tray:
                self.system_tray.cleanup()
            
            if self.ui_manager:
                await self.ui_manager.cleanup()
            
            if self.plugin_manager:
                await self.plugin_manager.cleanup()
            
            if self.feature_manager:
                await self.feature_manager.cleanup()
            
            if self.voice_engine:
                await self.voice_engine.cleanup()
            
            if self.ai_engine:
                await self.ai_engine.cleanup()
            
            if self.service_manager:
                await self.service_manager.cleanup()
            
            self.logger.info("✅ Cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")