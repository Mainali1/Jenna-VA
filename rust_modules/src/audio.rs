use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;
use cpal::traits::{DeviceTrait, HostTrait};
use ndarray::{Array1, ArrayView1};
use std::sync::{Arc, Mutex};
use std::collections::VecDeque;
use thiserror::Error;

#[derive(Error, Debug)]
pub enum AudioError {
    #[error("Audio device error: {0}")]
    DeviceError(String),
    
    #[error("Audio stream error: {0}")]
    StreamError(String),
    
    #[error("Audio format error: {0}")]
    FormatError(String),
}

/// A structure to hold audio buffer data
#[pyclass]
pub struct AudioBuffer {
    #[pyo3(get)]
    pub sample_rate: u32,
    #[pyo3(get)]
    pub channels: u16,
    buffer: Arc<Mutex<VecDeque<f32>>>,
    max_size: usize,
}

#[pymethods]
impl AudioBuffer {
    #[new]
    fn new(sample_rate: u32, channels: u16, max_size: usize) -> Self {
        AudioBuffer {
            sample_rate,
            channels,
            buffer: Arc::new(Mutex::new(VecDeque::with_capacity(max_size))),
            max_size,
        }
    }
    
    /// Add samples to the buffer
    fn add_samples(&mut self, samples: Vec<f32>) -> PyResult<()> {
        let mut buffer = self.buffer.lock().unwrap();
        for sample in samples {
            buffer.push_back(sample);
            if buffer.len() > self.max_size {
                buffer.pop_front();
            }
        }
        Ok(())
    }
    
    /// Get samples from the buffer
    fn get_samples(&self, count: usize) -> PyResult<Vec<f32>> {
        let buffer = self.buffer.lock().unwrap();
        let actual_count = std::cmp::min(count, buffer.len());
        let samples: Vec<f32> = buffer.iter().take(actual_count).cloned().collect();
        Ok(samples)
    }
    
    /// Clear the buffer
    fn clear(&mut self) -> PyResult<()> {
        let mut buffer = self.buffer.lock().unwrap();
        buffer.clear();
        Ok(())
    }
    
    /// Get the current buffer size
    fn len(&self) -> PyResult<usize> {
        let buffer = self.buffer.lock().unwrap();
        Ok(buffer.len())
    }
}

/// Process audio buffer with Rust for improved performance
/// 
/// This function takes a numpy array of audio samples and processes them
/// with various optimizations.
#[pyfunction]
pub fn process_audio_buffer(py: Python, input_buffer: &PyAny) -> PyResult<Py<PyAny>> {
    // Convert PyAny to numpy array
    let numpy = PyModule::import(py, "numpy")?;
    let array: &PyAny = numpy.getattr("array")?.call1((input_buffer,))?;
    
    // Get buffer as contiguous array of f32
    let buffer: Vec<f32> = array.extract()?;
    
    // Process the buffer (example: apply gain)
    let gain = 1.2;
    let processed: Vec<f32> = buffer.iter().map(|&x| x * gain).collect();
    
    // Convert back to numpy array
    let result = numpy.getattr("array")?.call1((processed,))?;
    Ok(result.into())
}

/// Get available input devices
#[pyfunction]
pub fn get_input_devices() -> PyResult<Vec<String>> {
    let host = cpal::default_host();
    match host.input_devices() {
        Ok(devices) => {
            let device_names: Vec<String> = devices
                .filter_map(|device| device.name().ok())
                .collect();
            Ok(device_names)
        },
        Err(err) => Err(PyValueError::new_err(format!("Failed to get input devices: {}", err)))
    }
}

/// Get available output devices
#[pyfunction]
pub fn get_output_devices() -> PyResult<Vec<String>> {
    let host = cpal::default_host();
    match host.output_devices() {
        Ok(devices) => {
            let device_names: Vec<String> = devices
                .filter_map(|device| device.name().ok())
                .collect();
            Ok(device_names)
        },
        Err(err) => Err(PyValueError::new_err(format!("Failed to get output devices: {}", err)))
    }
}