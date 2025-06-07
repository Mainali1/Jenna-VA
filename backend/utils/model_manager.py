"""Model Management System for Jenna Voice Assistant.

This module provides utilities for managing AI models, including:
- Model loading and unloading
- Model caching with LRU policy
- ONNX integration and optimization
- Model quantization
"""

import os
import time
import logging
import threading
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple, Union, Callable
from functools import lru_cache
from collections import OrderedDict
import json

import numpy as np
import onnxruntime as ort
from onnxruntime.quantization import quantize_dynamic, QuantType

from ..utils.helpers import get_available_memory, hash_string, Timer, ensure_directory
from ..core.logger import get_logger


logger = get_logger(__name__)


class LRUCache:
    """LRU Cache implementation for model caching."""
    
    def __init__(self, capacity: int):
        """Initialize the LRU cache.
        
        Args:
            capacity: Maximum number of items to store in the cache
        """
        self.capacity = capacity
        self.cache = OrderedDict()
        self.lock = threading.RLock()
    
    def get(self, key: str) -> Optional[Any]:
        """Get an item from the cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached item or None if not found
        """
        with self.lock:
            if key not in self.cache:
                return None
            
            # Move to end (most recently used)
            self.cache.move_to_end(key)
            return self.cache[key]
    
    def put(self, key: str, value: Any) -> None:
        """Add an item to the cache.
        
        Args:
            key: Cache key
            value: Item to cache
        """
        with self.lock:
            if key in self.cache:
                # Move to end (most recently used)
                self.cache.move_to_end(key)
            
            self.cache[key] = value
            
            # Remove oldest item if over capacity
            if len(self.cache) > self.capacity:
                self.cache.popitem(last=False)
    
    def remove(self, key: str) -> None:
        """Remove an item from the cache.
        
        Args:
            key: Cache key
        """
        with self.lock:
            if key in self.cache:
                del self.cache[key]
    
    def clear(self) -> None:
        """Clear the cache."""
        with self.lock:
            self.cache.clear()
    
    def __len__(self) -> int:
        """Get the number of items in the cache."""
        return len(self.cache)
    
    def keys(self) -> List[str]:
        """Get all keys in the cache."""
        with self.lock:
            return list(self.cache.keys())


