"""Plugin Manager for Jenna VA

This module provides a plugin system that extends the existing feature architecture
to support dynamic loading of external plugins with proper sandboxing and security.
"""

import asyncio
import os
import sys
import importlib.util
import inspect
import json
import toml
from pathlib import Path
from typing import Dict, Any, List, Optional, Type, Callable, Union, Set

import pydantic
from pydantic import BaseModel, Field, validator

from .logger import get_logger
from .config import Settings
from .feature_manager import Feature, FeatureManager
from ..utils.exceptions import PluginManagerException

# Try to import wasmer for WebAssembly support
try:
    import wasmer
    WASMER_AVAILABLE = True
except ImportError:
    WASMER_AVAILABLE = False

# Try to import extism for plugin system
try:
    import extism
    EXTISM_AVAILABLE = True
except ImportError:
    EXTISM_AVAILABLE = False


class PluginManifest(BaseModel):
    """Plugin manifest model that defines metadata for a plugin."""
    
    name: str = Field(..., description="Unique name of the plugin")
    version: str = Field(..., description="Version of the plugin in semver format")
    description: str = Field("", description="Description of the plugin")
    author: str = Field("", description="Author of the plugin")
    license: str = Field("", description="License of the plugin")
    repository: Optional[str] = Field(None, description="Repository URL")
    homepage: Optional[str] = Field(None, description="Homepage URL")
    
    # Plugin requirements
    requires_api: bool = Field(False, description="Whether the plugin requires API access")
    requires_internet: bool = Field(False, description="Whether the plugin requires internet access")
    requires_permissions: List[str] = Field([], description="List of permissions required by the plugin")
    
    # Plugin dependencies
    dependencies: Dict[str, str] = Field({}, description="Dictionary of plugin dependencies with version constraints")
    
    # Plugin entry points
    entry_point: str = Field(..., description="Entry point for the plugin")
    wasm_file: Optional[str] = Field(None, description="Path to the WebAssembly file relative to the plugin directory")
    python_module: Optional[str] = Field(None, description="Python module name for Python-based plugins")
    
    # Plugin settings schema
    settings_schema: Dict[str, Any] = Field({}, description="JSON Schema for plugin settings")
    
    @validator('entry_point')
    def validate_entry_point(cls, v, values):
        """Validate that either wasm_file or python_module is provided."""
        if not values.get('wasm_file') and not values.get('python_module'):
            raise ValueError("Either wasm_file or python_module must be provided")
        return v


