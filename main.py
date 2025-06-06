#!/usr/bin/env python3
"""
Jenna Voice Assistant - Main Entry Point

This script serves as the main entry point for the Jenna Voice Assistant application.
It initializes and starts the application, handling command-line arguments and
performing necessary setup tasks.
"""

import os
import sys
import time
import asyncio
import argparse
import logging
from pathlib import Path

# Add the project root directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.core.app import JennaApp


async def main():
    """Main entry point for the Jenna Voice Assistant application."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Jenna Voice Assistant")
    parser.add_argument(
        "--config", 
        type=str, 
        help="Path to configuration file",
        default=None
    )
    parser.add_argument(
        "--setup-models", 
        action="store_true", 
        help="Setup offline models"
    )
    parser.add_argument(
        "--build-rust", 
        action="store_true", 
        help="Build Rust modules"
    )
    parser.add_argument(
        "--debug", 
        action="store_true", 
        help="Enable debug mode"
    )
    args = parser.parse_args()
    
    # Setup offline models if requested
    if args.setup_models:
        await setup_models()
        return
    
    # Build Rust modules if requested
    if args.build_rust:
        await build_rust_modules()
        return
    
    # Create and initialize the application
    app = JennaApp(args.config)
    
    # Initialize the application
    success = await app.initialize()
    if not success:
        print("Failed to initialize Jenna Voice Assistant")
        return 1
    
    # Start the application
    success = await app.start()
    if not success:
        print("❌ Failed to start Jenna Voice Assistant. Even I'm not perfect! Try again?")
        return 1
    
    print("✨ Jenna Voice Assistant is up and running! I'm all yours now. Press Ctrl+C when you've had enough of my awesomeness. 💁‍♀️")
    
    try:
        # Keep the application running until interrupted
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down Jenna Voice Assistant...")
    finally:
        # Stop the application
        await app.stop()
    
    return 0


async def setup_models():
    """Setup offline models for voice recognition and text-to-speech."""
    from scripts.setup_vosk import main as setup_vosk
    from scripts.setup_larynx import main as setup_larynx
    from scripts.setup_rasa import main as setup_rasa
    
    print("💅 Getting my beauty products ready... I mean, setting up offline models! This might take a minute, darling.")
    
    # Setup Vosk models
    print("\n🎧 Time to make sure I can hear you properly! Setting up Vosk models for speech recognition...")
    await asyncio.to_thread(setup_vosk)
    
    # Setup Larynx models
    print("\n🗣️ Now let's work on my voice - it needs to be fabulous! Setting up Larynx models for text-to-speech...")
    await asyncio.to_thread(setup_larynx)
    
    # Setup Rasa models
    print("\n🧠 Upgrading my brain cells! Setting up Rasa models for natural language understanding...")
    await asyncio.to_thread(setup_rasa)
    
    print("\n✨ All done! My offline models are looking gorgeous and ready to slay! 💁‍♀️")


async def build_rust_modules():
    """Build Rust modules for enhanced performance."""
    from scripts.build_rust_modules import main as build_rust
    
    print("⚙️ Time to flex my muscles! Building those high-performance Rust modules... 💪")
    await asyncio.to_thread(build_rust)
    print("✨ Rust modules built and looking fierce! I'm basically a supermodel with these performance enhancements. 💁‍♀️")


if __name__ == "__main__":
    # Run the main function using asyncio
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except Exception as e:
        print(f"💔 Well, this is embarrassing... Something went wrong: {e}")
        print("🤦‍♀️ Even a queen has her off days! Try again later, darling.")
        sys.exit(1)