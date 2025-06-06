use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;
use porcupine::{Porcupine, PorcupineBuilder};
use std::path::Path;
use std::sync::{Arc, Mutex};

/// Wake word detector using Porcupine
#[pyclass]
pub struct WakeWordDetector {
    porcupine: Arc<Mutex<Option<Porcupine>>>,
    sensitivity: f32,
    is_active: bool,
}

#[pymethods]
impl WakeWordDetector {
    /// Create a new wake word detector
    #[new]
    fn new(model_path: Option<String>, keyword_path: Option<String>, sensitivity: Option<f32>) -> PyResult<Self> {
        let sensitivity = sensitivity.unwrap_or(0.5);
        
        Ok(WakeWordDetector {
            porcupine: Arc::new(Mutex::new(None)),
            sensitivity,
            is_active: false,
        })
    }
    
    /// Initialize the wake word detector with the given model and keyword files
    fn initialize(&mut self, model_path: String, keyword_path: String) -> PyResult<()> {
        let model_path = Path::new(&model_path);
        let keyword_path = Path::new(&keyword_path);
        
        if !model_path.exists() {
            return Err(PyValueError::new_err(format!("Model file not found: {}", model_path.display())));
        }
        
        if !keyword_path.exists() {
            return Err(PyValueError::new_err(format!("Keyword file not found: {}", keyword_path.display())));
        }
        
        match PorcupineBuilder::new_with_keyword_paths(
            model_path.to_str().unwrap(),
            &[keyword_path.to_str().unwrap()],
            &[self.sensitivity]
        ).build() {
            Ok(porcupine) => {
                let mut guard = self.porcupine.lock().unwrap();
                *guard = Some(porcupine);
                self.is_active = true;
                Ok(())
            },
            Err(err) => Err(PyValueError::new_err(format!("Failed to initialize Porcupine: {}", err)))
        }
    }
    
    /// Process audio frame and check for wake word
    fn process(&self, audio_frame: Vec<i16>) -> PyResult<bool> {
        let guard = self.porcupine.lock().unwrap();
        
        match &*guard {
            Some(porcupine) => {
                if audio_frame.len() != porcupine.frame_length() {
                    return Err(PyValueError::new_err(
                        format!(
                            "Audio frame size ({}) doesn't match required size ({})", 
                            audio_frame.len(), 
                            porcupine.frame_length()
                        )
                    ));
                }
                
                match porcupine.process(&audio_frame) {
                    Ok(keyword_index) => Ok(keyword_index >= 0),
                    Err(err) => Err(PyValueError::new_err(format!("Processing error: {}", err)))
                }
            },
            None => Err(PyValueError::new_err("Porcupine not initialized"))
        }
    }
    
    /// Get the required frame length for audio processing
    fn get_frame_length(&self) -> PyResult<usize> {
        let guard = self.porcupine.lock().unwrap();
        
        match &*guard {
            Some(porcupine) => Ok(porcupine.frame_length()),
            None => Err(PyValueError::new_err("Porcupine not initialized"))
        }
    }
    
    /// Get the required sample rate for audio processing
    fn get_sample_rate(&self) -> PyResult<u32> {
        let guard = self.porcupine.lock().unwrap();
        
        match &*guard {
            Some(porcupine) => Ok(porcupine.sample_rate()),
            None => Err(PyValueError::new_err("Porcupine not initialized"))
        }
    }
    
    /// Check if the detector is active
    fn is_active(&self) -> bool {
        self.is_active
    }
    
    /// Set the sensitivity of the wake word detector
    fn set_sensitivity(&mut self, sensitivity: f32) -> PyResult<()> {
        if sensitivity < 0.0 || sensitivity > 1.0 {
            return Err(PyValueError::new_err("Sensitivity must be between 0.0 and 1.0"));
        }
        
        self.sensitivity = sensitivity;
        Ok(())
    }
    
    /// Release resources
    fn release(&mut self) -> PyResult<()> {
        let mut guard = self.porcupine.lock().unwrap();
        *guard = None;
        self.is_active = false;
        Ok(())
    }
}