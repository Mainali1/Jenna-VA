"""Utility functions for plugin development and WebAssembly integration.

This module provides helper functions for plugin developers to create
and package plugins for the Jenna VA plugin system.
"""

import os
import sys
import json
import toml
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional, Union

from ..core.logger import get_logger

logger = get_logger("plugin_utils")

# Check for WebAssembly toolchain availability
try:
    import wasmer
    WASMER_AVAILABLE = True
except ImportError:
    WASMER_AVAILABLE = False

try:
    import extism
    import extism.pdk
    EXTISM_AVAILABLE = True
except ImportError:
    EXTISM_AVAILABLE = False


def create_plugin_scaffold(plugin_dir: Union[str, Path], plugin_name: str, 
                          author: str = "", description: str = "",
                          plugin_type: str = "python") -> bool:
    """Create a scaffold for a new plugin.
    
    Args:
        plugin_dir: Directory where the plugin will be created
        plugin_name: Name of the plugin
        author: Author of the plugin
        description: Description of the plugin
        plugin_type: Type of plugin ('python' or 'wasm')
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        plugin_dir = Path(plugin_dir)
        plugin_path = plugin_dir / plugin_name
        
        # Create plugin directory
        plugin_path.mkdir(parents=True, exist_ok=True)
        
        # Create manifest file
        manifest = {
            "name": plugin_name,
            "version": "0.1.0",
            "description": description,
            "author": author,
            "license": "MIT",
            "requires_api": False,
            "requires_internet": False,
            "requires_permissions": [],
            "dependencies": {},
            "settings_schema": {}
        }
        
        if plugin_type.lower() == "python":
            manifest["entry_point"] = "main"
            manifest["python_module"] = plugin_name
            
            # Create Python module file
            module_file = plugin_path / f"{plugin_name}.py"
            with open(module_file, "w") as f:
                f.write(f"""\
"""A {plugin_name} plugin for Jenna VA.

{description}
"""

from jenna.core.feature_manager import Feature


class {plugin_name.title().replace('-', '').replace('_', '')}Feature(Feature):
    """Implementation of the {plugin_name} feature."""
    
    def __init__(self):
        super().__init__()
        self.name = "{plugin_name}"
        self.description = "{description}"
        self.version = "0.1.0"
        self.author = "{author}"
        self.requires_api = False
        self.requires_internet = False
    
    async def _initialize_impl(self, settings):
        """Initialize the feature implementation."""
        # Your initialization code here
        return True
    
    async def _check_api_requirements(self):
        """Check if API requirements are met."""
        # Your API requirement checks here
        return True
    
    async def _on_enable(self):
        """Called when the feature is enabled."""
        # Your code to run when feature is enabled
        pass
    
    async def _on_disable(self):
        """Called when the feature is disabled."""
        # Your code to run when feature is disabled
        pass
    
    async def example_method(self, param1, param2=None):
        """Example method that can be called by the application.
        
        Args:
            param1: First parameter
            param2: Optional second parameter
            
        Returns:
            Result of the operation
        """
        if not self.enabled:
            raise Exception("Feature is not enabled")
            
        # Your implementation here
        return {"result": f"Processed {param1} and {param2}"}
""")
            
            # Create requirements.txt
            with open(plugin_path / "requirements.txt", "w") as f:
                f.write("# Add your dependencies here\n")
                
        elif plugin_type.lower() == "wasm":
            if not EXTISM_AVAILABLE:
                logger.warning("Extism PDK not available. Install extism package for better WASM plugin support.")
            
            manifest["entry_point"] = "main"
            manifest["wasm_file"] = "plugin.wasm"
            
            # Create Rust project if cargo is available
            cargo_path = shutil.which("cargo")
            if cargo_path:
                try:
                    subprocess.run(
                        [cargo_path, "new", "--lib", str(plugin_path / "src")],
                        check=True,
                        capture_output=True
                    )
                    
                    # Create Cargo.toml
                    cargo_toml = plugin_path / "src" / "Cargo.toml"
                    with open(cargo_toml, "w") as f:
                        f.write(f"""\
[package]
name = "{plugin_name}"
version = "0.1.0"
edition = "2021"

[lib]
crate-type = ["cdylib"]

[dependencies]
extism-pdk = "0.3.0"
serde = {{ version = "1.0", features = ["derive"] }}
serde_json = "1.0"
""")
                    
                    # Create lib.rs
                    lib_rs = plugin_path / "src" / "src" / "lib.rs"
                    with open(lib_rs, "w") as f:
                        f.write(f"""\
