import React from 'react'
import WasmDemo from '@components/wasm/WasmDemo'

const WasmDemoPage: React.FC = () => {
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-6">WebAssembly Demo</h1>
      
      <div className="mb-8">
        <p className="mb-4">
          This page demonstrates the integration of WebAssembly modules in the Jenna VA frontend.
          The demo below shows how to load and interact with a WebAssembly module using the custom
          hooks and utilities provided by the application.
        </p>
        
        <p className="mb-4">
          The WebAssembly module used in this demo is a simple example that provides basic
          mathematical operations and string processing functions. It is written in Rust and
          compiled to WebAssembly using wasm-pack.
        </p>
        
        <p className="text-sm text-gray-500">
          Note: To build the WebAssembly module, run <code className="bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded">npm run wasm:build</code> in the terminal.
        </p>
      </div>
      
      <div className="bg-gray-50 dark:bg-gray-900 p-6 rounded-lg shadow-md">
        <WasmDemo className="bg-white dark:bg-gray-800" />
      </div>
      
      <div className="mt-8">
        <h2 className="text-xl font-semibold mb-4">How It Works</h2>
        
        <div className="space-y-4">
          <p>
            The WebAssembly integration in Jenna VA consists of three main components:
          </p>
          
          <ol className="list-decimal list-inside space-y-2 pl-4">
            <li>
              <strong>Custom React Hooks</strong> - For loading and interacting with WebAssembly modules in React components
            </li>
            <li>
              <strong>Zustand Store</strong> - For managing WebAssembly modules at the application level
            </li>
            <li>
              <strong>Utility Functions</strong> - For working with WebAssembly memory and data
            </li>
          </ol>
          
          <p>
            The demo above uses both the custom hooks and the Zustand store to load and interact with the WebAssembly module.
            It demonstrates how to call functions in the WebAssembly module and how to pass data between JavaScript and WebAssembly.
          </p>
          
          <p>
            For more information, see the <a href="#" className="text-blue-500 hover:underline">WebAssembly documentation</a>.
          </p>
        </div>
      </div>
    </div>
  )
}

export default WasmDemoPage