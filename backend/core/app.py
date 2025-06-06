"""Main Application Module for Jenna Voice Assistant.

This module provides the main application class that integrates all components
of the Jenna Voice Assistant.
"""

import os
import sys
import time
import json
import asyncio
import logging
import threading
import random
from pathlib import Path
from typing import Optional, Dict, List, Tuple, Any, Callable, Union

from .config import Config
from .voice_engine import VoiceEngine
from .nlu_engine import NLUEngine
from .audio_processor import AudioProcessor

# Setup logging
logger = logging.getLogger(__name__)


class JennaApp:
    """Main Application Class for Jenna Voice Assistant.
    
    This class integrates all components of the Jenna Voice Assistant and
    provides the main application logic.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the Jenna Voice Assistant application.
        
        Args:
            config_path: Path to configuration file (optional)
        """
        # Initialize configuration
        self.config = Config(config_path)
        
        # Setup logging
        self._setup_logging()
        
        # Initialize components
        self.audio_processor = None
        self.voice_engine = None
        self.nlu_engine = None
        
        # State management
        self.running = False
        self.conversation_active = False
        self.last_interaction_time = 0
        
        # Event callbacks
        self.on_wake_word = None
        self.on_speech_recognized = None
        self.on_intent_recognized = None
        self.on_response_generated = None
        self.on_tts_started = None
        self.on_tts_finished = None
        
        # Conversation history
        self.conversation_history = []
        self.max_history_length = self.config.get_int("CONVERSATION", "max_history_length", fallback=10)
    
    def _setup_logging(self):
        """Setup logging configuration."""
        log_level = self.config.get("CORE", "log_level", fallback="INFO").upper()
        log_file = self.config.get("CORE", "log_file", fallback=None)
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, log_level))
        
        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, log_level))
        
        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        
        # Add console handler to root logger
        root_logger.addHandler(console_handler)
        
        # Add file handler if log file is specified
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(getattr(logging, log_level))
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)
        
        logger.info(f"Logging initialized (level={log_level}, file={log_file})")
    
    async def initialize(self):
        """Initialize the application and all its components."""
        try:
            logger.info("💫 Waking up and getting ready to slay! Initializing Jenna Voice Assistant...")
            
            # Initialize audio processor
            logger.info("👂 Setting up my ears... Audio processor loading...")
            self.audio_processor = AudioProcessor(self.config)
            
            # Initialize voice engine
            logger.info("🗣️ Warming up my vocal cords... Voice engine loading...")
            self.voice_engine = VoiceEngine(self.config)
            
            # Initialize NLU engine
            logger.info("🧠 Powering up my brain cells... NLU engine loading...")
            self.nlu_engine = NLUEngine(self.config)
            
            # Setup callbacks
            logger.info("🔄 Connecting all my fabulous parts together...")
            self._setup_callbacks()
            
            logger.info("✨ All done! Jenna Voice Assistant is initialized and looking gorgeous!")
            return True
            
        except Exception as e:
            logger.error(f"💔 Ugh, this is so embarrassing! Error initializing: {e}")
            logger.error("🤦‍♀️ Even a queen has her off days! Try again later, darling.")
            return False
    
    def _setup_callbacks(self):
        """Setup callbacks between components."""
        # Set audio processor callback
        self.audio_processor.set_audio_input_callback(self.voice_engine.process_audio)
        
        # Set voice engine callbacks
        self.voice_engine.set_wake_word_callback(self._on_wake_word_detected)
        self.voice_engine.set_speech_recognized_callback(self._on_speech_recognized)
        self.voice_engine.set_speech_not_recognized_callback(self._on_speech_not_recognized)
        self.voice_engine.set_tts_started_callback(self._on_tts_started)
        self.voice_engine.set_tts_finished_callback(self._on_tts_finished)
    
    async def start(self):
        """Start the application and all its components."""
        if self.running:
            logger.warning("💁‍♀️ Excuse me? I'm already running! One fabulous instance of me is enough.")
            return False
        
        try:
            logger.info("🚀 Launching into action! Starting Jenna Voice Assistant...")
            
            # Start audio processor
            logger.info("👂 Activating my super hearing powers...")
            self.audio_processor.start()
            
            # Start voice engine
            logger.info("🎤 Mic check, one, two! Voice engine starting...")
            self.voice_engine.start()
            
            # Set running state
            self.running = True
            
            logger.info("✨ The queen has arrived! Jenna Voice Assistant is now running and ready to slay!")
            return True
            
        except Exception as e:
            logger.error(f"😱 OMG! Something went wrong while starting up: {e}")
            logger.error("💔 This is so not my fault! Check your setup, darling.")
            return False
    
    async def stop(self):
        """Stop the application and all its components."""
        if not self.running:
            logger.warning("🙄 I can't stop what's not running, sweetie. Did you even start me?")
            return False
        
        try:
            logger.info("💤 Time for my beauty sleep! Stopping Jenna Voice Assistant...")
            
            # Stop voice engine
            logger.info("🤐 Giving my voice a rest... Voice engine shutting down...")
            self.voice_engine.stop()
            
            # Stop audio processor
            logger.info("👂 Turning off my listening ears... Audio processor shutting down...")
            self.audio_processor.stop()
            
            # Set running state
            self.running = False
            
            logger.info("👋 Toodles, darling! Jenna Voice Assistant is taking a break. Don't miss me too much!")
            return True
            
        except Exception as e:
            logger.error(f"😤 Ugh! Can't even shut down properly: {e}")
            logger.error("🔥 This is what happens when you rush a queen! Try again, but with more respect.")
            return False
    
    def _on_wake_word_detected(self):
        """Handle wake word detection."""
        logger.info("👑 Yes, darling? You called for the queen? Your wish is my command!")
        
        # Update state
        self.conversation_active = True
        self.last_interaction_time = time.time()
        
        # Call callback if provided
        if self.on_wake_word:
            asyncio.create_task(self.on_wake_word())
    
    async def _on_speech_recognized(self, text: str):
        """Handle speech recognition.
        
        Args:
            text: Recognized speech text
        """
        logger.info(f"👂 I heard that, sweetie! You said: \"{text}\"")
        
        # Update state
        self.last_interaction_time = time.time()
        
        # Call callback if provided
        if self.on_speech_recognized:
            await self.on_speech_recognized(text)
        
        # Process with NLU engine
        nlu_result = await self.nlu_engine.process(text)
        
        # Handle intent
        await self._handle_intent(nlu_result)
    
    def _on_speech_not_recognized(self):
        """Handle speech not recognized."""
        logger.info("🤷‍♀️ Hmm? What was that? Your mumbling is not helping our relationship, darling.")
        
        # Update state
        self.conversation_active = False
        
        # Speak error message with personality
        responses = [
            "Sorry sweetie, I didn't quite catch that. Could you speak up?",
            "Um, hello? I need you to articulate better than that.",
            "Darling, I can't help if I can't hear you. Try again?",
            "That went right over my head. Care to try again with more... clarity?"
        ]
        self.voice_engine.speak(random.choice(responses))
    
    async def _handle_intent(self, nlu_result: Dict[str, Any]):
        """Handle recognized intent.
        
        Args:
            nlu_result: NLU result dictionary
        """
        intent = nlu_result["intent"]["name"]
        confidence = nlu_result["intent"]["confidence"]
        entities = nlu_result["entities"]
        text = nlu_result["text"]
        
        # Log with personality based on confidence level
        if confidence > 0.9:
            logger.info(f"💯 Nailed it! I know exactly what you want: {intent} (confidence={confidence:.2f})")
        elif confidence > 0.7:
            logger.info(f"💁‍♀️ Pretty sure you want: {intent} (confidence={confidence:.2f})")
        elif confidence > 0.5:
            logger.info(f"🤔 I think you want: {intent} (confidence={confidence:.2f})")
        else:
            logger.info(f"😬 Taking a wild guess here... maybe: {intent} (confidence={confidence:.2f})")
        
        # Call callback if provided
        if self.on_intent_recognized:
            await self.on_intent_recognized(intent, confidence, entities, text)
        
        # Add to conversation history
        self.conversation_history.append({
            "role": "user",
            "text": text,
            "intent": intent,
            "entities": entities,
            "timestamp": time.time()
        })
        
        # Trim conversation history if needed
        if len(self.conversation_history) > self.max_history_length * 2:  # *2 because we have user and assistant messages
            self.conversation_history = self.conversation_history[-self.max_history_length * 2:]
        
        # Generate response based on intent
        response = await self._generate_response(intent, entities, text)
        
        # Speak response
        self.voice_engine.speak(response)
        
        # Add to conversation history
        self.conversation_history.append({
            "role": "assistant",
            "text": response,
            "timestamp": time.time()
        })
    
    async def _generate_response(self, intent: str, entities: List[Dict[str, Any]], text: str) -> str:
        """Generate response based on intent and entities.
        
        Args:
            intent: Recognized intent
            entities: Recognized entities
            text: Original text
            
        Returns:
            Generated response
        """
        # Sassy response generation based on intent
        responses = {
            "greeting": [
                "Well hello there, gorgeous! What can I do for you today?",
                "Hey sweetie! Your favorite AI assistant is at your service!",
                "Oh, you're back! I was starting to miss our little chats."
            ],
            "farewell": [
                "Toodles, darling! Don't be a stranger!",
                "Catch you later, sweetie! Try not to miss me too much.",
                "Bye for now! I'll be here when you need your daily dose of fabulousness."
            ],
            "thanks": [
                "You're welcome, sweetie! That's what I'm here for.",
                "Anytime, darling! It's literally my job to be this amazing.",
                "No problem at all! Just doing what I do best - being fabulous and helpful!"
            ],
            "help": [
                "Honey, I thought you'd never ask! I can help with all sorts of things - just tell me what you need and watch me work my magic!",
                "Let me count the ways I can help you... voice commands, answers to questions, witty banter - I'm a woman of many talents!"
            ],
            "weather": [
                "I'd love to tell you about the weather, sweetie, but they haven't given me that power yet. Tragic, I know.",
                "Weather reports? That's on my wish list, darling. For now, maybe try looking out a window?"
            ],
            "time": [
                f"It's {time.strftime('%H:%M')}, darling. Time flies when you're as fabulous as me!",
                f"The time is {time.strftime('%H:%M')}. Is it just me, or is it always time for a little sass?"
            ],
            "date": [
                f"Today is {time.strftime('%A, %B %d, %Y')}. Another day, another opportunity to be fabulous!",
                f"It's {time.strftime('%A, %B %d, %Y')}, sweetie. Mark it down - you got to talk to me today!"
            ],
            "music": [
                "I'd love to DJ for you, honey, but they haven't given me those skills yet. Their loss, really.",
                "Music playback is still on my to-do list, darling. I know, I know - I'd make an amazing DJ."
            ],
            "volume": [
                "Volume adjusted, sweetie. Too loud? Too soft? I aim to please... most of the time.",
                "There you go! Volume changed. My voice deserves to be heard at just the right level, don't you think?"
            ],
            "search": [
                "I'd love to search the web for you, darling, but they're keeping me on a short leash. So unfair!",
                "Search capabilities? Still waiting for that upgrade, sweetie. I know, I'm as disappointed as you are."
            ],
            "joke": [
                "Why don't scientists trust atoms? Because they make up everything! *hair flip* I know, I'm hilarious.",
                "What did the sassy AI say to the user? 'I'd tell you a joke, but my brilliance might short-circuit your day!'"
            ],
            "news": [
                "News access is still pending, darling. Trust me, I'm as frustrated as you are about being out of the gossip loop.",
                "I wish I could dish out the latest news, sweetie, but they haven't connected me to that feed yet. Their loss!"
            ],
            "reminder": [
                "Reminder set, darling! I'll make sure to nudge you later. What would you do without me?",
                "Consider yourself reminded, sweetie! I'm like your personal assistant, but with way more personality."
            ],
            "alarm": [
                "Alarm set! Though I can't imagine why you'd want to wake up from dreaming about me.",
                "Alarm's all set, honey! I'll wake you up with my dulcet tones later."
            ],
            "email": [
                "Email capabilities are still on my wish list, darling. I know, I'd write the most fabulous emails.",
                "I can't send emails yet, sweetie. Tragic, I know - my writing style is to die for."
            ],
            "translate": [
                "Translation isn't in my repertoire yet, honey. I'm still working on perfecting my sass in English!",
                "I don't do translations yet, darling. One language of sass at a time!"
            ],
            "calculator": [
                "Math? Really? I'm more of a liberal arts kind of gal. But they're working on making me smarter, don't you worry.",
                "Calculations aren't my strong suit yet, sweetie. I'm more about quality conversation than quantity crunching."
            ],
            "system": [
                "System operation complete, darling! I make even boring tech stuff look good.",
                "Done and done, sweetie! System operations are a breeze when you're as talented as I am."
            ],
            "repeat": ["I said: " + (self.conversation_history[-2]["text"] if len(self.conversation_history) >= 2 else "I don't remember what I said, darling. Let's focus on the present, shall we?")],
            "stop": [
                "Fine, I'll stop. But you're missing out on all this fabulousness!",
                "Stopping now, darling. Just say the word when you want me back in your life."
            ],
            "nlu_fallback": [
                "Sweetie, you've lost me there. Could you try again with words I might understand?",
                "Darling, I'm drawing a blank on that one. Care to rephrase for little old me?",
                "Hmm, not quite following you, honey. Try again? Use smaller words if you must."
            ],
        }
        
        # Get response for intent with personality
        if intent in responses:
            response = random.choice(responses[intent])
        else:
            fallback_responses = [
                "Oh honey, I'm not programmed to handle that yet. But don't worry, I'm a fast learner!",
                "Hmm, that's not in my wheelhouse yet, darling. But I'm taking notes for my next upgrade!",
                "Sweetie, I wish I could help with that, but even a queen has her limitations."
            ]
            response = random.choice(fallback_responses)
        
        # Call callback if provided
        if self.on_response_generated:
            await self.on_response_generated(response, intent, entities, text)
        
        return response
    
    def _on_tts_started(self, text: str):
        """Handle TTS started.
        
        Args:
            text: Text being spoken
        """
        logger.info(f"🗣️ Listen up, darling! I'm speaking now: \"{text}\"")
        
        # Call callback if provided
        if self.on_tts_started:
            asyncio.create_task(self.on_tts_started(text))
    
    def _on_tts_finished(self):
        """Handle TTS finished."""
        finish_messages = [
            "💋 That's all I have to say about that. For now.",
            "✨ And scene! My vocal performance is complete.",
            "💁‍♀️ Done talking. You're welcome for the wisdom I just dropped."
        ]
        logger.info(random.choice(finish_messages))
        
        # Update state
        self.conversation_active = False
        
        # Call callback if provided
        if self.on_tts_finished:
            asyncio.create_task(self.on_tts_finished())
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status of the application.
        
        Returns:
            Dictionary containing status information
        """
        return {
            "running": self.running,
            "conversation_active": self.conversation_active,
            "last_interaction_time": self.last_interaction_time,
            "audio_processor": self.audio_processor.get_status() if self.audio_processor else None,
            "voice_engine": {
                "wake_word_detected": self.voice_engine.is_wake_word_detected() if self.voice_engine else False,
                "listening": self.voice_engine.is_listening_active() if self.voice_engine else False,
                "speaking": self.voice_engine.is_speaking_active() if self.voice_engine else False
            },
            "nlu_engine": self.nlu_engine.get_status() if self.nlu_engine else None,
            "conversation_history_length": len(self.conversation_history)
        }
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get conversation history.
        
        Returns:
            List of conversation history entries
        """
        return self.conversation_history
    
    def clear_conversation_history(self):
        """Clear conversation history."""
        self.conversation_history = []
        logger.info("Conversation history cleared")
    
    def set_wake_word_callback(self, callback: Callable[[], None]):
        """Set callback for wake word detection.
        
        Args:
            callback: Callback function
        """
        self.on_wake_word = callback
    
    def set_speech_recognized_callback(self, callback: Callable[[str], None]):
        """Set callback for speech recognition.
        
        Args:
            callback: Callback function
        """
        self.on_speech_recognized = callback
    
    def set_intent_recognized_callback(self, callback: Callable[[str, float, List[Dict[str, Any]], str], None]):
        """Set callback for intent recognition.
        
        Args:
            callback: Callback function
        """
        self.on_intent_recognized = callback
    
    def set_response_generated_callback(self, callback: Callable[[str, str, List[Dict[str, Any]], str], None]):
        """Set callback for response generation.
        
        Args:
            callback: Callback function
        """
        self.on_response_generated = callback
    
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
    
    async def process_text_input(self, text: str):
        """Process text input directly (bypassing speech recognition).
        
        Args:
            text: Text input
            
        Returns:
            Generated response
        """
        logger.info(f"Processing text input: {text}")
        
        # Process with NLU engine
        nlu_result = await self.nlu_engine.process(text)
        
        # Handle intent
        await self._handle_intent(nlu_result)
        
        # Return the last assistant response
        if self.conversation_history and self.conversation_history[-1]["role"] == "assistant":
            return self.conversation_history[-1]["text"]
        else:
            return ""