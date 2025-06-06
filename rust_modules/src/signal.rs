use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;
use rustfft::{FftPlanner, num_complex::{Complex, Complex32}};
use ndarray::{Array1, ArrayView1};

/// Compute Fast Fourier Transform (FFT) on audio data
/// 
/// This function takes a numpy array of audio samples and computes the FFT
/// using the RustFFT library for improved performance.
#[pyfunction]
pub fn compute_fft(py: Python, input_buffer: &PyAny) -> PyResult<Py<PyAny>> {
    // Convert PyAny to numpy array
    let numpy = PyModule::import(py, "numpy")?;
    let array: &PyAny = numpy.getattr("array")?.call1((input_buffer,))?;
    
    // Get buffer as contiguous array of f32
    let buffer: Vec<f32> = array.extract()?;
    
    // Create complex input for FFT
    let mut complex_input: Vec<Complex32> = buffer
        .iter()
        .map(|&x| Complex32::new(x, 0.0))
        .collect();
    
    // Create FFT planner and get FFT instance
    let mut planner = FftPlanner::new();
    let fft = planner.plan_fft_forward(complex_input.len());
    
    // Perform FFT in-place
    fft.process(&mut complex_input);
    
    // Extract magnitudes
    let magnitudes: Vec<f32> = complex_input
        .iter()
        .map(|c| (c.re * c.re + c.im * c.im).sqrt())
        .collect();
    
    // Convert back to numpy array
    let result = numpy.getattr("array")?.call1((magnitudes,))?;
    Ok(result.into())
}

/// Apply a filter to audio data
/// 
/// This function applies a filter to audio data for noise reduction,
/// equalization, or other audio processing tasks.
#[pyfunction]
pub fn apply_filter(py: Python, input_buffer: &PyAny, filter_type: &str, params: Option<&PyDict>) -> PyResult<Py<PyAny>> {
    // Convert PyAny to numpy array
    let numpy = PyModule::import(py, "numpy")?;
    let array: &PyAny = numpy.getattr("array")?.call1((input_buffer,))?;
    
    // Get buffer as contiguous array of f32
    let buffer: Vec<f32> = array.extract()?;
    
    // Get parameters with defaults
    let params = params.unwrap_or_else(|| PyDict::new(py));
    let cutoff_low = params.get_item("cutoff_low").unwrap_or_else(|| py.None());
    let cutoff_high = params.get_item("cutoff_high").unwrap_or_else(|| py.None());
    let q_factor = params.get_item("q_factor").unwrap_or_else(|| py.None());
    
    let cutoff_low: Option<f32> = cutoff_low.extract().unwrap_or(None);
    let cutoff_high: Option<f32> = cutoff_high.extract().unwrap_or(None);
    let q_factor: f32 = q_factor.extract().unwrap_or(1.0);
    
    // Apply different filter types
    let filtered = match filter_type {
        "lowpass" => apply_lowpass_filter(&buffer, cutoff_high.unwrap_or(1000.0), q_factor),
        "highpass" => apply_highpass_filter(&buffer, cutoff_low.unwrap_or(500.0), q_factor),
        "bandpass" => apply_bandpass_filter(
            &buffer, 
            cutoff_low.unwrap_or(500.0), 
            cutoff_high.unwrap_or(2000.0), 
            q_factor
        ),
        "notch" => apply_notch_filter(
            &buffer, 
            cutoff_low.unwrap_or(500.0), 
            cutoff_high.unwrap_or(2000.0), 
            q_factor
        ),
        _ => return Err(PyValueError::new_err(format!("Unknown filter type: {}", filter_type)))
    };
    
    // Convert back to numpy array
    let result = numpy.getattr("array")?.call1((filtered,))?;
    Ok(result.into())
}

// Simple implementation of a low-pass filter
fn apply_lowpass_filter(buffer: &[f32], cutoff: f32, q: f32) -> Vec<f32> {
    // This is a simple first-order low-pass filter
    // In a real implementation, you would use more sophisticated filters
    let alpha = 0.1; // Simplified coefficient based on cutoff
    let mut output = vec![0.0; buffer.len()];
    
    if buffer.is_empty() {
        return output;
    }
    
    output[0] = buffer[0];
    for i in 1..buffer.len() {
        output[i] = output[i-1] + alpha * (buffer[i] - output[i-1]);
    }
    
    output
}

// Simple implementation of a high-pass filter
fn apply_highpass_filter(buffer: &[f32], cutoff: f32, q: f32) -> Vec<f32> {
    // This is a simple first-order high-pass filter
    let alpha = 0.9; // Simplified coefficient based on cutoff
    let mut output = vec![0.0; buffer.len()];
    
    if buffer.is_empty() {
        return output;
    }
    
    output[0] = buffer[0];
    for i in 1..buffer.len() {
        output[i] = alpha * (output[i-1] + buffer[i] - buffer[i-1]);
    }
    
    output
}

// Simple implementation of a band-pass filter
fn apply_bandpass_filter(buffer: &[f32], low_cutoff: f32, high_cutoff: f32, q: f32) -> Vec<f32> {
    // Apply low-pass and high-pass in sequence
    let highpassed = apply_highpass_filter(buffer, low_cutoff, q);
    apply_lowpass_filter(&highpassed, high_cutoff, q)
}

// Simple implementation of a notch filter
fn apply_notch_filter(buffer: &[f32], low_cutoff: f32, high_cutoff: f32, q: f32) -> Vec<f32> {
    // A notch filter can be implemented as the original signal minus the band-pass
    let bandpassed = apply_bandpass_filter(buffer, low_cutoff, high_cutoff, q);
    
    buffer.iter()
        .zip(bandpassed.iter())
        .map(|(&original, &filtered)| original - filtered)
        .collect()
}