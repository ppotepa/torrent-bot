"""
qBittorrent client for torrent management.
Handles adding torrents and status updates.
"""

import os
import time
try:
    import qbittorrentapi
    import requests
except ImportError as e:
    print(f"Warning: Missing dependency: {e}")
    # Placeholder for development
    class qbittorrentapi:
        class Client: pass
        class LoginFailed(Exception): pass
        class APIConnectionError(Exception): pass
        class Forbidden403Error(Exception): pass
        class TorrentFileError(Exception): pass
        class UnsupportedMediaType415Error(Exception): pass

from .config import config
from .utils import extract_infohash_from_magnet


class QBittorrentClient:
    """Client for interacting with qBittorrent."""
    
    def __init__(self):
        self.host = config.QBIT_HOST
        self.port = config.QBIT_PORT
        self.username = config.QBIT_USER
        self.password = config.QBIT_PASS
        self.save_root = config.QBIT_SAVE_ROOT
        self.downloads_dir = config.BOT_DOWNLOADS_DIR
        self._client = None
    
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
    
    def add_torrent_magnet(self, magnet_url: str, save_path: str) -> bool:
        """Add torrent via magnet link."""
        try:
            client = self.get_client()
            client.torrents_add(urls=magnet_url, save_path=save_path)
            return True
        except Exception as e:
            print(f"⚠️ Magnet link failed: {str(e)}")
            return False
    
    def add_torrent_file(self, torrent_bytes: bytes, save_path: str) -> bool:
        """Add torrent via .torrent file."""
        try:
            client = self.get_client()
            client.torrents_add(torrent_files={"file.torrent": torrent_bytes}, save_path=save_path)
            return True
        except Exception as e:
            print(f"⚠️ Torrent file failed: {str(e)}")
            return False
    
    def download_torrent_file(self, link_url: str, retries: int = 3) -> tuple[bytes | None, str | None]:
        """
        Download the .torrent file CONTENT via Jackett link with retries.
        Returns (bytes_or_None, error_message_or_None).
        """
        if not link_url:
            return None, "No link URL provided"
        
        last_error = None
        for attempt in range(retries):
            try:
                resp = requests.get(link_url, timeout=(config.CONNECT_TIMEOUT, 30))
                if resp.ok and resp.content:
                    ctype = resp.headers.get("Content-Type", "").lower()
                    if "torrent" in ctype or resp.content.startswith(b"d8:announce"):
                        return resp.content, None
                    # some trackers send application/octet-stream
                    if "octet-stream" in ctype:
                        return resp.content, None
                last_error = f"Invalid response: status={resp.status_code}, content-type={resp.headers.get('Content-Type', 'unknown')}"
            except requests.exceptions.Timeout:
                last_error = f"Timeout after 30s (attempt {attempt + 1}/{retries})"
            except requests.exceptions.ConnectionError:
                last_error = f"Connection error (attempt {attempt + 1}/{retries})"
            except Exception as e:
                last_error = f"Unexpected error: {str(e)} (attempt {attempt + 1}/{retries})"
            
            if attempt < retries - 1:
                time.sleep(1)  # Brief delay before retry
        
        return None, last_error
    
    def find_started_torrent(self, infohash, title_hint):
        """
        Try to find the torrent we just added, preferring infohash, else newest by added_on,
        else name contains title_hint.
        """
        try:
            client = self.get_client()
            if infohash:
                ts = client.torrents_info(hashes=infohash)
                if ts:
                    return ts[0]
            ts = client.torrents_info()
            if not ts:
                return None
            if title_hint:
                candidates = [t for t in ts if title_hint.lower() in (t.name or "").lower()]
                if candidates:
                    return max(candidates, key=lambda t: getattr(t, "added_on", 0) or 0)
            return max(ts, key=lambda t: getattr(t, "added_on", 0) or 0)
        except Exception as e:
            print(f"❌ Error finding torrent: {e}")
            return None
    
    def get_all_torrents(self):
        """Get all torrents as dictionaries for monitoring."""
        try:
            client = self.get_client()
            torrents = client.torrents_info()
            
            # Convert torrent objects to dictionaries
            result = []
            for torrent in torrents:
                result.append({
                    'hash': getattr(torrent, 'hash', ''),
                    'name': getattr(torrent, 'name', ''),
                    'state': getattr(torrent, 'state', ''),
                    'progress': getattr(torrent, 'progress', 0),
                    'size': getattr(torrent, 'size', 0),
                    'downloaded': getattr(torrent, 'downloaded', 0),
                    'save_path': getattr(torrent, 'save_path', ''),
                    'added_on': getattr(torrent, 'added_on', 0),
                    'completion_on': getattr(torrent, 'completion_on', 0),
                })
            
            return result
        except Exception as e:
            print(f"❌ Error getting torrents: {e}")
            return []
        except Exception:
            return None
    
    def update_downloads_txt(self):
        """Dump current torrents into downloads.txt in the bot's mounted folder."""
        try:
            self._ensure_dir(self.downloads_dir)
            out_path = os.path.join(self.downloads_dir, "downloads.txt")
            client = self.get_client()
            
            with open(out_path, "w", encoding="utf-8") as f:
                for tor in client.torrents_info():
                    line = f"{tor.name} | {tor.state} | {tor.progress*100:.1f}%\n"
                    f.write(line)
        except Exception as e:
            print(f"⚠️ Failed to update downloads.txt: {e}")
    
    def _ensure_dir(self, path: str):
        """Ensure directory exists."""
        try:
            os.makedirs(path, exist_ok=True)
        except Exception:
            pass
    
    def diagnose_connection(self):
        """
        Comprehensive qBittorrent connection and configuration diagnostics.
        Returns detailed report about qBittorrent status and potential issues.
        """
        report = []
        report.append("🔍 qBittorrent Diagnostics Report")
        report.append("=" * 50)
        
        try:
            # Test basic connection
            report.append(f"📡 Connection Test:")
            report.append(f"   Host: {self.host}:{self.port}")
            report.append(f"   Username: {self.username}")
            report.append(f"   Password: {'***' + self.password[-2:] if len(self.password) > 2 else 'SET'}")
            
            # Test HTTP connectivity first
            import requests
            url = f"http://{self.host}:{self.port}"
            try:
                response = requests.get(url, timeout=5)
                report.append(f"✅ HTTP connectivity: {response.status_code}")
            except Exception as e:
                report.append(f"❌ HTTP connectivity failed: {str(e)}")
                report.append("💡 Check if qBittorrent container is running")
                report.append("💡 Verify port mapping in docker-compose.yaml")
                return "\n".join(report)
            
            # Test qBittorrent API authentication
            try:
                client = self.get_client()
                report.append("✅ qBittorrent API authentication successful")
            except qbittorrentapi.LoginFailed:
                report.append("❌ qBittorrent login failed")
                report.append("💡 Check QBIT_USER and QBIT_PASS environment variables")
                report.append("💡 Verify qBittorrent WebUI credentials")
                return "\n".join(report)
            except Exception as e:
                report.append(f"❌ qBittorrent API error: {str(e)}")
                return "\n".join(report)
            
            # Get qBittorrent application info
            try:
                app_info = client.app.version_info
                report.append(f"\n📋 qBittorrent Information:")
                report.append(f"   Version: {app_info}")
                
                preferences = client.app.preferences
                report.append(f"   Web UI Port: {preferences.get('web_ui_port', 'Unknown')}")
                report.append(f"   Max Connections: {preferences.get('max_connec', 'Unknown')}")
                report.append(f"   Max Uploads: {preferences.get('max_uploads', 'Unknown')}")
                
            except Exception as e:
                report.append(f"⚠️ Could not get qBittorrent info: {str(e)}")
            
            # Check current torrents and their status
            try:
                torrents = client.torrents.info()
                report.append(f"\n📊 Current Torrents: {len(torrents)}")
                
                if torrents:
                    # Analyze torrent states
                    states = {}
                    for torrent in torrents:
                        state = torrent.state
                        states[state] = states.get(state, 0) + 1
                    
                    report.append("   States breakdown:")
                    for state, count in states.items():
                        report.append(f"     {state}: {count}")
                    
                    # Check for problematic torrents
                    stalled = [t for t in torrents if t.state in ['stalledDL', 'stalledUP']]
                    errored = [t for t in torrents if 'error' in t.state.lower()]
                    
                    if stalled:
                        report.append(f"\n⚠️ Stalled torrents: {len(stalled)}")
                        for torrent in stalled[:3]:  # Show first 3
                            report.append(f"     • {torrent.name[:50]}... ({torrent.state})")
                    
                    if errored:
                        report.append(f"\n❌ Errored torrents: {len(errored)}")
                        for torrent in errored[:3]:  # Show first 3
                            report.append(f"     • {torrent.name[:50]}... ({torrent.state})")
                
            except Exception as e:
                report.append(f"⚠️ Could not get torrent info: {str(e)}")
            
            # Check network connectivity and tracker access
            try:
                preferences = client.app.preferences
                
                report.append(f"\n🌐 Network Configuration:")
                report.append(f"   Listen Port: {preferences.get('listen_port', 'Unknown')}")
                report.append(f"   UPnP Enabled: {preferences.get('upnp', 'Unknown')}")
                report.append(f"   DHT Enabled: {preferences.get('dht', 'Unknown')}")
                report.append(f"   PeX Enabled: {preferences.get('pex', 'Unknown')}")
                report.append(f"   LSD Enabled: {preferences.get('lsd', 'Unknown')}")
                
                # Check if port is properly forwarded/accessible
                listen_port = preferences.get('listen_port')
                if listen_port:
                    report.append(f"\n🔌 Port Status:")
                    report.append(f"   Listening on: {listen_port}")
                    report.append("💡 Make sure this port is exposed in Docker and firewall")
                
            except Exception as e:
                report.append(f"⚠️ Could not get network config: {str(e)}")
            
            # Test with a small test magnet to check downloading capability
            report.append(f"\n🧪 Download Test:")
            report.append("   Testing with Ubuntu torrent...")
            
            # Ubuntu 22.04 LTS Desktop magnet (small, well-seeded)
            test_magnet = "magnet:?xt=urn:btih:8b2b1b5a8b3b3f4e4f5a4d3c2b1a0f9e8d7c6b5a&dn=ubuntu-22.04.3-desktop-amd64.iso"
            
            try:
                # Try to add test torrent in paused state
                result = client.torrents.add(
                    urls=test_magnet,
                    is_paused=True,  # Add paused so it doesn't actually download
                    category="bot-test"
                )
                
                # Check if it was added
                time.sleep(2)
                test_torrents = client.torrents.info(category="bot-test")
                
                if test_torrents:
                    test_torrent = test_torrents[0]
                    report.append(f"✅ Test torrent added successfully")
                    report.append(f"   Name: {test_torrent.name[:50]}...")
                    report.append(f"   State: {test_torrent.state}")
                    report.append(f"   Seeders: {test_torrent.num_seeds}")
                    report.append(f"   Peers: {test_torrent.num_leechs}")
                    
                    # Clean up test torrent
                    client.torrents.delete(delete_files=True, torrent_hashes=test_torrent.hash)
                    report.append("🧹 Test torrent cleaned up")
                    
                    if test_torrent.num_seeds == 0 and test_torrent.num_leechs == 0:
                        report.append("\n⚠️ No peers/seeders found for test torrent")
                        report.append("💡 This suggests connectivity issues:")
                        report.append("   • Check Docker port mapping (6881:6881)")
                        report.append("   • Verify firewall allows BitTorrent ports")
                        report.append("   • Ensure DHT/PeX/Trackers are enabled")
                        report.append("   • Check if ISP blocks BitTorrent traffic")
                
                else:
                    report.append("❌ Test torrent was not added properly")
                    
            except Exception as e:
                report.append(f"❌ Test torrent failed: {str(e)}")
                report.append("💡 This indicates qBittorrent cannot add torrents")
            
            # Docker-specific diagnostics
            report.append(f"\n🐳 Docker Environment Checks:")
            report.append("💡 Common Docker issues and solutions:")
            report.append("   1. Port Mapping:")
            report.append("      • Ensure 6881:6881 and 6881:6881/udp are mapped")
            report.append("      • Check 8080:8080 for WebUI access")
            report.append("   2. Volume Mounts:")
            report.append("      • Verify download path is properly mounted")
            report.append("      • Check permissions on mounted directories")
            report.append("   3. Network:")
            report.append("      • All containers should be on same network")
            report.append("      • Check if zerotier network allows BitTorrent")
            report.append("   4. Container Health:")
            report.append("      • Restart qBittorrent container if issues persist")
            report.append("      • Check container logs: docker logs qbittorrent")
            
            # Performance recommendations
            report.append(f"\n⚡ Performance Recommendations:")
            try:
                max_conn = preferences.get('max_connec', 0)
                max_uploads = preferences.get('max_uploads', 0)
                
                if max_conn < 100:
                    report.append(f"   • Increase max connections (current: {max_conn}, recommend: 200+)")
                if max_uploads < 10:
                    report.append(f"   • Increase max uploads (current: {max_uploads}, recommend: 20+)")
                
                report.append("   • Enable DHT, PeX, and LSD for better peer discovery")
                report.append("   • Consider using a VPN if ISP throttles BitTorrent")
            except:
                report.append("   • Could not analyze current settings")
            
        except Exception as e:
            report.append(f"❌ Diagnostics failed: {str(e)}")
            report.append("\n💡 Basic troubleshooting:")
            report.append("   • Check if qBittorrent container is running")
            report.append("   • Verify environment variables in docker-compose")
            report.append("   • Restart containers and try again")
        
        return "\n".join(report)
