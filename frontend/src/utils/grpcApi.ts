import { JennaServiceClient } from '@proto/jenna_grpc_web_pb';
import { StreamRequest, StreamResponse, CommandRequest, CommandResponse } from '@proto/jenna_pb';
import { grpc } from '@grpc/grpc-js';

// API Configuration
const GRPC_BASE_URL = import.meta.env.VITE_GRPC_BASE_URL || 'http://localhost:8080';

// Error classes
export class GrpcError extends Error {
  constructor(
    message: string,
    public code?: grpc.Code,
    public details?: any
  ) {
    super(message);
    this.name = 'GrpcError';
  }
}

export class NetworkError extends Error {
  constructor(message: string, public originalError?: Error) {
    super(message);
    this.name = 'NetworkError';
  }
}

// Client singleton
let client: JennaServiceClient | null = null;

/**
 * Get or create the gRPC client
 */
export function getClient(): JennaServiceClient {
  if (!client) {
    client = new JennaServiceClient(GRPC_BASE_URL);
  }
  return client;
}

/**
 * Reset the client (useful for changing endpoints)
 */
export function resetClient(): void {
  client = null;
}

/**
 * Execute a command using unary RPC
 */
export async function executeCommand(command: string, params: Record<string, string> = {}): Promise<string> {
  const client = getClient();
  const request = new CommandRequest();
  
  request.setCommand(command);
  request.setId(`cmd_${Date.now()}`);
  
  // Add parameters
  const paramsMap = request.getParamsMap();
  Object.entries(params).forEach(([key, value]) => {
    paramsMap.set(key, value);
  });
  
  return new Promise((resolve, reject) => {
    client.executeCommand(request, null, (err, response) => {
      if (err) {
        reject(new GrpcError(err.message, err.code, err.details));
        return;
      }
      
      if (!response) {
        reject(new Error('Empty response received'));
        return;
      }
      
      if (!response.getSuccess()) {
        reject(new Error(response.getMessage()));
        return;
      }
      
      resolve(response.getMessage());
    });
  });
}

/**
 * Start a long-running operation with server streaming
 */
export function startOperation(
  operationType: string, 
  params: Record<string, string> = {}, 
  onProgress: (progress: number, message: string) => void,
  onComplete: (data: Uint8Array | null) => void,
  onError: (error: Error) => void
): () => void {
  const client = getClient();
  const request = new CommandRequest();
  
  request.setCommand(operationType);
  request.setId(`op_${Date.now()}`);
  
  // Add parameters
  const paramsMap = request.getParamsMap();
  Object.entries(params).forEach(([key, value]) => {
    paramsMap.set(key, value);
  });
  
  const stream = client.startOperation(request);
  
  stream.on('data', (response) => {
    const status = response.getStatus();
    const progress = response.getProgress();
    const message = response.getMessage();
    
    if (status === 'completed') {
      onComplete(response.getData_asU8());
    } else {
      onProgress(progress, message);
    }
  });
  
  stream.on('error', (error) => {
    onError(new GrpcError(error.message, error.code, error.details));
  });
  
  stream.on('end', () => {
    // Stream ended without completion
    onComplete(null);
  });
  
  // Return cancel function
  return () => {
    stream.cancel();
  };
}

/**
 * Upload data using client streaming
 */
