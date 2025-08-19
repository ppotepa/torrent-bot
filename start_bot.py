#!/usr/bin/env python3
"""
Torrent Bot with OpenVoice TTS Integration
Run this script to start the bot with full OpenVoice support
"""

import os
import sys
import logging

def setup_environment():
    """Setup the environment for the bot"""
    print("🚀 Starting Torrent Bot with OpenVoice TTS...")
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("❌ Error: .env file not found!")
        print("Please copy .env.example to .env and configure your settings.")
        return False
    
    # Check required environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
        if not token or ":" not in token:
            print("❌ Error: Invalid TELEGRAM_BOT_TOKEN in .env file")
            print("Please get a token from @BotFather on Telegram")
            return False
        
        admin_id = os.getenv("ADMIN_USER_ID", "").strip()
        if not admin_id:
            print("⚠️  Warning: ADMIN_USER_ID not set in .env file")
            print("You should set this to your Telegram user ID for notifications")
        
        print("✅ Environment configuration looks good")
        return True
        
    except ImportError:
        print("❌ Error: python-dotenv not installed")
        print("Run: pip install python-dotenv")
        return False

def check_dependencies():
    """Check if all required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    # Check core dependencies
    try:
        import telebot
        print("✅ pyTelegramBotAPI")
    except ImportError:
        print("❌ pyTelegramBotAPI not installed")
        return False
    
    # Check OpenVoice dependencies
    try:
        from openvoice_engine import OPENVOICE_AVAILABLE, get_openvoice_tts
        if OPENVOICE_AVAILABLE:
            print("✅ OpenVoice TTS (Premium quality)")
        else:
            print("⚠️  OpenVoice dependencies partially available")
    except ImportError:
        print("⚠️  OpenVoice TTS not available (using fallback)")
    
    # Check other TTS engines
    try:
        from gtts import gTTS
        print("✅ Google TTS")
    except ImportError:
        print("⚠️  Google TTS not available")
    
    try:
        import pyttsx3
        print("✅ Local TTS (pyttsx3)")
    except ImportError:
        print("⚠️  Local TTS not available")
    
    print("✅ Dependency check completed")
    return True

def show_features():
    """Show available features"""
    print("\n🎯 Available Features:")
    print("  📱 Telegram Bot Commands:")
    print("    /start - Show help and available commands")
    print("    /t <query> - Search torrents")
    print("    /dl <url> - Download from YouTube/Facebook")
    print("    /d - Show downloads")
    print("    /si - System information")
    print("")
    print("  🎵 TTS & Audiobook Features:")
    print("    /audiobook <text> - Convert text to speech with OpenVoice")
    print("    /ab <text> [polish] - Polish TTS support")
    print("    /voice <text> [male/female] - Voice customization")
    print("")
    print("  🔧 Advanced Features:")
    print("    Rich search modes: /t <query> rich|all|music")
    print("    Download monitoring and notifications")
    print("    Multi-language TTS support")
    print("    Voice cloning with OpenVoice (when available)")

def main():
    """Main startup function"""
    print("=" * 60)
    print("🤖 TORRENT BOT WITH OPENVOICE TTS")
    print("=" * 60)
    
    # Setup environment
    if not setup_environment():
        return 1
    
    # Check dependencies
    if not check_dependencies():
        return 1
    
    # Show features
    show_features()
    
    print("\n🚀 Starting bot...")
    print("Press Ctrl+C to stop the bot")
    print("=" * 60)
    
    try:
        # Import and start the bot
        import bot
        print("✅ Bot started successfully!")
        print("📱 Send /start to your bot on Telegram to begin")
        
        # Keep the script running
        import time
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user")
        return 0
    except Exception as e:
        print(f"\n❌ Error starting bot: {e}")
        print("Check your configuration and try again")
        return 1

if __name__ == "__main__":
    sys.exit(main())
