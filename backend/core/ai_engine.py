"""AI Engine for Natural Language Processing and Command Interpretation"""

import asyncio
import re
import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
import openai

from .config import Settings
from .logger import get_logger
from ..utils.exceptions import AIEngineException


@dataclass
class AIResponse:
    """Response from AI processing."""
    text: str
    confidence: float
    intent: str
    entities: Dict[str, Any]
    actions: List[Dict[str, Any]]
    context_used: bool = False
    processing_time: float = 0.0


class IntentClassifier:
    """Classifies user intents from text input."""
    
    def __init__(self):
        self.intent_patterns = {
            # Core commands
            'greeting': [
                r'\b(hello|hi|hey|good morning|good afternoon|good evening)\b',
                r'\b(how are you|what\'s up)\b'
            ],
            'goodbye': [
                r'\b(goodbye|bye|see you|farewell|exit|quit)\b',
                r'\b(good night|talk to you later)\b'
            ],
            
            # Academic features
            'pomodoro': [
                r'\b(start|begin|initiate).*(pomodoro|timer|study session)\b',
                r'\b(pomodoro|timer).*(start|begin|go)\b',
                r'\b(study|work).*(timer|session)\b'
            ],
            'flashcards': [
                r'\b(flashcard|flash card|study card)\b',
                r'\b(quiz|test|review).*(card|material)\b',
                r'\b(practice|study).*(flashcard|quiz)\b'
            ],
            'summarize': [
                r'\b(summarize|summary|sum up)\b',
                r'\b(give me|create).*(summary|overview)\b',
                r'\b(condense|shorten).*(text|content)\b'
            ],
            'research': [
                r'\b(research|look up|find|search).*(about|for)\b',
                r'\b(what is|tell me about|information about)\b',
                r'\b(wikipedia|wiki).*(search|lookup)\b'
            ],
            
            # System features
            'weather': [
                r'\b(weather|temperature|forecast)\b',
                r'\b(how.*(hot|cold|warm)|what.*(temperature|weather))\b',
                r'\b(rain|snow|sunny|cloudy).*today\b'
            ],
            'time': [
                r'\b(what time|current time|time is it)\b',
                r'\b(what.*(day|date)|today.*(date|day))\b'
            ],
            'file_operation': [
                r'\b(open|create|delete|move|copy).*(file|folder|document)\b',
                r'\b(file|folder).*(operation|management)\b',
                r'\b(find|locate).*(file|document)\b'
            ],
            'app_launcher': [
                r'\b(open|launch|start|run).*(application|app|program)\b',
                r'\b(start|open).*(browser|notepad|calculator|word)\b'
            ],
            'music_control': [
                r'\b(play|pause|stop|skip|next|previous).*(music|song|track)\b',
                r'\b(music|audio).*(control|player)\b',
                r'\b(volume).*(up|down|increase|decrease)\b'
            ],
            'email': [
                r'\b(email|mail|message).*(send|check|read|compose)\b',
                r'\b(send|compose).*(email|message)\b',
                r'\b(check|read).*(email|mail|inbox)\b'
            ],
            
            # Settings and control
            'settings': [
                r'\b(settings|preferences|configuration|config)\b',
                r'\b(change|modify|update).*(setting|preference)\b'
            ],
            'help': [
                r'\b(help|assistance|support|guide)\b',
                r'\b(how to|what can you|what do you)\b',
                r'\b(commands|features|capabilities)\b'
            ],
            'status': [
                r'\b(status|state|condition|health)\b',
                r'\b(how.*(doing|working|running))\b'
            ]
        }
    
    def classify(self, text: str) -> Tuple[str, float]:
        """Classify intent from text input."""
        text_lower = text.lower()
        best_intent = 'unknown'
        best_confidence = 0.0
        
        for intent, patterns in self.intent_patterns.items():
            confidence = 0.0
            matches = 0
            
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    matches += 1
                    confidence += 1.0 / len(patterns)
            
            if matches > 0:
                # Boost confidence based on pattern specificity
                confidence *= (matches / len(patterns))
                
                if confidence > best_confidence:
                    best_confidence = confidence
                    best_intent = intent
        
        return best_intent, min(best_confidence, 1.0)


