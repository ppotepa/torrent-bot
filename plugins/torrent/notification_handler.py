"""
Torrent-specific notification handling.
Manages notifications for individual torrent downloads.
"""

import time
import threading
from typing import Dict, Set, Optional
from notification_system import get_notification_manager, NotificationRequest
from .utils import extract_infohash_from_magnet, human_size
from .qbittorrent_client import QBittorrentClient


class TorrentNotificationManager:
    """Manages notifications for specific torrent downloads."""
    
    def __init__(self):
        # Track torrents that need notifications
        self.monitored_torrents: Dict[str, Dict] = {}  # hash -> torrent info
        self.monitored_by_name: Dict[str, Dict] = {}   # name -> torrent info (fallback when no hash)
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
    
    def register_torrent_by_name(self, torrent_name: str, user_id: int, chat_id: int, additional_info: Dict = None):
        """Register a torrent for notification tracking by name (fallback when hash unavailable)."""
        # Create a safe identifier from the torrent name
        safe_name = torrent_name.replace(" ", "_").replace("/", "_").replace("\\", "_")[:50]
        notification_id = f"torrent_name_{safe_name}_{int(time.time())}"
        
        # Store torrent info for monitoring by name
        self.monitored_by_name[torrent_name] = {
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
                    'torrent_name': torrent_name,
                    'user_id': user_id,
                    'tracking_method': 'name',
                    'additional_info': additional_info or {}
                }
            )
            manager.register_notification(notification)
        
        print(f"📝 Registered name-based notification for torrent: {torrent_name} (user: {user_id})")
        
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
                if not self.monitored_torrents and not self.monitored_by_name:
                    # No torrents to monitor, sleep longer
                    time.sleep(60)
                    continue
                
                # Check torrent status
                client = QBittorrentClient()
                try:
                    qbt_client = client.get_client()
                    torrents = qbt_client.torrents.info()
                    
                    # Check hash-based tracked torrents
                    self._check_hash_based_torrents(torrents)
                    
                    # Check name-based tracked torrents
                    self._check_name_based_torrents(torrents)
                except Exception as qbt_error:
                    print(f"⚠️ Could not connect to qBittorrent for notification monitoring: {qbt_error}")
                    time.sleep(self.check_interval)
                    continue
                
                # Sleep for check interval
                for _ in range(self.check_interval):
                    if not self.running:
                        break
                    time.sleep(1)
                    
            except Exception as e:
                print(f"❌ Error in torrent notification monitoring: {e}")
                time.sleep(10)
        
        print("🔄 Torrent notification monitoring loop ended")
    
    def _check_hash_based_torrents(self, torrents):
        """Check hash-based tracked torrents for completion."""
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
    
    def _check_name_based_torrents(self, torrents):
        """Check name-based tracked torrents for completion."""
        completed_names = []
        
        for tracked_name, torrent_data in self.monitored_by_name.items():
            # Find torrent by name matching
            matching_torrent = None
            for torrent in torrents:
                if self._names_match(torrent.name, tracked_name):
                    matching_torrent = torrent
                    break
            
            if matching_torrent:
                # Check if completed
                if (matching_torrent.state in ['completedUP', 'completedDL', 'uploading', 'queuedUP', 'stalledUP'] and 
                    matching_torrent.progress >= 1.0):
                    
                    # Torrent is complete, send notification
                    self._send_name_based_notification(tracked_name, matching_torrent)
                    completed_names.append(tracked_name)
        
        # Remove completed torrents from monitoring
        for name in completed_names:
            self.monitored_by_name.pop(name, None)
    
    def _names_match(self, qbt_name: str, tracked_name: str) -> bool:
        """Check if torrent names match (with some flexibility for differences)."""
        if not qbt_name or not tracked_name:
            return False
        
        # Exact match
        if qbt_name == tracked_name:
            return True
        
        # Normalize and compare (remove common differences)
        def normalize_name(name):
            return name.lower().replace(" ", "").replace(".", "").replace("-", "").replace("_", "")
        
        normalized_qbt = normalize_name(qbt_name)
        normalized_tracked = normalize_name(tracked_name)
        
        # Check if one contains the other (with significant overlap)
        if len(normalized_tracked) > 10:  # Only for reasonably long names
            return (normalized_tracked in normalized_qbt or 
                   normalized_qbt in normalized_tracked)
        
        return False
    
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
    
    def _send_name_based_notification(self, tracked_name: str, torrent_info):
        """Send notification for a completed name-tracked torrent."""
        try:
            torrent_data = self.monitored_by_name.get(tracked_name)
            if not torrent_data:
                return
            
            # Update notification with actual completion info
            title = "Torrent Download Complete"
            message = f"📁 **{torrent_info.name}**\n\n"
            message += f"💾 Size: {human_size(torrent_info.size)}\n"
            message += f"📂 Location: {getattr(torrent_info, 'save_path', 'Unknown')}\n"
            message += f"⏰ Completed: {time.strftime('%H:%M:%S')}\n\n"
            message += f"✅ Your torrent download has finished!\n"
            message += f"🎉 Ready to enjoy!\n\n"
            message += f"_Tracked by name (no hash available)_"
            
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
                        'save_path': getattr(torrent_info, 'save_path', 'Unknown'),
                        'tracking_method': 'name'
                    })
                
                manager.send_notification_by_id(notification_id)
                print(f"📨 Sent name-based torrent completion notification: {torrent_info.name}")
            
        except Exception as e:
            print(f"❌ Error sending name-based torrent notification: {e}")

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
    
    def check_torrent_completion(self, notification_id: str) -> bool:
        """Check if a specific torrent notification should be sent (torrent is complete)."""
        try:
            # Extract infohash from notification_id (format: torrent_INFOHASH_USERID)
            if not notification_id.startswith('torrent_'):
                return False
            
            parts = notification_id.split('_')
            if len(parts) < 3:
                return False
            
            infohash = parts[1]
            
            # Connect to qBittorrent and check torrent status
            qbt_client = QBittorrentClient()
            client = qbt_client.get_client()
            
            if not client:
                print(f"❌ Cannot connect to qBittorrent for notification check")
                return False
            
            # Find the torrent by infohash
            torrents = client.torrents()
            for torrent in torrents:
                if torrent.hash.lower() == infohash.lower():
                    # Check if torrent is complete
                    if torrent.progress >= 1.0 and torrent.state in ['completed', 'uploading', 'stalledUP']:
                        print(f"✅ Torrent {infohash[:8]}... is complete ({torrent.progress*100:.1f}%)")
                        return True
                    else:
                        # Still downloading
                        return False
            
            # Torrent not found - might have been removed, consider it complete
            print(f"⚠️ Torrent {infohash[:8]}... not found in qBittorrent")
            return True
            
        except Exception as e:
            print(f"❌ Error checking torrent completion for {notification_id}: {e}")
            return False
    
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

def register_torrent_by_name(torrent_name: str, user_id: int, chat_id: int, additional_info: Dict = None):
    """Convenience function to register a torrent for notification by name (fallback when no hash)."""
    manager = get_torrent_notification_manager()
    manager.register_torrent_by_name(torrent_name, user_id, chat_id, additional_info)

def cancel_torrent_notification(torrent_hash: str):
    """Convenience function to cancel a torrent notification."""
    manager = get_torrent_notification_manager()
    return manager.cancel_notification(torrent_hash)
