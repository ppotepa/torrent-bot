#!/usr/bin/env python3
"""
Torrent Notification Handler - Basic implementation
"""

import logging

logger = logging.getLogger("torrent_notification")

class TorrentNotificationManager:
    """Basic torrent notification manager"""
    
    def __init__(self, notification_manager):
        self.notification_manager = notification_manager
        self.monitoring = False
        logger.info("Torrent notification manager initialized")
    
    def start_monitoring(self):
        """Start monitoring for torrent events"""
        self.monitoring = True
        logger.info("Torrent monitoring started")
    
    def stop_monitoring(self):
        """Stop monitoring for torrent events"""
        self.monitoring = False
        logger.info("Torrent monitoring stopped")
    
    def notify_download_complete(self, torrent_name, chat_id=None):
        """Notify when download completes"""
        message = f"🎬 Download complete: {torrent_name}"
        if self.notification_manager:
            self.notification_manager.send_notification(message, chat_id)
    
    def notify_download_started(self, torrent_name, chat_id=None):
        """Notify when download starts"""
        message = f"⬇️ Download started: {torrent_name}"
        if self.notification_manager:
            self.notification_manager.send_notification(message, chat_id)

# Global instance
_torrent_notification_manager = None

def initialize_torrent_notification_manager(notification_manager):
    """Initialize torrent notification manager"""
    global _torrent_notification_manager
    _torrent_notification_manager = TorrentNotificationManager(notification_manager)
    return _torrent_notification_manager

def get_torrent_notification_manager():
    """Get torrent notification manager"""
    return _torrent_notification_manager