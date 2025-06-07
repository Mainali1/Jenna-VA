import { useState, useEffect, useRef, useCallback } from 'react'

type WebAssemblyStatus = 'idle' | 'loading' | 'ready' | 'error'

interface WebAssemblyInstance {
  instance: WebAssembly.Instance
  module: WebAssembly.Module
  exports: any
}

interface UseWebAssemblyOptions {
  /**
   * Initial imports to provide to the WebAssembly module
   */
  imports?: WebAssembly.Imports
  /**
   * Whether to automatically instantiate the module when the hook is mounted
   */
  autoInstantiate?: boolean
  /**
   * Callback function called when the module is successfully instantiated
   */
  onInstantiated?: (instance: WebAssemblyInstance) => void
  /**
   * Callback function called when an error occurs during instantiation
   */
  onError?: (error: Error) => void
}

interface UseWebAssemblyReturn {
  /**
   * Current status of the WebAssembly module
   */
  status: WebAssemblyStatus
  /**
   * Error message if status is 'error'
   */
  error: Error | null
  /**
   * WebAssembly instance, module and exports
   */
  wasm: WebAssemblyInstance | null
  /**
   * Load and instantiate a WebAssembly module from a URL
   */
  instantiate: (urlOrBuffer: string | BufferSource) => Promise<WebAssemblyInstance>
  /**
   * Call a function exported by the WebAssembly module
   */
  callFunction: <T>(name: string, ...args: any[]) => T | undefined
}

/**
 * Custom hook for loading and interacting with WebAssembly modules
 * 
 * @param options - Configuration options for the WebAssembly module
 * 
 * @example
 * ```tsx
 * const { status, wasm, callFunction } = useWebAssembly({
 *   imports: { env: { memory } },
 *   autoInstantiate: true,
 *   onInstantiated: (instance) => console.log('Module ready', instance)
 * })
 * 
 * // Load a WASM module
 * useEffect(() => {
 *   instantiate('/path/to/module.wasm')
 * }, [])
 * 
 * // Call a function exported by the WASM module
 * const result = callFunction('add', 5, 3) // 8
 * ```
 */
export function useWebAssembly(options: UseWebAssemblyOptions = {}): UseWebAssemblyReturn {
  const {
    imports = {},
    autoInstantiate = false,
    onInstantiated,
    onError,
  } = options

  const [status, setStatus] = useState<WebAssemblyStatus>('idle')
  const [error, setError] = useState<Error | null>(null)
  const [wasm, setWasm] = useState<WebAssemblyInstance | null>(null)
  
  // Keep a reference to the latest callbacks
  const onInstantiatedRef = useRef(onInstantiated)
  const onErrorRef = useRef(onError)
  
  useEffect(() => {
    onInstantiatedRef.current = onInstantiated
    onErrorRef.current = onError
  }, [onInstantiated, onError])

  /**
   * Load and instantiate a WebAssembly module from a URL or buffer
   */
  const instantiate = useCallback(async (urlOrBuffer: string | BufferSource): Promise<WebAssemblyInstance> => {
    try {
      setStatus('loading')
      setError(null)

      let buffer: BufferSource
      
      // If a URL is provided, fetch the module
      if (typeof urlOrBuffer === 'string') {
        const response = await fetch(urlOrBuffer)
        if (!response.ok) {
          throw new Error(`Failed to fetch WebAssembly module: ${response.statusText}`)
        }
        buffer = await response.arrayBuffer()
      } else {
        buffer = urlOrBuffer
      }

      // Compile and instantiate the module
      const module = await WebAssembly.compile(buffer)
      const instance = await WebAssembly.instantiate(module, imports)
      
      const wasmInstance = {
        instance,
        module,
        exports: instance.exports,
      }
      
      setWasm(wasmInstance)
      setStatus('ready')
      
      // Call the onInstantiated callback if provided
      if (onInstantiatedRef.current) {
        onInstantiatedRef.current(wasmInstance)
      }
      
      return wasmInstance
    } catch (err) {
      const error = err instanceof Error ? err : new Error(String(err))
      setError(error)
      setStatus('error')
      
      // Call the onError callback if provided
      if (onErrorRef.current) {
        onErrorRef.current(error)
      }
      
      throw error
    }
  }, [imports])

  /**
   * Call a function exported by the WebAssembly module
   */
  const callFunction = useCallback(<T>(name: string, ...args: any[]): T | undefined => {
    if (!wasm || status !== 'ready') {
      console.warn(`Cannot call function '${name}': WebAssembly module not ready`)
      return undefined
    }

    const func = wasm.exports[name]
    if (typeof func !== 'function') {
      console.warn(`Function '${name}' not found in WebAssembly exports`)
      return undefined
    }

    try {
      return func(...args) as T
    } catch (err) {
      console.error(`Error calling WebAssembly function '${name}':`, err)
      return undefined
    }
  }, [wasm, status])

  return {
    status,
    error,
    wasm,
    instantiate,
    callFunction,
  }
}

/**
 * Helper hook to load a WebAssembly module from a URL
 */
export function useWebAssemblyModule(url: string, options: UseWebAssemblyOptions = {}) {
  const webAssembly = useWebAssembly(options)
  
  useEffect(() => {
    if (url) {
      webAssembly.instantiate(url).catch(err => {
        console.error('Failed to load WebAssembly module:', err)
      })
    }
  }, [url, webAssembly.instantiate])
  
  return webAssembly
}