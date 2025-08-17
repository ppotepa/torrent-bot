#!/usr/bin/env python3
"""
GitHub Actions deployment runner
Uses environment variables set by GitHub Actions secrets
"""
import os
import sys
from dotenv import load_dotenv

def main():
    print("🚀 Starting Torrent Bot for GitHub Actions deployment...")
    
    # Load environment variables
    load_dotenv()
    
    # Validate required environment variables
    required_vars = [
        'TELEGRAM_BOT_TOKEN',
        'JACKETT_API_KEY', 
        'JACKETT_URL',
        'QBITTORRENT_HOST',
        'QBITTORRENT_USERNAME',
        'QBITTORRENT_PASSWORD'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("💡 Make sure all GitHub secrets are configured properly.")
        sys.exit(1)
    
    print("✅ All required environment variables are set")
    print(f"📱 Bot Token: {os.getenv('TELEGRAM_BOT_TOKEN')[:20]}...")
    print(f"🔧 Jackett Key: {os.getenv('JACKETT_API_KEY')}")
    print(f"🌐 Jackett URL: {os.getenv('JACKETT_URL')}")
    print(f"⚡ qBittorrent: {os.getenv('QBITTORRENT_HOST')}")
    
    # Import and start the bot
    try:
        from bot import main as bot_main
        print("🎉 Starting bot with GitHub Actions configuration...")
        bot_main()
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
    except Exception as e:
        print(f"❌ Error starting bot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
