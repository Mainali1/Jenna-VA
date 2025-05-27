import { create } from 'zustand'
import { devtools, persist } from 'zustand/middleware'
import { immer } from 'zustand/middleware/immer'
import toast from 'react-hot-toast'

import type { 
  AppStore, 
  AppStatus, 
  ConnectionStatus, 
  User, 
  Theme, 
  AppConfig 
} from '@types/index'

// Default configuration
const defaultConfig: AppConfig = {
  version: __APP_VERSION__ || '1.0.0',
  buildDate: __BUILD_DATE__ || new Date().toISOString(),
  apiUrl: 'http://localhost:8080/api',
  wsUrl: 'ws://localhost:8080/ws',
  features: {
    voiceRecognition: true,
    textToSpeech: true,
    weatherService: true,
    emailIntegration: false,
    fileOperations: true,
    pomodoroTimer: true,
    flashcards: true,
    analytics: true,
    backupSystem: true,
    autoUpdates: true,
  },
  limits: {
    maxConversationHistory: 1000,
    maxFileSize: 10 * 1024 * 1024, // 10MB
    maxConcurrentRequests: 5,
    requestTimeout: 30000, // 30 seconds
  },
}

// Default user preferences
const defaultUser: User = {
  id: 'default-user',
  name: 'User',
  preferences: {
    theme: 'dark',
    language: 'en',
    voiceSettings: {
      wakePhrase: 'Jenna Ready',
      voiceSpeed: 1.0,
      voicePitch: 1.0,
      voiceVolume: 0.8,
      selectedVoice: 'default',
      noiseReduction: true,
      autoListen: true,
      confirmationSounds: true,
    },
    notifications: {
      enabled: true,
      soundEnabled: true,
      showInSystemTray: true,
      emailNotifications: false,
      reminderNotifications: true,
    },
    privacy: {
      saveConversations: true,
      shareAnalytics: false,
      allowCloudSync: false,
      dataRetentionDays: 30,
    },
    shortcuts: {
      toggleListening: 'ctrl+shift+j',
      openSettings: 'ctrl+shift+s',
      openHelp: 'ctrl+shift+h',
      goToDashboard: 'ctrl+shift+d',
      openChat: 'ctrl+shift+c',
    },
  },
  createdAt: new Date().toISOString(),
  lastActiveAt: new Date().toISOString(),
}

