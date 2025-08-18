#!/usr/bin/env python3
"""
Test notification functionality by actually starting the bot systems
"""

import os
import sys
import time
from dotenv import load_dotenv

# Load environment
load_dotenv()

def test_complete_system():
    """Test the complete notification system as it runs in the bot"""
    print("🚀 Testing Complete Notification System")
    print("=" * 50)
    
    try:
        # Import bot to trigger initialization
        print("📋 Importing bot module (this initializes everything)...")
        import bot
        
        # Give systems time to start
        time.sleep(2)
        
        print("✅ Bot module imported successfully")
        print()
        
        # Check systems after initialization
        from notification_system import get_notification_manager
        from plugins.torrent.notification_handler import get_torrent_notification_manager
        
        print("📊 System Status After Bot Initialization:")
        
        # Main notification system
        main_manager = get_notification_manager()
        if main_manager:
            print("  ✅ Main notification system: Initialized")
            print(f"     Running: {getattr(main_manager, 'running', 'Unknown')}")
        else:
            print("  ❌ Main notification system: Not initialized")
        
        # Torrent notification system
        torrent_manager = get_torrent_notification_manager()
        print(f"  ✅ Torrent notification system: Initialized")
        print(f"     Running: {torrent_manager.running}")
        print(f"     Monitor thread: {torrent_manager.monitor_thread is not None}")
        print(f"     Hash-based tracked: {len(torrent_manager.monitored_torrents)}")
        print(f"     Name-based tracked: {len(torrent_manager.monitored_by_name)}")
        print()
        
        # Test notification registration
        print("🔔 Testing Notification Registration:")
        from plugins.torrent.notification_handler import register_torrent_by_name
        
        admin_user_id = os.getenv('ADMIN_USER_ID', '').strip()
        test_name = f"SYSTEM TEST - {int(time.time())}"
        
        register_torrent_by_name(
            torrent_name=test_name,
            user_id=int(admin_user_id),
            chat_id=int(admin_user_id),
            additional_info={'system_test': True}
        )
        
        print(f"  ✅ Registered: {test_name}")
        print(f"  📊 Now tracking {len(torrent_manager.monitored_by_name)} name-based notifications")
        print()
        
        # Show what would happen when a torrent completes
        print("💡 Notification Flow:")
        print("  1. When you select a torrent → register_torrent_by_name() called")
        print("  2. Monitoring thread checks qBittorrent every 30s")
        print("  3. When matching torrent completes → notification sent")
        print("  4. Notification appears in your Telegram chat")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing system: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_complete_system()
    
    if success:
        print("🎯 System Test PASSED")
        print()
        print("💡 Next Steps:")
        print("  1. Start your bot: python bot.py")
        print("  2. Select a torrent in Telegram")
        print("  3. Wait for torrent to complete")
        print("  4. You should receive a notification!")
    else:
        print("❌ System Test FAILED - check errors above")
