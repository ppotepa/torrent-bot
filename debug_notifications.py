#!/usr/bin/env python3
"""
Debug notification system - check status, pending notifications, and test functionality
"""

import os
import time
import json
from dotenv import load_dotenv

# Load environment
load_dotenv()

def check_environment():
    """Check environment configuration"""
    print("🔧 Environment Configuration:")
    print("=" * 50)
    
    required_vars = [
        "TELEGRAM_BOT_TOKEN", 
        "ADMIN_USER_ID",
        "TELEGRAM_CHAT_ID",
        "QBIT_HOST",
        "QBIT_USER",
        "QBIT_PASS"
    ]
    
    for var in required_vars:
        value = os.getenv(var, "").strip()
        if value:
            # Mask sensitive data
            if "TOKEN" in var or "PASS" in var:
                masked = value[:8] + "***" if len(value) > 8 else "***"
                print(f"  ✅ {var}: {masked}")
            else:
                print(f"  ✅ {var}: {value}")
        else:
            print(f"  ❌ {var}: Not configured")
    print()

def check_notification_systems():
    """Check notification system status"""
    print("📊 Notification System Status:")
    print("=" * 50)
    
    try:
        from notification_system import get_notification_manager
        from plugins.torrent.notification_handler import get_torrent_notification_manager
        
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
        
    except Exception as e:
        print(f"  ❌ Error checking systems: {e}")
    print()

def check_notification_state():
    """Check pending/sent notifications"""
    print("📋 Notification State:")
    print("=" * 50)
    
    state_file = "notification_state/notifications.json"
    if os.path.exists(state_file):
        try:
            with open(state_file, 'r') as f:
                data = json.load(f)
            
            pending = data.get('pending', {})
            sent = data.get('sent', {})
            
            print(f"  📬 Pending notifications: {len(pending)}")
            print(f"  📨 Sent notifications: {len(sent)}")
            
            if pending:
                print("  \n📋 Pending notifications:")
                for notif_id, notif in list(pending.items())[:5]:  # Show first 5
                    title = notif.get('title', 'Unknown')
                    created = notif.get('created_at', 'Unknown')
                    print(f"     • {notif_id}: {title[:50]}...")
                    print(f"       Created: {created}")
            
            if sent:
                print("  \n📨 Recent sent notifications:")
                recent_sent = list(sent.items())[-3:]  # Show last 3
                for notif_id, timestamp in recent_sent:
                    print(f"     • {notif_id}: sent at {timestamp}")
                    
        except Exception as e:
            print(f"  ❌ Error reading state file: {e}")
    else:
        print("  ❌ No notification state file found")
    print()

def check_qbittorrent_connection():
    """Check qBittorrent connection"""
    print("🔗 qBittorrent Connection:")
    print("=" * 50)
    
    try:
        from plugins.torrent.qbittorrent_client import QBittorrentClient
        
        client = QBittorrentClient()
        torrents = client.get_all_torrents()
        
        if torrents:
            print(f"  ✅ Connected successfully")
            print(f"  📊 Total torrents: {len(torrents)}")
            
            # Show torrent states
            states = {}
            for torrent in torrents:
                state = torrent.get('state', 'unknown')
                states[state] = states.get(state, 0) + 1
            
            print("  📋 Torrent states:")
            for state, count in states.items():
                print(f"     • {state}: {count}")
                
            # Show recent completed torrents
            completed = [t for t in torrents if t.get('state') in ['uploading', 'stalledUP', 'queuedUP']]
            if completed:
                print("  \n🎉 Recently completed torrents:")
                for torrent in completed[:3]:
                    name = torrent.get('name', 'Unknown')
                    progress = torrent.get('progress', 0) * 100
                    print(f"     • {name[:50]}... ({progress:.1f}%)")
        else:
            print("  ✅ Connected but no torrents found")
            
    except Exception as e:
        print(f"  ❌ Connection failed: {e}")
    print()

def test_notification():
    """Test sending a notification"""
    print("🔔 Test Notification:")
    print("=" * 50)
    
    try:
        from plugins.torrent.notification_handler import register_torrent_by_name
        
        admin_user_id = os.getenv('ADMIN_USER_ID', '').strip()
        if not admin_user_id:
            print("  ❌ Cannot test - ADMIN_USER_ID not configured")
            return
        
        test_name = f"DEBUG TEST - {int(time.time())}"
        print(f"  🧪 Registering test notification: {test_name}")
        
        register_torrent_by_name(
            torrent_name=test_name,
            user_id=int(admin_user_id),
            chat_id=int(admin_user_id),
            additional_info={'debug_test': True, 'timestamp': time.time()}
        )
        
        print("  ✅ Test notification registered")
        print("  📝 Note: This won't trigger immediately - it waits for a matching torrent to complete")
        
    except Exception as e:
        print(f"  ❌ Test failed: {e}")
    print()

def show_monitoring_tips():
    """Show tips for monitoring"""
    print("💡 Monitoring Tips:")
    print("=" * 50)
    print("  🔍 To debug missed notifications:")
    print("     1. Check if notification was registered when you selected torrent")
    print("     2. Verify the torrent name matches what's in qBittorrent")
    print("     3. Ensure the torrent actually completed successfully")
    print("     4. Check notification_state/notifications.json for pending items")
    print()
    print("  🔧 Common issues:")
    print("     • Torrent name doesn't match exactly (name-based tracking)")
    print("     • qBittorrent connection problems")
    print("     • ADMIN_USER_ID not configured")
    print("     • Notification system not running")
    print()
    print("  ⚡ Quick fixes:")
    print("     • Restart the bot to reinitialize systems")
    print("     • Check .env file for all required variables")
    print("     • Verify qBittorrent is accessible from bot")
    print()

if __name__ == "__main__":
    print("🚀 Notification System Debug Tool")
    print("=" * 50)
    print()
    
    check_environment()
    check_notification_systems()
    check_notification_state()
    check_qbittorrent_connection()
    test_notification()
    show_monitoring_tips()
    
    print("🎯 Debug complete! Check the output above for any issues.")
