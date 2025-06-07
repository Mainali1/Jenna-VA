import asyncio
import grpc
import logging
import time
import uuid
from concurrent import futures
from datetime import datetime
from typing import Dict, List, Iterator, AsyncIterator

# Import generated protobuf code
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from proto import jenna_pb2
from proto import jenna_pb2_grpc

# Import core components
from backend.core.ai_engine import AIEngine
from backend.core.config import Settings
from backend.utils.logger import setup_logger

# Setup logging
logger = setup_logger('grpc_server')

# Active client connections
active_clients: Dict[str, List[asyncio.Queue]] = {}

class JennaServiceServicer(jenna_pb2_grpc.JennaServiceServicer):
    """Implementation of JennaService service."""

    def __init__(self, settings: Settings, ai_engine: AIEngine):
        self.settings = settings
        self.ai_engine = ai_engine
        self.client_streams = {}
        logger.info("🚀 JennaServiceServicer initialized")

    async def StreamConversation(self, request_iterator, context):
        """Implements the bidirectional streaming RPC method."""
        client_id = str(uuid.uuid4())
        logger.info(f"🔌 New client connected: {client_id}")
        
        # Create a queue for this client
        queue = asyncio.Queue()
        
        # Store the client's queue
        if 'global' not in active_clients:
            active_clients['global'] = []
        active_clients['global'].append(queue)
        
        # Store client-specific stream
        self.client_streams[client_id] = queue
        
        # Send welcome message
        welcome_response = jenna_pb2.StreamResponse(
            type="system",
            content="Welcome to Jenna Voice Assistant! I'm ready to help you.",
            timestamp=datetime.now().isoformat(),
            id=f"welcome_{int(time.time())}"
        )
        await queue.put(welcome_response)
        
        # Start the consumer task to process incoming messages
        consumer_task = asyncio.create_task(self._consume_messages(request_iterator, client_id, context))
        
        try:
            # Yield messages from the queue
            while True:
                if context.cancelled():
                    break
                    
                response = await queue.get()
                yield response
                queue.task_done()
        except asyncio.CancelledError:
            logger.info(f"🔌 Client stream cancelled: {client_id}")
        except Exception as e:
            logger.error(f"❌ Error in StreamConversation: {e}")
        finally:
            # Clean up
            consumer_task.cancel()
            try:
                await consumer_task
            except asyncio.CancelledError:
                pass
            
            # Remove client queue
            if 'global' in active_clients and queue in active_clients['global']:
                active_clients['global'].remove(queue)
            
            # Remove client stream
            if client_id in self.client_streams:
                del self.client_streams[client_id]
                
            logger.info(f"🔌 Client disconnected: {client_id}")

    async def _consume_messages(self, request_iterator, client_id, context):
        """Consumes messages from the client stream."""
        try:
            async for request in self._aiter(request_iterator):
                # Handle different message types
                if request.type == "ping":
                    # Respond to ping with pong
                    pong_response = jenna_pb2.StreamResponse(
                        type="pong",
                        timestamp=datetime.now().isoformat(),
                        id=f"pong_{request.id}"
                    )
                    await self.client_streams[client_id].put(pong_response)
                
                elif request.type == "text":
                    # Process text message with AI engine
                    logger.info(f"📝 Received text message from {client_id}: {request.content[:50]}...")
                    
                    # Acknowledge receipt
                    ack_response = jenna_pb2.StreamResponse(
                        type="ack",
                        content="Message received, processing...",
                        timestamp=datetime.now().isoformat(),
                        id=f"ack_{request.id}"
                    )
                    await self.client_streams[client_id].put(ack_response)
                    
                    # Process with AI engine (non-blocking)
                    asyncio.create_task(self._process_ai_request(client_id, request))
                
                elif request.type == "audio":
                    # Process audio message
                    logger.info(f"🎤 Received audio message from {client_id}")
                    
                    # Acknowledge receipt
                    ack_response = jenna_pb2.StreamResponse(
                        type="ack",
                        content="Audio received, processing...",
                        timestamp=datetime.now().isoformat(),
                        id=f"ack_{request.id}"
                    )
                    await self.client_streams[client_id].put(ack_response)
                    
                    # Process with speech recognition (non-blocking)
                    asyncio.create_task(self._process_audio_request(client_id, request))
                
                elif request.type == "disconnect":
                    logger.info(f"🔌 Client requested disconnect: {client_id}")
                    break
                
                else:
                    logger.warning(f"⚠️ Unknown message type from {client_id}: {request.type}")
        
        except asyncio.CancelledError:
            logger.info(f"🔌 Message consumer cancelled for {client_id}")
        except Exception as e:
            logger.error(f"❌ Error consuming messages for {client_id}: {e}")

    async def _process_ai_request(self, client_id, request):
        """Process a text request with the AI engine."""
        try:
            # Get AI response
            response_text = await asyncio.to_thread(
                self.ai_engine.process_command,
                request.content
            )
            
            # Send response back to client
            ai_response = jenna_pb2.StreamResponse(
                type="ai_response",
                content=response_text,
                timestamp=datetime.now().isoformat(),
                id=f"resp_{request.id}"
            )
            
            if client_id in self.client_streams:
                await self.client_streams[client_id].put(ai_response)
            
            # Also send as speech if TTS is enabled
            if self.settings.tts_enabled:
                # This would be handled by sending a separate audio response
                # with the synthesized speech
                pass
                
        except Exception as e:
            logger.error(f"❌ Error processing AI request: {e}")
            
            # Send error response
            error_response = jenna_pb2.StreamResponse(
                type="error",
                content=f"Sorry, I encountered an error: {str(e)}",
                timestamp=datetime.now().isoformat(),
                id=f"error_{request.id}"
            )
            
            if client_id in self.client_streams:
                await self.client_streams[client_id].put(error_response)

    async def _process_audio_request(self, client_id, request):
        """Process an audio request with speech recognition."""
        try:
            # Here we would process the audio with speech recognition
            # For now, just send a placeholder response
            processing_response = jenna_pb2.StreamResponse(
                type="processing",
                content="Processing audio...",
                timestamp=datetime.now().isoformat(),
                id=f"proc_{request.id}"
            )
            
            if client_id in self.client_streams:
                await self.client_streams[client_id].put(processing_response)
            
            # Simulate processing time
            await asyncio.sleep(1)
            
            # Send a placeholder result
            result_response = jenna_pb2.StreamResponse(
                type="recognition_result",
                content="I heard you say something",  # This would be the actual recognized text
                timestamp=datetime.now().isoformat(),
                id=f"recog_{request.id}"
            )
            
            if client_id in self.client_streams:
                await self.client_streams[client_id].put(result_response)
                
        except Exception as e:
            logger.error(f"❌ Error processing audio request: {e}")
            
            # Send error response
            error_response = jenna_pb2.StreamResponse(
                type="error",
                content=f"Sorry, I couldn't process your audio: {str(e)}",
                timestamp=datetime.now().isoformat(),
                id=f"error_{request.id}"
            )
            
            if client_id in self.client_streams:
                await self.client_streams[client_id].put(error_response)

    async def ExecuteCommand(self, request, context):
        """Implements the unary RPC method for command execution."""
        logger.info(f"⚡ Executing command: {request.command}")
        
        try:
            # Process command with AI engine
            result = await asyncio.to_thread(
                self.ai_engine.process_command,
                request.command
            )
            
            # Create response
            response = jenna_pb2.CommandResponse(
                success=True,
                message=result,
                id=request.id
            )
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Error executing command: {e}")
            return jenna_pb2.CommandResponse(
                success=False,
                message=f"Error: {str(e)}",
                id=request.id
            )

    async def StartOperation(self, request, context):
        """Implements the server streaming RPC method for long-running operations."""
        logger.info(f"🔄 Starting operation: {request.operation_type}")
        
        try:
            # Example implementation for a long-running operation
            for i in range(10):
                if context.cancelled():
                    break
                    
                # Simulate work
                await asyncio.sleep(0.5)
                
                # Send progress update
                progress = (i + 1) / 10
                yield jenna_pb2.OperationResponse(
                    status="running" if progress < 1 else "completed",
                    progress=progress,
                    message=f"Operation at {int(progress * 100)}%",
                    id=request.id
                )
                
        except Exception as e:
            logger.error(f"❌ Error in operation: {e}")
            yield jenna_pb2.OperationResponse(
                status="failed",
                progress=0,
                message=f"Operation failed: {str(e)}",
                id=request.id
            )

    async def UploadData(self, request_iterator, context):
        """Implements the client streaming RPC method for data upload."""
        logger.info("📤 Starting data upload")
        
        upload_id = None
        file_name = None
        content_type = None
        total_chunks = 0
        received_chunks = 0
        chunks_data = {}
        
        try:
            async for chunk in self._aiter(request_iterator):
                if upload_id is None:
                    upload_id = chunk.id
                    file_name = chunk.file_name
                    content_type = chunk.content_type
                    total_chunks = chunk.total_chunks
                    logger.info(f"📤 Upload started: {file_name} ({content_type}), {total_chunks} chunks")
                
                # Store chunk data
                chunks_data[chunk.chunk_index] = chunk.data
                received_chunks += 1
                
                logger.debug(f"📤 Received chunk {chunk.chunk_index}/{total_chunks} for {upload_id}")
            
            # Check if all chunks were received
            if received_chunks != total_chunks:
                raise ValueError(f"Expected {total_chunks} chunks but received {received_chunks}")
            
            # Combine chunks
            combined_data = b''.join([chunks_data[i] for i in range(total_chunks)])
            
            # Save file (example implementation)
            file_path = os.path.join("uploads", file_name)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, "wb") as f:
                f.write(combined_data)
            
            logger.info(f"📤 Upload completed: {file_path}, {len(combined_data)} bytes")
            
            # Return success response
            return jenna_pb2.UploadResponse(
                success=True,
                message="Upload successful",
                id=upload_id,
                file_path=file_path,
                file_size=len(combined_data)
            )
            
        except Exception as e:
            logger.error(f"❌ Error in upload: {e}")
            return jenna_pb2.UploadResponse(
                success=False,
                message=f"Upload failed: {str(e)}",
                id=upload_id or ""
            )

    @staticmethod
    async def _aiter(iterator):
        """Convert a synchronous iterator to an async iterator."""
        for item in iterator:
            yield item


