"""
Fallback mechanisms for torrent downloads.
Handles alternative download methods when primary methods fail.
"""

from .config import config
from .utils import extract_infohash_from_magnet


class FallbackManager:
    """Manages fallback download methods when primary download fails."""
    
    def __init__(self, qbt_client, jackett_client):
        self.qbt_client = qbt_client
        self.jackett_client = jackett_client
    
    def try_alternative_download_methods(self, chosen_result: dict, save_path: str) -> tuple[bool, str]:
        """
        Try alternative methods to download a torrent when magnet link fails.
        Returns (success: bool, message: str)
        """
        title = chosen_result.get("Title", "Unknown Title")
        
        # Method 1: Try torrent file download
        link = chosen_result.get("Link")
        if link:
            torrent_bytes, error = self.qbt_client.download_torrent_file(link, retries=config.MAX_FALLBACK_ATTEMPTS)
            if torrent_bytes:
                if self.qbt_client.add_torrent_file(torrent_bytes, save_path):
                    return True, "✅ Downloaded via .torrent file"
            
            if error:
                print(f"⚠️ Torrent file download failed: {error}")
        
        # Method 2: Try to construct magnet from available info
        info_hash = chosen_result.get("InfoHash")
        if info_hash:
            if self._try_reconstructed_magnet(info_hash, title, chosen_result, save_path):
                return True, "✅ Downloaded via reconstructed magnet link"
        
        # Method 3: Search for alternative sources (only if aggressive fallback is enabled)
        if config.ENABLE_AGGRESSIVE_FALLBACK:
            if self._try_alternative_sources(title, chosen_result, save_path):
                return True, "✅ Found alternative source"
        
        failure_msg = "❌ All download methods failed - no magnet link, torrent file download failed"
        if config.ENABLE_AGGRESSIVE_FALLBACK:
            failure_msg += ", and no alternative sources found"
        else:
            failure_msg += " (set ENABLE_AGGRESSIVE_FALLBACK=true for more alternatives)"
        
        return False, failure_msg
    
    def _try_reconstructed_magnet(self, info_hash: str, title: str, chosen_result: dict, save_path: str) -> bool:
        """Try to construct and use a magnet link from available info."""
        try:
            # Construct basic magnet link with just the info hash
            magnet = f"magnet:?xt=urn:btih:{info_hash}"
            
            # Add display name if available
            if title and title != "Unknown Title":
                magnet += f"&dn={title.replace(' ', '%20')}"
            
            # Add trackers if available
            tracker = chosen_result.get("Tracker")
            if tracker:
                # Add some common public trackers as fallback
                common_trackers = [
                    "udp://tracker.openbittorrent.com:80/announce",
                    "udp://tracker.opentrackr.org:1337/announce",
                    "udp://9.rarbg.to:2710/announce",
                    "udp://exodus.desync.com:6969/announce"
                ]
                for tr in common_trackers:
                    magnet += f"&tr={tr.replace(':', '%3A').replace('/', '%2F')}"
            
            return self.qbt_client.add_torrent_magnet(magnet, save_path)
            
        except Exception as e:
            print(f"⚠️ Reconstructed magnet failed: {str(e)}")
            return False
    
    def _try_alternative_sources(self, title: str, chosen_result: dict, save_path: str) -> bool:
        """Search for alternative sources for the same torrent."""
        try:
            # Try to find the same torrent from other indexers
            alt_results, _ = self.jackett_client.search_extended(title, limit=10)
            
            for alt_result in alt_results:
                # Skip if it's the same result
                if alt_result.get("Link") == chosen_result.get("Link"):
                    continue
                    
                # Try alternative magnet
                alt_magnet = alt_result.get("MagnetUri")
                if alt_magnet:
                    if self.qbt_client.add_torrent_magnet(alt_magnet, save_path):
                        print(f"✅ Found alternative magnet from {alt_result.get('Tracker', 'unknown tracker')}")
                        return True
                
                # Try alternative torrent file
                alt_link = alt_result.get("Link")
                if alt_link:
                    alt_torrent_bytes, alt_error = self.qbt_client.download_torrent_file(alt_link, retries=2)
                    if alt_torrent_bytes:
                        if self.qbt_client.add_torrent_file(alt_torrent_bytes, save_path):
                            print(f"✅ Found alternative .torrent file from {alt_result.get('Tracker', 'unknown tracker')}")
                            return True
        
        except Exception as e:
            print(f"⚠️ Alternative sources search failed: {str(e)}")
        
        return False
