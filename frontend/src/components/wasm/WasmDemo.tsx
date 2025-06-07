import React, { useState, useEffect } from 'react'
import { useWebAssemblyModule } from '@hooks/useWebAssembly'
import { useWasmStore, useWasmActions } from '@store/wasmStore'
import { readStringFromMemory, copyStringToMemory } from '@utils/wasmUtils'

interface WasmDemoProps {
  className?: string
}

const WasmDemo: React.FC<WasmDemoProps> = ({ className }) => {
  // Example of using the useWebAssemblyModule hook directly
  const { status: hookStatus, wasm, callFunction } = useWebAssemblyModule('/wasm/example.wasm')
  
  // Example of using the wasmStore
  const { loadModule, callFunction: storeCallFunction } = useWasmActions()
  const modules = useWasmStore(state => Object.values(state.modules))
  
  const [result, setResult] = useState<number | null>(null)
  const [stringResult, setStringResult] = useState<string | null>(null)
  const [input1, setInput1] = useState(5)
  const [input2, setInput2] = useState(3)
  const [textInput, setTextInput] = useState('')
  
  // Load a module using the store when the component mounts
  useEffect(() => {
    loadModule('example', '/wasm/example.wasm', {
      name: 'Example Module',
      description: 'A simple example WebAssembly module'
    })
  }, [loadModule])
  
  // Example of calling a simple add function from WebAssembly
  const handleCalculate = () => {
    // Using the hook
    if (hookStatus === 'ready' && wasm) {
      const hookResult = callFunction<number>('add', input1, input2)
      setResult(hookResult || null)
    }
    
    // Using the store
    const storeResult = storeCallFunction<number>('example', 'add', input1, input2)
    if (storeResult !== undefined) {
      setResult(storeResult)
    }
  }
  
  // Example of passing a string to WebAssembly and getting a string back
  const handleProcessString = () => {
    if (hookStatus === 'ready' && wasm && wasm.exports) {
      // Get memory view
      const memory = new Uint8Array((wasm.exports.memory as WebAssembly.Memory).buffer)
      
      // Allocate memory for the input string
      const ptr = (wasm.exports.allocate as Function)(textInput.length + 1)
      
      // Copy the string to WebAssembly memory
      copyStringToMemory(memory, textInput, ptr)
      
      // Call the WebAssembly function
      const resultPtr = (wasm.exports.processString as Function)(ptr, textInput.length)
      
      // Read the result string from WebAssembly memory
      const result = readStringFromMemory(memory, resultPtr)
      setStringResult(result)
      
      // Free the allocated memory
      (wasm.exports.deallocate as Function)(ptr)
      (wasm.exports.deallocate as Function)(resultPtr)
    }
  }
  
  return (
    <div className={`p-4 bg-white dark:bg-gray-800 rounded-lg shadow ${className}`}>
      <h2 className="text-xl font-semibold mb-4">WebAssembly Demo</h2>
      
      <div className="mb-6">
        <h3 className="text-lg font-medium mb-2">Module Status</h3>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Hook Status:</p>
            <p className={`font-mono ${hookStatus === 'ready' ? 'text-green-500' : hookStatus === 'error' ? 'text-red-500' : 'text-yellow-500'}`}>
              {hookStatus}
            </p>
          </div>
          <div>
            <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Store Modules:</p>
            <p className="font-mono">{modules.length}</p>
          </div>
        </div>
      </div>
      
      <div className="mb-6">
        <h3 className="text-lg font-medium mb-2">Simple Calculation</h3>
        <div className="flex items-center space-x-2 mb-4">
          <input
            type="number"
            value={input1}
            onChange={(e) => setInput1(parseInt(e.target.value) || 0)}
            className="w-16 p-2 border rounded dark:bg-gray-700 dark:border-gray-600"
          />
          <span>+</span>
          <input
            type="number"
            value={input2}
            onChange={(e) => setInput2(parseInt(e.target.value) || 0)}
            className="w-16 p-2 border rounded dark:bg-gray-700 dark:border-gray-600"
          />
          <button
            onClick={handleCalculate}
            disabled={hookStatus !== 'ready'}
            className="px-4 py-2 bg-blue-500 text-white rounded disabled:opacity-50"
          >
            Calculate
          </button>
        </div>
        {result !== null && (
          <div className="mt-2">
            <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Result:</p>
            <p className="font-mono text-lg">{result}</p>
          </div>
        )}
      </div>
      
      <div className="mb-6">
        <h3 className="text-lg font-medium mb-2">String Processing</h3>
        <div className="flex flex-col space-y-2 mb-4">
          <input
            type="text"
            value={textInput}
            onChange={(e) => setTextInput(e.target.value)}
            placeholder="Enter text to process"
            className="p-2 border rounded dark:bg-gray-700 dark:border-gray-600"
          />
          <button
            onClick={handleProcessString}
            disabled={hookStatus !== 'ready'}
            className="px-4 py-2 bg-blue-500 text-white rounded disabled:opacity-50"
          >
            Process String
          </button>
        </div>
        {stringResult && (
          <div className="mt-2">
            <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Result:</p>
            <p className="font-mono">{stringResult}</p>
          </div>
        )}
      </div>
      
      <div className="text-sm text-gray-500 dark:text-gray-400 mt-4">
        <p>Note: This demo requires WebAssembly modules to be available at the specified paths.</p>
        <p>Check the browser console for any errors loading the modules.</p>
      </div>
    </div>
  )
}

export default WasmDemo