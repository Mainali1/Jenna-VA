# Jenna Voice Assistant

![Jenna Voice Assistant](https://img.shields.io/badge/Jenna-Voice%20Assistant-blue)
![License](https://img.shields.io/badge/License-Proprietary-red)
![Python](https://img.shields.io/badge/Python-3.10%2B-green)
![Node.js](https://img.shields.io/badge/Node.js-16%2B-green)

Jenna Voice Assistant is a sophisticated, commercial-grade desktop voice assistant with advanced AI capabilities, modern UI, and comprehensive features designed to enhance productivity and provide a seamless voice-controlled experience.

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
- **Native Desktop Window**: Display the UI in a dedicated window

## Architecture

Jenna Voice Assistant is built with a modern, modular architecture:

- **Backend**: Python-based core with FastAPI for the web server
  - Core modules for voice recognition, AI processing, and system integration
  - Feature modules for specific functionality (tasks, notes, etc.)
  - Utility modules for common operations

- **Frontend**: React with TypeScript and Tailwind CSS
  - Modern, responsive UI
  - WebSocket communication with the backend
  - Component-based architecture

## Quick Start

### Prerequisites

- Python 3.10 or higher
- Node.js 16 or higher
- Microsoft Visual C++ Redistributable (latest version)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Mainali1/Jenna-VA.git
   cd Jenna-VA
   ```

2. Set up Python environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   source venv/bin/activate  # On macOS/Linux
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
   copy .env.template .env  # On Windows
   cp .env.template .env  # On macOS/Linux
   # Edit .env with your API keys and preferences
   ```

5. Run the application:
   ```bash
   python main.py
   ```

## Configuration

All settings are managed through the `.env` file. See [USAGE.md](./USAGE.md) for detailed configuration options.

## Deployment

For production deployment, you can build a standalone executable:

```bash
python build.py --release
```

This creates a complete installer in the `dist/` directory.

## Maintenance

### Cleaning the Codebase

To remove redundant files, development artifacts, and temporary files:

```bash
python cleanup.py  # Remove all redundant files
python cleanup.py --dry-run  # Show what would be removed without deleting
python cleanup.py --cache  # Remove only Python cache files
```

See `python cleanup.py --help` for more options.

## Security

- All sensitive data is stored locally by default
- API keys are stored in the `.env` file (not committed to version control)
- Communication with external services uses HTTPS

## UI Design

The UI is designed with a focus on:

- **Accessibility**: Clear contrast, keyboard navigation, screen reader support
- **Responsiveness**: Adapts to different screen sizes
- **Consistency**: Uniform design language throughout the application
- **Simplicity**: Intuitive interface with minimal learning curve

## Contributing

Jenna Voice Assistant is proprietary software. If you wish to contribute, please read [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines and the [LICENSE](./LICENSE) for terms.

## License

This project is licensed under a proprietary license - see the [LICENSE](./LICENSE) file for details.

## Support

For support, feature requests, or bug reports, please open an issue on the GitHub repository.

---

© 2023 Jenna Development Team. All rights reserved.