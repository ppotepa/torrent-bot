"""
Centralized notification system for the bot.
Provides reusable notification functionality across all plugins.
"""

import json
import os
import time
from datetime import datetime
from typing import Dict, Set, Optional, Callable, Any
from dataclasses import dataclass, asdict


@dataclass
class NotificationRequest:
    """Represents a notification request."""
    notification_id: str  # Unique identifier for this notification
    plugin: str  # Which plugin requested the notification (torrent, download, etc.)
    type: str  # Type of notification (download_complete, conversion_done, etc.)
    title: str  # Notification title
    message: str  # Notification message
    chat_id: Optional[int] = None  # Specific chat to notify (if None, uses default)
    created_at: float = None  # When notification was created
    metadata: Dict[str, Any] = None  # Additional data for the notification
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = time.time()
        if self.metadata is None:
            self.metadata = {}


class NotificationManager:
    """Manages notifications across all bot plugins."""
    
    def __init__(self, bot_instance, default_chat_id: Optional[int] = None):
        self.bot = bot_instance
        self.default_chat_id = default_chat_id
        
        # Track sent notifications to avoid duplicates
        self.sent_notifications: Set[str] = set()
        
        # Track pending notifications for items being monitored
        self.pending_notifications: Dict[str, NotificationRequest] = {}
        
        # State persistence
        self.state_dir = os.path.join(os.getcwd(), "notification_state")
        os.makedirs(self.state_dir, exist_ok=True)
        self.state_file = os.path.join(self.state_dir, "notifications.json")
        
        self._load_state()
    
    def _load_state(self):
        """Load notification state from file."""
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, 'r') as f:
                    data = json.load(f)
                    self.sent_notifications = set(data.get('sent_notifications', []))
                    
                    # Load pending notifications
                    pending_data = data.get('pending_notifications', {})
                    for notif_id, notif_dict in pending_data.items():
                        self.pending_notifications[notif_id] = NotificationRequest(**notif_dict)
                    
                print(f"📋 Loaded {len(self.sent_notifications)} sent and {len(self.pending_notifications)} pending notifications")
        except Exception as e:
            print(f"⚠️ Could not load notification state: {e}")
    
    def _save_state(self):
        """Save notification state to file."""
        try:
            data = {
                'sent_notifications': list(self.sent_notifications),
                'pending_notifications': {
                    notif_id: asdict(notif) for notif_id, notif in self.pending_notifications.items()
                },
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.state_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"⚠️ Could not save notification state: {e}")
    
    def register_notification(self, notification: NotificationRequest):
        """Register a notification to be sent when conditions are met."""
        self.pending_notifications[notification.notification_id] = notification
        self._save_state()
        print(f"📝 Registered {notification.plugin} notification: {notification.notification_id}")
    
    def send_notification(self, notification: NotificationRequest, force: bool = False):
        """Send a notification immediately."""
        # Check if already sent (unless forced)
        if not force and notification.notification_id in self.sent_notifications:
            print(f"📋 Notification {notification.notification_id} already sent, skipping")
            return False
        
        try:
            # Determine chat ID
            chat_id = notification.chat_id or self.default_chat_id
            if not chat_id:
                print(f"❌ No chat ID available for notification {notification.notification_id}")
                return False
            
            # Format the message
            full_message = f"🔔 **{notification.title}**\n\n{notification.message}"
            
            # Add plugin attribution if needed
            if notification.plugin:
                full_message += f"\n\n_via {notification.plugin}_"
            
            # Send the message
            self.bot.send_message(chat_id, full_message, parse_mode="Markdown")
            
            # Mark as sent
            self.sent_notifications.add(notification.notification_id)
            
            # Remove from pending if it was there
            self.pending_notifications.pop(notification.notification_id, None)
            
            self._save_state()
            
            print(f"📨 Sent notification: {notification.title}")
            return True
            
        except Exception as e:
            print(f"❌ Error sending notification {notification.notification_id}: {e}")
            return False
    
    def send_notification_by_id(self, notification_id: str, force: bool = False):
        """Send a pending notification by its ID."""
        if notification_id in self.pending_notifications:
            notification = self.pending_notifications[notification_id]
            return self.send_notification(notification, force)
        else:
            print(f"❌ No pending notification found with ID: {notification_id}")
            return False
    
    def cancel_notification(self, notification_id: str):
        """Cancel a pending notification."""
        if notification_id in self.pending_notifications:
            notification = self.pending_notifications.pop(notification_id)
            self._save_state()
            print(f"🚫 Cancelled notification: {notification.title}")
            return True
        return False
    
    def get_pending_notifications(self, plugin: Optional[str] = None) -> Dict[str, NotificationRequest]:
        """Get all pending notifications, optionally filtered by plugin."""
        if plugin:
            return {
                notif_id: notif for notif_id, notif in self.pending_notifications.items()
                if notif.plugin == plugin
            }
        return self.pending_notifications.copy()
    
    def cleanup_old_notifications(self, max_age_days: int = 7):
        """Clean up old sent notification IDs to prevent memory bloat."""
        cutoff_time = time.time() - (max_age_days * 24 * 60 * 60)
        
        # For sent notifications, we only have IDs, so we'll clean them periodically
        # This is a simple approach - in production you might want more sophisticated cleanup
        old_count = len(self.sent_notifications)
        
        # Clean up old pending notifications that were never sent
        old_pending = []
        for notif_id, notif in self.pending_notifications.items():
            if notif.created_at < cutoff_time:
                old_pending.append(notif_id)
        
        for notif_id in old_pending:
            self.pending_notifications.pop(notif_id, None)
        
        if old_pending:
            self._save_state()
            print(f"🧹 Cleaned up {len(old_pending)} old pending notifications")
    
    def get_status(self) -> str:
        """Get notification system status."""
        status = []
        status.append("🔔 Notification System Status")
        status.append(f"Sent notifications: {len(self.sent_notifications)}")
        status.append(f"Pending notifications: {len(self.pending_notifications)}")
        status.append(f"Default chat ID: {self.default_chat_id}")
        
        if self.pending_notifications:
            status.append(f"\n📋 Pending Notifications:")
            for notif_id, notif in list(self.pending_notifications.items())[:5]:  # Show first 5
                age_hours = (time.time() - notif.created_at) / 3600
                status.append(f"  • {notif.plugin}: {notif.title} ({age_hours:.1f}h ago)")
        
        return "\n".join(status)


