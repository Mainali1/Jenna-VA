"""Rust Bridge Module for Jenna Voice Assistant.

This module provides a bridge between the Python codebase and the Rust modules
for high-performance audio processing, wake word detection, and speech recognition.
"""

import os
import sys
import logging
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Union, Any

import numpy as np

# Setup logging
logger = logging.getLogger(__name__)

# Try to import the Rust module
try:
    # Add the rust_modules directory to the Python path
    rust_module_path = Path(__file__).parent.parent.parent / "rust_modules"
    if rust_module_path.exists() and str(rust_module_path) not in sys.path:
        sys.path.append(str(rust_module_path))
    
    # Import the Rust module
    import jenna_rust
    RUST_AVAILABLE = True
    logger.info("Rust modules loaded successfully")
except ImportError as e:
    RUST_AVAILABLE = False
    logger.warning(f"Failed to load Rust modules: {e}. Falling back to Python implementations.")


class AudioProcessor:
    """Audio processing using Rust for improved performance."""
    
    def __init__(self):
        self.buffer = None if not RUST_AVAILABLE else jenna_rust.AudioBuffer()
    
    def process_audio(self, audio_data: np.ndarray) -> np.ndarray:
        """Process audio data using Rust implementation if available.
        
        Args:
            audio_data: Audio data as numpy array
            
        Returns:
            Processed audio data
        """
        if not RUST_AVAILABLE:
            # Fallback to Python implementation
            return audio_data
        
        # Use Rust implementation
        if self.buffer is None:
            self.buffer = jenna_rust.AudioBuffer()
        
        # Process audio data using Rust
        self.buffer.add_samples(audio_data)
        return self.buffer.get_processed_data()
    
    def get_input_devices(self) -> List[Dict[str, str]]:
        """Get available audio input devices.
        
        Returns:
            List of input devices with name and id
        """
        if not RUST_AVAILABLE:
            # Fallback to Python implementation
            return []
        
        # Use Rust implementation
        return jenna_rust.get_input_devices()
    
    def get_output_devices(self) -> List[Dict[str, str]]:
        """Get available audio output devices.
        
        Returns:
            List of output devices with name and id
        """
        if not RUST_AVAILABLE:
            # Fallback to Python implementation
            return []
        
        # Use Rust implementation
        return jenna_rust.get_output_devices()


class SignalProcessor:
    """Signal processing using Rust for improved performance."""
    
    def __init__(self):
        self.rust_available = RUST_AVAILABLE
    
    def compute_fft(self, audio_data: np.ndarray) -> np.ndarray:
        """Compute FFT using Rust implementation if available.
        
        Args:
            audio_data: Audio data as numpy array
            
        Returns:
            FFT magnitudes
        """
        if not self.rust_available:
            # Fallback to Python implementation using numpy
            import numpy as np
            fft = np.fft.rfft(audio_data)
            return np.abs(fft)
        
        # Use Rust implementation
        return jenna_rust.compute_fft(audio_data)
    
    def apply_filter(self, audio_data: np.ndarray, filter_type: str, **kwargs) -> np.ndarray:
        """Apply filter using Rust implementation if available.
        
        Args:
            audio_data: Audio data as numpy array
            filter_type: Type of filter to apply (lowpass, highpass, bandpass, notch)
            **kwargs: Filter parameters
            
        Returns:
            Filtered audio data
        """
        if not self.rust_available:
            # Fallback to Python implementation
            # This is a simple placeholder implementation
            return audio_data
        
        # Use Rust implementation
        return jenna_rust.apply_filter(audio_data, filter_type, kwargs)


