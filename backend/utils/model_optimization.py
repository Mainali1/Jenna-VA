"""Model Optimization Utilities for Jenna Voice Assistant.

This module provides utilities for optimizing AI models, including:
- ONNX model conversion
- Model quantization
- Model pruning
- Model compression
"""

import os
import time
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple, Union, Callable

import numpy as np
import onnx
import onnxruntime as ort
from onnxruntime.quantization import quantize_dynamic, quantize_static, QuantType

from ..utils.helpers import Timer, ensure_directory
from ..core.logger import get_logger


logger = get_logger(__name__)


class ModelOptimizer:
    """Utilities for optimizing AI models."""
    
    @staticmethod
    def convert_to_onnx(model, input_names: List[str], output_names: List[str], 
                       dynamic_axes: Optional[Dict[str, Dict[int, str]]] = None,
                       input_sample: Optional[Union[np.ndarray, Dict[str, np.ndarray]]] = None,
                       output_path: Optional[Path] = None) -> Path:
        """Convert a PyTorch or TensorFlow model to ONNX format.
        
        Args:
            model: PyTorch or TensorFlow model
            input_names: Names of the input tensors
            output_names: Names of the output tensors
            dynamic_axes: Dictionary of dynamic axes for inputs/outputs
            input_sample: Sample input for tracing the model
            output_path: Path to save the ONNX model
            
        Returns:
            Path to the ONNX model
        """
        import torch
        
        if output_path is None:
            raise ValueError("output_path must be specified")
        
        # Ensure the parent directory exists
        ensure_directory(output_path.parent)
        
        # Convert to ONNX
        with Timer("ONNX conversion") as timer:
            if isinstance(model, torch.nn.Module):
                # PyTorch model
                model.eval()
                
                if input_sample is None:
                    raise ValueError("input_sample must be provided for PyTorch models")
                
                # Handle different input types
                if isinstance(input_sample, dict):
                    # Dictionary of named inputs
                    torch.onnx.export(
                        model,
                        tuple(input_sample.values()),
                        output_path,
                        input_names=input_names,
                        output_names=output_names,
                        dynamic_axes=dynamic_axes,
                        opset_version=12,
                        do_constant_folding=True,
                        export_params=True,
                        verbose=False
                    )
                else:
                    # Single input tensor or tuple of tensors
                    torch.onnx.export(
                        model,
                        input_sample,
                        output_path,
                        input_names=input_names,
                        output_names=output_names,
                        dynamic_axes=dynamic_axes,
                        opset_version=12,
                        do_constant_folding=True,
                        export_params=True,
                        verbose=False
                    )
            else:
                # Assume TensorFlow model
                try:
                    import tensorflow as tf
                    from tensorflow.python.keras.saving import saving_utils
                    
                    # Check if it's a Keras model
                    if isinstance(model, tf.keras.Model):
                        # Convert Keras model to ONNX
                        import tf2onnx
                        
                        # Get model signature
                        input_signature = None
                        if input_sample is not None:
                            if isinstance(input_sample, dict):
                                # Convert dict to TensorSpec
                                input_signature = [
                                    tf.TensorSpec(v.shape, tf.float32, name=k)
                                    for k, v in input_sample.items()
                                ]
                            else:
                                # Single input or tuple
                                if not isinstance(input_sample, (list, tuple)):
                                    input_sample = [input_sample]
                                
                                input_signature = [
                                    tf.TensorSpec(v.shape, tf.float32)
                                    for v in input_sample
                                ]
                        
                        # Convert to ONNX
                        model_proto, _ = tf2onnx.convert.from_keras(
                            model,
                            input_signature=input_signature,
                            opset=12,
                            output_path=str(output_path)
                        )
                    else:
                        raise TypeError("Unsupported model type")
                except ImportError:
                    raise ImportError("TensorFlow and tf2onnx are required for TensorFlow model conversion")
        
        logger.info(f"Converted model to ONNX format in {timer.elapsed:.2f}s")
        logger.info(f"ONNX model saved to {output_path}")
        
        return output_path
    
    @staticmethod
    def optimize_onnx_model(model_path: Path, output_path: Optional[Path] = None) -> Path:
        """Optimize an ONNX model using ONNX Runtime.
        
        Args:
            model_path: Path to the ONNX model
            output_path: Path to save the optimized model
            
        Returns:
            Path to the optimized model
        """
        if output_path is None:
            output_path = model_path.with_name(f"{model_path.stem}_optimized.onnx")
        
        # Ensure the parent directory exists
        ensure_directory(output_path.parent)
        
        # Load the model
        model = onnx.load(str(model_path))
        
        # Optimize the model
        with Timer("ONNX optimization") as timer:
            # Check and optimize the model
            try:
                # Basic model check
                onnx.checker.check_model(model)
                
                # Optimize with ONNX Runtime
                session_options = ort.SessionOptions()
                session_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
                session_options.optimized_model_filepath = str(output_path)
                _ = ort.InferenceSession(str(model_path), session_options)
                
                # Additional optimizations with ONNX
                from onnxruntime.transformers import optimizer
                optimized_model = optimizer.optimize_model(
                    str(model_path),
                    model_type='bert',  # Can be 'bert', 'gpt2', 'vit', etc.
                    num_heads=12,       # Adjust based on your model
                    hidden_size=768     # Adjust based on your model
                )
                optimized_model.save_model_to_file(str(output_path))
                
            except Exception as e:
                logger.warning(f"Advanced optimization failed: {e}. Using basic optimization.")
                # Fallback to basic optimization
                if not os.path.exists(output_path):
                    import shutil
                    shutil.copy(model_path, output_path)
        
        logger.info(f"Optimized ONNX model in {timer.elapsed:.2f}s")
        logger.info(f"Optimized model saved to {output_path}")
        
        return output_path
    
    @staticmethod
    def quantize_onnx_model(model_path: Path, output_path: Optional[Path] = None, 
                           quantization_type: str = "dynamic", 
                           calibration_data: Optional[Dict[str, np.ndarray]] = None) -> Path:
        """Quantize an ONNX model for better performance and smaller size.
        
        Args:
            model_path: Path to the ONNX model
            output_path: Path to save the quantized model
            quantization_type: Type of quantization ('dynamic' or 'static')
            calibration_data: Calibration data for static quantization
            
        Returns:
            Path to the quantized model
        """
        if output_path is None:
            output_path = model_path.with_name(f"{model_path.stem}_quantized.onnx")
        
        # Ensure the parent directory exists
        ensure_directory(output_path.parent)
        
        # Quantize the model
        with Timer("ONNX quantization") as timer:
            if quantization_type.lower() == "dynamic":
                # Dynamic quantization (no calibration data needed)
                quantize_dynamic(
                    str(model_path),
                    str(output_path),
                    weight_type=QuantType.QUInt8
                )
            elif quantization_type.lower() == "static" and calibration_data is not None:
                # Static quantization (requires calibration data)
                from onnxruntime.quantization import CalibrationDataReader
                
                # Create a calibration data reader
                class CalibrationData(CalibrationDataReader):
                    def __init__(self, data):
                        self.data = data
                        self.index = 0
                        self.input_names = list(data.keys())
                    
                    def get_next(self):
                        if self.index >= len(next(iter(self.data.values()))):
                            return None
                        
                        result = {name: data[self.index] for name, data in self.data.items()}
                        self.index += 1
                        return result
                    
                    def rewind(self):
                        self.index = 0
                
                # Perform static quantization
                calibration_reader = CalibrationData(calibration_data)
                quantize_static(
                    str(model_path),
                    str(output_path),
                    calibration_reader
                )
            else:
                raise ValueError("For static quantization, calibration_data must be provided")
        
        logger.info(f"Quantized ONNX model in {timer.elapsed:.2f}s using {quantization_type} quantization")
        logger.info(f"Quantized model saved to {output_path}")
        
        return output_path
    
    @staticmethod
    def benchmark_model(model_path: Path, input_data: Dict[str, np.ndarray], num_runs: int = 10) -> Dict[str, Any]:
        """Benchmark an ONNX model's performance.
        
        Args:
            model_path: Path to the ONNX model
            input_data: Dictionary of input names to numpy arrays
            num_runs: Number of inference runs for benchmarking
            
        Returns:
            Dictionary with benchmark results
        """
        # Create an ONNX Runtime session
        session_options = ort.SessionOptions()
        session_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        
        # Check for available providers
        providers = ['CPUExecutionProvider']
        if 'CUDAExecutionProvider' in ort.get_available_providers():
            providers.insert(0, 'CUDAExecutionProvider')
        
        session = ort.InferenceSession(
            str(model_path), 
            sess_options=session_options,
            providers=providers
        )
        
        # Warm-up run
        _ = session.run(None, input_data)
        
        # Benchmark runs
        latencies = []
        with Timer("Benchmark") as timer:
            for _ in range(num_runs):
                start = time.time()
                _ = session.run(None, input_data)
                latencies.append(time.time() - start)
        
        # Calculate statistics
        avg_latency = sum(latencies) / len(latencies)
        min_latency = min(latencies)
        max_latency = max(latencies)
        p95_latency = sorted(latencies)[int(0.95 * len(latencies))]
        
        # Get model size
        model_size = os.path.getsize(model_path)
        
        # Get model metadata
        model = onnx.load(str(model_path))
        model_metadata = {}
        if model.metadata_props:
            for prop in model.metadata_props:
                model_metadata[prop.key] = prop.value
        
        # Get input and output shapes
        inputs = []
        for input in session.get_inputs():
            inputs.append({
                "name": input.name,
                "shape": input.shape,
                "type": input.type
            })
        
        outputs = []
        for output in session.get_outputs():
            outputs.append({
                "name": output.name,
                "shape": output.shape,
                "type": output.type
            })
        
        # Return benchmark results
        return {
            "model_path": str(model_path),
            "model_size": model_size,
            "model_size_mb": model_size / (1024 * 1024),
            "providers": providers,
            "num_runs": num_runs,
            "avg_latency": avg_latency,
            "min_latency": min_latency,
            "max_latency": max_latency,
            "p95_latency": p95_latency,
            "throughput": 1.0 / avg_latency,
            "inputs": inputs,
            "outputs": outputs,
            "metadata": model_metadata
        }