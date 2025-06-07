import asyncio
import threading
import uvicorn
import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

# Import core components
from backend.core.ai_engine import AIEngine
from backend.core.config import Settings
from backend.utils.logger import setup_logger

# Import gRPC server
from backend.grpc_server import run_server

# Import API routers
from backend.api.routes.voice import router as voice_router
from backend.api.routes.chat import router as chat_router
from backend.api.routes.settings import router as settings_router
from backend.api.routes.system import router as system_router

# Setup logging
logger = setup_logger('server')

# Initialize settings and AI engine
settings = Settings()
ai_engine = AIEngine(settings)

# Create FastAPI app
app = FastAPI(
    title="Jenna Voice Assistant API",
    description="Backend API for Jenna Voice Assistant",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(voice_router, prefix="/api/voice", tags=["voice"])
app.include_router(chat_router, prefix="/api/chat", tags=["chat"])
app.include_router(settings_router, prefix="/api/settings", tags=["settings"])
app.include_router(system_router, prefix="/api/system", tags=["system"])

# Active WebSocket connections
active_connections = []

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    
    try:
        while True:
            data = await websocket.receive_json()
            
            # Process the message with AI engine
            if "content" in data:
                response = ai_engine.process_command(data["content"])
                
                # Send response back to client
                await websocket.send_json({
                    "type": "response",
                    "content": response,
                    "id": data.get("id", "")
                })
    except WebSocketDisconnect:
        active_connections.remove(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        if websocket in active_connections:
            active_connections.remove(websocket)

# Serve static files (frontend)
frontend_dir = Path(__file__).parent.parent / "frontend" / "dist"
if frontend_dir.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")

# Start gRPC server in a separate thread
def start_grpc_server():
    grpc_thread = threading.Thread(target=run_server, args=(settings, ai_engine))
    grpc_thread.daemon = True
    grpc_thread.start()
    logger.info("gRPC server started in background thread")

# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Starting Jenna Voice Assistant server")
    
    # Start gRPC server
    start_grpc_server()

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("⏹️ Shutting down Jenna Voice Assistant server")
    
    # Clean up AI engine resources
    ai_engine.cleanup()

# Run the server
def run_server():
    uvicorn.run(
        "backend.server:app",
        host="0.0.0.0",
        port=settings.api_port,
        reload=settings.development_mode,
        log_level="info"
    )

if __name__ == "__main__":
    run_server()