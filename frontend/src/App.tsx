import React, { useEffect, useState } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'

// Layout Components
import Sidebar from '@components/layout/Sidebar'
import Header from '@components/layout/Header'
import StatusBar from '@components/layout/StatusBar'

// Page Components
import Dashboard from '@pages/Dashboard'
import Chat from '@pages/Chat'
import Settings from '@pages/Settings'
import Features from '@pages/Features'
import Analytics from '@pages/Analytics'
import Help from '@pages/Help'

// Hooks
import { useAppStore } from '@store/appStore'
import { useWebSocket } from '@hooks/useWebSocket'
import { useKeyboardShortcuts } from '@hooks/useKeyboardShortcuts'

// Utils
import { cn } from '@utils/cn'

// Types
import type { AppStatus } from '@types/app'

const App: React.FC = () => {
  const [isLoading, setIsLoading] = useState(true)
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)
  
  // Global state
  const { 
    status, 
    isListening, 
    currentUser,
    theme,
    setStatus,
    setConnectionStatus,
    initializeApp 
  } = useAppStore()
  
  // WebSocket connection
  const { 
    isConnected, 
    connectionState, 
    sendMessage 
  } = useWebSocket({
    url: 'ws://localhost:8080/ws',
    onMessage: (data) => {
      // Handle incoming WebSocket messages
      console.log('WebSocket message:', data)
    },
    onConnect: () => {
      setConnectionStatus('connected')
    },
    onDisconnect: () => {
      setConnectionStatus('disconnected')
    },
    onError: (error) => {
      console.error('WebSocket error:', error)
      setConnectionStatus('error')
    }
  })
  
  // Keyboard shortcuts
  useKeyboardShortcuts({
    'ctrl+shift+j': () => {
      // Toggle Jenna listening
      sendMessage({ type: 'toggle_listening' })
    },
    'ctrl+shift+s': () => {
      // Open settings
      window.location.hash = '/settings'
    },
    'ctrl+shift+h': () => {
      // Open help
      window.location.hash = '/help'
    },
    'ctrl+shift+d': () => {
      // Go to dashboard
      window.location.hash = '/dashboard'
    },
    'escape': () => {
      // Close any open modals or overlays
      // This would be handled by individual components
    }
  })
  
  // Initialize app on mount
  useEffect(() => {
    const init = async () => {
      try {
        setStatus('initializing')
        
        // Initialize the application
        await initializeApp()
        
        // Check system requirements
        const hasRequiredFeatures = [
          'WebSocket',
          'localStorage',
          'fetch',
          'Promise'
        ].every(feature => feature in window)
        
        if (!hasRequiredFeatures) {
          throw new Error('Browser does not support required features')
        }
        
        // Set app as ready
        setStatus('ready')
        setIsLoading(false)
        
      } catch (error) {
        console.error('Failed to initialize app:', error)
        setStatus('error')
        setIsLoading(false)
      }
    }
    
    init()
  }, [initializeApp, setStatus])
  
  // Handle theme changes
  useEffect(() => {
    document.documentElement.className = theme
  }, [theme])
  
  // Loading screen
  if (isLoading) {
    return (
      <div className="min-h-screen bg-secondary-900 flex items-center justify-center">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="text-center"
        >
          <div className="spinner w-16 h-16 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-secondary-100 mb-2">
            Initializing Jenna
          </h2>
          <p className="text-secondary-400">
            Setting up your voice assistant...
          </p>
        </motion.div>
      </div>
    )
  }
  
  // Error state
  if (status === 'error') {
    return (
      <div className="min-h-screen bg-secondary-900 flex items-center justify-center p-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="card p-8 max-w-md w-full text-center"
        >
          <div className="text-error-500 text-6xl mb-4">⚠️</div>
          <h1 className="text-2xl font-bold text-secondary-100 mb-4">
            Initialization Failed
          </h1>
          <p className="text-secondary-400 mb-6">
            Jenna failed to start properly. Please check your system requirements and try again.
          </p>
          <button
            onClick={() => window.location.reload()}
            className="btn btn-primary btn-md w-full"
          >
            Restart Application
          </button>
        </motion.div>
      </div>
    )
  }
  
  return (
    <div className={cn(
      "min-h-screen bg-secondary-900 text-secondary-100",
      "flex flex-col overflow-hidden"
    )}>
      {/* Header */}
      <Header 
        sidebarCollapsed={sidebarCollapsed}
        onToggleSidebar={() => setSidebarCollapsed(!sidebarCollapsed)}
        isConnected={isConnected}
        isListening={isListening}
      />
      
      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        <Sidebar 
          collapsed={sidebarCollapsed}
          onCollapse={setSidebarCollapsed}
        />
        
        {/* Main Content */}
        <main className={cn(
          "flex-1 overflow-auto transition-all duration-300",
          sidebarCollapsed ? "ml-16" : "ml-64"
        )}>
          <AnimatePresence mode="wait">
            <Routes>
              {/* Default redirect */}
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              
              {/* Main pages */}
              <Route 
                path="/dashboard" 
                element={
                  <motion.div
                    key="dashboard"
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -20 }}
                    transition={{ duration: 0.2 }}
                  >
                    <Dashboard />
                  </motion.div>
                } 
              />
              
              <Route 
                path="/chat" 
                element={
                  <motion.div
                    key="chat"
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -20 }}
                    transition={{ duration: 0.2 }}
                  >
                    <Chat />
                  </motion.div>
                } 
              />
              
              <Route 
                path="/features" 
                element={
                  <motion.div
                    key="features"
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -20 }}
                    transition={{ duration: 0.2 }}
                  >
                    <Features />
                  </motion.div>
                } 
              />
              
              <Route 
                path="/analytics" 
                element={
                  <motion.div
                    key="analytics"
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -20 }}
                    transition={{ duration: 0.2 }}
                  >
                    <Analytics />
                  </motion.div>
                } 
              />
              
              <Route 
                path="/settings" 
                element={
                  <motion.div
                    key="settings"
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -20 }}
                    transition={{ duration: 0.2 }}
                  >
                    <Settings />
                  </motion.div>
                } 
              />
              
              <Route 
                path="/help" 
                element={
                  <motion.div
                    key="help"
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -20 }}
                    transition={{ duration: 0.2 }}
                  >
                    <Help />
                  </motion.div>
                } 
              />
              
              {/* 404 page */}
              <Route 
                path="*" 
                element={
                  <motion.div
                    key="404"
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.9 }}
                    transition={{ duration: 0.2 }}
                    className="flex items-center justify-center min-h-full p-4"
                  >
                    <div className="card p-8 text-center max-w-md">
                      <div className="text-6xl mb-4">🤖</div>
                      <h1 className="text-2xl font-bold mb-4">Page Not Found</h1>
                      <p className="text-secondary-400 mb-6">
                        The page you're looking for doesn't exist.
                      </p>
                      <button
                        onClick={() => window.history.back()}
                        className="btn btn-primary btn-md"
                      >
                        Go Back
                      </button>
                    </div>
                  </motion.div>
                } 
              />
            </Routes>
          </AnimatePresence>
        </main>
      </div>
      
      {/* Status Bar */}
      <StatusBar 
        status={status}
        isConnected={isConnected}
        connectionState={connectionState}
        isListening={isListening}
      />
    </div>
  )
}

export default App