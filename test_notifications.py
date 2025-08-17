#!/usr/bin/env python3
"""
Test script for the notification system.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from notification_system import NotificationRequest, send_notification, register_notification, get_notification_manager
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
