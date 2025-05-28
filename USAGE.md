# Jenna Voice Assistant - Usage Guidelines

## Overview

Jenna Voice Assistant is a sophisticated, commercial-grade desktop voice assistant with advanced AI capabilities, modern UI, and comprehensive features. This document provides guidelines for installation, configuration, usage, and contribution.

## Installation

### Prerequisites

- Python 3.10 or higher
- Node.js 16 or higher
- Windows 10/11 operating system
- Microsoft Visual C++ Redistributable (latest version)

### Installation Methods

#### Method 1: Using the Installer (Recommended)

1. Download the latest installer from the official website or release page
2. Run the installer and follow the on-screen instructions
3. Launch Jenna Voice Assistant from the Start Menu or desktop shortcut

#### Method 2: Manual Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Mainali1/Jenna-VA.git
   cd Jenna-VA
   ```

2. Set up Python environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Set up the frontend:
   ```bash
   cd frontend
   npm install
   npm run build
   cd ..
   ```

4. Configure environment:
   ```bash
   copy .env.template .env
   # Edit .env with your API keys and preferences
   ```

5. Run the application:
   ```bash
   python main.py
   ```

## Configuration

All settings are managed through the `.env` file and can be modified via the Settings page in the application interface.

### Core Settings

- **APP_NAME**: Application name (default: Jenna)
- **DEBUG**: Enable debug mode (true/false)
- **LOG_LEVEL**: Logging level (INFO, DEBUG, WARNING, ERROR)
- **DATA_DIR**: Directory for storing application data

### Voice Recognition Settings

- **WAKE_PHRASE**: Phrase to activate the assistant (default: "Jenna Ready")
- **VOICE_RECOGNITION_ENGINE**: Engine to use (hybrid, google, vosk, pocketsphinx)
- **OFFLINE_MODEL_PATH**: Path to offline recognition models
- **SPEECH_TIMEOUT**: Seconds of silence before processing speech
- **ENERGY_THRESHOLD**: Microphone sensitivity threshold

### Text-to-Speech Settings

- **TTS_ENGINE**: Engine to use for speech synthesis
- **VOICE_GENDER**: Preferred voice gender (male/female)
- **SPEECH_RATE**: Speed of speech output
- **VOLUME**: Volume level (0.0-1.0)

### API Keys

Some features require API keys from external services:

- **OPENAI_API_KEY**: For enhanced AI responses
- **WEATHER_API_KEY**: For weather information
- **GOOGLE_CLOUD_CREDENTIALS_PATH**: For Google Speech recognition

## Features

### Core Voice Control

- **Wake Phrase Detection**: Activate Jenna with "Jenna Ready"
- **Voice Commands**: Control your computer and access features by voice
- **AI Conversation**: Have natural conversations with AI-powered responses

### Productivity Features

- **Task Management**: Create, track, and manage tasks and projects
- **Notes**: Create and organize notes with voice or text
- **Reminders**: Set time-based reminders
- **Calendar Integration**: Manage your schedule and events

### Academic Features

- **Pomodoro Timer**: Structured study sessions with breaks
- **Flashcards**: Create and study flashcards with spaced repetition
- **Text Summarization**: Summarize text content for better retention
- **Research Assistant**: Quick information lookup and research help

### System Integration

- **File Operations**: Open, create, and manage files by voice
- **Screen Analysis**: Get context-aware assistance based on screen content
- **System Tray**: Access Jenna from the system tray even when minimized

## Voice Commands

Here are some example voice commands you can use with Jenna:

- "Set a timer for 10 minutes"
- "Start a Pomodoro session for 25 minutes"
- "What's the weather like in New York?"
- "Create a note about meeting agenda"
- "Remind me to call John at 3 PM"
- "Summarize this article"
- "What is 15% of 230?"

## Troubleshooting

### Common Issues

1. **Voice Recognition Not Working**
   - Check microphone permissions
   - Adjust energy threshold in settings
   - Ensure proper microphone setup in Windows

2. **Application Not Starting**
   - Verify Python and Node.js versions
   - Check for Microsoft Visual C++ Redistributable
   - Review log files in the data directory

3. **Features Not Available**
   - Confirm required API keys are configured
   - Check internet connection for online features
   - Verify feature is enabled in Settings

## Data Privacy

By default, all data is stored locally on your device. The application may send data to external services (like OpenAI or weather services) when using specific features. You can control data sharing in the Privacy section of the Settings page.

## Contribution Guidelines

Jenna Voice Assistant is proprietary software. If you wish to contribute or modify the software:

1. You MUST prominently credit the original work by linking to: `https://github.com/Mainali1/Jenna-VA`
2. Any modifications or derivative works MUST be substantially different, with at least 50% of the code changed or added compared to the original Software.
3. You MUST clearly indicate that your work is a modified version of Jenna Voice Assistant.

For full details, please refer to the LICENSE file.

## Support

For technical support, feature requests, or bug reports, please contact the Jenna Development Team or open an issue on the GitHub repository.

---

© 2023 Jenna Development Team. All rights reserved.