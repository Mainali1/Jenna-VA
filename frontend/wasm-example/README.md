# Jenna VA WebAssembly Example

This is a simple WebAssembly module for the Jenna Voice Assistant frontend. It demonstrates how to create a WASM module that can be loaded and used by the frontend.

## Prerequisites

Before building this WebAssembly module, you need to have the following installed:

- [Rust](https://www.rust-lang.org/tools/install)
- [wasm-pack](https://rustwasm.github.io/wasm-pack/installer/)

## Building

To build the WebAssembly module, run the following command from this directory:

```bash
wasm-pack build --target web
```

This will create a `pkg` directory containing the compiled WebAssembly module and JavaScript bindings.

## Using in the Frontend

After building, copy the `pkg/jenna_wasm_example_bg.wasm` file to the `public/wasm` directory in the frontend:

```bash
mkdir -p ../public/wasm
cp pkg/jenna_wasm_example_bg.wasm ../public/wasm/example.wasm
```

You can then use the WebAssembly module in your React components using the `useWebAssembly` hook or the `wasmStore`.

## Available Functions

This WebAssembly module provides the following functions:

- `add(a: number, b: number): number` - Adds two numbers
- `subtract(a: number, b: number): number` - Subtracts the second number from the first
- `multiply(a: number, b: number): number` - Multiplies two numbers
- `divide(a: number, b: number): number` - Divides the first number by the second
- `fibonacci(n: number): number` - Calculates the nth Fibonacci number
- `allocate(size: number): number` - Allocates memory in the WebAssembly module
- `deallocate(ptr: number, size: number): void` - Deallocates memory in the WebAssembly module
- `process_string(ptr: number, len: number): number` - Processes a string (reverses it) and returns a pointer to the result

## Example Usage

See the `WasmDemo.tsx` component in the frontend for an example of how to use this WebAssembly module.