"""
Torrent-specific notification handling.
Manages notifications for individual torrent downloads.
"""

import time
import threading
from typing import Dict, Set, Optional
from notification_system import get_notification_manager, NotificationRequest
from .utils import extract_infohash_from_magnet, human_size


class TorrentNotificationManager:
    """Manages notifications for specific torrent downloads."""
    
    def __init__(self):
        # Track torrents that need notifications
        self.monitored_torrents: Dict[str, Dict] = {}  # hash -> torrent info
        self.check_interval = 30  # seconds
        self.running = False
        self.monitor_thread = None
    
    def register_torrent_notification(self, torrent_hash: str, torrent_name: str, 
                                    user_id: int, chat_id: int, additional_info: Dict = None):
        """Register a specific torrent for completion notification."""
        notification_id = f"torrent_{torrent_hash}"
        
        # Store torrent info for monitoring
        self.monitored_torrents[torrent_hash] = {
            'name': torrent_name,
            'user_id': user_id,
            'chat_id': chat_id,
            'added_at': time.time(),
            'notification_id': notification_id,
            'additional_info': additional_info or {}
        }
        
        # Create notification message
        title = "Torrent Download Complete"
        message = f"📁 **{torrent_name}**\n\n"
        message += f"✅ Your torrent download has finished!\n"
        message += f"🎉 Ready to enjoy!"
        
        # Register with notification system
        manager = get_notification_manager()
        if manager:
            notification = NotificationRequest(
                notification_id=notification_id,
                plugin="torrent",
                type="download_complete",
                title=title,
                message=message,
                chat_id=chat_id,
                metadata={
                    'torrent_hash': torrent_hash,
                    'torrent_name': torrent_name,
                    'user_id': user_id,
                    'additional_info': additional_info or {}
                }
            )
            manager.register_notification(notification)
        
        print(f"📝 Registered notification for torrent: {torrent_name} (user: {user_id})")
        
        # Start monitoring if not already running
        if not self.running:
            self.start_monitoring()
    
    def start_monitoring(self):
        """Start monitoring registered torrents for completion."""
        if self.running:
            return
        
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        print("🔍 Torrent notification monitoring started")
    
    def stop_monitoring(self):
        """Stop monitoring torrents."""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        print("🛑 Torrent notification monitoring stopped")
    
    def _monitor_loop(self):
        """Monitor registered torrents for completion."""
        from .qbittorrent_client import QBittorrentClient
        
        while self.running:
            try:
                if not self.monitored_torrents:
                    # No torrents to monitor, sleep longer
                    time.sleep(60)
                    continue
                
                # Check torrent status
                client = QBittorrentClient()
                if not client.connect():
                    print("⚠️ Could not connect to qBittorrent for notification monitoring")
                    time.sleep(self.check_interval)
                    continue
                
                torrents = client.client.torrents.info()
                completed_hashes = []
                
                for torrent in torrents:
                    torrent_hash = torrent.hash
                    
                    if torrent_hash in self.monitored_torrents:
                        # Check if completed
                        if (torrent.state in ['completedUP', 'completedDL', 'uploading', 'queuedUP', 'stalledUP'] and 
                            torrent.progress >= 1.0):
                            
                            # Torrent is complete, send notification
                            self._send_torrent_notification(torrent_hash, torrent)
                            completed_hashes.append(torrent_hash)
                
                # Remove completed torrents from monitoring
                for torrent_hash in completed_hashes:
                    self.monitored_torrents.pop(torrent_hash, None)
                
                # Sleep for check interval
                for _ in range(self.check_interval):
                    if not self.running:
                        break
                    time.sleep(1)
                    
            except Exception as e:
                print(f"❌ Error in torrent notification monitoring: {e}")
                time.sleep(10)
        
        print("🔄 Torrent notification monitoring loop ended")
    
    def _send_torrent_notification(self, torrent_hash: str, torrent_info):
        """Send notification for a completed torrent."""
        try:
            torrent_data = self.monitored_torrents.get(torrent_hash)
            if not torrent_data:
                return
            
            # Update notification with actual completion info
            title = "Torrent Download Complete"
            message = f"📁 **{torrent_info.name}**\n\n"
            message += f"💾 Size: {human_size(torrent_info.size)}\n"
            message += f"📂 Location: {getattr(torrent_info, 'save_path', 'Unknown')}\n"
            message += f"⏰ Completed: {time.strftime('%H:%M:%S')}\n\n"
            message += f"✅ Your torrent download has finished!\n"
            message += f"🎉 Ready to enjoy!"
            
            # Send the notification
            manager = get_notification_manager()
            if manager:
                notification_id = torrent_data['notification_id']
                
                # Update the pending notification with actual completion details
                if notification_id in manager.pending_notifications:
                    notification = manager.pending_notifications[notification_id]
                    notification.message = message
                    notification.metadata.update({
                        'completed_at': time.time(),
                        'size': torrent_info.size,
                        'save_path': getattr(torrent_info, 'save_path', 'Unknown')
                    })
                
                manager.send_notification_by_id(notification_id)
                print(f"📨 Sent torrent completion notification: {torrent_info.name}")
            
        except Exception as e:
            print(f"❌ Error sending torrent notification: {e}")
    
    def cancel_notification(self, torrent_hash: str):
        """Cancel notification for a specific torrent."""
        if torrent_hash in self.monitored_torrents:
            torrent_data = self.monitored_torrents.pop(torrent_hash)
            
            # Cancel in notification system
            manager = get_notification_manager()
            if manager:
                manager.cancel_notification(torrent_data['notification_id'])
            
            print(f"🚫 Cancelled notification for torrent: {torrent_data['name']}")
            return True
        return False
    
    def get_monitored_torrents(self) -> Dict[str, Dict]:
        """Get currently monitored torrents."""
        return self.monitored_torrents.copy()
    
    def get_status(self) -> str:
        """Get notification monitoring status."""
        status = []
        status.append("🔔 Torrent Notification Monitor")
        status.append(f"Running: {'✅ Yes' if self.running else '❌ No'}")
        status.append(f"Monitored torrents: {len(self.monitored_torrents)}")
        
        if self.monitored_torrents:
            status.append(f"\n📋 Monitored Torrents:")
            for torrent_hash, data in list(self.monitored_torrents.items())[:5]:  # Show first 5
                age_hours = (time.time() - data['added_at']) / 3600
                status.append(f"  • {data['name'][:50]}... (user: {data['user_id']}, {age_hours:.1f}h ago)")
        
        return "\n".join(status)


# Global torrent notification manager
_torrent_notification_manager = None

def get_torrent_notification_manager() -> TorrentNotificationManager:
    """Get the global torrent notification manager."""
    global _torrent_notification_manager
    if _torrent_notification_manager is None:
        _torrent_notification_manager = TorrentNotificationManager()
    return _torrent_notification_manager

def register_torrent_for_notification(torrent_hash: str, torrent_name: str, user_id: int, chat_id: int, additional_info: Dict = None):
    """Convenience function to register a torrent for notification."""
    manager = get_torrent_notification_manager()
    manager.register_torrent_notification(torrent_hash, torrent_name, user_id, chat_id, additional_info)

def cancel_torrent_notification(torrent_hash: str):
    """Convenience function to cancel a torrent notification."""
    manager = get_torrent_notification_manager()
    return manager.cancel_notification(torrent_hash)
