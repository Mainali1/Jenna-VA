"""Voice Engine Module for Jenna Voice Assistant.

This module provides voice recognition and text-to-speech capabilities
using both online and offline engines.
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

from .config import Config
from .rust_bridge import WakeWordDetector, SpeechRecognizer, TextToSpeech, AudioProcessor, SignalProcessor

# Setup logging
logger = logging.getLogger(__name__)


class VoiceEngine:
    """Voice Engine for Jenna Voice Assistant.
    
    This class provides voice recognition and text-to-speech capabilities
    using both online and offline engines.
    """
    
    def __init__(self, config: Config):
        """Initialize the voice engine.
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.is_listening = False
        self.is_speaking = False
        self.audio_processor = AudioProcessor()
        self.signal_processor = SignalProcessor()
        
        # Initialize wake word detector
        self.wake_word_detector = self._initialize_wake_word_detector()
        
        # Initialize speech recognizer
        self.speech_recognizer = self._initialize_speech_recognizer()
        
        # Initialize text-to-speech engine
        self.tts_engine = self._initialize_tts_engine()
        
        # Audio buffers and queues
        self.audio_queue = queue.Queue()
        self.recognition_queue = queue.Queue()
        self.tts_queue = queue.Queue()
        
        # Callbacks
        self.on_wake_word_detected = None
        self.on_speech_recognized = None
        self.on_speech_not_recognized = None
        self.on_tts_started = None
        self.on_tts_finished = None
        
        # Threads
        self.wake_word_thread = None
        self.recognition_thread = None
        self.tts_thread = None
        
        # Thread control
        self.running = False
        self.wake_word_detected = False
    
    def _initialize_wake_word_detector(self) -> WakeWordDetector:
        """Initialize the wake word detector.
        
        Returns:
            Initialized wake word detector
        """
        # Get wake word model and keyword paths
        models_dir = Path(self.config.get("VOICE_RECOGNITION", "models_dir", fallback="models"))
        wake_word_engine = self.config.get("VOICE_RECOGNITION", "wake_word_engine", fallback="porcupine")
        
        if wake_word_engine == "porcupine":
            model_path = models_dir / "porcupine" / "porcupine_params.pv"
            keyword_path = models_dir / "porcupine" / "jenna_windows.ppn"
            
            # Check if model files exist, if not, use default paths from config
            if not model_path.exists() or not keyword_path.exists():
                model_path = self.config.get("VOICE_RECOGNITION", "wake_word_model_path", fallback="")
                keyword_path = self.config.get("VOICE_RECOGNITION", "wake_word_keyword_path", fallback="")
        else:
            # Use default paths from config for other engines
            model_path = self.config.get("VOICE_RECOGNITION", "wake_word_model_path", fallback="")
            keyword_path = self.config.get("VOICE_RECOGNITION", "wake_word_keyword_path", fallback="")
        
        # Get sensitivity
        sensitivity = self.config.get_float("VOICE_RECOGNITION", "wake_word_sensitivity", fallback=0.5)
        
        # Initialize wake word detector
        detector = WakeWordDetector(str(model_path) if model_path else None, 
                                   str(keyword_path) if keyword_path else None, 
                                   sensitivity)
        
        # Initialize if model and keyword paths are provided
        if model_path and keyword_path and Path(model_path).exists() and Path(keyword_path).exists():
            detector.initialize(str(model_path), str(keyword_path))
        
        return detector
    
    def _initialize_speech_recognizer(self) -> SpeechRecognizer:
        """Initialize the speech recognizer.
        
        Returns:
            Initialized speech recognizer
        """
        # Get speech recognition model path
        models_dir = Path(self.config.get("VOICE_RECOGNITION", "models_dir", fallback="models"))
        speech_recognition_engine = self.config.get("VOICE_RECOGNITION", "speech_recognition_engine", fallback="vosk")
        
        if speech_recognition_engine == "vosk":
            # Try to find a Vosk model
            vosk_dir = models_dir / "vosk"
            if vosk_dir.exists():
                # Find the first model directory
                model_dirs = [d for d in vosk_dir.iterdir() if d.is_dir() and d.name.startswith("vosk-model")]
                if model_dirs:
                    model_path = model_dirs[0]
                else:
                    # No model found, use default path from config
                    model_path = self.config.get("VOICE_RECOGNITION", "speech_recognition_model_path", fallback="")
            else:
                # No Vosk directory, use default path from config
                model_path = self.config.get("VOICE_RECOGNITION", "speech_recognition_model_path", fallback="")
        else:
            # Use default path from config for other engines
            model_path = self.config.get("VOICE_RECOGNITION", "speech_recognition_model_path", fallback="")
        
        # Get sample rate
        sample_rate = self.config.get_int("VOICE_RECOGNITION", "sample_rate", fallback=16000)
        
        # Initialize speech recognizer
        recognizer = SpeechRecognizer(str(model_path) if model_path else "", sample_rate)
        
        # Initialize if model path is provided
        if model_path and Path(model_path).exists():
            recognizer.initialize()
        
        return recognizer
    
    def _initialize_tts_engine(self) -> TextToSpeech:
        """Initialize the text-to-speech engine.
        
        Returns:
            Initialized text-to-speech engine
        """
        # Get TTS model path
        models_dir = Path(self.config.get("TEXT_TO_SPEECH", "models_dir", fallback="models"))
        tts_engine = self.config.get("TEXT_TO_SPEECH", "engine", fallback="larynx")
        
        if tts_engine == "larynx":
            # Try to find a Larynx model
            larynx_dir = models_dir / "larynx"
            if larynx_dir.exists():
                # Find a voice directory
                voice_dirs = [d for d in larynx_dir.iterdir() if d.is_dir() and d.name.startswith("larynx-") and not d.name.startswith("larynx-hifi-gan")]
                if voice_dirs:
                    model_path = larynx_dir
                    voice = voice_dirs[0].name
                else:
                    # No voice found, use default path from config
                    model_path = self.config.get("TEXT_TO_SPEECH", "model_path", fallback="")
                    voice = self.config.get("TEXT_TO_SPEECH", "voice", fallback="default")
            else:
                # No Larynx directory, use default path from config
                model_path = self.config.get("TEXT_TO_SPEECH", "model_path", fallback="")
                voice = self.config.get("TEXT_TO_SPEECH", "voice", fallback="default")
        else:
            # Use default path from config for other engines
            model_path = self.config.get("TEXT_TO_SPEECH", "model_path", fallback="")
            voice = self.config.get("TEXT_TO_SPEECH", "voice", fallback="default")
        
        # Get sample rate
        sample_rate = self.config.get_int("TEXT_TO_SPEECH", "sample_rate", fallback=22050)
        
        # Initialize TTS engine
        tts = TextToSpeech(str(model_path) if model_path else "", voice, sample_rate)
        
        # Initialize if model path is provided
        if model_path and Path(model_path).exists():
            tts.initialize()
        
        return tts
    
    def start(self):
        """Start the voice engine."""
        if self.running:
            logger.warning("Voice engine is already running")
            return
        
        self.running = True
        
        # Start wake word detection thread
        self.wake_word_thread = threading.Thread(target=self._wake_word_detection_loop)
        self.wake_word_thread.daemon = True
        self.wake_word_thread.start()
        
        # Start speech recognition thread
        self.recognition_thread = threading.Thread(target=self._speech_recognition_loop)
        self.recognition_thread.daemon = True
        self.recognition_thread.start()
        
        # Start TTS thread
        self.tts_thread = threading.Thread(target=self._tts_loop)
        self.tts_thread.daemon = True
        self.tts_thread.start()
        
        logger.info("Voice engine started")
    
    def stop(self):
        """Stop the voice engine."""
        if not self.running:
            logger.warning("Voice engine is not running")
            return
        
        self.running = False
        
        # Wait for threads to finish
        if self.wake_word_thread and self.wake_word_thread.is_alive():
            self.wake_word_thread.join(timeout=1.0)
        
        if self.recognition_thread and self.recognition_thread.is_alive():
            self.recognition_thread.join(timeout=1.0)
        
        if self.tts_thread and self.tts_thread.is_alive():
            self.tts_thread.join(timeout=1.0)
        
        # Release resources
        if self.wake_word_detector:
            self.wake_word_detector.release()
        
        if self.speech_recognizer:
            self.speech_recognizer.release()
        
        if self.tts_engine:
            self.tts_engine.release()
        
        logger.info("Voice engine stopped")
    
    def _wake_word_detection_loop(self):
        """Wake word detection loop."""
        if not self.wake_word_detector or not self.wake_word_detector.is_active():
            logger.warning("Wake word detector is not active")
            return
        
        frame_length = self.wake_word_detector.get_frame_length()
        sample_rate = self.wake_word_detector.get_sample_rate()
        
        logger.info(f"Wake word detection started (frame_length={frame_length}, sample_rate={sample_rate})")
        
        while self.running:
            try:
                # Skip if we're already listening
                if self.is_listening or self.is_speaking:
                    time.sleep(0.1)
                    continue
                
                # Get audio frame from queue
                try:
                    audio_frame = self.audio_queue.get(timeout=0.1)
                except queue.Empty:
                    continue
                
                # Process audio frame
                if len(audio_frame) != frame_length:
                    # Resample if needed
                    # This is a simple implementation, in practice you would use a proper resampler
                    if len(audio_frame) > frame_length:
                        audio_frame = audio_frame[:frame_length]
                    else:
                        # Pad with zeros
                        audio_frame = np.pad(audio_frame, (0, frame_length - len(audio_frame)))
                
                # Convert to int16 if needed
                if audio_frame.dtype != np.int16:
                    audio_frame = (audio_frame * 32767).astype(np.int16)
                
                # Detect wake word
                wake_word_detected = self.wake_word_detector.process(audio_frame)
                
                if wake_word_detected:
                    logger.info("Wake word detected")
                    self.wake_word_detected = True
                    self.is_listening = True
                    
                    # Call callback if provided
                    if self.on_wake_word_detected:
                        self.on_wake_word_detected()
            except Exception as e:
                logger.error(f"Error in wake word detection loop: {e}")
                time.sleep(0.1)
        
        logger.info("Wake word detection stopped")
    
    def _speech_recognition_loop(self):
        """Speech recognition loop."""
        if not self.speech_recognizer or not self.speech_recognizer.is_active():
            logger.warning("Speech recognizer is not active")
            return
        
        sample_rate = self.speech_recognizer.get_sample_rate()
        
        logger.info(f"Speech recognition started (sample_rate={sample_rate})")
        
        # Variables for speech recognition
        speech_timeout = self.config.get_float("VOICE_RECOGNITION", "speech_timeout", fallback=5.0)
        silence_threshold = self.config.get_float("VOICE_RECOGNITION", "silence_threshold", fallback=0.1)
        silence_duration = self.config.get_float("VOICE_RECOGNITION", "silence_duration", fallback=1.0)
        
        # Buffers for speech recognition
        audio_buffer = []
        silence_start = None
        speech_start = None
        
        while self.running:
            try:
                # Skip if we're not listening or we're speaking
                if not self.is_listening or self.is_speaking:
                    time.sleep(0.1)
                    continue
                
                # Get audio frame from queue
                try:
                    audio_frame = self.audio_queue.get(timeout=0.1)
                except queue.Empty:
                    continue
                
                # Add to buffer
                audio_buffer.append(audio_frame)
                
                # Check if we've reached the speech timeout
                if speech_start and time.time() - speech_start > speech_timeout:
                    logger.info("Speech timeout reached")
                    
                    # Process the audio buffer
                    audio_data = np.concatenate(audio_buffer)
                    
                    # Convert to int16 if needed
                    if audio_data.dtype != np.int16:
                        audio_data = (audio_data * 32767).astype(np.int16)
                    
                    # Recognize speech
                    text = self.speech_recognizer.process(audio_data)
                    
                    # Reset buffers
                    audio_buffer = []
                    silence_start = None
                    speech_start = None
                    
                    # Reset listening state
                    self.is_listening = False
                    
                    # Call callback if provided
                    if text and self.on_speech_recognized:
                        self.on_speech_recognized(text)
                    elif self.on_speech_not_recognized:
                        self.on_speech_not_recognized()
                    
                    continue
                
                # Check for silence
                energy = np.mean(np.abs(audio_frame))
                
                if energy < silence_threshold:
                    # Silence detected
                    if silence_start is None:
                        silence_start = time.time()
                    elif time.time() - silence_start > silence_duration:
                        # Silence duration reached, process the audio buffer
                        if audio_buffer and speech_start:
                            logger.info("Silence duration reached, processing speech")
                            
                            # Process the audio buffer
                            audio_data = np.concatenate(audio_buffer)
                            
                            # Convert to int16 if needed
                            if audio_data.dtype != np.int16:
                                audio_data = (audio_data * 32767).astype(np.int16)
                            
                            # Recognize speech
                            text = self.speech_recognizer.process(audio_data)
                            
                            # Reset buffers
                            audio_buffer = []
                            silence_start = None
                            speech_start = None
                            
                            # Reset listening state
                            self.is_listening = False
                            
                            # Call callback if provided
                            if text and self.on_speech_recognized:
                                self.on_speech_recognized(text)
                            elif self.on_speech_not_recognized:
                                self.on_speech_not_recognized()
                else:
                    # Speech detected
                    silence_start = None
                    if speech_start is None:
                        speech_start = time.time()
            except Exception as e:
                logger.error(f"Error in speech recognition loop: {e}")
                time.sleep(0.1)
        
        logger.info("Speech recognition stopped")
    
    def _tts_loop(self):
        """Text-to-speech loop."""
        if not self.tts_engine:
            logger.warning("TTS engine is not initialized")
            return
        
        logger.info("TTS loop started")
        
        while self.running:
            try:
                # Get text from queue
                try:
                    text = self.tts_queue.get(timeout=0.1)
                except queue.Empty:
                    continue
                
                # Set speaking state
                self.is_speaking = True
                
                # Call callback if provided
                if self.on_tts_started:
                    self.on_tts_started(text)
                
                # Synthesize speech
                audio_data = self.tts_engine.synthesize(text)
                
                # TODO: Play audio data
                # This would typically involve sending the audio data to an audio output device
                # For now, we just sleep to simulate the speech duration
                time.sleep(len(audio_data) / self.tts_engine.get_sample_rate())
                
                # Reset speaking state
                self.is_speaking = False
                
                # Call callback if provided
                if self.on_tts_finished:
                    self.on_tts_finished()
            except Exception as e:
                logger.error(f"Error in TTS loop: {e}")
                time.sleep(0.1)
        
        logger.info("TTS loop stopped")
    
    def process_audio(self, audio_data: np.ndarray):
        """Process audio data.
        
        Args:
            audio_data: Audio data as numpy array
        """
        # Add to audio queue
        self.audio_queue.put(audio_data)
    
    def speak(self, text: str):
        """Speak text.
        
        Args:
            text: Text to speak
        """
        # Add to TTS queue
        self.tts_queue.put(text)
    
    def set_wake_word_callback(self, callback: Callable[[], None]):
        """Set callback for wake word detection.
        
        Args:
            callback: Callback function
        """
        self.on_wake_word_detected = callback
    
    def set_speech_recognized_callback(self, callback: Callable[[str], None]):
        """Set callback for speech recognition.
        
        Args:
            callback: Callback function
        """
        self.on_speech_recognized = callback
    
    def set_speech_not_recognized_callback(self, callback: Callable[[], None]):
        """Set callback for speech not recognized.
        
        Args:
            callback: Callback function
        """
        self.on_speech_not_recognized = callback
    
    def set_tts_started_callback(self, callback: Callable[[str], None]):
        """Set callback for TTS started.
        
        Args:
            callback: Callback function
        """
        self.on_tts_started = callback
    
    def set_tts_finished_callback(self, callback: Callable[[], None]):
        """Set callback for TTS finished.
        
        Args:
            callback: Callback function
        """
        self.on_tts_finished = callback
    
    def is_wake_word_detected(self) -> bool:
        """Check if wake word is detected.
        
        Returns:
            True if wake word is detected, False otherwise
        """
        return self.wake_word_detected
    
    def reset_wake_word_detection(self):
        """Reset wake word detection."""
        self.wake_word_detected = False
    
    def is_listening_active(self) -> bool:
        """Check if listening is active.
        
        Returns:
            True if listening is active, False otherwise
        """
        return self.is_listening
    
    def is_speaking_active(self) -> bool:
        """Check if speaking is active.
        
        Returns:
            True if speaking is active, False otherwise
        """
        return self.is_speaking
    
    def set_tts_voice(self, voice: str) -> bool:
        """Set TTS voice.
        
        Args:
            voice: Voice name
            
        Returns:
            True if successful, False otherwise
        """
        if not self.tts_engine:
            logger.warning("TTS engine is not initialized")
            return False
        
        return self.tts_engine.set_voice(voice)
    
    def get_tts_voice(self) -> str:
        """Get current TTS voice.
        
        Returns:
            Voice name
        """
        if not self.tts_engine:
            logger.warning("TTS engine is not initialized")
            return ""
        
        return self.tts_engine.get_voice()
    
    def set_wake_word_sensitivity(self, sensitivity: float) -> bool:
        """Set wake word sensitivity.
        
        Args:
            sensitivity: Sensitivity value between 0.0 and 1.0
            
        Returns:
            True if successful, False otherwise
        """
        if not self.wake_word_detector:
            logger.warning("Wake word detector is not initialized")
            return False
        
        return self.wake_word_detector.set_sensitivity(sensitivity)