# Global notification manager instance
_notification_manager = None

def get_notification_manager() -> Optional[NotificationManager]:
    """Get the global notification manager instance."""
    global _notification_manager
    return _notification_manager

def initialize_notification_manager(bot_instance, default_chat_id: Optional[int] = None) -> NotificationManager:
    """Initialize the global notification manager."""
    global _notification_manager
    _notification_manager = NotificationManager(bot_instance, default_chat_id)
    return _notification_manager

def send_notification(plugin: str, notification_type: str, title: str, message: str, 
                     item_id: str = None, chat_id: int = None, metadata: Dict = None) -> bool:
    """Convenience function to send a notification immediately."""
    manager = get_notification_manager()
    if not manager:
        print("❌ Notification manager not initialized")
        return False
    
    # Generate notification ID if not provided
    if not item_id:
        item_id = f"{plugin}_{notification_type}_{int(time.time())}"
    
    notification = NotificationRequest(
        notification_id=item_id,
        plugin=plugin,
        type=notification_type,
        title=title,
        message=message,
        chat_id=chat_id,
        metadata=metadata or {}
    )
    
    return manager.send_notification(notification)

def register_notification(plugin: str, notification_type: str, title: str, message: str,
                         item_id: str, chat_id: int = None, metadata: Dict = None):
    """Convenience function to register a notification for later sending."""
    manager = get_notification_manager()
    if not manager:
        print("❌ Notification manager not initialized")
        return False
    
    notification = NotificationRequest(
        notification_id=item_id,
        plugin=plugin,
        type=notification_type,
        title=title,
        message=message,
        chat_id=chat_id,
        metadata=metadata or {}
    )
    
    manager.register_notification(notification)
    return True
