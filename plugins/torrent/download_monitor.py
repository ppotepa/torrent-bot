#!/usr/bin/env python3
"""
Torrent download monitor - Basic stub implementation
"""

import logging

logger = logging.getLogger("download_monitor")

class DownloadMonitor:
    """Basic download monitor"""
    
    def __init__(self):
        self.running = False
        self.notification_callback = None
        logger.info("Download monitor initialized")
    
    def start(self, notification_callback=None):
        """Start monitoring"""
        self.running = True
        self.notification_callback = notification_callback
        logger.info("Download monitor started")
    
    def stop(self):
        """Stop monitoring"""
        self.running = False
        self.notification_callback = None
        logger.info("Download monitor stopped")

# Global monitor instance
_monitor = DownloadMonitor()

def start_download_monitoring(notification_callback=None):
    """Start download monitoring"""
    _monitor.start(notification_callback)

def stop_download_monitoring():
    """Stop download monitoring"""
    _monitor.stop()

def get_download_monitor():
    """Get download monitor instance"""
    return _monitor
