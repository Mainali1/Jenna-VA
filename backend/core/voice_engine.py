"""Voice Engine for Speech Recognition and Text-to-Speech"""

import asyncio
import threading
import queue
import time
from typing import Optional, Callable, Dict, Any
from pathlib import Path

import speech_recognition as sr
import pyttsx3
import sounddevice as sd
import numpy as np
from vosk import Model, KaldiRecognizer
import json
import os
from pocketsphinx import LiveSpeech, get_model_path

from .config import Settings
from .logger import get_logger, VoiceLogger
from ..utils.exceptions import VoiceEngineException


class VoiceEngine:
    """Handles voice recognition and text-to-speech functionality."""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = get_logger(__name__)
        self.voice_logger = VoiceLogger(settings)
        
        # Recognition components
        self.recognizer = sr.Recognizer()
        self.microphone = None
        self.vosk_model = None
        self.vosk_recognizer = None
        self.pocketsphinx_model = None
        self.pocketsphinx_recognizer = None
        
        # TTS components
        self.tts_engine = None
        self.tts_lock = threading.Lock()
        
        # State management
        self.is_listening = False
        self.is_speaking = False
        self.wake_word_detected = False
        self.audio_queue = queue.Queue()
        
        # Event callbacks
        self.on_wake_word_detected: Optional[Callable] = None
        self.on_speech_recognized: Optional[Callable] = None
        self.on_speech_timeout: Optional[Callable] = None
        
        # Audio settings
        self.sample_rate = settings.audio_sample_rate
        self.chunk_size = settings.audio_chunk_size
        self.channels = settings.audio_channels
        
        # Performance tracking
        self.last_recognition_time = 0
        self.recognition_count = 0
        self.error_count = 0
    
    async def initialize(self):
        """Initialize voice engine components."""
        try:
            self.logger.info("🎤 Initializing voice engine...")
            
            if not self.settings.dev_skip_audio_init:
                await self._initialize_microphone()
                await self._initialize_recognition_engines()
                await self._initialize_tts_engine()
            else:
                self.logger.info("⚠️ Skipping audio initialization (dev mode)")
            
            self.logger.info("✅ Voice engine initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize voice engine: {e}")
            raise VoiceEngineException(f"Voice engine initialization failed: {e}")
    
    async def _initialize_microphone(self):
        """Initialize microphone for speech recognition."""
        try:
            self.microphone = sr.Microphone()
            
            # Adjust for ambient noise
            self.logger.info("🔧 Calibrating microphone for ambient noise...")
            with self.microphone as source:
                if self.settings.dynamic_energy_threshold:
                    self.recognizer.adjust_for_ambient_noise(source, duration=1)
                else:
                    self.recognizer.energy_threshold = self.settings.energy_threshold
            
            self.logger.info(f"🎚️ Energy threshold set to: {self.recognizer.energy_threshold}")
            
        except Exception as e:
            raise VoiceEngineException(f"Microphone initialization failed: {e}")
    
    async def _initialize_recognition_engines(self):
        """Initialize speech recognition engines."""
        engine = self.settings.voice_recognition_engine
        
        if engine in ['vosk', 'hybrid'] or (engine == 'pocketsphinx' and self.settings.preferred_offline_engine == 'vosk'):
            await self._initialize_vosk()
        
        if engine in ['pocketsphinx', 'hybrid'] or (engine == 'vosk' and self.settings.preferred_offline_engine == 'pocketsphinx'):
            await self._initialize_pocketsphinx()
        
        if engine in ['google', 'hybrid']:
            await self._initialize_google_speech()
        
        self.logger.info(f"🗣️ Voice recognition engine: {engine}")
    
    async def _initialize_vosk(self):
        """Initialize Vosk offline speech recognition."""
        try:
            model_path = self.settings.offline_model_path
            
            if not model_path.exists():
                self.logger.warning(f"⚠️ Vosk model not found at {model_path}")
                self.logger.info("📥 Please download a Vosk model for offline recognition")
                return
            
            self.vosk_model = Model(str(model_path))
            self.vosk_recognizer = KaldiRecognizer(self.vosk_model, self.sample_rate)
            
            self.logger.info("✅ Vosk offline recognition initialized")
            
        except Exception as e:
            self.logger.warning(f"⚠️ Vosk initialization failed: {e}")
    
    async def _initialize_pocketsphinx(self):
        """Initialize PocketSphinx offline speech recognition."""
        try:
            model_path = self.settings.pocketsphinx_model_path
            
            if not model_path.exists():
                self.logger.warning(f"⚠️ PocketSphinx model not found at {model_path}")
                self.logger.info("📥 Using default PocketSphinx model")
                # Use default model path from pocketsphinx
                model_path = Path(get_model_path())
            
            # Store model path for later use
            self.pocketsphinx_model = str(model_path)
            
            # Test if we can initialize LiveSpeech (we'll create actual recognizer when needed)
            test_config = {
                'verbose': False,
                'sampling_rate': self.sample_rate,
                'buffer_size': self.chunk_size,
                'no_search': False,
                'full_utt': False,
                'hmm': os.path.join(self.pocketsphinx_model, 'en-us'),
                'lm': os.path.join(self.pocketsphinx_model, 'en-us.lm.bin'),
                'dict': os.path.join(self.pocketsphinx_model, 'cmudict-en-us.dict')
            }
            
            # Just test if we can create it, don't actually start listening
            # We'll create a new instance when needed
            LiveSpeech(**test_config)
            
            self.logger.info("✅ PocketSphinx offline recognition initialized")
            
        except Exception as e:
            self.logger.warning(f"⚠️ PocketSphinx initialization failed: {e}")
    
    async def _initialize_google_speech(self):
        """Initialize Google Speech Recognition."""
        try:
            # Test Google Speech API availability
            if self.settings.google_cloud_credentials_path:
                import os
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = self.settings.google_cloud_credentials_path
            
            self.logger.info("✅ Google Speech Recognition configured")
            
        except Exception as e:
            self.logger.warning(f"⚠️ Google Speech setup failed: {e}")
    
    async def _initialize_tts_engine(self):
        """Initialize text-to-speech engine."""
        try:
            self.tts_engine = pyttsx3.init()
            
            # Configure voice settings
            voices = self.tts_engine.getProperty('voices')
            
            # Select voice based on gender preference
            selected_voice = None
            if self.settings.voice_id:
                # Use specific voice ID if provided
                for voice in voices:
                    if self.settings.voice_id in voice.id:
                        selected_voice = voice.id
                        break
            else:
                # Select by gender
                for voice in voices:
                    if self.settings.voice_gender.lower() in voice.name.lower():
                        selected_voice = voice.id
                        break
                
                # Fallback to first available voice
                if not selected_voice and voices:
                    selected_voice = voices[0].id
            
            if selected_voice:
                self.tts_engine.setProperty('voice', selected_voice)
                self.logger.info(f"🗣️ TTS voice selected: {selected_voice}")
            
            # Set speech rate and volume
            self.tts_engine.setProperty('rate', self.settings.speech_rate)
            self.tts_engine.setProperty('volume', self.settings.volume)
            
            self.logger.info("✅ Text-to-speech engine initialized")
            
        except Exception as e:
            self.logger.warning(f"⚠️ TTS initialization failed: {e}")
    
    async def start_listening(self):
        """Start continuous voice listening for wake word and commands."""
        if self.settings.dev_skip_audio_init:
            self.logger.info("⚠️ Audio listening skipped (dev mode)")
            return
        
        self.is_listening = True
        self.logger.info("👂 Starting voice listening...")
        
        try:
            while self.is_listening:
                await self._listen_for_wake_word()
                if self.wake_word_detected:
                    await self._listen_for_command()
                    self.wake_word_detected = False
                
                # Small delay to prevent excessive CPU usage
                await asyncio.sleep(0.1)
                
        except Exception as e:
            self.logger.error(f"Error in voice listening loop: {e}")
            self.error_count += 1
        finally:
            self.is_listening = False
    
    async def _listen_for_wake_word(self):
        """Listen for the wake word using continuous recognition."""
        try:
            with self.microphone as source:
                # Listen for audio with timeout
                audio = self.recognizer.listen(
                    source, 
                    timeout=1, 
                    phrase_time_limit=self.settings.phrase_timeout
                )
            
            # Recognize speech
            text = await self._recognize_speech(audio)
            
            if text and self.settings.wake_phrase.lower() in text.lower():
                self.wake_word_detected = True
                self.voice_logger.log_wake_word()
                
                if self.on_wake_word_detected:
                    await self.on_wake_word_detected()
        
        except sr.WaitTimeoutError:
            # Normal timeout, continue listening
            pass
        except Exception as e:
            self.logger.debug(f"Wake word detection error: {e}")
    
    async def _listen_for_command(self):
        """Listen for voice command after wake word detection."""
        try:
            self.voice_logger.log_speech_start()
            
            with self.microphone as source:
                # Listen for command with longer timeout
                audio = self.recognizer.listen(
                    source,
                    timeout=self.settings.speech_timeout,
                    phrase_time_limit=10  # Allow longer commands
                )
            
            # Recognize the command
            text = await self._recognize_speech(audio)
            
            if text:
                self.voice_logger.log_speech_end(text)
                self.recognition_count += 1
                self.last_recognition_time = time.time()
                
                if self.on_speech_recognized:
                    await self.on_speech_recognized(text)
            else:
                self.voice_logger.log_speech_timeout()
                if self.on_speech_timeout:
                    await self.on_speech_timeout()
        
        except sr.WaitTimeoutError:
            self.voice_logger.log_speech_timeout()
            if self.on_speech_timeout:
                await self.on_speech_timeout()
        except Exception as e:
            self.logger.error(f"Command recognition error: {e}")
            self.error_count += 1
    
    async def _recognize_speech(self, audio) -> Optional[str]:
        """Recognize speech using configured engine(s)."""
        engine = self.settings.voice_recognition_engine
        
        if engine == 'hybrid':
            # Try offline first based on preferred engine, fallback to online
            if self.settings.preferred_offline_engine == 'vosk':
                text = await self._recognize_with_vosk(audio)
                if not text:
                    text = await self._recognize_with_pocketsphinx(audio)
            else:  # preferred_offline_engine == 'pocketsphinx'
                text = await self._recognize_with_pocketsphinx(audio)
                if not text:
                    text = await self._recognize_with_vosk(audio)
            
            # If both offline engines fail, try online
            if not text:
                text = await self._recognize_with_google(audio)
            return text
        elif engine == 'vosk':
            return await self._recognize_with_vosk(audio)
        elif engine == 'pocketsphinx':
            return await self._recognize_with_pocketsphinx(audio)
        elif engine == 'google':
            return await self._recognize_with_google(audio)
        
        return None
    
    async def _recognize_with_vosk(self, audio) -> Optional[str]:
        """Recognize speech using Vosk offline engine."""
        if not self.vosk_recognizer:
            return None
        
        try:
            # Convert audio to the format Vosk expects
            audio_data = np.frombuffer(audio.get_raw_data(), dtype=np.int16)
            
            # Process audio
            if self.vosk_recognizer.AcceptWaveform(audio_data.tobytes()):
                result = json.loads(self.vosk_recognizer.Result())
                return result.get('text', '').strip()
            
        except Exception as e:
            self.logger.debug(f"Vosk recognition error: {e}")
        
        return None
    
    async def _recognize_with_pocketsphinx(self, audio) -> Optional[str]:
        """Recognize speech using PocketSphinx offline engine."""
        if not self.pocketsphinx_model:
            return None
        
        try:
            # Convert audio to the format PocketSphinx expects
            audio_data = np.frombuffer(audio.get_raw_data(), dtype=np.int16)
            
            # Create a temporary WAV file for PocketSphinx to process
            import tempfile
            import wave
            
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_filename = temp_file.name
            
            # Write audio data to WAV file
            with wave.open(temp_filename, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(2)  # 16-bit audio
                wf.setframerate(self.sample_rate)
                wf.writeframes(audio_data.tobytes())
            
            # Configure PocketSphinx for file-based recognition
            from pocketsphinx import AudioFile, get_model_path
            
            config = {
                'verbose': False,
                'audio_file': temp_filename,
                'buffer_size': self.chunk_size,
                'no_search': False,
                'full_utt': True,
                'hmm': os.path.join(self.pocketsphinx_model, 'en-us'),
                'lm': os.path.join(self.pocketsphinx_model, 'en-us.lm.bin'),
                'dict': os.path.join(self.pocketsphinx_model, 'cmudict-en-us.dict')
            }
            
            # Process audio file
            audio_file = AudioFile(**config)
            result = ""
            
            # Get the best hypothesis
            for phrase in audio_file:
                if phrase and hasattr(phrase, 'segments'):
                    result = str(phrase)
                    break
            
            # Clean up temporary file
            try:
                os.unlink(temp_filename)
            except Exception:
                pass
            
            return result.strip() if result else None
            
        except Exception as e:
            self.logger.debug(f"PocketSphinx recognition error: {e}")
            return None
    
    async def _recognize_with_google(self, audio) -> Optional[str]:
        """Recognize speech using Google Speech Recognition."""
        try:
            # Use Google Speech Recognition
            text = self.recognizer.recognize_google(audio)
            return text.strip() if text else None
            
        except sr.UnknownValueError:
            # Speech was unintelligible
            return None
        except sr.RequestError as e:
            self.logger.warning(f"Google Speech API error: {e}")
            return None
        except Exception as e:
            self.logger.debug(f"Google recognition error: {e}")
            return None
    
    async def speak(self, text: str):
        """Convert text to speech and play it."""
        if not self.tts_engine or self.settings.dev_skip_audio_init:
            self.logger.info(f"🔊 TTS (simulated): {text}")
            return
        
        try:
            self.is_speaking = True
            self.voice_logger.log_tts_start(text)
            
            # Use thread to avoid blocking
            def speak_thread():
                with self.tts_lock:
                    self.tts_engine.say(text)
                    self.tts_engine.runAndWait()
            
            # Run TTS in executor to avoid blocking
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, speak_thread)
            
            self.voice_logger.log_tts_end()
            
        except Exception as e:
            self.logger.error(f"TTS error: {e}")
            self.voice_logger.log_audio_error(str(e))
        finally:
            self.is_speaking = False
    
    async def play_activation_sound(self):
        """Play a sound to indicate activation."""
        try:
            # Generate a simple activation tone
            duration = 0.2  # seconds
            frequency = 800  # Hz
            
            t = np.linspace(0, duration, int(self.sample_rate * duration))
            tone = 0.3 * np.sin(2 * np.pi * frequency * t)
            
            # Fade in/out to avoid clicks
            fade_samples = int(0.01 * self.sample_rate)
            tone[:fade_samples] *= np.linspace(0, 1, fade_samples)
            tone[-fade_samples:] *= np.linspace(1, 0, fade_samples)
            
            # Play the tone
            sd.play(tone, self.sample_rate)
            
        except Exception as e:
            self.logger.debug(f"Activation sound error: {e}")
    
    def stop_listening(self):
        """Stop voice listening."""
        self.is_listening = False
        self.logger.info("🛑 Voice listening stopped")
    
    async def update_settings(self, settings: Settings):
        """Update voice engine settings."""
        self.settings = settings
        
        # Update recognizer settings
        if self.recognizer:
            if settings.dynamic_energy_threshold:
                # Re-calibrate for ambient noise
                try:
                    with self.microphone as source:
                        self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                except:
                    pass
            else:
                self.recognizer.energy_threshold = settings.energy_threshold
        
        # Update TTS settings
        if self.tts_engine:
            try:
                self.tts_engine.setProperty('rate', settings.speech_rate)
                self.tts_engine.setProperty('volume', settings.volume)
            except:
                pass
        
        self.logger.info("⚙️ Voice engine settings updated")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status of the voice engine."""
        available_engines = []
        if self.vosk_recognizer:
            available_engines.append('vosk')
        if self.pocketsphinx_model:
            available_engines.append('pocketsphinx')
        available_engines.append('google')  # Always available as fallback
        
        return {
            'is_listening': self.is_listening,
            'is_speaking': self.is_speaking,
            'wake_word_detected': self.wake_word_detected,
            'recognition_count': self.recognition_count,
            'error_count': self.error_count,
            'energy_threshold': getattr(self.recognizer, 'energy_threshold', None),
            'available_engines': available_engines,
            'current_engine': self.settings.voice_recognition_engine,
            'preferred_offline_engine': self.settings.preferred_offline_engine
        }
    
    async def cleanup(self):
        """Cleanup voice engine resources."""
        try:
            self.logger.info("🧹 Cleaning up voice engine...")
            
            self.stop_listening()
            
            if self.tts_engine:
                try:
                    self.tts_engine.stop()
                except:
                    pass
            
            # Clear audio queue
            while not self.audio_queue.empty():
                try:
                    self.audio_queue.get_nowait()
                except:
                    break
            
            self.logger.info("✅ Voice engine cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during voice engine cleanup: {e}")