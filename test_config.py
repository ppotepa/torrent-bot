#!/usr/bin/env python3
"""
Test script to verify bot configuration and connectivity.
"""

import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Loaded environment variables from .env file")
except ImportError:
    print("⚠️ python-dotenv not installed, using system environment variables only")

def test_configuration():
    """Test the bot configuration and connectivity."""
    try:
        print("🔍 Testing bot configuration...")
        
        # Test Telegram Bot Token
        token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
        if not token or ":" not in token:
            print("❌ TELEGRAM_BOT_TOKEN is missing or invalid")
            return False
        else:
            print(f"✅ Telegram Bot Token: {token[:10]}...{token[-4:]}")
        
        # Test Jackett API Key
        jackett_key = os.getenv("JACKETT_API_KEY", "").strip()
        if not jackett_key:
            print("❌ JACKETT_API_KEY is missing")
            return False
        else:
            print(f"✅ Jackett API Key: {'*' * len(jackett_key[:-4])}{jackett_key[-4:]}")
        
        # Test qBittorrent credentials
        qbit_user = os.getenv("QBIT_USER", "").strip()
        qbit_pass = os.getenv("QBIT_PASS", "").strip()
        if not qbit_user or not qbit_pass:
            print("❌ qBittorrent credentials missing")
            return False
        else:
            print(f"✅ qBittorrent User: {qbit_user}")
            print(f"✅ qBittorrent Pass: {'*' * len(qbit_pass)}")
        
        # Test bot connectivity
        print("\n🔍 Testing Telegram Bot connectivity...")
        try:
            import telebot
            bot = telebot.TeleBot(token)
            bot_info = bot.get_me()
            print(f"✅ Bot connected successfully!")
            print(f"   Bot Name: {bot_info.first_name}")
            print(f"   Bot Username: @{bot_info.username}")
            print(f"   Bot ID: {bot_info.id}")
        except Exception as e:
            print(f"❌ Failed to connect to Telegram: {e}")
            return False
        
        print("\n🎉 All configuration tests passed!")
        print("📋 Bot is ready to run locally!")
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_configuration()
    sys.exit(0 if success else 1)