use extism_pdk::*;
use serde::{{Deserialize, Serialize}};

#[derive(Deserialize)]
struct Input {{
    method: String,
    args: Vec<serde_json::Value>,
    kwargs: serde_json::Map<String, serde_json::Value>,
}}

#[derive(Serialize)]
struct Output {{
    result: String,
}}

#[plugin_fn]
pub fn main(input: String) -> FnResult<Json<Output>> {{
    let input: Input = serde_json::from_str(&input)?;
    
    match input.method.as_str() {{
        "example_method" => {{
            // Extract parameters from args or kwargs
            let param1 = if !input.args.is_empty() {{
                input.args[0].to_string()
            }} else if let Some(value) = input.kwargs.get("param1") {{
                value.to_string()
            }} else {{
                return Err(Error::new("Missing required parameter: param1"));
            }};
            
            // Your implementation here
            let result = format!("Processed {{}}", param1);
            
            Ok(Json(Output {{ result }}))
        }},
        _ => Err(Error::new(&format!("Unknown method: {{}}", input.method))),
    }}
}}
""")
                    
                    logger.info(f"Created Rust project scaffold for WASM plugin: {plugin_name}")
                except subprocess.CalledProcessError as e:
                    logger.error(f"Failed to create Rust project: {e}")
            else:
                # Create a placeholder for the WASM file
                wasm_placeholder = plugin_path / "README.md"
                with open(wasm_placeholder, "w") as f:
                    f.write(f"""\
# {plugin_name} WASM Plugin

{description}

This plugin requires a WebAssembly (.wasm) file to be built and placed in this directory.

## Building the Plugin

You can use tools like Rust with wasm-pack, AssemblyScript, or C/C++ with Emscripten to build your WASM plugin.

For Rust:
1. Create a new library project: `cargo new --lib src`
2. Configure Cargo.toml for cdylib output
3. Build with wasm-pack: `wasm-pack build --target web`
4. Copy the resulting .wasm file to this directory as "plugin.wasm"
""")
        else:
            logger.error(f"Unknown plugin type: {plugin_type}")
            return False
        
        # Write manifest file
        with open(plugin_path / "plugin.toml", "w") as f:
            toml.dump(manifest, f)
        
        logger.info(f"Created plugin scaffold for {plugin_name} in {plugin_path}")
        return True
    
    except Exception as e:
        logger.error(f"Failed to create plugin scaffold: {e}")
        return False


def build_wasm_plugin(plugin_dir: Union[str, Path], output_dir: Optional[Union[str, Path]] = None) -> bool:
    """Build a WebAssembly plugin from source.
    
    Args:
        plugin_dir: Directory containing the plugin source
        output_dir: Directory where the built plugin will be placed (defaults to plugin_dir)
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        plugin_dir = Path(plugin_dir)
        if output_dir is None:
            output_dir = plugin_dir
        else:
            output_dir = Path(output_dir)
        
        # Check if it's a Rust project
        cargo_toml = plugin_dir / "Cargo.toml"
        if cargo_toml.exists():
            # Check for wasm-pack
            wasm_pack = shutil.which("wasm-pack")
            if not wasm_pack:
                logger.error("wasm-pack not found. Please install it with 'cargo install wasm-pack'")
                return False
            
            # Build with wasm-pack
            try:
                subprocess.run(
                    [wasm_pack, "build", "--target", "web", str(plugin_dir)],
                    check=True,
                    capture_output=True
                )
                
                # Copy the resulting .wasm file
                wasm_file = plugin_dir / "pkg" / f"{plugin_dir.name}_bg.wasm"
                if wasm_file.exists():
                    shutil.copy(wasm_file, output_dir / "plugin.wasm")
                    logger.info(f"Built WASM plugin and copied to {output_dir / 'plugin.wasm'}")
                    return True
                else:
                    logger.error(f"WASM file not found after build: {wasm_file}")
            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to build WASM plugin: {e}")
        else:
            logger.error(f"No Cargo.toml found in {plugin_dir}. Not a Rust project.")
        
        return False
    
    except Exception as e:
        logger.error(f"Failed to build WASM plugin: {e}")
        return False


