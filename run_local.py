#!/usr/bin/env python3
"""
Local startup script for the Torrent Bot.
This script loads environment variables and starts the bot.
"""

import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("🚀 Starting Torrent Bot locally...")

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Loaded environment variables from .env file")
except ImportError:
    print("⚠️ python-dotenv not installed, using system environment variables only")

# Quick configuration check
def check_config():
    """Quick configuration check before starting."""
    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    jackett_key = os.getenv("JACKETT_API_KEY", "").strip()
    qbit_user = os.getenv("QBIT_USER", "").strip()
    
    if not token or ":" not in token:
        print("❌ TELEGRAM_BOT_TOKEN is missing or invalid in .env file")
        return False
    if not jackett_key:
        print("❌ JACKETT_API_KEY is missing in .env file")
        return False
    if not qbit_user:
        print("❌ qBittorrent credentials missing in .env file")
        return False
    
    print(f"✅ Configuration OK - Starting bot @{token.split(':')[0]}")
    return True

if __name__ == "__main__":
    if not check_config():
        print("\n💡 Please check your .env file configuration")
        sys.exit(1)
    
    # Import and run the main bot
    try:
        print("📡 Starting Telegram Bot...")
        from bot import bot
        
        print("🎉 Bot is running! Press Ctrl+C to stop.")
        print("💬 Send /help to your bot to see available commands")
        
        # Start the bot
        bot.infinity_polling()
        
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user")
    except Exception as e:
        print(f"\n❌ Bot failed to start: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
