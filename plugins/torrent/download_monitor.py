"""
Download completion monitor for qBittorrent.
Monitors for completed downloads and sends notifications via Telegram.
"""

import asyncio
import json
import os
import time
import threading
from datetime import datetime
from typing import Dict, Set, Optional, Callable

try:
    import qbittorrentapi
except ImportError as e:
    print(f"Warning: Missing dependency: {e}")
    class qbittorrentapi:
        class Client: pass

from .config import config


class DownloadMonitor:
    """Monitors qBittorrent for download completions and sends notifications."""
    
    def __init__(self, notification_callback: Optional[Callable] = None):
        self.host = config.QBIT_HOST
        self.port = config.QBIT_PORT
        self.username = config.QBIT_USER
        self.password = config.QBIT_PASS
        self._client = None
        
        # Notification callback (function to send Telegram messages)
        self.notification_callback = notification_callback
        
        # Track download states
        self.known_torrents: Dict[str, Dict] = {}  # hash -> torrent info
        self.completed_torrents: Set[str] = set()  # hashes of already notified torrents
        
        # Monitor settings
        self.check_interval = int(os.getenv("DOWNLOAD_MONITOR_INTERVAL", "30"))  # seconds
        self.running = False
        self.monitor_thread = None
        
        # State file for persistence
        self.state_file = os.path.join(config.BOT_DOWNLOADS_DIR, "download_monitor_state.json")
        self._load_state()
    
    def get_client(self):
        """Get authenticated qBittorrent client."""
        if self._client is None:
            self._client = qbittorrentapi.Client(
                host=self.host, 
                port=self.port, 
                username=self.username, 
                password=self.password
            )
            self._client.auth_log_in()
        return self._client
    
    def _load_state(self):
        """Load previous state from file to avoid duplicate notifications."""
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, 'r') as f:
                    data = json.load(f)
                    self.completed_torrents = set(data.get('completed_torrents', []))
                    print(f"📋 Loaded {len(self.completed_torrents)} completed torrents from state")
        except Exception as e:
            print(f"⚠️ Could not load monitor state: {e}")
    
    def _save_state(self):
        """Save current state to file."""
        try:
            os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
            with open(self.state_file, 'w') as f:
                json.dump({
                    'completed_torrents': list(self.completed_torrents),
                    'last_updated': datetime.now().isoformat()
                }, f, indent=2)
        except Exception as e:
            print(f"⚠️ Could not save monitor state: {e}")
    
    def format_notification_message(self, torrent_info: Dict) -> str:
        """Format a nice notification message for completed download."""
        name = torrent_info.get('name', 'Unknown')
        size = torrent_info.get('size', 0)
        completed_on = torrent_info.get('completed_on', 0)
        category = torrent_info.get('category', '')
        save_path = torrent_info.get('save_path', '')
        
        # Format size nicely
        def format_size(bytes_size):
            for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
                if bytes_size < 1024.0:
                    return f"{bytes_size:.1f} {unit}"
                bytes_size /= 1024.0
            return f"{bytes_size:.1f} PB"
        
        # Format completion time
        if completed_on > 0:
            completed_time = datetime.fromtimestamp(completed_on).strftime("%H:%M:%S")
        else:
            completed_time = "now"
        
        message = f"✅ **Download Completed!**\n\n"
        message += f"📁 **{name}**\n"
        message += f"💾 Size: {format_size(size)}\n"
        message += f"⏰ Completed: {completed_time}\n"
        
        if category:
            message += f"🏷️ Category: {category}\n"
        
        if save_path:
            # Clean up path for display
            display_path = save_path.replace('/', ' / ').replace('\\', ' \\ ')
            message += f"📂 Location: {display_path}\n"
        
        message += f"\n🎉 Ready to enjoy!"
        
        return message
    
    def check_for_completions(self):
        """Check qBittorrent for newly completed downloads."""
        try:
            client = self.get_client()
            torrents = client.torrents.info()
            
            newly_completed = []
            
            for torrent in torrents:
                torrent_hash = torrent.hash
                torrent_state = torrent.state
                
                # Track this torrent
                self.known_torrents[torrent_hash] = {
                    'name': torrent.name,
                    'state': torrent_state,
                    'progress': torrent.progress,
                    'size': torrent.size,
                    'completed_on': getattr(torrent, 'completed_on', 0),
                    'category': getattr(torrent, 'category', ''),
                    'save_path': getattr(torrent, 'save_path', ''),
                    'added_on': getattr(torrent, 'added_on', 0)
                }
                
                # Check if this is a newly completed download
                if (torrent_state in ['completedUP', 'completedDL', 'uploading', 'queuedUP', 'stalledUP'] and 
                    torrent.progress >= 1.0 and 
                    torrent_hash not in self.completed_torrents):
                    
                    newly_completed.append(self.known_torrents[torrent_hash])
                    self.completed_torrents.add(torrent_hash)
                    
                    print(f"✅ New completion detected: {torrent.name}")
            
            # Send notifications for newly completed downloads
            for torrent_info in newly_completed:
                self._send_notification(torrent_info)
            
            # Save state if we had new completions
            if newly_completed:
                self._save_state()
                
        except Exception as e:
            print(f"❌ Error checking download completions: {e}")
    
    def _send_notification(self, torrent_info: Dict):
        """Send notification for a completed download."""
        try:
            if self.notification_callback:
                message = self.format_notification_message(torrent_info)
                self.notification_callback(message)
                print(f"📨 Sent completion notification for: {torrent_info['name']}")
            else:
                print(f"📋 Would notify: {torrent_info['name']} completed")
        except Exception as e:
            print(f"❌ Error sending notification: {e}")
    
    def start_monitoring(self):
        """Start the download monitor in a background thread."""
        if self.running:
            print("⚠️ Download monitor is already running")
            return
        
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        print(f"🔍 Download monitor started (checking every {self.check_interval}s)")
    
    def stop_monitoring(self):
        """Stop the download monitor."""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        print("🛑 Download monitor stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop that runs in background thread."""
        print(f"🔄 Download monitor loop started")
        
        while self.running:
            try:
                self.check_for_completions()
                
                # Sleep for the specified interval
                for _ in range(self.check_interval):
                    if not self.running:
                        break
                    time.sleep(1)
                    
            except Exception as e:
                print(f"❌ Error in monitor loop: {e}")
                # Sleep a bit before retrying
                time.sleep(10)
        
        print("🔄 Download monitor loop ended")
    
    def get_monitor_status(self) -> str:
        """Get current monitor status for diagnostics."""
        status = []
        status.append(f"🔍 Download Monitor Status")
        status.append(f"Running: {'✅ Yes' if self.running else '❌ No'}")
        status.append(f"Check interval: {self.check_interval}s")
        status.append(f"Known torrents: {len(self.known_torrents)}")
        status.append(f"Completed notifications sent: {len(self.completed_torrents)}")
        
        if self.known_torrents:
            status.append(f"\n📊 Current Downloads:")
            for hash_id, info in list(self.known_torrents.items())[-5:]:  # Show last 5
                progress = info.get('progress', 0) * 100
                state = info.get('state', 'unknown')
                name = info.get('name', 'Unknown')[:50]
                status.append(f"  • {name}... ({progress:.1f}% - {state})")
        
        return "\n".join(status)
    
    def force_check(self) -> str:
        """Force an immediate check for completions (for testing)."""
        print("🔍 Forcing download completion check...")
        self.check_for_completions()
        return f"✅ Forced check completed. Monitoring {len(self.known_torrents)} torrents."


# Global monitor instance
_download_monitor = None

def get_download_monitor() -> DownloadMonitor:
    """Get the global download monitor instance."""
    global _download_monitor
    if _download_monitor is None:
        _download_monitor = DownloadMonitor()
    return _download_monitor

def start_download_monitoring(notification_callback: Callable):
    """Start download monitoring with notification callback."""
    monitor = get_download_monitor()
    monitor.notification_callback = notification_callback
    monitor.start_monitoring()
    return monitor

def stop_download_monitoring():
    """Stop download monitoring."""
    global _download_monitor
    if _download_monitor:
        _download_monitor.stop_monitoring()