class ModelManager:
    """Manager for AI models with caching and optimization."""
    
    def __init__(self, models_dir: Path, cache_size: int = 5, memory_limit_mb: int = 1024):
        """Initialize the model manager.
        
        Args:
            models_dir: Directory to store models
            cache_size: Maximum number of models to keep in memory
            memory_limit_mb: Memory limit for models in MB
        """
        self.models_dir = ensure_directory(models_dir)
        self.cache = LRUCache(cache_size)
        self.memory_limit_mb = memory_limit_mb
        self.model_metadata = {}
        self.metadata_file = self.models_dir / "model_metadata.json"
        self.load_metadata()
        
        # Set ONNX Runtime session options
        self.session_options = ort.SessionOptions()
        self.session_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        self.session_options.enable_cpu_mem_arena = True
        self.session_options.enable_mem_pattern = True
        
        # Set execution providers
        self.providers = ['CPUExecutionProvider']
        
        # Check for CUDA availability
        if 'CUDAExecutionProvider' in ort.get_available_providers():
            self.providers.insert(0, 'CUDAExecutionProvider')
            logger.info("CUDA execution provider available for ONNX Runtime")
    
    def load_metadata(self) -> None:
        """Load model metadata from file."""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    self.model_metadata = json.load(f)
                logger.info(f"Loaded metadata for {len(self.model_metadata)} models")
            except Exception as e:
                logger.error(f"Error loading model metadata: {e}")
                self.model_metadata = {}
    
    def save_metadata(self) -> None:
        """Save model metadata to file."""
        try:
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.model_metadata, f, indent=2)
            logger.debug("Saved model metadata")
        except Exception as e:
            logger.error(f"Error saving model metadata: {e}")
    
    def get_model_path(self, model_name: str, model_type: str) -> Path:
        """Get the path for a model file.
        
        Args:
            model_name: Name of the model
            model_type: Type of the model (e.g., 'onnx', 'pytorch')
            
        Returns:
            Path to the model file
        """
        model_dir = ensure_directory(self.models_dir / model_type)
        return model_dir / f"{model_name}.{model_type}"
    
    def get_quantized_model_path(self, model_name: str) -> Path:
        """Get the path for a quantized ONNX model file.
        
        Args:
            model_name: Name of the model
            
        Returns:
            Path to the quantized model file
        """
        model_dir = ensure_directory(self.models_dir / "onnx")
        return model_dir / f"{model_name}_quantized.onnx"
    
    def quantize_model(self, model_path: Path, output_path: Optional[Path] = None) -> Path:
        """Quantize an ONNX model for better performance and smaller size.
        
        Args:
            model_path: Path to the ONNX model
            output_path: Optional path for the quantized model
            
        Returns:
            Path to the quantized model
        """
        if output_path is None:
            output_path = model_path.with_name(f"{model_path.stem}_quantized.onnx")
        
        with Timer("Model quantization") as timer:
            quantize_dynamic(str(model_path), str(output_path), weight_type=QuantType.QUInt8)
        
        logger.info(f"Quantized model saved to {output_path} (took {timer.elapsed:.2f}s)")
        
        # Update metadata
        model_name = model_path.stem
        if model_name in self.model_metadata:
            self.model_metadata[model_name]["quantized"] = True
            self.model_metadata[model_name]["quantized_path"] = str(output_path)
            self.model_metadata[model_name]["quantized_size"] = output_path.stat().st_size
            self.save_metadata()
        
        return output_path
    
    def load_onnx_model(self, model_name: str, use_quantized: bool = True) -> ort.InferenceSession:
        """Load an ONNX model.
        
        Args:
            model_name: Name of the model
            use_quantized: Whether to use the quantized version if available
            
        Returns:
            ONNX Runtime inference session
        """
        # Generate cache key
        cache_key = f"onnx_{model_name}_{use_quantized}"
        
        # Check cache first
        cached_model = self.cache.get(cache_key)
        if cached_model is not None:
            logger.debug(f"Using cached model: {model_name}")
            return cached_model
        
        # Determine model path
        if use_quantized and model_name in self.model_metadata and self.model_metadata[model_name].get("quantized", False):
            model_path = Path(self.model_metadata[model_name]["quantized_path"])
            logger.info(f"Loading quantized model: {model_name}")
        else:
            model_path = self.get_model_path(model_name, "onnx")
            logger.info(f"Loading original model: {model_name}")
        
        # Check if model exists
        if not model_path.exists():
            raise FileNotFoundError(f"Model not found: {model_path}")
        
        # Load the model
        with Timer(f"Loading model {model_name}") as timer:
            session = ort.InferenceSession(
                str(model_path), 
                sess_options=self.session_options,
                providers=self.providers
            )
        
        logger.info(f"Loaded model {model_name} in {timer.elapsed:.2f}s")
        
        # Update metadata
        if model_name not in self.model_metadata:
            self.model_metadata[model_name] = {}
        
        self.model_metadata[model_name].update({
            "last_used": time.time(),
            "load_time": timer.elapsed,
            "size": model_path.stat().st_size,
            "path": str(model_path),
        })
        self.save_metadata()
        
        # Cache the model
        self.cache.put(cache_key, session)
        
        return session
    
    def run_inference(self, model_name: str, inputs: Dict[str, np.ndarray], use_quantized: bool = True) -> Dict[str, np.ndarray]:
        """Run inference with an ONNX model.
        
        Args:
            model_name: Name of the model
            inputs: Dictionary of input names to numpy arrays
            use_quantized: Whether to use the quantized version if available
            
        Returns:
            Dictionary of output names to numpy arrays
        """
        # Load the model
        session = self.load_onnx_model(model_name, use_quantized)
        
        # Run inference
        with Timer(f"Inference with {model_name}") as timer:
            outputs = session.run(None, inputs)
        
        logger.debug(f"Inference with {model_name} took {timer.elapsed:.4f}s")
        
        # Update metadata
        if model_name in self.model_metadata:
            self.model_metadata[model_name]["last_used"] = time.time()
            self.model_metadata[model_name]["inference_count"] = self.model_metadata[model_name].get("inference_count", 0) + 1
            self.model_metadata[model_name]["avg_inference_time"] = (
                (self.model_metadata[model_name].get("avg_inference_time", 0) * 
                 (self.model_metadata[model_name]["inference_count"] - 1) + 
                 timer.elapsed) / self.model_metadata[model_name]["inference_count"]
            )
            self.save_metadata()
        
        # Create a dictionary of outputs
        output_names = [output.name for output in session.get_outputs()]
        return {name: output for name, output in zip(output_names, outputs)}
    
    def unload_model(self, model_name: str) -> None:
        """Unload a model from memory.
        
        Args:
            model_name: Name of the model
        """
        # Remove from cache
        self.cache.remove(f"onnx_{model_name}_True")
        self.cache.remove(f"onnx_{model_name}_False")
        
        logger.info(f"Unloaded model: {model_name}")
    
    def get_model_info(self, model_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a model.
        
        Args:
            model_name: Name of the model
            
        Returns:
            Dictionary of model information or None if not found
        """
        return self.model_metadata.get(model_name)
    
    def list_models(self) -> List[str]:
        """List all available models.
        
        Returns:
            List of model names
        """
        return list(self.model_metadata.keys())
    
    def cleanup(self) -> None:
        """Clean up resources used by the model manager."""
        # Clear the cache
        self.cache.clear()
        
        # Save metadata
        self.save_metadata()
        
        logger.info("Model manager cleaned up")


# Decorator for caching model inference results
def cache_inference(maxsize: int = 128):
    """Decorator for caching model inference results.
    
    Args:
        maxsize: Maximum size of the cache
        
    Returns:
        Decorated function
    """
    def decorator(func):
        cache = lru_cache(maxsize=maxsize)(func)
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate a cache key based on the input data
            cache_key = args
            if kwargs:
                cache_key = cache_key + tuple(sorted(kwargs.items()))
            
            return cache(*args, **kwargs)
        
        # Add a method to clear the cache
        wrapper.cache_clear = cache.cache_clear
        wrapper.cache_info = cache.cache_info
        
        return wrapper
    
    return decorator