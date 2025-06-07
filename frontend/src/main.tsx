import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter, HashRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Toaster } from 'react-hot-toast'

import App from './App.tsx'
import './index.css'

// Create a client for React Query
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      gcTime: 1000 * 60 * 10, // 10 minutes
      retry: (failureCount, error: any) => {
        // Don't retry on 4xx errors
        if (error?.response?.status >= 400 && error?.response?.status < 500) {
          return false
        }
        return failureCount < 3
      },
      refetchOnWindowFocus: false,
    },
    mutations: {
      retry: 1,
    },
  },
})

// Error boundary for the entire app
class ErrorBoundary extends React.Component<
  { children: React.ReactNode },
  { hasError: boolean; error?: Error }
> {
  constructor(props: { children: React.ReactNode }) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Application Error:', error, errorInfo)
    // Here you could send error to logging service
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-secondary-900 flex items-center justify-center p-4">
          <div className="bg-secondary-800 rounded-lg p-8 max-w-md w-full text-center">
            <div className="text-error-500 text-6xl mb-4">⚠️</div>
            <h1 className="text-2xl font-bold text-secondary-100 mb-4">
              Something went wrong
            </h1>
            <p className="text-secondary-400 mb-6">
              Jenna encountered an unexpected error. Please restart the application.
            </p>
            <button
              onClick={() => window.location.reload()}
              className="bg-primary-600 hover:bg-primary-700 text-white px-6 py-2 rounded-lg transition-colors"
            >
              Restart Application
            </button>
            {this.state.error && (
              <details className="mt-4 text-left">
                <summary className="text-secondary-400 cursor-pointer hover:text-secondary-300">
                  Technical Details
                </summary>
                <pre className="mt-2 text-xs text-error-400 bg-secondary-900 p-2 rounded overflow-auto">
                  {this.state.error.stack}
                </pre>
              </details>
            )}
          </div>
        </div>
      )
    }

    return this.props.children
  }
}

// Check if we're running in Electron
const isElectron = window.__IS_ELECTRON__ === true

// Initialize the application
const initializeApp = async () => {
  try {
    // Check if we're running in development mode
    const isDev = import.meta.env.DEV
    
    if (isDev) {
      console.log('🚀 Jenna Voice Assistant - Development Mode')
      console.log('📦 Version:', __APP_VERSION__)
      console.log('🏗️ Build Date:', __BUILD_DATE__)
      console.log('🖥️ Running in Electron:', isElectron ? 'Yes' : 'No')
    }

    // Initialize service worker for PWA (only in web mode, not in Electron)
    if ('serviceWorker' in navigator && !isDev && !isElectron) {
      try {
        await navigator.serviceWorker.register('/sw.js')
        console.log('Service Worker registered successfully')
      } catch (error) {
        console.warn('Service Worker registration failed:', error)
      }
    }

    // Check for required browser features
    const requiredFeatures = {
      'WebSocket': typeof WebSocket !== 'undefined',
      'localStorage': typeof Storage !== 'undefined',
      'fetch': typeof fetch !== 'undefined',
      'Promise': typeof Promise !== 'undefined',
    }

    const missingFeatures = Object.entries(requiredFeatures)
      .filter(([, supported]) => !supported)
      .map(([feature]) => feature)

    if (missingFeatures.length > 0) {
      console.error('Missing required browser features:', missingFeatures)
      // You could show a compatibility warning here
    }

    // Render the application
    const root = ReactDOM.createRoot(document.getElementById('root')!)
    
    // Use HashRouter for Electron and BrowserRouter for web
    const Router = isElectron ? HashRouter : BrowserRouter
    
    root.render(
      <React.StrictMode>
        <ErrorBoundary>
          <QueryClientProvider client={queryClient}>
            <Router>
              <App />
              <Toaster
                position="top-right"
                toastOptions={{
                  duration: 4000,
                  style: {
                    background: '#1e293b',
                    color: '#e2e8f0',
                    border: '1px solid #334155',
                  },
                  success: {
                    iconTheme: {
                      primary: '#22c55e',
                      secondary: '#1e293b',
                    },
                  },
                  error: {
                    iconTheme: {
                      primary: '#ef4444',
                      secondary: '#1e293b',
                    },
                  },
                }}
              />
            </Router>
          </QueryClientProvider>
        </ErrorBoundary>
      </React.StrictMode>
    )

    // Mark app as ready (removes loading screen)
    setTimeout(() => {
      document.body.classList.add('app-ready')
    }, 100)

  } catch (error) {
    console.error('Failed to initialize application:', error)
    
    // Show a basic error message if React fails to render
    document.getElementById('root')!.innerHTML = `
      <div style="
        min-height: 100vh;
        background: #0f172a;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 1rem;
        font-family: system-ui, sans-serif;
      ">
        <div style="
          background: #1e293b;
          border-radius: 0.5rem;
          padding: 2rem;
          max-width: 400px;
          text-align: center;
          color: #e2e8f0;
        ">
          <h1 style="font-size: 1.5rem; margin-bottom: 1rem; color: #ef4444;">
            Failed to Start Jenna
          </h1>
          <p style="margin-bottom: 1.5rem; color: #94a3b8;">
            The application failed to initialize. Please check your browser compatibility and try again.
          </p>
          <button 
            onclick="window.location.reload()" 
            style="
              background: #3b82f6;
              color: white;
              border: none;
              padding: 0.5rem 1rem;
              border-radius: 0.25rem;
              cursor: pointer;
            "
          >
            Retry
          </button>
        </div>
      </div>
    `
  }
}

// Start the application
initializeApp()

// Global error handlers
window.addEventListener('error', (event) => {
  console.error('Global error:', event.error)
})

window.addEventListener('unhandledrejection', (event) => {
  console.error('Unhandled promise rejection:', event.reason)
})

// Development helpers
if (import.meta.env.DEV) {
  // Make query client available in dev tools
  ;(window as any).__REACT_QUERY_CLIENT__ = queryClient
}

// Extend Window interface to include Electron flag
declare global {
  interface Window {
    __IS_ELECTRON__?: boolean;
  }
}