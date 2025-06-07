import { useState, useEffect, useRef, useCallback } from 'react'
import { createConversationStream, GrpcError, NetworkError } from '@utils/grpcApi'
import type { ConnectionStatus } from '@types/index'

interface UseGrpcStreamOptions {
  enabled?: boolean
  onMessage?: (data: any) => void
  onConnect?: () => void
  onDisconnect?: () => void
  onError?: (error: GrpcError | NetworkError) => void
}

interface UseGrpcStreamReturn {
  isConnected: boolean
  connectionState: ConnectionStatus
  lastMessage: any
  sendMessage: (message: any) => void
  reconnect: () => void
}

export function useGrpcStream(options: UseGrpcStreamOptions = {}): UseGrpcStreamReturn {
  const {
    enabled = true,
    onMessage,
    onConnect,
    onDisconnect,
    onError
  } = options

  const [isConnected, setIsConnected] = useState(false)
  const [connectionState, setConnectionState] = useState<ConnectionStatus>('disconnected')
  const [lastMessage, setLastMessage] = useState<any>(null)
  const [error, setError] = useState<GrpcError | NetworkError | null>(null)
  
  const streamRef = useRef<ReturnType<typeof createConversationStream> | null>(null)
  const callbacksRef = useRef({ onMessage, onConnect, onDisconnect, onError })
  
  // Update callbacks ref when they change
  useEffect(() => {
    callbacksRef.current = { onMessage, onConnect, onDisconnect, onError }
  }, [onMessage, onConnect, onDisconnect, onError])

  // Initialize gRPC stream
  const initStream = useCallback(() => {
    if (!enabled) {
      return
    }
    
    try {
      setConnectionState('connecting')
      
      // Create bidirectional stream
      const stream = createConversationStream(
        (message) => {
          setLastMessage(message)
          callbacksRef.current.onMessage?.(message)
        },
        (error) => {
          console.error('gRPC stream error:', error)
          setIsConnected(false)
          setConnectionState('error')
          setError(error as GrpcError | NetworkError)
          callbacksRef.current.onError?.(error as GrpcError | NetworkError)
        },
        () => {
          // Stream ended
          setIsConnected(false)
          setConnectionState('disconnected')
          callbacksRef.current.onDisconnect?.()
        }
      )
      
      streamRef.current = stream
      
      // Mark as connected
      setIsConnected(true)
      setConnectionState('connected')
      setError(null)
      callbacksRef.current.onConnect?.()
      
      return stream
    } catch (err) {
      console.error('Failed to initialize gRPC stream:', err)
      setIsConnected(false)
      setConnectionState('error')
      setError(err as GrpcError | NetworkError)
      callbacksRef.current.onError?.(err as GrpcError | NetworkError)
      return null
    }
  }, [enabled])
  
  // Initialize on mount
  useEffect(() => {
    const stream = initStream()
    
    // Cleanup function
    return () => {
      if (streamRef.current) {
        try {
          streamRef.current.close()
          streamRef.current = null
        } catch (err) {
          console.error('Error closing gRPC stream:', err)
        }
      }
    }
  }, [initStream])
  
  // Send message function
  const sendMessage = useCallback((message: any) => {
    if (!streamRef.current || !isConnected) {
      console.error('Cannot send message: gRPC stream not connected')
      return false
    }
    
    try {
      // Determine message type and send accordingly
      if (typeof message === 'string') {
        // Text message
        streamRef.current.sendMessage(message)
      } else if (message instanceof Uint8Array || message instanceof ArrayBuffer) {
        // Convert ArrayBuffer to Uint8Array if needed
        const audioData = message instanceof ArrayBuffer 
          ? new Uint8Array(message) 
          : message
        
        // Audio data
        streamRef.current.sendAudio(audioData)
      } else {
        // JSON message
        streamRef.current.sendMessage(message)
      }
      return true
    } catch (err) {
      console.error('Error sending message via gRPC:', err)
      setError(err as GrpcError | NetworkError)
      callbacksRef.current.onError?.(err as GrpcError | NetworkError)
      return false
    }
  }, [isConnected])
  
  // Reconnect function
  const reconnect = useCallback(() => {
    if (streamRef.current) {
      try {
        streamRef.current.close()
      } catch (err) {
        console.error('Error closing existing gRPC stream:', err)
      }
      streamRef.current = null
    }
    
    // Initialize new stream
    initStream()
  }, [initStream])
  
  return {
    isConnected,
    connectionState,
    lastMessage,
    sendMessage,
    reconnect
  }
}

export default useGrpcStream