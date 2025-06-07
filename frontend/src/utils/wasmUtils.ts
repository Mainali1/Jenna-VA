/**
 * Utility functions for working with WebAssembly
 */

/**
 * Load a WebAssembly module from a URL
 * 
 * @param url - URL of the WebAssembly module
 * @param imports - Imports to provide to the WebAssembly module
 * @returns A promise that resolves to the WebAssembly instance and module
 */
export async function loadWasmModule(url: string, imports: WebAssembly.Imports = {}) {
  try {
    // Fetch the WebAssembly module
    const response = await fetch(url)
    if (!response.ok) {
      throw new Error(`Failed to fetch WebAssembly module: ${response.statusText}`)
    }
    
    const buffer = await response.arrayBuffer()
    
    // Compile and instantiate the module
    const module = await WebAssembly.compile(buffer)
    const instance = await WebAssembly.instantiate(module, imports)
    
    return {
      instance,
      module,
      exports: instance.exports,
    }
  } catch (error) {
    console.error('Failed to load WebAssembly module:', error)
    throw error
  }
}

/**
 * Create a typed array view of a WebAssembly memory
 * 
 * @param memory - WebAssembly memory instance
 * @param type - Type of array to create
 * @returns A typed array view of the WebAssembly memory
 */
export function createMemoryView<T extends TypedArray>(memory: WebAssembly.Memory, type: TypedArrayConstructor<T>): T {
  return new type(memory.buffer)
}

/**
 * Copy a string to WebAssembly memory
 * 
 * @param memory - Typed array view of WebAssembly memory
 * @param str - String to copy
 * @param offset - Offset in memory to start copying
 * @returns The next offset after the string
 */
export function copyStringToMemory(memory: Uint8Array, str: string, offset: number): number {
  const encoder = new TextEncoder()
  const bytes = encoder.encode(str)
  memory.set(bytes, offset)
  // Add null terminator
  memory[offset + bytes.length] = 0
  return offset + bytes.length + 1
}

/**
 * Read a null-terminated string from WebAssembly memory
 * 
 * @param memory - Typed array view of WebAssembly memory
 * @param offset - Offset in memory to start reading
 * @returns The string read from memory
 */
export function readStringFromMemory(memory: Uint8Array, offset: number): string {
  let end = offset
  while (memory[end] !== 0) {
    end++
  }
  
  const bytes = memory.slice(offset, end)
  const decoder = new TextDecoder()
  return decoder.decode(bytes)
}

/**
 * Allocate memory in a WebAssembly module
 * 
 * @param exports - Exports from a WebAssembly instance
 * @param size - Size of memory to allocate in bytes
 * @returns Pointer to the allocated memory
 */
export function allocateMemory(exports: any, size: number): number {
  if (typeof exports.malloc !== 'function') {
    throw new Error('WebAssembly module does not export a malloc function')
  }
  
  return exports.malloc(size)
}

/**
 * Free memory in a WebAssembly module
 * 
 * @param exports - Exports from a WebAssembly instance
 * @param pointer - Pointer to the memory to free
 */
export function freeMemory(exports: any, pointer: number): void {
  if (typeof exports.free !== 'function') {
    throw new Error('WebAssembly module does not export a free function')
  }
  
  exports.free(pointer)
}

// Type definitions for typed arrays
type TypedArray = 
  | Int8Array 
  | Uint8Array 
  | Uint8ClampedArray 
  | Int16Array 
  | Uint16Array 
  | Int32Array 
  | Uint32Array 
  | Float32Array 
  | Float64Array

type TypedArrayConstructor<T extends TypedArray> = {
  new (buffer: ArrayBufferLike): T
  new (length: number): T
  new (buffer: ArrayBufferLike, byteOffset: number, length?: number): T
}