#!/usr/bin/env python3
"""
Rasa Model Setup Script for Jenna Voice Assistant.

This script sets up the Rasa model for offline natural language understanding.
It creates a basic Rasa project with intents and entities relevant to Jenna VA.
"""

import os
import sys
import argparse
import logging
import subprocess
import shutil
from pathlib import Path
from typing import Optional, Dict, List, Tuple, Any

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Define basic intents for Jenna VA
BASIC_INTENTS = [
    "greeting",
    "goodbye",
    "thank_you",
    "help",
    "set_alarm",
    "check_weather",
    "play_music",
    "stop_music",
    "volume_up",
    "volume_down",
    "mute",
    "unmute",
    "search_web",
    "open_application",
    "close_application",
    "take_note",
    "read_notes",
    "delete_note",
    "set_reminder",
    "check_reminders",
    "delete_reminder",
    "start_timer",
    "stop_timer",
    "check_time",
    "check_date",
    "tell_joke",
    "system_status",
    "restart_system",
    "shutdown_system",
]

# Define basic entities for Jenna VA
BASIC_ENTITIES = [
    "time",
    "date",
    "duration",
    "location",
    "person",
    "application",
    "song",
    "artist",
    "playlist",
    "note_content",
    "reminder_content",
    "search_query",
    "number",
]

# Define example training data for NLU
NLU_TRAINING_DATA = """
version: "3.1"

nlu:
- intent: greeting
  examples: |
    - hello
    - hi
    - hey
    - good morning
    - good afternoon
    - good evening
    - what's up
    - how are you

- intent: goodbye
  examples: |
    - goodbye
    - bye
    - see you later
    - see you soon
    - talk to you later
    - I'm leaving

- intent: thank_you
  examples: |
    - thank you
    - thanks
    - thanks a lot
    - I appreciate it
    - thank you so much

- intent: help
  examples: |
    - help
    - I need help
    - can you help me
    - what can you do
    - show me what you can do
    - what are your features

- intent: set_alarm
  examples: |
    - set an alarm for [7 am](time)
    - wake me up at [6:30](time)
    - set alarm for [tomorrow morning](time)
    - I need to wake up at [5:45](time)
    - set an alarm for [one hour](duration) from now

- intent: check_weather
  examples: |
    - what's the weather like
    - how's the weather today
    - what's the forecast for [tomorrow](date)
    - will it rain [today](date)
    - what's the weather like in [New York](location)
    - temperature in [London](location)

- intent: play_music
  examples: |
    - play some music
    - play [jazz](playlist)
    - play [Bohemian Rhapsody](song)
    - play songs by [Queen](artist)
    - I want to listen to [rock](playlist) music

- intent: stop_music
  examples: |
    - stop the music
    - pause
    - stop playing
    - pause the song
    - stop the song

- intent: volume_up
  examples: |
    - turn it up
    - increase volume
    - louder
    - volume up
    - increase the volume by [20](number) percent

- intent: volume_down
  examples: |
    - turn it down
    - decrease volume
    - quieter
    - volume down
    - lower the volume by [10](number) percent

- intent: mute
  examples: |
    - mute
    - silence
    - be quiet
    - turn off the sound
    - no sound

- intent: unmute
  examples: |
    - unmute
    - turn sound back on
    - restore volume
    - I want to hear again

- intent: search_web
  examples: |
    - search for [quantum physics](search_query)
    - google [best restaurants near me](search_query)
    - find information about [climate change](search_query)
    - search the web for [upcoming movies](search_query)
    - look up [how to make pasta](search_query)

- intent: open_application
  examples: |
    - open [Chrome](application)
    - launch [Spotify](application)
    - start [Word](application)
    - run [Photoshop](application)
    - open [calculator](application)

- intent: close_application
  examples: |
    - close [Chrome](application)
    - exit [Spotify](application)
    - quit [Word](application)
    - terminate [Photoshop](application)
    - close [calculator](application)

- intent: take_note
  examples: |
    - take a note
    - write this down: [meeting at 3 pm](note_content)
    - note that [I need to buy milk](note_content)
    - create a note saying [call mom tomorrow](note_content)
    - remember [doctor appointment on Friday](note_content)

- intent: read_notes
  examples: |
    - read my notes
    - what are my notes
    - show me my notes
    - read my latest note
    - what did I note earlier

- intent: delete_note
  examples: |
    - delete my last note
    - remove the note about [meeting](note_content)
    - delete all notes
    - clear my notes
    - remove notes from [yesterday](date)

- intent: set_reminder
  examples: |
    - remind me to [call mom](reminder_content) at [5 pm](time)
    - set a reminder for [the meeting](reminder_content) [tomorrow](date) at [10 am](time)
    - remind me about [doctor appointment](reminder_content) on [Friday](date)
    - I need a reminder to [take my medicine](reminder_content) [every day](time) at [9 am](time)
    - remind me to [buy groceries](reminder_content) in [two hours](duration)

- intent: check_reminders
  examples: |
    - what are my reminders
    - show me my reminders
    - do I have any reminders
    - what do I need to remember
    - check my reminders for [today](date)

- intent: delete_reminder
  examples: |
    - delete the reminder about [meeting](reminder_content)
    - remove the [doctor appointment](reminder_content) reminder
    - cancel my reminder for [tomorrow](date)
    - clear all reminders
    - delete reminders for [today](date)

- intent: start_timer
  examples: |
    - start a timer for [5 minutes](duration)
    - set a timer for [30 seconds](duration)
    - countdown from [10 minutes](duration)
    - time [20 minutes](duration)
    - start a [1 hour](duration) timer

- intent: stop_timer
  examples: |
    - stop the timer
    - cancel the timer
    - end countdown
    - stop counting
    - cancel countdown

- intent: check_time
  examples: |
    - what time is it
    - tell me the time
    - current time
    - what's the time now
    - do you have the time

- intent: check_date
  examples: |
    - what's today's date
    - what day is it
    - what's the date
    - tell me the date
    - what day of the week is it

- intent: tell_joke
  examples: |
    - tell me a joke
    - say something funny
    - make me laugh
    - do you know any jokes
    - I want to hear a joke

- intent: system_status
  examples: |
    - how's the system
    - system status
    - are you working properly
    - check system health
    - is everything okay

- intent: restart_system
  examples: |
    - restart
    - reboot
    - restart the system
    - reboot yourself
    - restart Jenna

- intent: shutdown_system
  examples: |
    - shutdown
    - turn off
    - power off
    - shut down the system
    - go to sleep
"""

