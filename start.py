#!/usr/bin/env python3
"""
Startup script for the Telegram Bot
Handles environment setup and launches the main application
"""

import os
import sys
from pathlib import Path

def main():
    """Main startup function"""
    print("🤖 Starting Telegram Bot with Reflection-Based Plugin System")
    print("=" * 60)
    
    # Add src directory to Python path
    src_path = Path(__file__).parent / "src"
    if not src_path.exists():
        print("❌ Error: src/ directory not found!")
        print("   Make sure you're running this from the project root.")    
        sys.exit(1)
    
    sys.path.insert(0, str(src_path))
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required!")
        print(f"   Current version: {sys.version}")
        sys.exit(1)
    
    print(f"✅ Python version: {sys.version.split()[0]}")
    
    # Check for required environment variables
    required_vars = ["TELEGRAM_BOT_TOKEN"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Error: Missing required environment variables:")
        for var in missing_vars:
            print(f"   • {var}")
        print("\n💡 Create a .env file in the project root with:")
        print("   TELEGRAM_BOT_TOKEN=your_bot_token_here")
        print("   ADMIN_USER_IDS=your_user_id")
        sys.exit(1)
    
    # Check for optional but recommended variables
    optional_vars = ["ADMIN_USER_IDS", "OWNER_USER_IDS"]
    for var in optional_vars:
        if os.getenv(var):
            print(f"✅ {var} configured")
        else:
            print(f"⚠️  {var} not configured (optional)")
    
    # Try to import main dependencies
    try:
        import telebot
        print("✅ pyTelegramBotAPI available")
    except ImportError:
        print("❌ Error: pyTelegramBotAPI not installed!")
        print("   Run: pip install -r src/requirements.txt")
        sys.exit(1)
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ Environment variables loaded")
    except ImportError:
        print("⚠️  python-dotenv not available (optional)")
    
    print("=" * 60)
    print("🚀 Launching bot...")
    print()
    
    # Import and run the main application
    try:
        from main import main as bot_main
        bot_main()
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
    except Exception as e:
        print(f"\n💥 Bot crashed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

