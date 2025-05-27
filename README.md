# Jenna - Commercial Desktop Voice Assistant

A sophisticated, commercial-grade desktop voice assistant application with advanced AI capabilities, modern UI, and comprehensive feature set.

## 🌟 Features

### Core Voice Control
- **Customizable Wake Phrase**: "Jenna Ready" activation
- **Hybrid Recognition**: Google Speech (online) + Vosk (offline)
- **Low-Latency Audio**: SoundDevice backend for quick responses
- **AI Mode**: Enhanced conversational abilities

### Academic Features
- **Smart Pomodoro Timer**: 25-minute study sessions
- **Flashcard System**: Spaced repetition learning
- **Text Summarization**: NLTK-based knowledge retention
- **Quick Research**: Instant Wikipedia integration

### Enhanced Capabilities
- **Weather Service**: Real-time weather updates
- **Mood Detection**: Context-aware responses
- **File System Integration**: Organized file access
- **Email Management**: Comprehensive email handling
- **Dynamic Responses**: AI-powered conversation
- **Session Management**: Secure user sessions
- **Automated Backup**: Data protection
- **Screen Analysis**: Context-aware assistance

### System Integration
- **App Launcher**: Extensive application control
- **File Operations**: Direct file access and management
- **Music Control**: Audio playbook management
- **System Tray**: Continuous background operation
- **Startup Launch**: Automatic system integration

## 🏗️ Architecture

```
Jenna-VA/
├── backend/                 # Python backend services
│   ├── core/               # Core voice and AI functionality
│   ├── features/           # Feature implementations
│   ├── services/           # External service integrations
│   └── utils/              # Utility functions
├── frontend/               # React + Tailwind CSS UI
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Application pages
│   │   ├── hooks/          # Custom React hooks
│   │   └── utils/          # Frontend utilities
│   └── public/             # Static assets
├── installer/              # Installation and packaging
├── customer/               # Customer deployment package
├── docs/                   # Documentation
└── tests/                  # Test suites
```

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 16+
- Windows 10/11

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/jenna-va.git
   cd jenna-va
   ```

2. **Setup Python environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Setup Frontend**
   ```bash
   cd frontend
   npm install
   npm run build
   cd ..
   ```

4. **Configure Environment**
   ```bash
   copy .env.template .env
   # Edit .env with your API keys
   ```

5. **Run Development Server**
   ```bash
   python main.py
   ```

## 🔧 Configuration

All settings are managed through the `.env` file and can be modified via the frontend interface:

- Voice recognition settings
- API key configurations
- Feature toggles
- UI preferences
- Security settings

## 📦 Deployment

The application uses PyInstaller/Nuitka with Inno Setup for one-click installation:

```bash
python build.py --release
```

This creates a complete installer in the `dist/` directory.

## 🔐 Security

- All code and packages are secured against information leaks
- API keys are encrypted and stored securely
- Session management with JWT tokens
- Automatic feature disabling for missing API keys

## 🎨 UI Design

Inspired by Jarvis from Iron Man:
- Skeletal hollow spinning ball visualization
- Wave-like lighting effects during speech
- Modern, responsive design
- Dark theme with accent colors

## 📝 License

Proprietary software with commercial licensing protection.

## 🤝 Contributing

This is a commercial project. Please contact the development team for contribution guidelines.

## 📞 Support

For technical support and feature requests, please contact our support team.