# Define example domain file
DOMAIN_FILE = """
version: "3.1"

intents:
  - greeting
  - goodbye
  - thank_you
  - help
  - set_alarm
  - check_weather
  - play_music
  - stop_music
  - volume_up
  - volume_down
  - mute
  - unmute
  - search_web
  - open_application
  - close_application
  - take_note
  - read_notes
  - delete_note
  - set_reminder
  - check_reminders
  - delete_reminder
  - start_timer
  - stop_timer
  - check_time
  - check_date
  - tell_joke
  - system_status
  - restart_system
  - shutdown_system

entities:
  - time
  - date
  - duration
  - location
  - person
  - application
  - song
  - artist
  - playlist
  - note_content
  - reminder_content
  - search_query
  - number

responses:
  utter_greeting:
    - text: "Hello! How can I help you today?"
  utter_goodbye:
    - text: "Goodbye! Have a great day!"
  utter_thank_you:
    - text: "You're welcome!"
  utter_help:
    - text: "I can help you with various tasks like setting alarms, checking the weather, playing music, taking notes, and more. Just ask!"
  utter_default:
    - text: "I'm not sure I understand. Could you rephrase that?"

session_config:
  session_expiration_time: 60  # minutes
  carry_over_slots_to_new_session: true
"""

# Define example rules file
RULES_FILE = """
version: "3.1"

rules:
  - rule: Respond to greeting
    steps:
      - intent: greeting
      - action: utter_greeting

  - rule: Respond to goodbye
    steps:
      - intent: goodbye
      - action: utter_goodbye

  - rule: Respond to thank you
    steps:
      - intent: thank_you
      - action: utter_thank_you

  - rule: Respond to help
    steps:
      - intent: help
      - action: utter_help
"""

# Define example stories file
STORIES_FILE = """
version: "3.1"

stories:
  - story: User greets and asks for help
    steps:
      - intent: greeting
      - action: utter_greeting
      - intent: help
      - action: utter_help

  - story: User greets and says goodbye
    steps:
      - intent: greeting
      - action: utter_greeting
      - intent: goodbye
      - action: utter_goodbye

  - story: User thanks and says goodbye
    steps:
      - intent: thank_you
      - action: utter_thank_you
      - intent: goodbye
      - action: utter_goodbye
"""