class WakeWordDetector:
    """Wake word detection using Porcupine via Rust."""
    
    def __init__(self, model_path: Optional[str] = None, keyword_path: Optional[str] = None, sensitivity: float = 0.5):
        self.rust_available = RUST_AVAILABLE
        self.model_path = model_path
        self.keyword_path = keyword_path
        self.sensitivity = sensitivity
        self.detector = None
        
        if self.rust_available:
            try:
                self.detector = jenna_rust.WakeWordDetector(model_path, keyword_path, sensitivity)
            except Exception as e:
                logger.error(f"Failed to initialize wake word detector: {e}")
                self.rust_available = False
    
    def initialize(self, model_path: str, keyword_path: str) -> bool:
        """Initialize the wake word detector.
        
        Args:
            model_path: Path to the Porcupine model file
            keyword_path: Path to the keyword file
            
        Returns:
            True if initialization was successful, False otherwise
        """
        self.model_path = model_path
        self.keyword_path = keyword_path
        
        if not self.rust_available:
            # Fallback to Python implementation
            logger.warning("Rust not available, wake word detection will not work")
            return False
        
        try:
            if self.detector is None:
                self.detector = jenna_rust.WakeWordDetector(None, None, self.sensitivity)
            
            self.detector.initialize(model_path, keyword_path)
            return True
        except Exception as e:
            logger.error(f"Failed to initialize wake word detector: {e}")
            return False
    
    def process(self, audio_frame: np.ndarray) -> bool:
        """Process audio frame and check for wake word.
        
        Args:
            audio_frame: Audio frame as numpy array of int16 values
            
        Returns:
            True if wake word detected, False otherwise
        """
        if not self.rust_available or self.detector is None:
            # Fallback to Python implementation
            return False
        
        try:
            # Convert to int16 if needed
            if audio_frame.dtype != np.int16:
                audio_frame = (audio_frame * 32767).astype(np.int16)
            
            return self.detector.process(audio_frame)
        except Exception as e:
            logger.error(f"Error processing audio frame: {e}")
            return False
    
    def get_frame_length(self) -> int:
        """Get the required frame length for audio processing.
        
        Returns:
            Frame length in samples
        """
        if not self.rust_available or self.detector is None:
            # Default frame length
            return 512
        
        try:
            return self.detector.get_frame_length()
        except Exception as e:
            logger.error(f"Error getting frame length: {e}")
            return 512
    
    def get_sample_rate(self) -> int:
        """Get the required sample rate for audio processing.
        
        Returns:
            Sample rate in Hz
        """
        if not self.rust_available or self.detector is None:
            # Default sample rate
            return 16000
        
        try:
            return self.detector.get_sample_rate()
        except Exception as e:
            logger.error(f"Error getting sample rate: {e}")
            return 16000
    
    def is_active(self) -> bool:
        """Check if the detector is active.
        
        Returns:
            True if active, False otherwise
        """
        if not self.rust_available or self.detector is None:
            return False
        
        return self.detector.is_active()
    
    def set_sensitivity(self, sensitivity: float) -> bool:
        """Set the sensitivity of the wake word detector.
        
        Args:
            sensitivity: Sensitivity value between 0.0 and 1.0
            
        Returns:
            True if successful, False otherwise
        """
        self.sensitivity = sensitivity
        
        if not self.rust_available or self.detector is None:
            return False
        
        try:
            self.detector.set_sensitivity(sensitivity)
            return True
        except Exception as e:
            logger.error(f"Error setting sensitivity: {e}")
            return False
    
    def release(self) -> bool:
        """Release resources.
        
        Returns:
            True if successful, False otherwise
        """
        if not self.rust_available or self.detector is None:
            return False
        
        try:
            self.detector.release()
            return True
        except Exception as e:
            logger.error(f"Error releasing resources: {e}")
            return False


class SpeechRecognizer:
    """Speech recognition using Vosk via Rust."""
    
    def __init__(self, model_path: str, sample_rate: int = 16000):
        self.rust_available = RUST_AVAILABLE
        self.model_path = model_path
        self.sample_rate = sample_rate
        self.recognizer = None
        
        if self.rust_available:
            try:
                self.recognizer = jenna_rust.SpeechRecognizer(model_path, sample_rate)
            except Exception as e:
                logger.error(f"Failed to initialize speech recognizer: {e}")
                self.rust_available = False
    
    def initialize(self) -> bool:
        """Initialize the speech recognizer.
        
        Returns:
            True if initialization was successful, False otherwise
        """
        if not self.rust_available:
            # Fallback to Python implementation
            logger.warning("Rust not available, speech recognition will not work")
            return False
        
        try:
            if self.recognizer is None:
                self.recognizer = jenna_rust.SpeechRecognizer(self.model_path, self.sample_rate)
            
            self.recognizer.initialize()
            return True
        except Exception as e:
            logger.error(f"Failed to initialize speech recognizer: {e}")
            return False
    
    def process(self, audio_frame: np.ndarray) -> Optional[str]:
        """Process audio frame and return recognized text.
        
        Args:
            audio_frame: Audio frame as numpy array of int16 values
            
        Returns:
            Recognized text or None if no recognition result
        """
        if not self.rust_available or self.recognizer is None:
            # Fallback to Python implementation
            return None
        
        try:
            # Convert to int16 if needed
            if audio_frame.dtype != np.int16:
                audio_frame = (audio_frame * 32767).astype(np.int16)
            
            return self.recognizer.process(audio_frame)
        except Exception as e:
            logger.error(f"Error processing audio frame: {e}")
            return None
    
    def reset(self) -> bool:
        """Reset the recognizer state.
        
        Returns:
            True if successful, False otherwise
        """
        if not self.rust_available or self.recognizer is None:
            return False
        
        try:
            self.recognizer.reset()
            return True
        except Exception as e:
            logger.error(f"Error resetting recognizer: {e}")
            return False
    
    def set_sample_rate(self, sample_rate: int) -> bool:
        """Set the sample rate for audio processing.
        
        Args:
            sample_rate: Sample rate in Hz
            
        Returns:
            True if successful, False otherwise
        """
        self.sample_rate = sample_rate
        
        if not self.rust_available or self.recognizer is None:
            return False
        
        try:
            self.recognizer.set_sample_rate(sample_rate)
            return True
        except Exception as e:
            logger.error(f"Error setting sample rate: {e}")
            return False
    
    def get_sample_rate(self) -> int:
        """Get the sample rate for audio processing.
        
        Returns:
            Sample rate in Hz
        """
        if not self.rust_available or self.recognizer is None:
            return self.sample_rate
        
        return self.recognizer.get_sample_rate()
    
    def is_active(self) -> bool:
        """Check if the recognizer is active.
        
        Returns:
            True if active, False otherwise
        """
        if not self.rust_available or self.recognizer is None:
            return False
        
        return self.recognizer.is_active()
    
    def set_active(self, active: bool) -> bool:
        """Set the active state of the recognizer.
        
        Args:
            active: True to activate, False to deactivate
            
        Returns:
            True if successful, False otherwise
        """
        if not self.rust_available or self.recognizer is None:
            return False
        
        try:
            self.recognizer.set_active(active)
            return True
        except Exception as e:
            logger.error(f"Error setting active state: {e}")
            return False
    
    def release(self) -> bool:
        """Release resources.
        
        Returns:
            True if successful, False otherwise
        """
        if not self.rust_available or self.recognizer is None:
            return False
        
        try:
            self.recognizer.release()
            return True
        except Exception as e:
            logger.error(f"Error releasing resources: {e}")
            return False