export const useAppStore = create<AppStore>()()
  devtools(
    persist(
      immer((set, get) => ({
        // Initial state
        status: 'initializing',
        connectionStatus: 'disconnected',
        isListening: false,
        currentUser: defaultUser,
        theme: 'dark',
        config: defaultConfig,

        // Actions
        setStatus: (status: AppStatus) => {
          set((state) => {
            state.status = status
          })
          
          // Show status notifications for important changes
          if (status === 'ready') {
            toast.success('Jenna is ready to assist you!')
          } else if (status === 'error') {
            toast.error('Jenna encountered an error')
          } else if (status === 'offline') {
            toast.error('Jenna is offline')
          }
        },

        setConnectionStatus: (connectionStatus: ConnectionStatus) => {
          set((state) => {
            state.connectionStatus = connectionStatus
          })
          
          // Show connection status notifications
          if (connectionStatus === 'connected') {
            toast.success('Connected to Jenna backend')
          } else if (connectionStatus === 'disconnected') {
            toast.error('Disconnected from backend')
          } else if (connectionStatus === 'reconnecting') {
            toast.loading('Reconnecting to backend...')
          }
        },

        setListening: (isListening: boolean) => {
          set((state) => {
            state.isListening = isListening
            
            // Update last active time when user interacts
            if (state.currentUser) {
              state.currentUser.lastActiveAt = new Date().toISOString()
            }
          })
          
          // Show listening status
          if (isListening) {
            toast.success('🎤 Listening...', {
              duration: 2000,
              icon: '👂',
            })
          }
        },

        setUser: (user: User | null) => {
          set((state) => {
            state.currentUser = user
            
            // Update theme when user changes
            if (user?.preferences.theme) {
              state.theme = user.preferences.theme
            }
          })
        },

        setTheme: (theme: Theme) => {
          set((state) => {
            state.theme = theme
            
            // Update user preferences if user exists
            if (state.currentUser) {
              state.currentUser.preferences.theme = theme
            }
          })
          
          // Apply theme to document
          document.documentElement.className = theme
        },

        setConfig: (config: AppConfig) => {
          set((state) => {
            state.config = config
          })
        },

        initializeApp: async () => {
          try {
            set((state) => {
              state.status = 'initializing'
            })

            // Check system requirements
            const hasRequiredFeatures = [
              'WebSocket',
              'localStorage',
              'fetch',
              'Promise',
              'AudioContext',
            ].every(feature => {
              if (feature === 'AudioContext') {
                return 'AudioContext' in window || 'webkitAudioContext' in window
              }
              return feature in window
            })

            if (!hasRequiredFeatures) {
              throw new Error('Browser does not support required features')
            }

            // Load user preferences from localStorage
            const savedUser = localStorage.getItem('jenna-user')
            if (savedUser) {
              try {
                const parsedUser = JSON.parse(savedUser)
                set((state) => {
                  state.currentUser = { ...defaultUser, ...parsedUser }
                })
              } catch (error) {
                console.warn('Failed to parse saved user data:', error)
              }
            }

            // Load app configuration
            try {
              const response = await fetch('/api/config')
              if (response.ok) {
                const config = await response.json()
                set((state) => {
                  state.config = { ...defaultConfig, ...config }
                })
              }
            } catch (error) {
              console.warn('Failed to load remote config, using defaults:', error)
            }

            // Check for updates if enabled
            const { config } = get()
            if (config?.features.autoUpdates) {
              try {
                const response = await fetch('/api/version')
                if (response.ok) {
                  const { version, updateAvailable } = await response.json()
                  if (updateAvailable) {
                    toast('🔄 Update available!', {
                      duration: 5000,
                      onClick: () => {
                        // Handle update logic
                        window.open('/update', '_blank')
                      },
                    })
                  }
                }
              } catch (error) {
                console.warn('Failed to check for updates:', error)
              }
            }

            // Initialize analytics if enabled
            const { currentUser } = get()
            if (currentUser?.preferences.privacy.shareAnalytics) {
              try {
                await fetch('/api/analytics/init', {
                  method: 'POST',
                  headers: { 'Content-Type': 'application/json' },
                  body: JSON.stringify({
                    userId: currentUser.id,
                    version: config?.version,
                    platform: navigator.platform,
                  }),
                })
              } catch (error) {
                console.warn('Failed to initialize analytics:', error)
              }
            }

            // Mark app as ready
            set((state) => {
              state.status = 'ready'
            })

            console.log('✅ Jenna Voice Assistant initialized successfully')

          } catch (error) {
            console.error('❌ Failed to initialize app:', error)
            set((state) => {
              state.status = 'error'
            })
            throw error
          }
        },

        cleanup: () => {
          // Save user data before cleanup
          const { currentUser } = get()
          if (currentUser) {
            localStorage.setItem('jenna-user', JSON.stringify(currentUser))
          }

          // Reset state
          set((state) => {
            state.status = 'initializing'
            state.connectionStatus = 'disconnected'
            state.isListening = false
          })

          console.log('🧹 App cleanup completed')
        },
      })),
      {
        name: 'jenna-app-store',
        partialize: (state) => ({
          currentUser: state.currentUser,
          theme: state.theme,
        }),
        version: 1,
        migrate: (persistedState: any, version: number) => {
          // Handle state migrations for future versions
          if (version === 0) {
            // Migration from version 0 to 1
            return {
              ...persistedState,
              currentUser: { ...defaultUser, ...persistedState.currentUser },
            }
          }
          return persistedState
        },
      }
    ),
    {
      name: 'jenna-app-store',
      enabled: import.meta.env.DEV,
    }
  )

// Selectors for commonly used state combinations
export const useAppStatus = () => useAppStore((state) => state.status)
export const useConnectionStatus = () => useAppStore((state) => state.connectionStatus)
export const useIsListening = () => useAppStore((state) => state.isListening)
export const useCurrentUser = () => useAppStore((state) => state.currentUser)
export const useTheme = () => useAppStore((state) => state.theme)
export const useConfig = () => useAppStore((state) => state.config)

// Computed selectors
export const useIsReady = () => useAppStore((state) => state.status === 'ready')
export const useIsConnected = () => useAppStore((state) => state.connectionStatus === 'connected')
export const useUserPreferences = () => useAppStore((state) => state.currentUser?.preferences)
export const useVoiceSettings = () => useAppStore((state) => state.currentUser?.preferences.voiceSettings)
export const useNotificationSettings = () => useAppStore((state) => state.currentUser?.preferences.notifications)
export const usePrivacySettings = () => useAppStore((state) => state.currentUser?.preferences.privacy)
export const useKeyboardShortcuts = () => useAppStore((state) => state.currentUser?.preferences.shortcuts)

// Action selectors
export const useAppActions = () => useAppStore((state) => ({
  setStatus: state.setStatus,
  setConnectionStatus: state.setConnectionStatus,
  setListening: state.setListening,
  setUser: state.setUser,
  setTheme: state.setTheme,
  setConfig: state.setConfig,
  initializeApp: state.initializeApp,
  cleanup: state.cleanup,
}))