"""
Utility functions for torrent operations.
Handles formatting, parsing, and data manipulation.
"""

import re
from urllib.parse import urlparse, parse_qs


def human_size(num_bytes):
    """Convert bytes to human readable format."""
    if not num_bytes or num_bytes <= 0:
        return "0 B"
    units = ["B", "KB", "MB", "GB", "TB"]
    size = float(num_bytes)
    i = 0
    while size >= 1024 and i < len(units) - 1:
        size /= 1024.0
        i += 1
    return f"{size:.2f} {units[i]}"


def human_speed(bps):
    """Convert bytes per second to human readable format."""
    if bps is None:
        return "0 B/s"
    units = ["B/s", "KB/s", "MB/s", "GB/s"]
    s = float(max(0, bps))
    i = 0
    while s >= 1024 and i < len(units) - 1:
        s /= 1024.0
        i += 1
    return f"{s:.2f} {units[i]}"


def format_eta(seconds):
    """Format ETA seconds into human readable time."""
    try:
        s = int(seconds)
        if s < 0 or s >= 10**8:
            return "unknown"
        h, rem = divmod(s, 3600)
        m, s = divmod(rem, 60)
        if h:
            return f"{h}h {m}m"
        if m:
            return f"{m}m {s}s"
        return f"{s}s"
    except Exception:
        return "unknown"


def extract_infohash_from_magnet(url_or_magnet: str):
    """Extract info hash from a magnet link."""
    try:
        if not url_or_magnet or not url_or_magnet.startswith("magnet:?"):
            return None
        q = parse_qs(urlparse(url_or_magnet).query)
        xts = q.get("xt", [])
        for xt in xts:
            if xt.lower().startswith("urn:btih:"):
                return xt.split(":")[-1]
        return None
    except Exception:
        return None


def get_seeders_count(result):
    """
    Extract and normalize seeders count from a torrent result.
    Some indexers return strings, some return integers, some use different field names.
    """
    # Try different possible field names for seeders
    possible_fields = ["Seeders", "seeders", "Seeds", "seeds", "seed_count", "SeedCount"]
    
    for field in possible_fields:
        value = result.get(field)
        if value is not None:
            try:
                # Convert to integer, handle string numbers
                if isinstance(value, str):
                    # Remove any non-numeric characters except minus
                    clean_value = re.sub(r'[^\d-]', '', value)
                    if clean_value:
                        return max(0, int(clean_value))  # Ensure non-negative
                elif isinstance(value, (int, float)):
                    return max(0, int(value))  # Ensure non-negative
            except (ValueError, TypeError):
                continue
    
    # Fallback: return 0 if no valid seeders found
    return 0


def sort_results_by_seeders(results):
    """
    Sort torrent results by seeders count in descending order.
    Uses robust seeder extraction to handle different indexer formats.
    """
    def sort_key(result):
        seeders = get_seeders_count(result)
        # Secondary sort by title to ensure consistent ordering for same seeder counts
        title = result.get("Title", "").lower()
        return (seeders, title)
    
    sorted_results = sorted(results, key=sort_key, reverse=True)
    
    # Debug logging for seeder extraction
    if sorted_results and len(sorted_results) > 1:
        print(f"🔍 Sorted {len(sorted_results)} results by seeders:")
        for i, result in enumerate(sorted_results[:5]):  # Show top 5
            title = result.get("Title", "Unknown")[:50]
            seeders = get_seeders_count(result)
            print(f"  {i+1}. {seeders} seeders - {title}")
    
    return sorted_results


def deduplicate_results(results):
    """
    Deduplicate by MagnetUri if present, else by (Title, Size).
    Keeps the first (usually highest seeders due to sorted merge).
    """
    seen = set()
    out = []
    for r in results:
        key = r.get("MagnetUri") or (r.get("Title"), r.get("Size"))
        if key in seen:
            continue
        seen.add(key)
        out.append(r)
    return out
