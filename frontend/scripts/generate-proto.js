const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

// Configuration
const PROTO_DIR = path.resolve(__dirname, '../../proto');
const OUTPUT_DIR = path.resolve(__dirname, '../src/proto');
const PROTOC_GEN_TS_PATH = path.resolve(__dirname, '../node_modules/.bin/protoc-gen-ts');
const PROTOC_GEN_GRPC_PATH = path.resolve(__dirname, '../node_modules/.bin/grpc_tools_node_protoc_plugin');
const PROTOC_GEN_WEB_PATH = path.resolve(__dirname, '../node_modules/.bin/protoc-gen-grpc-web');

// Create output directory if it doesn't exist
if (!fs.existsSync(OUTPUT_DIR)) {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
}

// Get all proto files
const protoFiles = fs.readdirSync(PROTO_DIR).filter(file => file.endsWith('.proto'));

if (protoFiles.length === 0) {
  console.error('No proto files found in', PROTO_DIR);
  process.exit(1);
}

console.log('🚀 Generating gRPC-Web code from proto files...');

for (const protoFile of protoFiles) {
  const protoPath = path.join(PROTO_DIR, protoFile);
  console.log(`Processing ${protoFile}...`);

  try {
    // Generate JavaScript code using grpc-tools
    execSync(
      `npx grpc_tools_node_protoc \
        --js_out=import_style=commonjs,binary:${OUTPUT_DIR} \
        --grpc_out=grpc_js:${OUTPUT_DIR} \
        --plugin=protoc-gen-grpc=${PROTOC_GEN_GRPC_PATH} \
        -I ${PROTO_DIR} \
        ${protoPath}`,
      { stdio: 'inherit' }
    );

    // Generate TypeScript definitions
    execSync(
      `npx grpc_tools_node_protoc \
        --plugin=protoc-gen-ts=${PROTOC_GEN_TS_PATH} \
        --ts_out=grpc_js:${OUTPUT_DIR} \
        -I ${PROTO_DIR} \
        ${protoPath}`,
      { stdio: 'inherit' }
    );

    // Generate gRPC-Web code
    execSync(
      `npx grpc_tools_node_protoc \
        --plugin=protoc-gen-grpc-web=${PROTOC_GEN_WEB_PATH} \
        --grpc-web_out=import_style=typescript,mode=grpcwebtext:${OUTPUT_DIR} \
        -I ${PROTO_DIR} \
        ${protoPath}`,
      { stdio: 'inherit' }
    );

    console.log(`✅ Successfully generated code for ${protoFile}`);
  } catch (error) {
    console.error(`❌ Error generating code for ${protoFile}:`, error.message);
    process.exit(1);
  }
}

console.log('✨ All proto files processed successfully!');

// Create an index.ts file to export all generated files
const generatedFiles = fs.readdirSync(OUTPUT_DIR).filter(file => 
  file.endsWith('_pb.js') || 
  file.endsWith('_pb.d.ts') || 
  file.endsWith('_grpc_web_pb.js') || 
  file.endsWith('_grpc_web_pb.d.ts')
);

const uniqueModules = new Set();
generatedFiles.forEach(file => {
  const baseName = file.split('.')[0].replace(/_pb$|_grpc_web_pb$/, '');
  uniqueModules.add(baseName);
});

const indexContent = Array.from(uniqueModules).map(module => {
  return `export * from './${module}_pb';
export * from './${module}_grpc_web_pb';`;
}).join('\n');

fs.writeFileSync(path.join(OUTPUT_DIR, 'index.ts'), indexContent);
console.log('📝 Created index.ts with exports for all generated modules');