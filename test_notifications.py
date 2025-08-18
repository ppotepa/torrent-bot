#!/usr/bin/env python3
"""
Diagnostic script for the notification system.
"""

import os
import sys
import time
from typing import Dict

def test_notification_system():
    """Test the notification system components."""
    print("🔍 Diagnosing Notification System")
    print("=" * 50)
    
    # Test 1: Check if notification system initializes
    try:
        from notification_system import get_notification_manager, initialize_notification_manager
        
        # Create a dummy bot class for testing
        class DummyBot:
            def send_message(self, chat_id, text, parse_mode=None):
                print(f"[DUMMY BOT] Would send to {chat_id}: {text}")
        
        dummy_bot = DummyBot()
        test_chat_id = 12345
        
        # Initialize notification manager
        manager = initialize_notification_manager(dummy_bot, test_chat_id)
        print("✅ Notification system initialized successfully")
        
        # Test notification registration
        from notification_system import NotificationRequest
        test_notification = NotificationRequest(
            notification_id="test_notification_123",
            plugin="test",
            type="test_complete",
            title="Test Notification",
            message="This is a test notification",
            chat_id=test_chat_id
        )
        
        manager.register_notification(test_notification)
        print("✅ Test notification registered successfully")
        
        # Check pending notifications
        pending = manager.get_pending_notifications()
        print(f"✅ Pending notifications: {len(pending)}")
        
        # Test sending notification
        success = manager.send_notification_by_id("test_notification_123")
        print(f"✅ Test notification sent: {success}")
        
    except Exception as e:
        print(f"❌ Notification system error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 2: Check torrent notification handler
    print("\n🔍 Testing Torrent Notification Handler")
    print("-" * 30)
    
    try:
        from plugins.torrent.notification_handler import get_torrent_notification_manager
        
        torrent_manager = get_torrent_notification_manager()
        print("✅ Torrent notification manager created")
        
        # Test torrent registration
        test_hash = "1234567890abcdef1234567890abcdef12345678"
        test_name = "Test Movie 2024 1080p BluRay x264-TEST"
        test_user_id = 67890
        test_chat_id = 12345
        
        torrent_manager.register_torrent_notification(
            torrent_hash=test_hash,
            torrent_name=test_name,
            user_id=test_user_id,
            chat_id=test_chat_id
        )
        print("✅ Test torrent registered for notification")
        
        # Check status
        status = torrent_manager.get_status()
        print(f"✅ Torrent manager status:\n{status}")
        
        # Check if monitoring started
        print(f"✅ Monitoring running: {torrent_manager.running}")
        
    except Exception as e:
        print(f"❌ Torrent notification error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 3: Check qBittorrent connection
    print("\n🔍 Testing qBittorrent Connection")
    print("-" * 30)
    
    try:
        from plugins.torrent.qbittorrent_client import QBittorrentClient
        
        client = QBittorrentClient()
        try:
            qbt_client = client.get_client()
            connected = True
        except Exception as e:
            connected = False
            print(f"⚠️ qBittorrent connection failed: {e}")
        
        print(f"✅ qBittorrent connection: {'Success' if connected else 'Failed'}")
        
        if connected:
            # Test getting torrents
            try:
                torrents = qbt_client.torrents.info()
                print(f"✅ Found {len(torrents)} torrents in qBittorrent")
                
                # Show first few torrents for reference
                for i, torrent in enumerate(torrents[:3]):
                    print(f"  {i+1}. {torrent.name} - State: {torrent.state} - Progress: {torrent.progress*100:.1f}%")
                    
            except Exception as e:
                print(f"⚠️ Could not get torrent list: {e}")
        else:
            print("❌ Cannot test torrent monitoring without qBittorrent connection")
            
    except Exception as e:
        print(f"❌ qBittorrent client error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 4: Check notification state persistence
    print("\n🔍 Testing Notification State")
    print("-" * 30)
    
    try:
        state_dir = os.path.join(os.getcwd(), "notification_state")
        state_file = os.path.join(state_dir, "notifications.json")
        
        print(f"✅ State directory: {state_dir}")
        print(f"✅ State file exists: {os.path.exists(state_file)}")
        
        if os.path.exists(state_file):
            import json
            with open(state_file, 'r') as f:
                data = json.load(f)
            print(f"✅ State file contains: {len(data.get('pending_notifications', {}))} pending, {len(data.get('sent_notifications', []))} sent")
        
    except Exception as e:
        print(f"❌ State persistence error: {e}")
        return False
    
    print("\n🎉 Notification system diagnostic completed!")
    return True

if __name__ == "__main__":
    test_notification_system()
from plugins.torrent.notification_handler import register_torrent_for_notification, get_torrent_notification_manager

def test_notification_system():
    print("=== Testing Notification System ===")
    
    # Test 1: Basic notification creation
    print("\n1. Testing notification creation...")
    notification = NotificationRequest(
        notification_id="test_notification_1",
        plugin="test",
        type="test_complete",
        title="Test Notification",
        message="This is a test notification message.",
        metadata={"test_data": "example"}
    )
    print(f"   Created notification: {notification.notification_id}")
    print(f"   Title: {notification.title}")
    print(f"   Message: {notification.message}")
    
    # Test 2: Convenience functions
    print("\n2. Testing convenience functions...")
    success = send_notification(
        plugin="test",
        notification_type="immediate_test",
        title="Immediate Test",
        message="This would be sent immediately if bot was available",
        item_id="test_immediate",
        metadata={"test": True}
    )
    print(f"   Immediate send result: {success} (expected False - no bot)")
    
    success = register_notification(
        plugin="test",
        notification_type="pending_test", 
        title="Pending Test",
        message="This would be sent later",
        item_id="test_pending",
        metadata={"test": True}
    )
    print(f"   Registration result: {success} (expected False - no bot)")
    
    # Test 3: Torrent notification system
    print("\n3. Testing torrent notification system...")
    torrent_manager = get_torrent_notification_manager()
    print(f"   Torrent manager created: {torrent_manager is not None}")
    print(f"   Initial monitored torrents: {len(torrent_manager.monitored_torrents)}")
    print(f"   Monitor running: {torrent_manager.running}")
    
    # Test 4: Status reporting
    print("\n4. Testing status reporting...")
    status = torrent_manager.get_status()
    print(f"   Torrent manager status:\n{status}")
    
    print("\n✅ Notification system tests completed!")
    print("🔄 To fully test with bot, restart the bot and try: /t ubuntu:[notify]")

if __name__ == "__main__":
    test_notification_system()
