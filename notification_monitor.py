#!/usr/bin/env python3
"""
Standalone notification monitoring service.
This can run independently of the bot to monitor downloads.
"""

import os
import sys
import time
import signal
import threading
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from notification_system import NotificationManager
from plugins.torrent.notification_handler import TorrentNotificationManager

class StandaloneNotificationMonitor:
    """Standalone notification monitoring service."""
    
    def __init__(self):
        self.running = False
        self.notification_manager = None
        self.torrent_handler = None
        
    def initialize(self):
        """Initialize the monitoring service."""
        print("🚀 Initializing Standalone Notification Monitor")
        print("=" * 50)
        
        # Create a minimal bot-like object for notifications
        class MinimalBot:
            def send_message(self, chat_id, message, parse_mode=None):
                print(f"📨 [Would send to {chat_id}]: {message}")
                # In a real implementation, you'd use requests to send to Telegram API
                return True
        
        # Get admin user ID from environment
        admin_user_id = os.getenv("ADMIN_USER_ID", "").strip()
        default_chat_id = int(admin_user_id) if admin_user_id else None
        
        if not default_chat_id:
            print("⚠️ Warning: No ADMIN_USER_ID set. Notifications will only be printed.")
        
        # Initialize notification system
        bot = MinimalBot()
        self.notification_manager = NotificationManager(bot, default_chat_id)
        self.torrent_handler = TorrentNotificationManager()
        
        print(f"✅ Notification system initialized (admin: {default_chat_id})")
        
    def start_monitoring(self):
        """Start the monitoring service."""
        if not self.notification_manager:
            self.initialize()
        
        self.running = True
        
        # Start monitoring thread
        self.notification_manager.start_monitoring()
        
        print("🔄 Notification monitoring started")
        print("📋 Monitoring for torrent completion notifications...")
        print("🛑 Press Ctrl+C to stop")
        
        try:
            while self.running:
                # Check torrent notifications
                try:
                    pending = self.notification_manager.get_pending_notifications()
                    torrent_pending = [n for n in pending.values() if n.plugin == 'torrent']
                    
                    if torrent_pending:
                        print(f"📝 Monitoring {len(torrent_pending)} torrent notifications...")
                        for notif in torrent_pending:
                            print(f"   • {notif.notification_id}: {notif.title}")
                    
                except Exception as e:
                    print(f"❌ Error checking notifications: {e}")
                
                # Wait 30 seconds between checks
                for _ in range(30):
                    if not self.running:
                        break
                    time.sleep(1)
                        
        except KeyboardInterrupt:
            print("\n🛑 Received interrupt signal")
        finally:
            self.stop_monitoring()
    
    def stop_monitoring(self):
        """Stop the monitoring service."""
        print("🛑 Stopping notification monitor...")
        self.running = False
        
        if self.notification_manager:
            self.notification_manager.stop_monitoring()
        
        print("✅ Notification monitor stopped")

def signal_handler(signum, frame):
    """Handle shutdown signals."""
    print(f"\n🛑 Received signal {signum}")
    monitor.stop_monitoring()
    sys.exit(0)

if __name__ == "__main__":
    # Set up signal handlers
    monitor = StandaloneNotificationMonitor()
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("🔔 Standalone Notification Monitor")
    print("=" * 40)
    print("This service monitors torrent downloads and sends notifications")
    print("when downloads complete, independent of the main bot.")
    print()
    
    # Check if we can connect to qBittorrent
    try:
        from plugins.torrent.qbittorrent_client import QBittorrentClient
        qbt_client = QBittorrentClient()
        client = qbt_client.get_client()
        
        if client:
            torrents = client.torrents()
            print(f"✅ qBittorrent connected: {len(torrents)} torrents found")
        else:
            print("❌ Cannot connect to qBittorrent")
            print("   Make sure qBittorrent is running and accessible")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ qBittorrent connection failed: {e}")
        print("   Make sure qBittorrent is running and configuration is correct")
        sys.exit(1)
    
    print()
    
    # Start monitoring
    monitor.start_monitoring()