class PluginInstance:
    """Represents a loaded plugin instance."""
    
    def __init__(self, manifest: PluginManifest, plugin_dir: Path):
        self.manifest = manifest
        self.plugin_dir = plugin_dir
        self.instance = None  # Will hold the plugin instance (WASM or Python)
        self.feature = None  # Will hold the Feature instance if Python-based
        self.logger = get_logger(f"plugin:{manifest.name}")
        
    async def initialize(self, settings: Settings) -> bool:
        """Initialize the plugin instance."""
        try:
            if self.manifest.wasm_file:
                return await self._initialize_wasm(settings)
            elif self.manifest.python_module:
                return await self._initialize_python(settings)
            return False
        except Exception as e:
            self.logger.error(f"Failed to initialize plugin {self.manifest.name}: {e}")
            return False
    
    async def _initialize_wasm(self, settings: Settings) -> bool:
        """Initialize a WebAssembly-based plugin."""
        if not WASMER_AVAILABLE and not EXTISM_AVAILABLE:
            self.logger.error("WebAssembly support is not available. Install wasmer or extism package.")
            return False
        
        wasm_path = self.plugin_dir / self.manifest.wasm_file
        if not wasm_path.exists():
            self.logger.error(f"WebAssembly file not found: {wasm_path}")
            return False
        
        try:
            if EXTISM_AVAILABLE:
                # Use Extism for plugin loading (preferred)
                manifest = {
                    "wasm": [{
                        "path": str(wasm_path)
                    }]
                }
                
                # Configure allowed hosts if internet access is required
                config = {}
                if self.manifest.requires_internet:
                    config["allowed_hosts"] = ["*"]
                else:
                    config["allowed_hosts"] = []
                
                # Create plugin instance
                self.instance = extism.Plugin(manifest, config=config)
                self.logger.info(f"Loaded WASM plugin {self.manifest.name} with Extism")
                return True
            elif WASMER_AVAILABLE:
                # Use Wasmer as fallback
                wasm_bytes = wasm_path.read_bytes()
                store = wasmer.Store()
                module = wasmer.Module(store, wasm_bytes)
                import_object = wasmer.ImportObject()
                self.instance = wasmer.Instance(module, import_object)
                self.logger.info(f"Loaded WASM plugin {self.manifest.name} with Wasmer")
                return True
        except Exception as e:
            self.logger.error(f"Failed to load WASM plugin {self.manifest.name}: {e}")
            return False
    
    async def _initialize_python(self, settings: Settings) -> bool:
        """Initialize a Python-based plugin."""
        try:
            # Add plugin directory to path temporarily
            sys.path.insert(0, str(self.plugin_dir))
            
            # Import the module
            module_name = self.manifest.python_module
            spec = importlib.util.find_spec(module_name)
            if spec is None:
                self.logger.error(f"Module {module_name} not found")
                return False
            
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Find the Feature class in the module
            feature_class = None
            for name, obj in inspect.getmembers(module):
                if inspect.isclass(obj) and issubclass(obj, Feature) and obj != Feature:
                    feature_class = obj
                    break
            
            if feature_class is None:
                self.logger.error(f"No Feature subclass found in module {module_name}")
                return False
            
            # Create an instance of the feature
            self.feature = feature_class()
            
            # Override feature attributes with manifest values
            self.feature.name = self.manifest.name
            self.feature.description = self.manifest.description
            self.feature.version = self.manifest.version
            self.feature.author = self.manifest.author
            self.feature.requires_api = self.manifest.requires_api
            self.feature.requires_internet = self.manifest.requires_internet
            
            # Initialize the feature
            await self.feature.initialize(settings)
            self.logger.info(f"Loaded Python plugin {self.manifest.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load Python plugin {self.manifest.name}: {e}")
            return False
        finally:
            # Remove plugin directory from path
            if str(self.plugin_dir) in sys.path:
                sys.path.remove(str(self.plugin_dir))
    
    async def call_method(self, method_name: str, *args, **kwargs) -> Any:
        """Call a method on the plugin."""
        if self.feature:  # Python-based plugin
            if hasattr(self.feature, method_name):
                method = getattr(self.feature, method_name)
                if callable(method):
                    return await method(*args, **kwargs)
                return method
            raise PluginManagerException(f"Method {method_name} not found in plugin {self.manifest.name}")
        
        elif self.instance:  # WASM-based plugin
            if EXTISM_AVAILABLE and isinstance(self.instance, extism.Plugin):
                # Convert args and kwargs to JSON for passing to WASM
                input_data = json.dumps({
                    "method": method_name,
                    "args": args,
                    "kwargs": kwargs
                }).encode('utf-8')
                
                # Call the function
                if self.instance.function_exists(method_name):
                    result = self.instance.call(method_name, input_data)
                    return json.loads(result)
                raise PluginManagerException(f"Function {method_name} not found in plugin {self.manifest.name}")
            
            elif WASMER_AVAILABLE:
                # Basic Wasmer support
                if hasattr(self.instance.exports, method_name):
                    func = getattr(self.instance.exports, method_name)
                    if callable(func):
                        # Limited support for primitive types
                        return func(*args)
                raise PluginManagerException(f"Function {method_name} not found in plugin {self.manifest.name}")
        
        raise PluginManagerException(f"Plugin {self.manifest.name} is not properly initialized")
    
    async def cleanup(self) -> None:
        """Clean up plugin resources."""
        try:
            if self.feature:
                await self.feature.cleanup()
            
            # For WASM plugins, explicit cleanup may be needed
            if EXTISM_AVAILABLE and isinstance(self.instance, extism.Plugin):
                self.instance.close()
            
            self.instance = None
            self.feature = None
        except Exception as e:
            self.logger.error(f"Error cleaning up plugin {self.manifest.name}: {e}")


