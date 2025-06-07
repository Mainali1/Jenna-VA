import { create } from 'zustand'
import { devtools } from 'zustand/middleware'
import { immer } from 'zustand/middleware/immer'
import toast from 'react-hot-toast'

interface WasmModule {
  id: string
  name: string
  description: string
  url: string
  status: 'idle' | 'loading' | 'ready' | 'error'
  error?: string
  instance?: WebAssembly.Instance
  exports?: any
  lastLoaded?: string
}

interface WasmState {
  // State
  modules: Record<string, WasmModule>
  isLoading: boolean
  error: string | null
  
  // Actions
  loadModule: (id: string, url: string, options?: { name?: string, description?: string }) => Promise<WebAssembly.Instance | undefined>
  unloadModule: (id: string) => void
  callFunction: <T>(moduleId: string, functionName: string, ...args: any[]) => T | undefined
  getModule: (id: string) => WasmModule | undefined
  cleanup: () => void
}

export const useWasmStore = create<WasmState>()(
  devtools(
    immer((set, get) => ({
      // Initial state
      modules: {},
      isLoading: false,
      error: null,

      // Load a WebAssembly module
      loadModule: async (id: string, url: string, options = {}) => {
        const { name = id, description = '' } = options
        
        // Update module status to loading
        set((state) => {
          state.isLoading = true
          state.modules[id] = {
            id,
            name,
            description,
            url,
            status: 'loading',
          }
        })
        
        try {
          // Fetch and instantiate the WebAssembly module
          const response = await fetch(url)
          if (!response.ok) {
            throw new Error(`Failed to fetch WebAssembly module: ${response.statusText}`)
          }
          
          const buffer = await response.arrayBuffer()
          const module = await WebAssembly.compile(buffer)
          const instance = await WebAssembly.instantiate(module, {})
          
          // Update module status to ready
          set((state) => {
            state.isLoading = false
            state.modules[id] = {
              ...state.modules[id],
              status: 'ready',
              instance,
              exports: instance.exports,
              lastLoaded: new Date().toISOString(),
            }
          })
          
          toast.success(`WebAssembly module '${name}' loaded successfully`)
          return instance
        } catch (error) {
          // Update module status to error
          set((state) => {
            state.isLoading = false
            state.modules[id] = {
              ...state.modules[id],
              status: 'error',
              error: error instanceof Error ? error.message : String(error),
            }
          })
          
          toast.error(`Failed to load WebAssembly module: ${error instanceof Error ? error.message : String(error)}`)
          console.error('Failed to load WebAssembly module:', error)
          return undefined
        }
      },

      // Unload a WebAssembly module
      unloadModule: (id: string) => {
        set((state) => {
          const { [id]: removed, ...rest } = state.modules
          state.modules = rest
        })
      },

      // Call a function exported by a WebAssembly module
      callFunction: <T>(moduleId: string, functionName: string, ...args: any[]): T | undefined => {
        const module = get().modules[moduleId]
        
        if (!module || module.status !== 'ready') {
          console.warn(`Cannot call function '${functionName}': WebAssembly module '${moduleId}' not ready`)
          return undefined
        }
        
        const func = module.exports[functionName]
        if (typeof func !== 'function') {
          console.warn(`Function '${functionName}' not found in WebAssembly module '${moduleId}'`)
          return undefined
        }
        
        try {
          return func(...args) as T
        } catch (error) {
          console.error(`Error calling WebAssembly function '${functionName}':`, error)
          return undefined
        }
      },

      // Get a WebAssembly module by ID
      getModule: (id: string) => {
        return get().modules[id]
      },

      // Clean up all modules
      cleanup: () => {
        set((state) => {
          state.modules = {}
          state.isLoading = false
          state.error = null
        })
      },
    })),
    {
      name: 'jenna-wasm-store',
      enabled: import.meta.env.DEV,
    }
  )
)

// Selectors
export const useWasmModule = (id: string) => {
  return useWasmStore(state => state.getModule(id))
}

export const useWasmModules = () => {
  return useWasmStore(state => Object.values(state.modules))
}

export const useWasmStatus = () => {
  return useWasmStore(state => ({
    isLoading: state.isLoading,
    error: state.error,
  }))
}

export const useWasmActions = () => {
  return useWasmStore(state => ({
    loadModule: state.loadModule,
    unloadModule: state.unloadModule,
    callFunction: state.callFunction,
    cleanup: state.cleanup,
  }))
}