class EntityExtractor:
    """Extracts entities from text input."""
    
    def __init__(self):
        self.entity_patterns = {
            'time': [
                r'\b(\d{1,2}:\d{2}(?:\s*(?:am|pm))?)\b',
                r'\b(\d{1,2}\s*(?:am|pm))\b',
                r'\b(morning|afternoon|evening|night)\b',
                r'\b(today|tomorrow|yesterday)\b'
            ],
            'duration': [
                r'\b(\d+)\s*(minute|hour|second|day)s?\b',
                r'\b(for|in)\s*(\d+)\s*(minute|hour)s?\b'
            ],
            'location': [
                r'\b(in|at|near)\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b'
            ],
            'file_path': [
                r'\b([A-Za-z]:\\[^\s]+)\b',  # Windows path
                r'\b(/[^\s]+)\b',  # Unix path
                r'\b([^\s]+\.[a-zA-Z]{2,4})\b'  # File with extension
            ],
            'application': [
                r'\b(notepad|calculator|browser|chrome|firefox|word|excel|powerpoint)\b',
                r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\.exe)\b'
            ],
            'email_address': [
                r'\b([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\b'
            ],
            'number': [
                r'\b(\d+(?:\.\d+)?)\b'
            ]
        }
    
    def extract(self, text: str) -> Dict[str, List[str]]:
        """Extract entities from text."""
        entities = {}
        
        for entity_type, patterns in self.entity_patterns.items():
            matches = []
            
            for pattern in patterns:
                found = re.findall(pattern, text, re.IGNORECASE)
                if found:
                    if isinstance(found[0], tuple):
                        matches.extend([match for group in found for match in group if match])
                    else:
                        matches.extend(found)
            
            if matches:
                entities[entity_type] = list(set(matches))  # Remove duplicates
        
        return entities


class ResponseGenerator:
    """Generates natural language responses."""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = get_logger(__name__)
        
        # Response templates
        self.response_templates = {
            'greeting': [
                "Hello! I'm Jenna, your voice assistant. How can I help you today?",
                "Hi there! I'm ready to assist you. What would you like to do?",
                "Good to see you! What can I help you with?"
            ],
            'goodbye': [
                "Goodbye! Have a great day!",
                "See you later! Feel free to call me anytime.",
                "Take care! I'll be here when you need me."
            ],
            'pomodoro_started': [
                "Perfect! I've started a 25-minute Pomodoro timer for you. Focus on your work!",
                "Your study session has begun! I'll let you know when the 25 minutes are up.",
                "Pomodoro timer is running. Time to concentrate and be productive!"
            ],
            'weather_unavailable': [
                "I'd love to help with weather information, but I need a weather API key to be configured.",
                "Weather service is currently unavailable. Please check the API configuration."
            ],
            'feature_disabled': [
                "That feature is currently disabled. You can enable it in the settings.",
                "This functionality isn't available right now. Check your feature settings."
            ],
            'error': [
                "I'm sorry, I encountered an error processing your request. Could you try again?",
                "Something went wrong. Let me try to help you in a different way.",
                "I had trouble with that request. Could you rephrase it?"
            ],
            'unknown': [
                "I'm not sure I understand. Could you rephrase that or ask for help to see what I can do?",
                "I didn't quite catch that. Try asking me for help to see my capabilities.",
                "Could you be more specific? I'm here to help with various tasks."
            ],
            'help': [
                "I can help you with many things! Try saying 'start pomodoro timer', 'what's the weather', 'open calculator', or 'summarize this text'.",
                "Here are some things I can do: manage timers, check weather, control music, open applications, help with studying, and much more!",
                "I'm your personal assistant! I can help with productivity, research, system control, and daily tasks. What would you like to try?"
            ]
        }
    
    def generate(self, intent: str, entities: Dict[str, Any], context: List[Dict] = None) -> str:
        """Generate a response based on intent and entities."""
        import random
        
        # Get base response template
        templates = self.response_templates.get(intent, self.response_templates['unknown'])
        base_response = random.choice(templates)
        
        # Customize response based on entities
        if entities:
            base_response = self._customize_response(base_response, entities)
        
        return base_response
    
    def _customize_response(self, response: str, entities: Dict[str, Any]) -> str:
        """Customize response with entity information."""
        # Add entity-specific customizations
        if 'time' in entities:
            response += f" I noticed you mentioned {entities['time'][0]}."
        
        if 'duration' in entities:
            response += f" For {entities['duration'][0]}."
        
        return response


