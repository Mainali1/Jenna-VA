const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

// Ensure the public/wasm directory exists
const wasmDir = path.resolve(__dirname, '../public/wasm');
if (!fs.existsSync(wasmDir)) {
  console.log(`Creating directory: ${wasmDir}`);
  fs.mkdirSync(wasmDir, { recursive: true });
}

// Build the WebAssembly module
console.log('Building WebAssembly module...');
try {
  execSync('wasm-pack build --target web', { stdio: 'inherit' });
  console.log('WebAssembly module built successfully.');
} catch (error) {
  console.error('Failed to build WebAssembly module:', error);
  process.exit(1);
}

// Copy the WebAssembly module to the public/wasm directory
const sourceWasm = path.resolve(__dirname, 'pkg/jenna_wasm_example_bg.wasm');
const destWasm = path.resolve(wasmDir, 'example.wasm');

console.log(`Copying ${sourceWasm} to ${destWasm}...`);
try {
  fs.copyFileSync(sourceWasm, destWasm);
  console.log('WebAssembly module copied successfully.');
} catch (error) {
  console.error('Failed to copy WebAssembly module:', error);
  process.exit(1);
}

console.log('Done!');