def package_plugin(plugin_dir: Union[str, Path], output_file: Optional[Union[str, Path]] = None) -> bool:
    """Package a plugin for distribution.
    
    Args:
        plugin_dir: Directory containing the plugin
        output_file: Output file path (defaults to plugin_dir.zip)
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        plugin_dir = Path(plugin_dir)
        
        # Determine plugin name from directory
        plugin_name = plugin_dir.name
        
        # Default output file
        if output_file is None:
            output_file = plugin_dir.parent / f"{plugin_name}.zip"
        else:
            output_file = Path(output_file)
        
        # Create zip archive
        shutil.make_archive(
            str(output_file.with_suffix('')),  # Remove .zip extension if present
            'zip',
            plugin_dir.parent,  # Root directory
            plugin_name  # Directory to include
        )
        
        logger.info(f"Packaged plugin {plugin_name} to {output_file}")
        return True
    
    except Exception as e:
        logger.error(f"Failed to package plugin: {e}")
        return False


def install_plugin(plugin_package: Union[str, Path], install_dir: Union[str, Path]) -> bool:
    """Install a plugin package.
    
    Args:
        plugin_package: Path to the plugin package (.zip)
        install_dir: Directory where the plugin will be installed
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        plugin_package = Path(plugin_package)
        install_dir = Path(install_dir)
        
        # Ensure install directory exists
        install_dir.mkdir(parents=True, exist_ok=True)
        
        # Extract the package
        shutil.unpack_archive(plugin_package, install_dir)
        
        # Get the plugin name from the extracted directory
        # Assuming the zip contains a single directory with the plugin name
        extracted_dirs = [d for d in install_dir.iterdir() if d.is_dir()]
        if not extracted_dirs:
            logger.error("No plugin directory found in the package")
            return False
        
        plugin_name = extracted_dirs[0].name
        logger.info(f"Installed plugin {plugin_name} to {install_dir}")
        return True
    
    except Exception as e:
        logger.error(f"Failed to install plugin: {e}")
        return False


def validate_plugin(plugin_dir: Union[str, Path]) -> Dict[str, Any]:
    """Validate a plugin directory.
    
    Args:
        plugin_dir: Directory containing the plugin
        
    Returns:
        Dict with validation results
    """
    result = {
        "valid": False,
        "errors": [],
        "warnings": [],
        "info": {}
    }
    
    try:
        plugin_dir = Path(plugin_dir)
        
        # Check if directory exists
        if not plugin_dir.exists() or not plugin_dir.is_dir():
            result["errors"].append(f"Plugin directory does not exist: {plugin_dir}")
            return result
        
        # Check for manifest file
        manifest_file = None
        for ext in [".toml", ".json"]:
            candidate = plugin_dir / f"plugin{ext}"
            if candidate.exists():
                manifest_file = candidate
                break
        
        if not manifest_file:
            result["errors"].append("No plugin manifest file found (plugin.toml or plugin.json)")
            return result
        
        # Load manifest
        try:
            if manifest_file.suffix == ".toml":
                manifest = toml.load(manifest_file)
            else:  # .json
                manifest = json.loads(manifest_file.read_text())
            
            result["info"]["manifest"] = manifest
        except Exception as e:
            result["errors"].append(f"Failed to parse manifest file: {e}")
            return result
        
        # Check required fields
        required_fields = ["name", "version", "entry_point"]
        for field in required_fields:
            if field not in manifest:
                result["errors"].append(f"Missing required field in manifest: {field}")
        
        # Check that either wasm_file or python_module is specified
        if "wasm_file" not in manifest and "python_module" not in manifest:
            result["errors"].append("Either wasm_file or python_module must be specified in manifest")
        
        # Check for WASM file if specified
        if "wasm_file" in manifest and manifest["wasm_file"]:
            wasm_file = plugin_dir / manifest["wasm_file"]
            if not wasm_file.exists():
                result["errors"].append(f"WASM file not found: {wasm_file}")
            else:
                result["info"]["wasm_file"] = str(wasm_file)
        
        # Check for Python module if specified
        if "python_module" in manifest and manifest["python_module"]:
            module_name = manifest["python_module"]
            module_file = plugin_dir / f"{module_name}.py"
            package_dir = plugin_dir / module_name
            
            if not module_file.exists() and not package_dir.exists():
                result["errors"].append(f"Python module not found: {module_name}")
            else:
                result["info"]["python_module"] = module_name
        
        # Set valid flag based on errors
        result["valid"] = len(result["errors"]) == 0
        
        return result
    
    except Exception as e:
        result["errors"].append(f"Validation failed: {e}")
        return result