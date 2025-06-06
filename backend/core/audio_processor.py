"""Audio Processing Module for Jenna Voice Assistant.

This module provides audio input/output capabilities and signal processing
functionality using Rust modules for improved performance.
"""

import os
import sys
import time
import queue
import logging
import threading
from pathlib import Path
from typing import Optional, Dict, List, Tuple, Any, Callable, Union

import numpy as np
import sounddevice as sd

from .rust_bridge import AudioProcessor as RustAudioProcessor, SignalProcessor as RustSignalProcessor

# Setup logging
logger = logging.getLogger(__name__)


class AudioProcessor:
    """Audio Processor for Jenna Voice Assistant.
    
    This class provides audio input/output capabilities and signal processing
    functionality using Rust modules for improved performance.
    """
    
    def __init__(self, config):
        """Initialize the audio processor.
        
        Args:
            config: Configuration object
        """
        self.config = config
        
        # Audio settings
        self.sample_rate = config.get_int("AUDIO", "sample_rate", fallback=16000)
        self.channels = config.get_int("AUDIO", "channels", fallback=1)
        self.chunk_size = config.get_int("AUDIO", "chunk_size", fallback=1024)
        self.device_index = config.get_int("AUDIO", "device_index", fallback=None)
        
        # Initialize Rust audio processor
        self.rust_audio_processor = RustAudioProcessor()
        
        # Initialize Rust signal processor
        self.rust_signal_processor = RustSignalProcessor()
        
        # Audio buffers and queues
        self.input_queue = queue.Queue(maxsize=100)  # Limit queue size to prevent memory issues
        self.output_queue = queue.Queue(maxsize=100)
        
        # Audio streams
        self.input_stream = None
        self.output_stream = None
        
        # Thread control
        self.running = False
        self.input_thread = None
        self.output_thread = None
        
        # Callbacks
        self.on_audio_input = None
        
        # Audio device info
        self.input_devices = []
        self.output_devices = []
        self._update_device_info()
    
    def _update_device_info(self):
        """Update audio device information."""
        try:
            # Get device info from sounddevice
            devices = sd.query_devices()
            
            # Filter input and output devices
            self.input_devices = [d for d in devices if d['max_input_channels'] > 0]
            self.output_devices = [d for d in devices if d['max_output_channels'] > 0]
            
            # Log available devices
            logger.info(f"Available input devices: {len(self.input_devices)}")
            for i, device in enumerate(self.input_devices):
                logger.info(f"  [{i}] {device['name']}")
            
            logger.info(f"Available output devices: {len(self.output_devices)}")
            for i, device in enumerate(self.output_devices):
                logger.info(f"  [{i}] {device['name']}")
            
        except Exception as e:
            logger.error(f"Error updating device info: {e}")
    
    def start(self):
        """Start audio processing."""
        if self.running:
            logger.warning("Audio processor is already running")
            return
        
        self.running = True
        
        # Start input thread
        self.input_thread = threading.Thread(target=self._input_loop)
        self.input_thread.daemon = True
        self.input_thread.start()
        
        # Start output thread
        self.output_thread = threading.Thread(target=self._output_loop)
        self.output_thread.daemon = True
        self.output_thread.start()
        
        logger.info("Audio processor started")
    
    def stop(self):
        """Stop audio processing."""
        if not self.running:
            logger.warning("Audio processor is not running")
            return
        
        self.running = False
        
        # Stop input stream
        if self.input_stream:
            self.input_stream.stop()
            self.input_stream.close()
            self.input_stream = None
        
        # Stop output stream
        if self.output_stream:
            self.output_stream.stop()
            self.output_stream.close()
            self.output_stream = None
        
        # Wait for threads to finish
        if self.input_thread and self.input_thread.is_alive():
            self.input_thread.join(timeout=1.0)
        
        if self.output_thread and self.output_thread.is_alive():
            self.output_thread.join(timeout=1.0)
        
        logger.info("Audio processor stopped")
    
    def _input_callback(self, indata, frames, time, status):
        """Callback for audio input stream.
        
        Args:
            indata: Input audio data
            frames: Number of frames
            time: Stream time
            status: Stream status
        """
        if status:
            logger.warning(f"Audio input status: {status}")
        
        # Convert to mono if needed
        if self.channels > 1:
            audio_data = np.mean(indata, axis=1)
        else:
            audio_data = indata.copy().flatten()
        
        # Process audio data with Rust module if available
        try:
            processed_data = self.rust_audio_processor.process_input(audio_data)
        except Exception as e:
            logger.debug(f"Error processing audio with Rust: {e}")
            processed_data = audio_data
        
        # Add to queue
        try:
            if not self.input_queue.full():
                self.input_queue.put(processed_data, block=False)
            else:
                logger.warning("Input queue is full, dropping audio frame")
        except queue.Full:
            pass
        
        # Call callback if provided
        if self.on_audio_input:
            self.on_audio_input(processed_data)
    
    def _output_callback(self, outdata, frames, time, status):
        """Callback for audio output stream.
        
        Args:
            outdata: Output audio buffer to fill
            frames: Number of frames
            time: Stream time
            status: Stream status
        """
        if status:
            logger.warning(f"Audio output status: {status}")
        
        try:
            # Get audio data from queue
            audio_data = self.output_queue.get_nowait()
            
            # Ensure correct shape
            if len(audio_data) < frames:
                # Pad with zeros
                audio_data = np.pad(audio_data, (0, frames - len(audio_data)))
            elif len(audio_data) > frames:
                # Truncate
                audio_data = audio_data[:frames]
            
            # Convert to correct shape for output
            if self.channels > 1:
                # Duplicate mono to all channels
                outdata[:] = np.repeat(audio_data.reshape(-1, 1), self.channels, axis=1)
            else:
                outdata[:] = audio_data.reshape(-1, 1)
            
        except queue.Empty:
            # No audio data available, output silence
            outdata.fill(0)
    
    def _input_loop(self):
        """Audio input processing loop."""
        try:
            # Create input stream
            self.input_stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                callback=self._input_callback,
                blocksize=self.chunk_size,
                device=self.device_index
            )
            
            # Start input stream
            self.input_stream.start()
            
            logger.info(f"Audio input started (sample_rate={self.sample_rate}, channels={self.channels}, chunk_size={self.chunk_size})")
            
            # Keep thread alive
            while self.running:
                time.sleep(0.1)
                
        except Exception as e:
            logger.error(f"Error in audio input loop: {e}")
        finally:
            # Ensure stream is closed
            if self.input_stream:
                try:
                    self.input_stream.stop()
                    self.input_stream.close()
                except:
                    pass
                self.input_stream = None
        
        logger.info("Audio input stopped")
    
    def _output_loop(self):
        """Audio output processing loop."""
        try:
            # Create output stream
            self.output_stream = sd.OutputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                callback=self._output_callback,
                blocksize=self.chunk_size,
                device=self.device_index
            )
            
            # Start output stream
            self.output_stream.start()
            
            logger.info(f"Audio output started (sample_rate={self.sample_rate}, channels={self.channels}, chunk_size={self.chunk_size})")
            
            # Keep thread alive
            while self.running:
                time.sleep(0.1)
                
        except Exception as e:
            logger.error(f"Error in audio output loop: {e}")
        finally:
            # Ensure stream is closed
            if self.output_stream:
                try:
                    self.output_stream.stop()
                    self.output_stream.close()
                except:
                    pass
                self.output_stream = None
        
        logger.info("Audio output stopped")
    
    def get_audio_frame(self) -> Optional[np.ndarray]:
        """Get audio frame from input queue.
        
        Returns:
            Audio frame as numpy array, or None if queue is empty
        """
        try:
            return self.input_queue.get_nowait()
        except queue.Empty:
            return None
    
    def play_audio(self, audio_data: np.ndarray):
        """Play audio data.
        
        Args:
            audio_data: Audio data as numpy array
        """
        try:
            # Process audio data with Rust module if available
            try:
                processed_data = self.rust_audio_processor.process_output(audio_data)
            except Exception as e:
                logger.debug(f"Error processing audio with Rust: {e}")
                processed_data = audio_data
            
            # Add to output queue
            if not self.output_queue.full():
                self.output_queue.put(processed_data, block=False)
            else:
                logger.warning("Output queue is full, dropping audio frame")
        except Exception as e:
            logger.error(f"Error playing audio: {e}")
    
    def apply_filter(self, audio_data: np.ndarray, filter_type: str, cutoff_freq: float, order: int = 4) -> np.ndarray:
        """Apply filter to audio data.
        
        Args:
            audio_data: Audio data as numpy array
            filter_type: Filter type (lowpass, highpass, bandpass, bandstop)
            cutoff_freq: Cutoff frequency in Hz (or tuple of frequencies for bandpass/bandstop)
            order: Filter order
            
        Returns:
            Filtered audio data
        """
        try:
            # Use Rust signal processor if available
            return self.rust_signal_processor.apply_filter(audio_data, filter_type, cutoff_freq, order, self.sample_rate)
        except Exception as e:
            logger.debug(f"Error applying filter with Rust: {e}")
            
            # Fallback to Python implementation
            from scipy import signal
            
            nyquist = 0.5 * self.sample_rate
            
            if filter_type == "lowpass":
                b, a = signal.butter(order, cutoff_freq / nyquist, btype="lowpass")
            elif filter_type == "highpass":
                b, a = signal.butter(order, cutoff_freq / nyquist, btype="highpass")
            elif filter_type == "bandpass":
                if isinstance(cutoff_freq, (list, tuple)) and len(cutoff_freq) == 2:
                    b, a = signal.butter(order, [f / nyquist for f in cutoff_freq], btype="bandpass")
                else:
                    raise ValueError("Bandpass filter requires a tuple of (low, high) cutoff frequencies")
            elif filter_type == "bandstop":
                if isinstance(cutoff_freq, (list, tuple)) and len(cutoff_freq) == 2:
                    b, a = signal.butter(order, [f / nyquist for f in cutoff_freq], btype="bandstop")
                else:
                    raise ValueError("Bandstop filter requires a tuple of (low, high) cutoff frequencies")
            else:
                raise ValueError(f"Unknown filter type: {filter_type}")
            
            return signal.filtfilt(b, a, audio_data)
    
    def compute_fft(self, audio_data: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Compute FFT of audio data.
        
        Args:
            audio_data: Audio data as numpy array
            
        Returns:
            Tuple of (frequencies, magnitudes)
        """
        try:
            # Use Rust signal processor if available
            return self.rust_signal_processor.compute_fft(audio_data, self.sample_rate)
        except Exception as e:
            logger.debug(f"Error computing FFT with Rust: {e}")
            
            # Fallback to Python implementation
            from scipy.fft import rfft, rfftfreq
            
            # Compute FFT
            fft_data = rfft(audio_data)
            freqs = rfftfreq(len(audio_data), 1.0 / self.sample_rate)
            
            # Compute magnitude
            magnitudes = np.abs(fft_data)
            
            return freqs, magnitudes
    
    def set_audio_input_callback(self, callback: Callable[[np.ndarray], None]):
        """Set callback for audio input.
        
        Args:
            callback: Callback function
        """
        self.on_audio_input = callback
    
    def get_input_devices(self) -> List[Dict[str, Any]]:
        """Get available input devices.
        
        Returns:
            List of input devices
        """
        return self.input_devices
    
    def get_output_devices(self) -> List[Dict[str, Any]]:
        """Get available output devices.
        
        Returns:
            List of output devices
        """
        return self.output_devices
    
    def set_device(self, device_index: int) -> bool:
        """Set audio device.
        
        Args:
            device_index: Device index
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if device exists
            devices = sd.query_devices()
            if device_index >= len(devices):
                logger.error(f"Device index {device_index} out of range")
                return False
            
            # Update device index
            self.device_index = device_index
            
            # Restart audio processing if running
            if self.running:
                self.stop()
                self.start()
            
            return True
        except Exception as e:
            logger.error(f"Error setting device: {e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status of the audio processor.
        
        Returns:
            Dictionary containing status information
        """
        return {
            "running": self.running,
            "sample_rate": self.sample_rate,
            "channels": self.channels,
            "chunk_size": self.chunk_size,
            "device_index": self.device_index,
            "input_queue_size": self.input_queue.qsize() if self.input_queue else 0,
            "output_queue_size": self.output_queue.qsize() if self.output_queue else 0,
            "rust_audio_processor_available": self.rust_audio_processor is not None,
            "rust_signal_processor_available": self.rust_signal_processor is not None
        }