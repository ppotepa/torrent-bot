"""Utility functions and helpers."""

import re
import hashlib
from typing import Optional, Tuple
from urllib.parse import parse_qs, urlparse


def format_size(size_bytes: int) -> str:
    """Format size in bytes to human readable format."""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"


def format_speed(speed_bytes_per_sec: int) -> str:
    """Format speed in bytes per second to human readable format."""
    return f"{format_size(speed_bytes_per_sec)}/s"


def format_eta(eta_seconds: int) -> str:
    """Format ETA in seconds to human readable format."""
    if eta_seconds <= 0 or eta_seconds == 8640000:  # qBittorrent uses 8640000 for unknown
        return "Unknown"
    
    if eta_seconds < 60:
        return f"{eta_seconds}s"
    elif eta_seconds < 3600:
        minutes = eta_seconds // 60
        return f"{minutes}m"
    elif eta_seconds < 86400:
        hours = eta_seconds // 3600
        minutes = (eta_seconds % 3600) // 60
        return f"{hours}h {minutes}m"
    else:
        days = eta_seconds // 86400
        hours = (eta_seconds % 86400) // 3600
        return f"{days}d {hours}h"


def extract_magnet_info(magnet_link: str) -> Tuple[Optional[str], Optional[str]]:
    """Extract info hash and display name from magnet link."""
    if not magnet_link.startswith("magnet:"):
        return None, None
    
    # Parse the magnet URL
    parsed = urlparse(magnet_link)
    params = parse_qs(parsed.query)
    
    # Extract info hash
    info_hash = None
    if "xt" in params:
        for xt in params["xt"]:
            if xt.startswith("urn:btih:"):
                info_hash = xt.split(":")[-1]
                break
    
    # Extract display name
    display_name = None
    if "dn" in params and params["dn"]:
        display_name = params["dn"][0]
    
    return info_hash, display_name


def validate_magnet_link(magnet_link: str) -> bool:
    """Validate if a string is a valid magnet link."""
    if not isinstance(magnet_link, str):
        return False
    
    if not magnet_link.startswith("magnet:"):
        return False
    
    # Check if it contains at least an info hash
    info_hash, _ = extract_magnet_info(magnet_link)
    return info_hash is not None


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for filesystem compatibility."""
    # Replace invalid characters
    invalid_chars = r'[<>:"/\\|?*]'
    sanitized = re.sub(invalid_chars, "_", filename)
    
    # Remove leading/trailing spaces and dots
    sanitized = sanitized.strip(". ")
    
    # Limit length
    if len(sanitized) > 250:
        sanitized = sanitized[:250]
    
    return sanitized


def create_progress_bar(progress: float, length: int = 10, filled_char: str = "█", empty_char: str = "░") -> str:
    """Create a text-based progress bar."""
    if progress < 0:
        progress = 0
    elif progress > 100:
        progress = 100
    
    filled_length = int(progress / 100 * length)
    bar = filled_char * filled_length + empty_char * (length - filled_length)
    return f"[{bar}]"


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate text to specified length with optional suffix."""
    if len(text) <= max_length:
        return text
    
    if len(suffix) >= max_length:
        return text[:max_length]
    
    return text[:max_length - len(suffix)] + suffix


def parse_category(category_input: str) -> str:
    """Parse and normalize category input."""
    if not category_input:
        return ""
    
    category = category_input.lower().strip()
    
    # Category aliases
    aliases = {
        "movie": "movies",
        "film": "movies",
        "tv": "tv",
        "series": "tv",
        "show": "tv",
        "television": "tv",
        "music": "music",
        "audio": "music",
        "song": "music",
        "album": "music",
        "game": "games",
        "gaming": "games",
        "software": "software",
        "app": "software",
        "application": "software",
        "book": "books",
        "ebook": "books",
        "anime": "anime",
        "manga": "anime"
    }
    
    return aliases.get(category, category)


def generate_short_hash(text: str, length: int = 8) -> str:
    """Generate a short hash from text."""
    hash_object = hashlib.md5(text.encode())
    return hash_object.hexdigest()[:length]


class RateLimiter:
    """Simple rate limiter implementation."""
    
    def __init__(self, max_calls: int, time_window: int):
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = []
    
    def is_allowed(self) -> bool:
        """Check if a call is allowed based on rate limits."""
        import time
        current_time = time.time()
        
        # Remove calls outside the time window
        self.calls = [call_time for call_time in self.calls if current_time - call_time < self.time_window]
        
        # Check if we're under the limit
        if len(self.calls) < self.max_calls:
            self.calls.append(current_time)
            return True
        
        return False
    
    def time_until_next_call(self) -> float:
        """Get time in seconds until the next call is allowed."""
        if not self.calls:
            return 0
        
        import time
        current_time = time.time()
        oldest_call = min(self.calls)
        return max(0, self.time_window - (current_time - oldest_call))
