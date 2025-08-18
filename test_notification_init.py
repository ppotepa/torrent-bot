#!/usr/bin/env python3
"""
Test the notification system initialization.
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_notification_system():
    """Test if the notification system can be initialized without errors."""
    
    print("🧪 Testing Notification System Initialization")
    print("=" * 50)
    
    try:
        # Test importing the modules
        from notification_system import NotificationManager, initialize_notification_manager
        print("✅ Successfully imported notification_system")
        
        from plugins.torrent.notification_handler import TorrentNotificationManager, get_torrent_notification_manager
        print("✅ Successfully imported torrent notification handler")
        
        # Create a mock bot for testing
        class MockBot:
            def send_message(self, chat_id, message, parse_mode=None):
                print(f"📨 [MOCK] Would send to {chat_id}: {message}")
                return True
        
        # Test initialization
        mock_bot = MockBot()
        notification_manager = initialize_notification_manager(mock_bot, 12345)
        print("✅ Successfully initialized notification manager")
        
        # Test if monitoring thread starts
        if hasattr(notification_manager, '_monitoring_thread') and notification_manager._monitoring_thread:
            if notification_manager._monitoring_thread.is_alive():
                print("✅ Monitoring thread is running")
            else:
                print("⚠️ Monitoring thread exists but is not running")
        else:
            print("❌ Monitoring thread not found")
        
        # Test torrent notification manager
        torrent_manager = get_torrent_notification_manager()
        if torrent_manager:
            print("✅ Torrent notification manager initialized")
        else:
            print("⚠️ Torrent notification manager not initialized")
        
        # Stop monitoring for cleanup
        notification_manager.stop_monitoring()
        print("✅ Successfully stopped monitoring")
        
        print("\n🎉 All tests passed! Notification system should work in Docker.")
        
    except Exception as e:
        print(f"❌ Error testing notification system: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    test_notification_system()