class AIEngine:
    """Main AI engine for processing commands and generating responses."""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = get_logger(__name__)
        
        # AI components
        self.intent_classifier = IntentClassifier()
        self.entity_extractor = EntityExtractor()
        self.response_generator = ResponseGenerator(settings)
        
        # OpenAI client (if available)
        self.openai_client = None
        
        # Context management
        self.conversation_context = []
        self.user_preferences = {}
        
        # Performance tracking
        self.total_requests = 0
        self.successful_requests = 0
        self.average_response_time = 0.0
    
    async def initialize(self):
        """Initialize AI engine components."""
        try:
            self.logger.info("🧠 Initializing AI engine...")
            
            # Initialize OpenAI if API key is available
            if self.settings.openai_api_key:
                openai.api_key = self.settings.openai_api_key
                self.openai_client = openai
                self.logger.info("✅ OpenAI integration enabled")
            else:
                self.logger.info("⚠️ OpenAI API key not provided - using basic responses")
            
            self.logger.info("✅ AI engine initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize AI engine: {e}")
            raise AIEngineException(f"AI engine initialization failed: {e}")
    
    async def process_command(self, text: str, context: List[Dict] = None, features=None) -> AIResponse:
        """Process a command and generate an appropriate response."""
        start_time = asyncio.get_event_loop().time()
        self.total_requests += 1
        
        try:
            self.logger.info(f"🧠 Processing command: {text[:50]}{'...' if len(text) > 50 else ''}")
            
            # Classify intent
            intent, confidence = self.intent_classifier.classify(text)
            self.logger.debug(f"Intent: {intent} (confidence: {confidence:.2f})")
            
            # Extract entities
            entities = self.entity_extractor.extract(text)
            self.logger.debug(f"Entities: {entities}")
            
            # Determine actions based on intent
            actions = await self._determine_actions(intent, entities, features)
            
            # Generate response
            if self.openai_client and confidence < 0.7:
                # Use OpenAI for complex or unclear requests
                response_text = await self._generate_openai_response(text, context)
            else:
                # Use template-based response
                response_text = self.response_generator.generate(intent, entities, context)
            
            # Calculate processing time
            processing_time = asyncio.get_event_loop().time() - start_time
            self.average_response_time = (
                (self.average_response_time * (self.total_requests - 1) + processing_time) / 
                self.total_requests
            )
            
            self.successful_requests += 1
            
            return AIResponse(
                text=response_text,
                confidence=confidence,
                intent=intent,
                entities=entities,
                actions=actions,
                context_used=bool(context),
                processing_time=processing_time
            )
            
        except Exception as e:
            self.logger.error(f"Error processing command: {e}")
            
            return AIResponse(
                text="I'm sorry, I encountered an error processing your request.",
                confidence=0.0,
                intent="error",
                entities={},
                actions=[],
                processing_time=asyncio.get_event_loop().time() - start_time
            )
    
    async def _determine_actions(self, intent: str, entities: Dict[str, Any], features) -> List[Dict[str, Any]]:
        """Determine what actions to take based on intent and entities."""
        actions = []
        
        # Map intents to feature actions
        intent_action_map = {
            'pomodoro': {'feature': 'pomodoro', 'action': 'start_timer', 'duration': 25},
            'weather': {'feature': 'weather', 'action': 'get_current_weather'},
            'time': {'feature': 'system', 'action': 'get_current_time'},
            'file_operation': {'feature': 'file_manager', 'action': 'handle_file_operation'},
            'app_launcher': {'feature': 'app_launcher', 'action': 'launch_application'},
            'music_control': {'feature': 'music_control', 'action': 'control_playback'},
            'email': {'feature': 'email', 'action': 'handle_email'},
            'research': {'feature': 'research', 'action': 'search_wikipedia'},
            'summarize': {'feature': 'text_processor', 'action': 'summarize_text'},
            'flashcards': {'feature': 'flashcards', 'action': 'start_session'}
        }
        
        if intent in intent_action_map:
            action = intent_action_map[intent].copy()
            
            # Add entity data to action
            if entities:
                action['entities'] = entities
            
            # Check if feature is available
            if features and hasattr(features, 'is_feature_available'):
                if features.is_feature_available(action['feature']):
                    actions.append(action)
                else:
                    # Feature not available, create notification action
                    actions.append({
                        'feature': 'system',
                        'action': 'notify_feature_unavailable',
                        'feature_name': action['feature']
                    })
            else:
                actions.append(action)
        
        return actions
    
    async def _generate_openai_response(self, text: str, context: List[Dict] = None) -> str:
        """Generate response using OpenAI API."""
        try:
            # Prepare conversation context
            messages = [
                {
                    "role": "system",
                    "content": "You are Jenna, a helpful voice assistant. Provide concise, friendly responses. You can help with productivity, research, system control, and daily tasks."
                }
            ]
            
            # Add conversation context
            if context:
                for msg in context[-5:]:  # Last 5 messages for context
                    role = "user" if msg['type'] == 'user' else "assistant"
                    messages.append({"role": role, "content": msg['content']})
            
            # Add current message
            messages.append({"role": "user", "content": text})
            
            # Call OpenAI API
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.openai_client.ChatCompletion.create(
                    model=self.settings.openai_model,
                    messages=messages,
                    max_tokens=self.settings.openai_max_tokens,
                    temperature=0.7
                )
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            self.logger.warning(f"OpenAI API error: {e}")
            # Fallback to template response
            return "I'm here to help! Could you be more specific about what you'd like me to do?"
    
    def add_to_context(self, user_input: str, assistant_response: str):
        """Add interaction to conversation context."""
        self.conversation_context.append({
            'timestamp': datetime.now().isoformat(),
            'user_input': user_input,
            'assistant_response': assistant_response
        })
        
        # Limit context size
        if len(self.conversation_context) > self.settings.max_conversation_history:
            self.conversation_context = self.conversation_context[-self.settings.max_conversation_history:]
    
    def update_user_preferences(self, preferences: Dict[str, Any]):
        """Update user preferences for personalized responses."""
        self.user_preferences.update(preferences)
        self.logger.info("👤 User preferences updated")
    
    async def update_settings(self, settings: Settings):
        """Update AI engine settings."""
        self.settings = settings
        
        # Update OpenAI configuration if needed
        if settings.openai_api_key and not self.openai_client:
            openai.api_key = settings.openai_api_key
            self.openai_client = openai
            self.logger.info("✅ OpenAI integration enabled")
        
        self.logger.info("⚙️ AI engine settings updated")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current AI engine status."""
        return {
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "success_rate": self.successful_requests / max(self.total_requests, 1),
            "average_response_time": self.average_response_time,
            "openai_available": self.openai_client is not None,
            "context_size": len(self.conversation_context),
            "user_preferences": len(self.user_preferences)
        }
    
    async def cleanup(self):
        """Cleanup AI engine resources."""
        try:
            self.logger.info("🧹 Cleaning up AI engine...")
            
            # Clear context and preferences
            self.conversation_context.clear()
            self.user_preferences.clear()
            
            self.logger.info("✅ AI engine cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during AI engine cleanup: {e}")