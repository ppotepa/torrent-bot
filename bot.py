#!/usr/bin/env python3
"""
Main entry point for the Telegram Bot
Uses the new reflection-based plugin system with automatic command discovery

This bot includes:
- 🔍 Torrent search and download (via qBittorrent + Jackett)
- 🎥 YouTube video/audio download (yt-dlp)
- 📘 Facebook video download
- 🎧 Text-to-speech audiobook conversion (multiple engines)
- 🖥️ System information and monitoring
- ❓ Advanced help system
"""

import os
import sys
from pathlib import Path

def main():
    """Main entry point - delegates to the new reflection-based system"""
    
    print("🤖 Starting Telegram Bot with Reflection-Based Plugin System")
    print("=" * 60)
    
    # Add src directory to Python path
    src_path = Path(__file__).parent / "src"
    if not src_path.exists():
        print("❌ Error: src/ directory not found!")
        print("   The new plugin system is located in src/")
        print("   Run: python start.py")
        sys.exit(1)
    
    sys.path.insert(0, str(src_path))
    
    # Import and run the new system
    try:
        from main import main as new_main
        new_main()
    except ImportError as e:
        print(f"❌ Error importing new system: {e}")
        print("\n💡 The bot has been refactored to use a new plugin system.")
        print("   Please use one of these entry points:")
        print("   • python start.py        (recommended)")
        print("   • python src/main.py     (direct)")
        print("   • python bot_legacy.py   (old system)")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Bot crashed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()