async def broadcast_message(message_type: str, content: str, metadata: Dict = None):
    """Broadcast a message to all connected clients."""
    if 'global' not in active_clients:
        return
    
    response = jenna_pb2.StreamResponse(
        type=message_type,
        content=content,
        timestamp=datetime.now().isoformat(),
        id=f"broadcast_{int(time.time())}"
    )
    
    if metadata:
        for key, value in metadata.items():
            response.metadata[key] = value
    
    for queue in active_clients['global']:
        await queue.put(response)


async def serve(settings: Settings, ai_engine: AIEngine):
    """Start the gRPC server."""
    server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=10))
    jenna_pb2_grpc.add_JennaServiceServicer_to_server(
        JennaServiceServicer(settings, ai_engine), server
    )
    
    # Get server address from settings
    server_address = f"0.0.0.0:{settings.grpc_port}"
    server.add_insecure_port(server_address)
    
    logger.info(f"🚀 Starting gRPC server on {server_address}")
    await server.start()
    
    try:
        await server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("⏹️ Stopping gRPC server")
        await server.stop(0)


def run_server(settings: Settings, ai_engine: AIEngine):
    """Run the gRPC server in a separate thread."""
    asyncio.run(serve(settings, ai_engine))


if __name__ == "__main__":
    # For testing/standalone operation
    from backend.core.ai_engine import AIEngine
    from backend.core.config import Settings
    
    settings = Settings()
    ai_engine = AIEngine(settings)
    
    run_server(settings, ai_engine)