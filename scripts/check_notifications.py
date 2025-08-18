#!/usr/bin/env python3
"""
Check if notification monitoring service is working properly.
"""

import time
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from notification_system import get_notification_manager
from plugins.torrent.notification_handler import get_torrent_notification_manager

def check_notification_monitoring():
    """Check if the notification monitoring is working."""
    
    print("🔍 Checking Notification Monitoring Status")
    print("=" * 50)
    
    # Check if notification manager is initialized
    notification_manager = get_notification_manager()
    print(f"📋 Notification Manager: {'✅ Active' if notification_manager else '❌ Not initialized'}")
    
    # Check if torrent notification manager is initialized  
    torrent_notification_manager = get_torrent_notification_manager()
    print(f"🔄 Torrent Notification Manager: {'✅ Active' if torrent_notification_manager else '❌ Not initialized'}")
    
    if not notification_manager:
        print("❌ Notification system not initialized! Run the bot first.")
        return
    
    # Check if monitoring thread is running
    if hasattr(notification_manager, '_monitoring_thread'):
        thread = notification_manager._monitoring_thread
        is_alive = thread.is_alive() if thread else False
        print(f"🧵 Monitoring Thread: {'✅ Running' if is_alive else '❌ Not running'}")
    else:
        print("🧵 Monitoring Thread: ❌ Not found")
    
    # Check registered notifications
    try:
        notifications = notification_manager.get_pending_notifications()
        print(f"📝 Pending Notifications: {len(notifications)}")
        
        for notif_id, notif in notifications.items():
            print(f"   • {notif_id}: {notif.plugin} - {notif.type}")
    except Exception as e:
        print(f"📝 Pending Notifications: ❌ Error: {e}")
    
    print()
    print("🔧 Testing Remote qBittorrent Connection...")
    
    # Test qBittorrent connection
    try:
        from plugins.torrent.qbittorrent_client import QBittorrentClient
        qbt_client = QBittorrentClient()
        client = qbt_client.get_client()
        
        if client:
            # Test basic connection
            torrents = client.torrents()
            print(f"✅ qBittorrent Connection: SUCCESS ({len(torrents)} torrents found)")
            
            # Show some torrent info
            for i, torrent in enumerate(torrents[:3]):
                status = f"{torrent.name} - {torrent.state} ({torrent.progress*100:.1f}%)"
                print(f"   {i+1}. {status}")
                
            if len(torrents) > 3:
                print(f"   ... and {len(torrents)-3} more torrents")
                
        else:
            print("❌ qBittorrent Connection: FAILED - No client returned")
            
    except Exception as e:
        print(f"❌ qBittorrent Connection: FAILED - {e}")
    
    print()
    print("💡 Recommendations:")
    if not notification_manager:
        print("   • Notification manager is not initialized in bot.py")
    elif not hasattr(notification_manager, '_monitoring_thread') or not notification_manager._monitoring_thread.is_alive():
        print("   • Monitoring thread is not running - call notification_manager.start_monitoring()")
    else:
        print("   • Notification system appears to be set up correctly")
        print("   • Test by adding a torrent with notify flag: /t test:[notify]")

if __name__ == "__main__":
    check_notification_monitoring()
