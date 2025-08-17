"""Modern Torrent Bot with SOLID architecture - Main entry point."""

import asyncio
import logging
import os
import sys
from pathlib import Path

# Add src to Python path for imports
current_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(current_dir))

from src.main import main


if __name__ == "__main__":
    """Entry point for the refactored torrent bot."""
    
    print("🤖 Starting Modern Torrent Bot with SOLID Architecture...")
    print("📁 Using new architecture with proper separation of concerns")
    print("🔧 Configuration loaded from environment variables")
    print("🐳 Designed for Docker deployment with zerotier network")
    print()
    
    # Set event loop policy for Windows
    if sys.platform.startswith('win'):
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    try:
        # Run the application
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️ Interrupted by user")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)
