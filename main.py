#!/usr/bin/env python3
"""
Jenna Voice Assistant - Main Entry Point

A commercial-grade desktop voice assistant with advanced AI capabilities.
Author: Jenna Development Team
Version: 1.0.0
"""

import sys
import os
import asyncio
import signal
from pathlib import Path
from typing import Optional

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from backend.core.application import JennaApplication
from backend.core.config import Settings
from backend.core.logger import setup_logger
from backend.utils.system import check_system_requirements, setup_directories
from backend.utils.exceptions import JennaException


def handle_shutdown(signum, frame):
    """Handle graceful shutdown on system signals."""
    print("\nReceived shutdown signal. Gracefully shutting down...")
    sys.exit(0)


def setup_signal_handlers():
    """Setup signal handlers for graceful shutdown."""
    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)
    if hasattr(signal, 'SIGBREAK'):  # Windows
        signal.signal(signal.SIGBREAK, handle_shutdown)


def check_environment() -> bool:
    """Check if the environment is properly configured."""
    env_file = project_root / ".env"
    if not env_file.exists():
        print("❌ Environment file (.env) not found!")
        print("📋 Please copy .env.template to .env and configure your settings.")
        return False
    
    return True


def display_banner():
    """Display application banner."""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║        🤖 JENNA - Voice Assistant v1.0.0                    ║
    ║                                                              ║
    ║        Commercial-Grade Desktop AI Assistant                 ║
    ║        Ready to assist with voice and text commands         ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)


async def main():
    """Main application entry point."""
    try:
        # Display banner
        display_banner()
        
        # Setup signal handlers
        setup_signal_handlers()
        
        # Check environment configuration
        if not check_environment():
            return 1
        
        # Load settings
        settings = Settings()
        
        # Setup logging
        logger = setup_logger(settings)
        logger.info("Starting Jenna Voice Assistant...")
        
        # Check system requirements
        if not check_system_requirements():
            logger.error("System requirements not met")
            return 1
        
        # Setup directories
        setup_directories(settings)
        
        # Initialize and start the application
        app = JennaApplication(settings)
        
        logger.info("Initializing application components...")
        await app.initialize()
        
        logger.info("🚀 Jenna is ready! Say 'Jenna Ready' to activate.")
        print("\n✅ Jenna is now running in the background.")
        print("💬 Say 'Jenna Ready' to activate voice commands.")
        print("🎯 Check the system tray for quick access.")
        print("⏹️  Press Ctrl+C to stop.\n")
        
        # Start the main application loop
        await app.run()
        
    except KeyboardInterrupt:
        print("\n👋 Goodbye! Jenna is shutting down...")
        return 0
    except JennaException as e:
        print(f"❌ Jenna Error: {e}")
        return 1
    except Exception as e:
        print(f"💥 Unexpected error: {e}")
        if settings and settings.debug:
            import traceback
            traceback.print_exc()
        return 1
    finally:
        # Cleanup
        if 'app' in locals():
            await app.cleanup()


if __name__ == "__main__":
    # Check Python version
    if sys.version_info < (3, 10):
        print("❌ Python 3.10 or higher is required!")
        print(f"📍 Current version: {sys.version}")
        sys.exit(1)
    
    # Run the application
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)