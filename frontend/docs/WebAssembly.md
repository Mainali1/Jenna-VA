# WebAssembly Integration in Jenna VA Frontend

This document explains how to use the WebAssembly integration in the Jenna VA frontend.

## Overview

The WebAssembly integration in Jenna VA consists of three main components:

1. **Custom React Hooks** - For loading and interacting with WebAssembly modules in React components
2. **Zustand Store** - For managing WebAssembly modules at the application level
3. **Utility Functions** - For working with WebAssembly memory and data

## Custom React Hooks

### `useWebAssembly`

The `useWebAssembly` hook provides a way to load and interact with a WebAssembly module in a React component.

```typescript
import { useWebAssembly } from '@hooks/useWebAssembly';

function MyComponent() {
  const { status, error, wasm, callFunction } = useWebAssembly();
  
  // Load a WebAssembly module
  const handleLoadModule = async () => {
    await instantiate('/path/to/module.wasm');
  };
  
  // Call a function in the WebAssembly module
  const handleCallFunction = () => {
    const result = callFunction('add', 2, 3);
    console.log(result); // 5
  };
  
  return (
    <div>
      <p>Status: {status}</p>
      {error && <p>Error: {error.message}</p>}
      <button onClick={handleLoadModule}>Load Module</button>
      <button onClick={handleCallFunction} disabled={status !== 'ready'}>Call Function</button>
    </div>
  );
}
```

### `useWebAssemblyModule`

The `useWebAssemblyModule` hook is a simplified version of `useWebAssembly` that automatically loads a WebAssembly module from a URL.

```typescript
import { useWebAssemblyModule } from '@hooks/useWebAssembly';

function MyComponent() {
  const { status, error, wasm, callFunction } = useWebAssemblyModule('/path/to/module.wasm');
  
  // Call a function in the WebAssembly module
  const handleCallFunction = () => {
    const result = callFunction('add', 2, 3);
    console.log(result); // 5
  };
  
  return (
    <div>
      <p>Status: {status}</p>
      {error && <p>Error: {error.message}</p>}
      <button onClick={handleCallFunction} disabled={status !== 'ready'}>Call Function</button>
    </div>
  );
}
```

## Zustand Store

The `wasmStore` provides a way to manage WebAssembly modules at the application level.

```typescript
import { useWasmStore, useWasmActions } from '@store/wasmStore';

function MyComponent() {
  // Get actions from the store
  const { loadModule, unloadModule, callFunction } = useWasmActions();
  
  // Get modules from the store
  const modules = useWasmStore(state => Object.values(state.modules));
  
  // Load a WebAssembly module
  const handleLoadModule = () => {
    loadModule('example', '/path/to/module.wasm', {
      name: 'Example Module',
      description: 'A simple example WebAssembly module'
    });
  };
  
  // Call a function in the WebAssembly module
  const handleCallFunction = () => {
    const result = callFunction('example', 'add', 2, 3);
    console.log(result); // 5
  };
  
  return (
    <div>
      <p>Loaded Modules: {modules.length}</p>
      <button onClick={handleLoadModule}>Load Module</button>
      <button onClick={handleCallFunction}>Call Function</button>
    </div>
  );
}
```

## Utility Functions

The `wasmUtils` module provides utility functions for working with WebAssembly memory and data.

```typescript
import { copyStringToMemory, readStringFromMemory } from '@utils/wasmUtils';

// Example of passing a string to WebAssembly and getting a string back
const handleProcessString = () => {
  if (wasm && wasm.exports) {
    // Get memory view
    const memory = new Uint8Array((wasm.exports.memory as WebAssembly.Memory).buffer);
    
    // Allocate memory for the input string
    const ptr = (wasm.exports.allocate as Function)(textInput.length + 1);
    
    // Copy the string to WebAssembly memory
    copyStringToMemory(memory, textInput, ptr);
    
    // Call the WebAssembly function
    const resultPtr = (wasm.exports.processString as Function)(ptr, textInput.length);
    
    // Read the result string from WebAssembly memory
    const result = readStringFromMemory(memory, resultPtr);
    setStringResult(result);
    
    // Free the allocated memory
    (wasm.exports.deallocate as Function)(ptr);
    (wasm.exports.deallocate as Function)(resultPtr);
  }
};
```

## Example WebAssembly Module

An example WebAssembly module is provided in the `frontend/wasm-example` directory. It demonstrates how to create a WebAssembly module that can be used with the frontend integration.

To build the example module, run:

```bash
npm run wasm:build
```

This will build the WebAssembly module and copy it to the `public/wasm` directory, where it can be loaded by the frontend.

## Demo Component

A demo component is provided in `frontend/src/components/wasm/WasmDemo.tsx`. It demonstrates how to use the WebAssembly integration in a React component.

## Best Practices

1. **Memory Management** - Always free memory allocated in WebAssembly modules to prevent memory leaks.
2. **Error Handling** - Always check the status of WebAssembly modules before calling functions.
3. **Performance** - Use WebAssembly for computationally intensive tasks that benefit from native performance.
4. **Compatibility** - Ensure your WebAssembly modules are compatible with the target browsers.
5. **Testing** - Test your WebAssembly modules thoroughly to ensure they work as expected.