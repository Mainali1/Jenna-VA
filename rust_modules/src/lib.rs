use pyo3::prelude::*;

mod audio;
mod signal;
mod wake_word;
mod speech;

/// Jenna Voice Assistant Rust modules
/// 
/// This module provides high-performance audio processing, wake word detection,
/// and speech recognition capabilities for the Jenna Voice Assistant.
#[pymodule]
fn jenna_rust(_py: Python, m: &PyModule) -> PyResult<()> {
    // Register audio module
    m.add_class::<audio::AudioBuffer>()?;
    m.add_function(wrap_pyfunction!(audio::get_input_devices, m)?)?;
    m.add_function(wrap_pyfunction!(audio::get_output_devices, m)?)?;
    
    // Register signal processing module
    m.add_function(wrap_pyfunction!(signal::compute_fft, m)?)?;
    m.add_function(wrap_pyfunction!(signal::apply_filter, m)?)?;
    
    // Register wake word detection module
    m.add_class::<wake_word::WakeWordDetector>()?;
    
    // Register speech recognition module
    m.add_class::<speech::SpeechRecognizer>()?;
    m.add_class::<speech::TextToSpeech>()?;
    
    Ok(())
}