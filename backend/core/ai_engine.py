"""AI Engine for Jenna"""

import asyncio
import json
from pathlib import Path
from typing import List, Dict, Any, Optional

from .config import Settings
from .logger import get_logger
from .feature_manager import FeatureManager
from .plugin_manager import PluginManager
from ..utils.exceptions import JennaException
from ..utils.helpers import Timer, get_available_memory
from ..utils.model_manager import ModelManager
from ..utils.model_optimization import ModelOptimizer


class AIResponse:
    """Response from the AI engine."""
    
    def __init__(self, text: str, actions: List[Dict[str, Any]] = None):
        self.text = text
        self.actions = actions or []


class AIEngine:
    """AI Engine for processing commands and generating responses."""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = get_logger(__name__)
        self.model = None
        
        # Initialize model manager
        models_dir = Path(settings.data_dir) / "models"
        self.model_manager = ModelManager(
            models_dir=models_dir,
            cache_size=settings.performance_model_cache_size,
            memory_limit_mb=settings.performance_memory_limit_mb
        )
    
    async def initialize(self):
        """Initialize the AI engine."""
        self.logger.info("Initializing AI Engine...")
        
        # Initialize model manager
        try:
            # Check for available models
            available_models = self.model_manager.list_models()
            if available_models:
                self.logger.info(f"Found {len(available_models)} models: {', '.join(available_models)}")
            else:
                self.logger.info("No models found in model directory")
                
            # TODO: Initialize AI model based on settings
            # For now, we'll just use the model manager for future model loading
            
            self.logger.info("AI Engine initialized")
        except Exception as e:
            self.logger.error(f"Error initializing AI Engine: {e}")
            raise JennaException(f"Failed to initialize AI Engine: {e}")
    
    async def process_command(
        self, 
        command: str, 
        context: List[Dict[str, Any]] = None,
        features: Optional[FeatureManager] = None,
        plugins: Optional[PluginManager] = None
    ) -> AIResponse:
        """Process a command and generate a response.
        
        Args:
            command: The user command to process
            context: Optional conversation context
            features: Optional feature manager for executing actions
            plugins: Optional plugin manager for plugin functionality
            
        Returns:
            AIResponse object with text and actions
        """
        self.logger.debug(f"Processing command: {command}")
        
        # TODO: Replace with actual AI processing
        # This is a simple mock implementation
        response_text = f"I received your command: {command}"
        actions = []
        
        # Simple keyword-based responses for testing
        if "hello" in command.lower() or "hi" in command.lower():
            response_text = "Hello! How can I help you today?"
        
        elif "weather" in command.lower():
            response_text = "I'm sorry, I don't have access to weather information yet."
        
        elif "time" in command.lower():
            import datetime
            now = datetime.datetime.now()
            response_text = f"The current time is {now.strftime('%H:%M:%S')}"
        
        elif "date" in command.lower():
            import datetime
            now = datetime.datetime.now()
            response_text = f"Today is {now.strftime('%A, %B %d, %Y')}"
        
        elif "joke" in command.lower():
            response_text = "Why don't scientists trust atoms? Because they make up everything!"
        
        elif "calculator" in command.lower() and plugins:
            # Example of using a plugin
            if "calculator" in plugins.get_loaded_plugins():
                try:
                    # Extract numbers from the command
                    import re
                    numbers = re.findall(r'\d+', command)
                    if len(numbers) >= 2:
                        num1 = int(numbers[0])
                        num2 = int(numbers[1])
                        
                        # Determine operation
                        operation = None
                        if "add" in command.lower() or "plus" in command.lower() or "+" in command:
                            operation = "add"
                        elif "subtract" in command.lower() or "minus" in command.lower() or "-" in command:
                            operation = "subtract"
                        elif "multiply" in command.lower() or "times" in command.lower() or "*" in command:
                            operation = "multiply"
                        elif "divide" in command.lower() or "/" in command:
                            operation = "divide"
                            
                        if operation:
                            # Create an action for the plugin
                            actions.append({
                                "type": "plugin",
                                "plugin_name": "calculator",
                                "method": "calculate",
                                "args": [operation, num1, num2],
                                "kwargs": {}
                            })
                            response_text = f"I'll calculate {num1} {operation} {num2} for you."
                        else:
                            response_text = "I'm not sure what calculation you want to perform. Try specifying add, subtract, multiply, or divide."
                    else:
                        response_text = "I need at least two numbers to perform a calculation."
                except Exception as e:
                    self.logger.error(f"Error processing calculator command: {e}")
                    response_text = "I had trouble understanding that calculation request."
            else:
                response_text = "The calculator plugin is not loaded."
        
        # Add more keyword handlers as needed
        
        return AIResponse(response_text, actions)
    
    async def load_model(self, model_name: str, use_quantized: bool = True):
        """Load an AI model.
        
        Args:
            model_name: Name of the model to load
            use_quantized: Whether to use the quantized version if available
        """
        try:
            with Timer(f"Loading model {model_name}") as timer:
                # Check available memory
                available_memory = get_available_memory() / (1024 * 1024)  # Convert to MB
                self.logger.info(f"Available memory before loading model: {available_memory:.2f} MB")
                
                # Load the model using the model manager
                model = self.model_manager.load_onnx_model(model_name, use_quantized)
                
                # Update the current model
                self.model = model
                
                # Check memory after loading
                new_available_memory = get_available_memory() / (1024 * 1024)  # Convert to MB
                memory_used = available_memory - new_available_memory
                self.logger.info(f"Model loaded in {timer.elapsed:.2f}s, using {memory_used:.2f} MB of memory")
                
                return model
        except Exception as e:
            self.logger.error(f"Error loading model {model_name}: {e}")
            raise JennaException(f"Failed to load model {model_name}: {e}")
    
    async def optimize_model(self, model_path: Path, output_path: Optional[Path] = None):
        """Optimize an ONNX model.
        
        Args:
            model_path: Path to the ONNX model
            output_path: Optional path for the optimized model
            
        Returns:
            Path to the optimized model
        """
        try:
            # Optimize the model
            optimized_path = ModelOptimizer.optimize_onnx_model(model_path, output_path)
            self.logger.info(f"Model optimized and saved to {optimized_path}")
            return optimized_path
        except Exception as e:
            self.logger.error(f"Error optimizing model: {e}")
            raise JennaException(f"Failed to optimize model: {e}")
    
    async def quantize_model(self, model_path: Path, output_path: Optional[Path] = None):
        """Quantize an ONNX model.
        
        Args:
            model_path: Path to the ONNX model
            output_path: Optional path for the quantized model
            
        Returns:
            Path to the quantized model
        """
        try:
            # Quantize the model
            quantized_path = ModelOptimizer.quantize_onnx_model(model_path, output_path)
            self.logger.info(f"Model quantized and saved to {quantized_path}")
            return quantized_path
        except Exception as e:
            self.logger.error(f"Error quantizing model: {e}")
            raise JennaException(f"Failed to quantize model: {e}")
    
    async def update_settings(self, settings: Settings):
        """Update settings for the AI engine."""
        self.settings = settings
        # Apply any necessary changes based on new settings
        
        # Update model manager settings
        self.model_manager.memory_limit_mb = settings.performance_memory_limit_mb
    
    async def cleanup(self):
        """Clean up resources used by the AI engine."""
        self.logger.info("Cleaning up AI Engine resources...")
        
        # Clean up model manager
        if hasattr(self, 'model_manager'):
            self.model_manager.cleanup()
        
        self.logger.info("AI Engine cleanup completed")