export async function uploadData(
  data: Uint8Array,
  fileName: string,
  contentType: string,
  onProgress?: (chunkIndex: number, totalChunks: number) => void
): Promise<string> {
  const client = getClient();
  const uploadId = `upload_${Date.now()}`;
  
  // Split data into chunks (1MB chunks)
  const chunkSize = 1024 * 1024;
  const totalChunks = Math.ceil(data.length / chunkSize);
  
  return new Promise((resolve, reject) => {
    const stream = client.uploadData((err, response) => {
      if (err) {
        reject(new GrpcError(err.message, err.code, err.details));
        return;
      }
      
      if (!response) {
        reject(new Error('Empty response received'));
        return;
      }
      
      if (!response.getSuccess()) {
        reject(new Error(response.getMessage()));
        return;
      }
      
      resolve(response.getFilePath());
    });
    
    // Send chunks
    for (let i = 0; i < totalChunks; i++) {
      const start = i * chunkSize;
      const end = Math.min(start + chunkSize, data.length);
      const chunkData = data.slice(start, end);
      
      const chunk = new DataChunk();
      chunk.setId(uploadId);
      chunk.setData(chunkData);
      chunk.setChunkIndex(i);
      chunk.setTotalChunks(totalChunks);
      chunk.setFileName(fileName);
      chunk.setContentType(contentType);
      
      stream.write(chunk);
      
      if (onProgress) {
        onProgress(i + 1, totalChunks);
      }
    }
    
    stream.end();
  });
}

/**
 * Create a bidirectional stream for real-time conversation
 */
export function createConversationStream(
  onMessage: (message: any) => void,
  onError: (error: Error) => void,
  onEnd: () => void
): {
  stream: grpc.ClientDuplexStream<StreamRequest, StreamResponse>;
  sendMessage: (message: string | object) => void;
  sendAudio: (audioData: Uint8Array) => void;
  close: () => void;
} {
  const client = getClient();
  const stream = client.streamConversation();
  
  stream.on('data', (response) => {
    try {
      // Convert protobuf message to plain object
      const message = {
        type: response.getType(),
        content: response.getContent(),
        timestamp: response.getTimestamp(),
        id: response.getId(),
        metadata: response.getMetadataMap()?.toObject() || {}
      };
      
      onMessage(message);
    } catch (error) {
      console.error('Error parsing gRPC message:', error);
    }
  });
  
  stream.on('error', (error) => {
    onError(new GrpcError(error.message, error.code, error.details));
  });
  
  stream.on('end', () => {
    onEnd();
  });
  
  // Send a text message
  const sendMessage = (message: string | object) => {
    try {
      const request = new StreamRequest();
      
      if (typeof message === 'string') {
        request.setType('text');
        request.setContent(message);
      } else {
        request.setType((message as any).type || 'data');
        request.setContent((message as any).content || '');
        
        if ((message as any).metadata) {
          const metadataMap = request.getMetadataMap();
          Object.entries((message as any).metadata).forEach(([key, value]) => {
            metadataMap.set(key, String(value));
          });
        }
      }
      
      request.setTimestamp(new Date().toISOString());
      request.setId(`msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`);
      
      stream.write(request);
    } catch (error) {
      console.error('Error sending message:', error);
      onError(new Error(`Failed to send message: ${error}`));
    }
  };
  
  // Send audio data
  const sendAudio = (audioData: Uint8Array) => {
    try {
      const request = new StreamRequest();
      request.setType('audio');
      // Convert binary audio data to base64 string
      const base64Audio = btoa(String.fromCharCode(...new Uint8Array(audioData)));
      request.setContent(base64Audio);
      request.setTimestamp(new Date().toISOString());
      request.setId(`audio_${Date.now()}`);
      
      const metadataMap = request.getMetadataMap();
      metadataMap.set('format', 'wav'); // or whatever format you're using
      
      stream.write(request);
    } catch (error) {
      console.error('Error sending audio:', error);
      onError(new Error(`Failed to send audio: ${error}`));
    }
  };
  
  // Close the stream
  const close = () => {
    try {
      // Send disconnect message
      const request = new StreamRequest();
      request.setType('disconnect');
      request.setTimestamp(new Date().toISOString());
      stream.write(request);
      
      // End the stream
      stream.end();
    } catch (error) {
      console.error('Error closing stream:', error);
    }
  };
  
  return {
    stream,
    sendMessage,
    sendAudio,
    close
  };
}

export default {
  getClient,
  resetClient,
  executeCommand,
  startOperation,
  uploadData,
  createConversationStream
};