# Define example config file
CONFIG_FILE = """
language: en

pipeline:
  - name: WhitespaceTokenizer
  - name: RegexFeaturizer
  - name: LexicalSyntacticFeaturizer
  - name: CountVectorsFeaturizer
  - name: CountVectorsFeaturizer
    analyzer: char_wb
    min_ngram: 1
    max_ngram: 4
  - name: DIETClassifier
    epochs: 100
    constrain_similarities: true
  - name: EntitySynonymMapper
  - name: ResponseSelector
    epochs: 100
    constrain_similarities: true
  - name: FallbackClassifier
    threshold: 0.7

policies:
  - name: MemoizationPolicy
  - name: RulePolicy
  - name: TEDPolicy
    max_history: 5
    epochs: 100
    constrain_similarities: true
"""


def check_rasa_installed() -> bool:
    """Check if Rasa is installed.
    
    Returns:
        True if Rasa is installed, False otherwise
    """
    try:
        subprocess.run(
            ["rasa", "--version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            text=True,
        )
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        return False


def install_rasa() -> bool:
    """Install Rasa using pip.
    
    Returns:
        True if installation was successful, False otherwise
    """
    try:
        logger.info("Installing Rasa...")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "rasa"],
            check=True,
            text=True,
        )
        return True
    except subprocess.SubprocessError as e:
        logger.error(f"Failed to install Rasa: {e}")
        return False


def create_rasa_project(project_dir: Path) -> bool:
    """Create a new Rasa project.
    
    Args:
        project_dir: Directory to create the project in
        
    Returns:
        True if project creation was successful, False otherwise
    """
    try:
        # Create project directory if it doesn't exist
        project_dir.mkdir(parents=True, exist_ok=True)
        
        # Create data directory
        data_dir = project_dir / "data"
        data_dir.mkdir(exist_ok=True)
        
        # Create NLU data file
        nlu_file = data_dir / "nlu.yml"
        with open(nlu_file, "w") as f:
            f.write(NLU_TRAINING_DATA)
        
        # Create domain file
        domain_file = project_dir / "domain.yml"
        with open(domain_file, "w") as f:
            f.write(DOMAIN_FILE)
        
        # Create rules file
        rules_file = data_dir / "rules.yml"
        with open(rules_file, "w") as f:
            f.write(RULES_FILE)
        
        # Create stories file
        stories_file = data_dir / "stories.yml"
        with open(stories_file, "w") as f:
            f.write(STORIES_FILE)
        
        # Create config file
        config_file = project_dir / "config.yml"
        with open(config_file, "w") as f:
            f.write(CONFIG_FILE)
        
        logger.info(f"Rasa project created at {project_dir}")
        return True
    except Exception as e:
        logger.error(f"Failed to create Rasa project: {e}")
        return False


def train_rasa_model(project_dir: Path) -> bool:
    """Train a Rasa model.
    
    Args:
        project_dir: Directory containing the Rasa project
        
    Returns:
        True if training was successful, False otherwise
    """
    try:
        logger.info("Training Rasa model...")
        subprocess.run(
            ["rasa", "train"],
            cwd=project_dir,
            check=True,
            text=True,
        )
        
        # Check if model was created
        models_dir = project_dir / "models"
        if not models_dir.exists() or not list(models_dir.glob("*.tar.gz")):
            logger.error("No model file found after training")
            return False
        
        logger.info(f"Rasa model trained successfully")
        return True
    except subprocess.SubprocessError as e:
        logger.error(f"Failed to train Rasa model: {e}")
        return False


def setup_rasa_model(models_dir: Path, force: bool = False) -> bool:
    """Setup a Rasa model for Jenna Voice Assistant.
    
    Args:
        models_dir: Directory to store models
        force: Force setup even if model already exists
        
    Returns:
        True if setup was successful, False otherwise
    """
    # Create models directory if it doesn't exist
    rasa_dir = models_dir / "rasa"
    rasa_dir.mkdir(parents=True, exist_ok=True)
    
    # Check if model already exists
    model_files = list(rasa_dir.glob("models/*.tar.gz"))
    if model_files and not force:
        logger.info(f"Rasa model already exists at {model_files[0]}")
        return True
    
    # Check if Rasa is installed
    if not check_rasa_installed():
        logger.info("Rasa is not installed")
        if not install_rasa():
            logger.error("Failed to install Rasa")
            return False
    
    # Create Rasa project
    if not create_rasa_project(rasa_dir):
        return False
    
    # Train Rasa model
    if not train_rasa_model(rasa_dir):
        return False
    
    logger.info(f"Rasa model setup complete at {rasa_dir}")
    return True


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Setup Rasa model for Jenna Voice Assistant")
    parser.add_argument(
        "--models-dir",
        type=Path,
        default=Path(__file__).parent.parent / "models",
        help="Directory to store models"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force setup even if model already exists"
    )
    
    args = parser.parse_args()
    
    if not setup_rasa_model(args.models_dir, args.force):
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())