class PluginManager:
    """Manager for loading and managing plugins."""
    
    def __init__(self, settings: Settings, feature_manager: FeatureManager):
        self.settings = settings
        self.feature_manager = feature_manager
        self.logger = get_logger("plugin_manager")
        self.plugins: Dict[str, PluginInstance] = {}
        self.plugin_dirs: List[Path] = []
        
        # Set up plugin directories
        self._setup_plugin_dirs()
    
    def _setup_plugin_dirs(self) -> None:
        """Set up plugin directories."""
        # Default plugin directory in the application directory
        app_plugin_dir = Path(self.settings.app_dir) / "plugins"
        app_plugin_dir.mkdir(exist_ok=True)
        self.plugin_dirs.append(app_plugin_dir)
        
        # User plugin directory
        user_plugin_dir = Path(self.settings.user_data_dir) / "plugins"
        user_plugin_dir.mkdir(exist_ok=True, parents=True)
        self.plugin_dirs.append(user_plugin_dir)
        
        # Additional plugin directories from settings
        if hasattr(self.settings, 'plugin_dirs') and self.settings.plugin_dirs:
            for dir_path in self.settings.plugin_dirs:
                plugin_dir = Path(dir_path)
                if plugin_dir.exists() and plugin_dir.is_dir():
                    self.plugin_dirs.append(plugin_dir)
    
    async def initialize(self) -> bool:
        """Initialize the plugin manager and load all plugins."""
        try:
            self.logger.info("Initializing Plugin Manager")
            
            # Check for WebAssembly support
            if not WASMER_AVAILABLE and not EXTISM_AVAILABLE:
                self.logger.warning("WebAssembly support is not available. Only Python plugins will be loaded.")
            
            # Discover and load plugins
            await self.discover_plugins()
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize Plugin Manager: {e}")
            return False
    
    async def discover_plugins(self) -> None:
        """Discover plugins in all plugin directories."""
        discovered_plugins = []
        
        for plugin_dir in self.plugin_dirs:
            self.logger.debug(f"Searching for plugins in {plugin_dir}")
            
            # Look for subdirectories that might contain plugins
            for item in plugin_dir.iterdir():
                if not item.is_dir():
                    continue
                
                # Check for manifest file
                manifest_file = None
                for ext in [".toml", ".json"]:
                    candidate = item / f"plugin{ext}"
                    if candidate.exists():
                        manifest_file = candidate
                        break
                
                if not manifest_file:
                    continue
                
                try:
                    # Load manifest
                    if manifest_file.suffix == ".toml":
                        manifest_data = toml.load(manifest_file)
                    else:  # .json
                        manifest_data = json.loads(manifest_file.read_text())
                    
                    # Create manifest object
                    manifest = PluginManifest(**manifest_data)
                    discovered_plugins.append((manifest, item))
                    self.logger.debug(f"Discovered plugin: {manifest.name} v{manifest.version}")
                except Exception as e:
                    self.logger.error(f"Error loading plugin manifest from {manifest_file}: {e}")
        
        # Load plugins in dependency order
        await self._load_plugins_in_order(discovered_plugins)
    
    async def _load_plugins_in_order(self, discovered_plugins: List[tuple]) -> None:
        """Load plugins in dependency order."""
        # Build dependency graph
        dependency_graph = {}
        plugin_map = {}
        
        for manifest, plugin_dir in discovered_plugins:
            plugin_map[manifest.name] = (manifest, plugin_dir)
            dependency_graph[manifest.name] = set(manifest.dependencies.keys())
        
        # Resolve dependencies using topological sort
        resolved = []
        unresolved = set(dependency_graph.keys())
        
        while unresolved:
            progress = False
            remaining = set()
            
            for plugin_name in unresolved:
                if all(dep in resolved for dep in dependency_graph[plugin_name]):
                    # All dependencies are resolved, load this plugin
                    manifest, plugin_dir = plugin_map[plugin_name]
                    await self._load_plugin(manifest, plugin_dir)
                    resolved.append(plugin_name)
                    progress = True
                else:
                    remaining.add(plugin_name)
            
            if not progress and remaining:
                # Circular dependency or missing dependency
                self.logger.warning(f"Could not resolve dependencies for plugins: {remaining}")
                for plugin_name in remaining:
                    manifest, plugin_dir = plugin_map[plugin_name]
                    self.logger.warning(f"Loading plugin {plugin_name} despite unresolved dependencies")
                    await self._load_plugin(manifest, plugin_dir)
                break
            
            unresolved = remaining
    
    async def _load_plugin(self, manifest: PluginManifest, plugin_dir: Path) -> None:
        """Load a single plugin."""
        if manifest.name in self.plugins:
            self.logger.warning(f"Plugin {manifest.name} is already loaded. Skipping.")
            return
        
        self.logger.info(f"Loading plugin: {manifest.name} v{manifest.version}")
        
        # Create plugin instance
        plugin = PluginInstance(manifest, plugin_dir)
        
        # Initialize plugin
        success = await plugin.initialize(self.settings)
        if not success:
            self.logger.error(f"Failed to initialize plugin {manifest.name}")
            return
        
        # Register plugin
        self.plugins[manifest.name] = plugin
        
        # If it's a Python-based plugin with a Feature, register with FeatureManager
        if plugin.feature:
            self.feature_manager.register_feature(plugin.feature)
            self.logger.info(f"Registered plugin {manifest.name} as a feature")
    
    async def call_plugin_method(self, plugin_name: str, method_name: str, *args, **kwargs) -> Any:
        """Call a method on a specific plugin."""
        if plugin_name not in self.plugins:
            raise PluginManagerException(f"Plugin {plugin_name} not found")
        
        plugin = self.plugins[plugin_name]
        return await plugin.call_method(method_name, *args, **kwargs)
    
    async def cleanup(self) -> None:
        """Clean up all plugins."""
        self.logger.info("Cleaning up plugins")
        
        cleanup_tasks = []
        for name, plugin in self.plugins.items():
            self.logger.debug(f"Cleaning up plugin {name}")
            cleanup_tasks.append(plugin.cleanup())
        
        if cleanup_tasks:
            await asyncio.gather(*cleanup_tasks)
        
        self.plugins.clear()