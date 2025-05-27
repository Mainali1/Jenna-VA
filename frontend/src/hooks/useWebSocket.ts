import { useEffect, useRef, useState, useCallback } from 'react'
import { useAppStore } from '@store/appStore'
import type { WebSocketMessage, WebSocketMessageType, ConnectionStatus } from '@types/index'

interface UseWebSocketOptions {
  url: string
  protocols?: string | string[]
  onOpen?: (event: Event) => void
  onClose?: (event: CloseEvent) => void
  onMessage?: (data: any) => void
  onError?: (event: Event) => void
  onConnect?: () => void
  onDisconnect?: () => void
  shouldReconnect?: boolean
  reconnectAttempts?: number
  reconnectDelay?: number
  heartbeatInterval?: number
}

interface UseWebSocketReturn {
  isConnected: boolean
  connectionState: ConnectionStatus
  lastMessage: any
  sendMessage: (message: any) => void
  sendJsonMessage: (message: WebSocketMessage) => void
  disconnect: () => void
  reconnect: () => void
}

export function useWebSocket(options: UseWebSocketOptions): UseWebSocketReturn {
  const {
    url,
    protocols,
    onOpen,
    onClose,
    onMessage,
    onError,
    onConnect,
    onDisconnect,
    shouldReconnect = true,
    reconnectAttempts = 5,
    reconnectDelay = 3000,
    heartbeatInterval = 30000,
  } = options

  const [isConnected, setIsConnected] = useState(false)
  const [connectionState, setConnectionState] = useState<ConnectionStatus>('disconnected')
  const [lastMessage, setLastMessage] = useState<any>(null)
  const [reconnectCount, setReconnectCount] = useState(0)

  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const heartbeatTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const heartbeatIntervalRef = useRef<NodeJS.Timeout | null>(null)
  const mountedRef = useRef(true)

  const { setConnectionStatus } = useAppStore()

  // Clear all timeouts
  const clearTimeouts = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
      reconnectTimeoutRef.current = null
    }
    if (heartbeatTimeoutRef.current) {
      clearTimeout(heartbeatTimeoutRef.current)
      heartbeatTimeoutRef.current = null
    }
    if (heartbeatIntervalRef.current) {
      clearInterval(heartbeatIntervalRef.current)
      heartbeatIntervalRef.current = null
    }
  }, [])

  // Send heartbeat ping
  const sendHeartbeat = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      const pingMessage: WebSocketMessage = {
        type: 'ping',
        timestamp: new Date().toISOString(),
      }
      wsRef.current.send(JSON.stringify(pingMessage))
      
      // Set timeout for pong response
      heartbeatTimeoutRef.current = setTimeout(() => {
        console.warn('WebSocket heartbeat timeout - connection may be lost')
        if (wsRef.current) {
          wsRef.current.close()
        }
      }, 5000) // 5 second timeout for pong response
    }
  }, [])

  // Start heartbeat
  const startHeartbeat = useCallback(() => {
    if (heartbeatInterval > 0) {
      heartbeatIntervalRef.current = setInterval(sendHeartbeat, heartbeatInterval)
    }
  }, [sendHeartbeat, heartbeatInterval])

  // Stop heartbeat
  const stopHeartbeat = useCallback(() => {
    if (heartbeatIntervalRef.current) {
      clearInterval(heartbeatIntervalRef.current)
      heartbeatIntervalRef.current = null
    }
    if (heartbeatTimeoutRef.current) {
      clearTimeout(heartbeatTimeoutRef.current)
      heartbeatTimeoutRef.current = null
    }
  }, [])

  // Connect to WebSocket
  const connect = useCallback(() => {
    if (!mountedRef.current) return
    
    try {
      setConnectionState('connecting')
      setConnectionStatus('connecting')
      
      console.log(`🔌 Connecting to WebSocket: ${url}`)
      
      const ws = new WebSocket(url, protocols)
      wsRef.current = ws

      ws.onopen = (event) => {
        console.log('✅ WebSocket connected')
        setIsConnected(true)
        setConnectionState('connected')
        setConnectionStatus('connected')
        setReconnectCount(0)
        
        startHeartbeat()
        onOpen?.(event)
        onConnect?.()
      }

      ws.onclose = (event) => {
        console.log('❌ WebSocket disconnected:', event.code, event.reason)
        setIsConnected(false)
        setConnectionState('disconnected')
        setConnectionStatus('disconnected')
        
        stopHeartbeat()
        onClose?.(event)
        onDisconnect?.()

        // Attempt reconnection if enabled and not a normal closure
        if (shouldReconnect && event.code !== 1000 && reconnectCount < reconnectAttempts && mountedRef.current) {
          setConnectionState('reconnecting')
          setConnectionStatus('reconnecting')
          
          const delay = reconnectDelay * Math.pow(1.5, reconnectCount) // Exponential backoff
          console.log(`🔄 Reconnecting in ${delay}ms (attempt ${reconnectCount + 1}/${reconnectAttempts})`)
          
          reconnectTimeoutRef.current = setTimeout(() => {
            setReconnectCount(prev => prev + 1)
            connect()
          }, delay)
        } else if (reconnectCount >= reconnectAttempts) {
          console.error('❌ Max reconnection attempts reached')
          setConnectionState('error')
          setConnectionStatus('error')
        }
      }

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          
          // Handle heartbeat pong
          if (data.type === 'pong') {
            if (heartbeatTimeoutRef.current) {
              clearTimeout(heartbeatTimeoutRef.current)
              heartbeatTimeoutRef.current = null
            }
            return
          }
          
          setLastMessage(data)
          onMessage?.(data)
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error)
          setLastMessage(event.data)
          onMessage?.(event.data)
        }
      }

      ws.onerror = (event) => {
        console.error('❌ WebSocket error:', event)
        setConnectionState('error')
        setConnectionStatus('error')
        onError?.(event)
      }

    } catch (error) {
      console.error('Failed to create WebSocket connection:', error)
      setConnectionState('error')
      setConnectionStatus('error')
    }
  }, [url, protocols, onOpen, onClose, onMessage, onError, onConnect, onDisconnect, shouldReconnect, reconnectAttempts, reconnectDelay, reconnectCount, startHeartbeat, stopHeartbeat, setConnectionStatus])

  // Disconnect from WebSocket
  const disconnect = useCallback(() => {
    console.log('🔌 Disconnecting WebSocket')
    clearTimeouts()
    stopHeartbeat()
    
    if (wsRef.current) {
      wsRef.current.close(1000, 'Manual disconnect')
      wsRef.current = null
    }
    
    setIsConnected(false)
    setConnectionState('disconnected')
    setConnectionStatus('disconnected')
    setReconnectCount(0)
  }, [clearTimeouts, stopHeartbeat, setConnectionStatus])

  // Reconnect to WebSocket
  const reconnect = useCallback(() => {
    console.log('🔄 Manual reconnect requested')
    disconnect()
    setTimeout(connect, 1000)
  }, [disconnect, connect])

  // Send raw message
  const sendMessage = useCallback((message: any) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      const messageStr = typeof message === 'string' ? message : JSON.stringify(message)
      wsRef.current.send(messageStr)
    } else {
      console.warn('Cannot send message: WebSocket is not connected')
    }
  }, [])

  // Send JSON message with proper typing
  const sendJsonMessage = useCallback((message: WebSocketMessage) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      const messageWithTimestamp: WebSocketMessage = {
        ...message,
        timestamp: message.timestamp || new Date().toISOString(),
        id: message.id || `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      }
      wsRef.current.send(JSON.stringify(messageWithTimestamp))
    } else {
      console.warn('Cannot send JSON message: WebSocket is not connected')
    }
  }, [])

  // Initialize connection on mount
  useEffect(() => {
    mountedRef.current = true
    connect()

    return () => {
      mountedRef.current = false
      clearTimeouts()
      stopHeartbeat()
      
      if (wsRef.current) {
        wsRef.current.close(1000, 'Component unmount')
      }
    }
  }, [connect, clearTimeouts, stopHeartbeat])

  // Handle URL changes
  useEffect(() => {
    if (wsRef.current && wsRef.current.url !== url) {
      reconnect()
    }
  }, [url, reconnect])

  // Handle page visibility changes
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.hidden) {
        // Page is hidden, reduce heartbeat frequency or pause
        stopHeartbeat()
      } else {
        // Page is visible, resume normal heartbeat
        if (isConnected) {
          startHeartbeat()
        }
      }
    }

    document.addEventListener('visibilitychange', handleVisibilityChange)
    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange)
    }
  }, [isConnected, startHeartbeat, stopHeartbeat])

  // Handle online/offline events
  useEffect(() => {
    const handleOnline = () => {
      console.log('🌐 Network online - attempting to reconnect')
      if (!isConnected && shouldReconnect) {
        reconnect()
      }
    }

    const handleOffline = () => {
      console.log('🌐 Network offline')
      setConnectionState('disconnected')
      setConnectionStatus('disconnected')
    }

    window.addEventListener('online', handleOnline)
    window.addEventListener('offline', handleOffline)

    return () => {
      window.removeEventListener('online', handleOnline)
      window.removeEventListener('offline', handleOffline)
    }
  }, [isConnected, shouldReconnect, reconnect, setConnectionStatus])

  return {
    isConnected,
    connectionState,
    lastMessage,
    sendMessage,
    sendJsonMessage,
    disconnect,
    reconnect,
  }
}

export default useWebSocket