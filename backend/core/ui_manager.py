"""UI Manager for Web-based Frontend Interface"""

import asyncio
import json
import webbrowser
from pathlib import Path
from typing import Optional, Callable, Dict, Any, List
from datetime import datetime

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from .config import Settings
from .logger import get_logger
from ..utils.exceptions import UIManagerException


class WebSocketManager:
    """Manages WebSocket connections for real-time communication."""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.logger = get_logger(__name__)
    
    async def connect(self, websocket: WebSocket):
        """Accept a new WebSocket connection."""
        await websocket.accept()
        self.active_connections.append(websocket)
        self.logger.info(f"🔌 WebSocket connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            self.logger.info(f"🔌 WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send a message to a specific WebSocket connection."""
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            self.logger.error(f"Error sending personal message: {e}")
    
    async def broadcast(self, message: dict):
        """Broadcast a message to all connected clients."""
        if not self.active_connections:
            return
        
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except Exception as e:
                self.logger.warning(f"Failed to send message to connection: {e}")
                disconnected.append(connection)
        
        # Remove disconnected connections
        for connection in disconnected:
            self.disconnect(connection)


class UIManager:
    """Manages the web-based user interface."""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = get_logger(__name__)
        
        # FastAPI app
        self.app = FastAPI(
            title="Jenna Voice Assistant",
            description="Commercial-grade desktop voice assistant",
            version="1.0.0"
        )
        
        # WebSocket manager
        self.websocket_manager = WebSocketManager()
        
        # UI state
        self.current_status = "idle"
        self.conversation_history = []
        self.system_stats = {}
        
        # Event callbacks
        self.on_command_received: Optional[Callable] = None
        self.on_settings_changed: Optional[Callable] = None
        
        # Server configuration
        self.host = "127.0.0.1"
        self.port = 8080
        self.server = None
        
        # Setup routes
        self._setup_routes()
        self._setup_middleware()
    
    def _setup_middleware(self):
        """Setup FastAPI middleware."""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    def _setup_routes(self):
        """Setup FastAPI routes."""
        
        @self.app.get("/", response_class=HTMLResponse)
        async def read_root():
            """Serve the main UI page."""
            frontend_path = Path(__file__).parent.parent.parent / "frontend" / "dist" / "index.html"
            if frontend_path.exists():
                return FileResponse(frontend_path)
            else:
                return HTMLResponse(
                    content=self._get_fallback_html(),
                    status_code=200
                )
        
        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            """WebSocket endpoint for real-time communication."""
            await self.websocket_manager.connect(websocket)
            
            # Send initial state
            await self.websocket_manager.send_personal_message({
                "type": "status_update",
                "status": self.current_status,
                "conversation": self.conversation_history[-10:],  # Last 10 messages
                "stats": self.system_stats
            }, websocket)
            
            try:
                while True:
                    data = await websocket.receive_text()
                    message = json.loads(data)
                    await self._handle_websocket_message(message, websocket)
            except WebSocketDisconnect:
                self.websocket_manager.disconnect(websocket)
            except Exception as e:
                self.logger.error(f"WebSocket error: {e}")
                self.websocket_manager.disconnect(websocket)
        
        @self.app.get("/api/status")
        async def get_status():
            """Get current system status."""
            return {
                "status": self.current_status,
                "conversation_count": len(self.conversation_history),
                "stats": self.system_stats,
                "timestamp": datetime.now().isoformat()
            }
        
        @self.app.post("/api/command")
        async def send_command(command_data: dict):
            """Send a text command to the assistant."""
            try:
                command = command_data.get("command", "")
                if not command:
                    raise HTTPException(status_code=400, detail="Command is required")
                
                # Process command
                if self.on_command_received:
                    await self.on_command_received(command)
                
                return {"status": "success", "message": "Command received"}
                
            except Exception as e:
                self.logger.error(f"Error processing command: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/settings")
        async def get_settings():
            """Get current settings."""
            return {
                "wake_phrase": self.settings.wake_phrase,
                "voice_gender": self.settings.voice_gender,
                "speech_rate": self.settings.speech_rate,
                "volume": self.settings.volume,
                "ui_theme": self.settings.ui_theme,
                "ui_accent_color": self.settings.ui_accent_color,
                "features": {
                    "pomodoro": self.settings.feature_pomodoro,
                    "flashcards": self.settings.feature_flashcards,
                    "weather": self.settings.feature_weather,
                    "email": self.settings.feature_email,
                    "file_operations": self.settings.feature_file_operations,
                    "app_launcher": self.settings.feature_app_launcher,
                    "music_control": self.settings.feature_music_control,
                    "screen_analysis": self.settings.feature_screen_analysis,
                    "mood_detection": self.settings.feature_mood_detection,
                    "backup": self.settings.feature_backup
                }
            }
        
        @self.app.post("/api/settings")
        async def update_settings(settings_data: dict):
            """Update settings."""
            try:
                if self.on_settings_changed:
                    await self.on_settings_changed(settings_data)
                
                return {"status": "success", "message": "Settings updated"}
                
            except Exception as e:
                self.logger.error(f"Error updating settings: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/conversation")
        async def get_conversation():
            """Get conversation history."""
            return {
                "conversation": self.conversation_history,
                "total_messages": len(self.conversation_history)
            }
        
        @self.app.delete("/api/conversation")
        async def clear_conversation():
            """Clear conversation history."""
            self.conversation_history.clear()
            
            # Notify connected clients
            await self.websocket_manager.broadcast({
                "type": "conversation_cleared"
            })
            
            return {"status": "success", "message": "Conversation cleared"}
        
        # Serve static files
        frontend_static = Path(__file__).parent.parent.parent / "frontend" / "dist"
        if frontend_static.exists():
            self.app.mount("/static", StaticFiles(directory=str(frontend_static)), name="static")
    
    async def _handle_websocket_message(self, message: dict, websocket: WebSocket):
        """Handle incoming WebSocket messages."""
        try:
            message_type = message.get("type")
            
            if message_type == "command":
                command = message.get("data", "")
                if command and self.on_command_received:
                    await self.on_command_received(command)
            
            elif message_type == "settings_update":
                settings_data = message.get("data", {})
                if self.on_settings_changed:
                    await self.on_settings_changed(settings_data)
            
            elif message_type == "ping":
                await self.websocket_manager.send_personal_message({
                    "type": "pong",
                    "timestamp": datetime.now().isoformat()
                }, websocket)
            
            else:
                self.logger.warning(f"Unknown WebSocket message type: {message_type}")
        
        except Exception as e:
            self.logger.error(f"Error handling WebSocket message: {e}")
    
    def _get_fallback_html(self) -> str:
        """Get fallback HTML when frontend build is not available."""
        return """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Jenna Voice Assistant</title>
            <style>
                body {
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                    color: white;
                    margin: 0;
                    padding: 0;
                    min-height: 100vh;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }
                .container {
                    text-align: center;
                    max-width: 600px;
                    padding: 2rem;
                }
                .logo {
                    font-size: 3rem;
                    margin-bottom: 1rem;
                    animation: pulse 2s infinite;
                }
                @keyframes pulse {
                    0% { transform: scale(1); }
                    50% { transform: scale(1.05); }
                    100% { transform: scale(1); }
                }
                .status {
                    background: rgba(255, 255, 255, 0.1);
                    padding: 1rem;
                    border-radius: 10px;
                    margin: 1rem 0;
                }
                .command-input {
                    width: 100%;
                    padding: 1rem;
                    border: none;
                    border-radius: 25px;
                    font-size: 1rem;
                    margin: 1rem 0;
                    background: rgba(255, 255, 255, 0.9);
                    color: #333;
                }
                .send-btn {
                    background: #00ff88;
                    color: #333;
                    border: none;
                    padding: 1rem 2rem;
                    border-radius: 25px;
                    font-size: 1rem;
                    cursor: pointer;
                    transition: all 0.3s ease;
                }
                .send-btn:hover {
                    background: #00cc6a;
                    transform: translateY(-2px);
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="logo">🤖</div>
                <h1>Jenna Voice Assistant</h1>
                <p>Your intelligent desktop companion is ready!</p>
                
                <div class="status">
                    <h3>Status: <span id="status">Ready</span></h3>
                    <p>Say "Jenna Ready" to activate voice commands</p>
                </div>
                
                <div>
                    <input type="text" id="commandInput" class="command-input" 
                           placeholder="Type a command here..." 
                           onkeypress="handleKeyPress(event)">
                    <br>
                    <button class="send-btn" onclick="sendCommand()">Send Command</button>
                </div>
                
                <div id="response" style="margin-top: 2rem; padding: 1rem; background: rgba(255,255,255,0.1); border-radius: 10px; display: none;"></div>
            </div>
            
            <script>
                function handleKeyPress(event) {
                    if (event.key === 'Enter') {
                        sendCommand();
                    }
                }
                
                async function sendCommand() {
                    const input = document.getElementById('commandInput');
                    const command = input.value.trim();
                    
                    if (!command) return;
                    
                    try {
                        const response = await fetch('/api/command', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify({ command: command })
                        });
                        
                        const result = await response.json();
                        
                        const responseDiv = document.getElementById('response');
                        responseDiv.style.display = 'block';
                        responseDiv.innerHTML = `<strong>Command sent:</strong> ${command}<br><strong>Status:</strong> ${result.status}`;
                        
                        input.value = '';
                    } catch (error) {
                        console.error('Error sending command:', error);
                        alert('Error sending command. Please try again.');
                    }
                }
                
                // Auto-focus on input
                document.getElementById('commandInput').focus();
            </script>
        </body>
        </html>
        """
    
    async def initialize(self):
        """Initialize UI manager."""
        try:
            self.logger.info("🖥️ Initializing UI manager...")
            
            # Check if frontend build exists
            frontend_path = Path(__file__).parent.parent.parent / "frontend" / "dist"
            if frontend_path.exists():
                self.logger.info("✅ Frontend build found")
            else:
                self.logger.warning("⚠️ Frontend build not found, using fallback UI")
            
            self.logger.info("✅ UI manager initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize UI manager: {e}")
            raise UIManagerException(f"UI manager initialization failed: {e}")
    
    async def start_server(self):
        """Start the web server."""
        try:
            self.logger.info(f"🌐 Starting web server on http://{self.host}:{self.port}")
            
            config = uvicorn.Config(
                app=self.app,
                host=self.host,
                port=self.port,
                log_level="warning" if not self.settings.debug else "info",
                access_log=self.settings.debug
            )
            
            self.server = uvicorn.Server(config)
            await self.server.serve()
            
        except Exception as e:
            self.logger.error(f"Failed to start web server: {e}")
            raise UIManagerException(f"Web server startup failed: {e}")
    
    async def update_status(self, status: str):
        """Update the current status and notify clients."""
        self.current_status = status
        
        await self.websocket_manager.broadcast({
            "type": "status_update",
            "status": status,
            "timestamp": datetime.now().isoformat()
        })
    
    async def add_message(self, sender: str, message: str):
        """Add a message to the conversation history."""
        conversation_message = {
            "id": len(self.conversation_history) + 1,
            "sender": sender,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        
        self.conversation_history.append(conversation_message)
        
        # Limit conversation history
        if len(self.conversation_history) > self.settings.max_conversation_history:
            self.conversation_history = self.conversation_history[-self.settings.max_conversation_history:]
        
        # Notify clients
        await self.websocket_manager.broadcast({
            "type": "new_message",
            "message": conversation_message
        })
    
    async def update_stats(self, stats: Dict[str, Any]):
        """Update system statistics."""
        self.system_stats.update(stats)
        
        await self.websocket_manager.broadcast({
            "type": "stats_update",
            "stats": self.system_stats
        })
    
    def show_window(self):
        """Show the UI window (open in browser)."""
        try:
            url = f"http://{self.host}:{self.port}"
            webbrowser.open(url)
            self.logger.info(f"🌐 Opening UI in browser: {url}")
        except Exception as e:
            self.logger.error(f"Failed to open browser: {e}")
    
    def hide_window(self):
        """Hide the UI window (browser-based, so just log)."""
        self.logger.info("🙈 UI window hide requested (browser-based)")
    
    def get_url(self) -> str:
        """Get the UI URL."""
        return f"http://{self.host}:{self.port}"
    
    async def cleanup(self):
        """Cleanup UI manager resources."""
        try:
            self.logger.info("🧹 Cleaning up UI manager...")
            
            # Close all WebSocket connections
            for connection in self.websocket_manager.active_connections.copy():
                try:
                    await connection.close()
                except:
                    pass
            
            # Stop server
            if self.server:
                self.server.should_exit = True
            
            self.logger.info("✅ UI manager cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during UI manager cleanup: {e}")