class TextToSpeech:
    """Text-to-speech using Larynx via Rust."""
    
    def __init__(self, model_path: str, voice: str = "default", sample_rate: int = 22050):
        self.rust_available = RUST_AVAILABLE
        self.model_path = model_path
        self.voice = voice
        self.sample_rate = sample_rate
        self.tts = None
        
        if self.rust_available:
            try:
                self.tts = jenna_rust.TextToSpeech(model_path, voice, sample_rate)
            except Exception as e:
                logger.error(f"Failed to initialize text-to-speech: {e}")
                self.rust_available = False
    
    def initialize(self) -> bool:
        """Initialize the text-to-speech engine.
        
        Returns:
            True if initialization was successful, False otherwise
        """
        if not self.rust_available:
            # Fallback to Python implementation
            logger.warning("Rust not available, text-to-speech will not work")
            return False
        
        try:
            if self.tts is None:
                self.tts = jenna_rust.TextToSpeech(self.model_path, self.voice, self.sample_rate)
            
            self.tts.initialize()
            return True
        except Exception as e:
            logger.error(f"Failed to initialize text-to-speech: {e}")
            return False
    
    def synthesize(self, text: str) -> np.ndarray:
        """Synthesize speech from text.
        
        Args:
            text: Text to synthesize
            
        Returns:
            Audio data as numpy array
        """
        if not self.rust_available or self.tts is None:
            # Fallback to Python implementation
            return np.array([], dtype=np.int16)
        
        try:
            audio_data = self.tts.synthesize(text)
            return np.array(audio_data, dtype=np.int16)
        except Exception as e:
            logger.error(f"Error synthesizing speech: {e}")
            return np.array([], dtype=np.int16)
    
    def set_voice(self, voice: str) -> bool:
        """Set the voice for speech synthesis.
        
        Args:
            voice: Voice name
            
        Returns:
            True if successful, False otherwise
        """
        self.voice = voice
        
        if not self.rust_available or self.tts is None:
            return False
        
        try:
            self.tts.set_voice(voice)
            return True
        except Exception as e:
            logger.error(f"Error setting voice: {e}")
            return False
    
    def get_voice(self) -> str:
        """Get the current voice.
        
        Returns:
            Voice name
        """
        if not self.rust_available or self.tts is None:
            return self.voice
        
        return self.tts.get_voice()
    
    def set_sample_rate(self, sample_rate: int) -> bool:
        """Set the sample rate for speech synthesis.
        
        Args:
            sample_rate: Sample rate in Hz
            
        Returns:
            True if successful, False otherwise
        """
        self.sample_rate = sample_rate
        
        if not self.rust_available or self.tts is None:
            return False
        
        try:
            self.tts.set_sample_rate(sample_rate)
            return True
        except Exception as e:
            logger.error(f"Error setting sample rate: {e}")
            return False
    
    def get_sample_rate(self) -> int:
        """Get the sample rate for speech synthesis.
        
        Returns:
            Sample rate in Hz
        """
        if not self.rust_available or self.tts is None:
            return self.sample_rate
        
        return self.tts.get_sample_rate()
    
    def release(self) -> bool:
        """Release resources.
        
        Returns:
            True if successful, False otherwise
        """
        if not self.rust_available or self.tts is None:
            return False
        
        try:
            self.tts.release()
            return True
        except Exception as e:
            logger.error(f"Error releasing resources: {e}")
            return False