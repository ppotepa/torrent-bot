import os
import time
import qbittorrentapi
import requests
from telebot import types
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse, parse_qs

# --------------------
# qBittorrent config
# --------------------
QBIT_HOST = os.getenv("QBIT_HOST", "qbittorrent")
QBIT_PORT = int(os.getenv("QBIT_PORT", "8080"))
QBIT_USER = os.getenv("QBIT_USER", "admin")
QBIT_PASS = os.getenv("QBIT_PASS", "adminadmin")

# Where qBittorrent saves inside *its* container (matches your compose volume)
QBIT_SAVE_ROOT = os.getenv("QBIT_SAVE_ROOT", "/downloads")

# Where THIS bot container sees the mounted music folder (for downloads.txt)
BOT_DOWNLOADS_DIR = os.getenv("BOT_DOWNLOADS_DIR", "/app/downloads")

# --------------------
# Jackett config
# --------------------
JACKETT_URL = os.getenv("JACKETT_URL", "http://jackett:9117").rstrip("/")
JACKETT_API_KEY = os.getenv("JACKETT_API_KEY", "")

# Popular fast indexers by default (override via env JACKETT_INDEXERS)
# Extended list to match common desktop configurations
POPULAR_INDEXERS_DEFAULT = "yts,nyaa,eztv,limetorrents,linuxtracker,1337x,thepiratebay,rarbg,torrentgalaxy,glodls"
JACKETT_INDEXERS = os.getenv("JACKETT_INDEXERS", POPULAR_INDEXERS_DEFAULT).replace(" ", "")

# Timeouts & concurrency tuned for quick responses
CONNECT_TIMEOUT = int(os.getenv("JACKETT_CONNECT_TIMEOUT", "3"))   # seconds to connect
READ_TIMEOUT = int(os.getenv("JACKETT_READ_TIMEOUT", "12"))        # seconds to read per indexer
MAX_WORKERS = int(os.getenv("JACKETT_MAX_WORKERS", "4"))           # parallel requests
RESULT_LIMIT = int(os.getenv("JACKETT_RESULT_LIMIT", "5"))         # stop when we have this many results

# Fallback settings
ENABLE_AGGRESSIVE_FALLBACK = os.getenv("ENABLE_AGGRESSIVE_FALLBACK", "true").lower() == "true"
MAX_FALLBACK_ATTEMPTS = int(os.getenv("MAX_FALLBACK_ATTEMPTS", "3"))  # Max retry attempts for failed downloads

# Rich mode settings
RICH_MODE_LIMIT = int(os.getenv("RICH_MODE_LIMIT", "15"))  # More results in rich mode
RICH_MODE_TIMEOUT = int(os.getenv("RICH_MODE_TIMEOUT", "20"))  # Longer timeout for rich searches

# All available indexers for rich mode
ALL_INDEXERS = [
    "yts", "nyaa", "eztv", "limetorrents", "linuxtracker", 
    "1337x", "rarbg", "thepiratebay", "kickasstorrents",
    "torrentgalaxy", "glodls", "magnetdl", "btdiggg", 
    "torrentproject", "zooqle", "torlock", "torrentfunk",
    "skytorrents", "solidtorrents", "torrentdownloads"
]

# Cache: user_id → {results, folder}
search_cache = {}

# Busy indicator cache: user_id → message_id
busy_indicators = {}


# --------------- helpers ---------------

def create_busy_indicator(bot, message, search_type="normal"):
    """Create and send a busy indicator message"""
    if search_type == "rich":
        busy_text = (
            "🔍 Rich search in progress...\n"
            "📡 Querying all available indexers\n"
            "⏳ This may take a moment"
        )
    else:
        busy_text = (
            "🔍 Searching torrents...\n"
            "⏳ Please wait"
        )
    
    busy_msg = bot.send_message(message.chat.id, busy_text)
    busy_indicators[message.from_user.id] = busy_msg.message_id
    return busy_msg

def update_busy_indicator(bot, message, current_indexer=None, total_indexers=None, found_results=0):
    """Update the busy indicator with progress"""
    user_id = message.from_user.id
    if user_id not in busy_indicators:
        return
    
    if current_indexer and total_indexers:
        progress_text = (
            f"🔍 Rich search in progress...\n"
            f"📡 Searching: {current_indexer}\n"
            f"📊 Progress: {len(found_results)}/{total_indexers} indexers\n"
            f"✅ Found: {found_results} torrents so far"
        )
    else:
        progress_text = (
            f"🔍 Search in progress...\n"
            f"⏳ Querying indexers...\n"
            f"✅ Found: {found_results} torrents so far"
        )
    
    try:
        bot.edit_message_text(
            progress_text,
            message.chat.id,
            busy_indicators[user_id]
        )
    except Exception:
        pass  # Ignore edit failures

def remove_busy_indicator(bot, message):
    """Remove the busy indicator"""
    user_id = message.from_user.id
    if user_id in busy_indicators:
        try:
            bot.delete_message(message.chat.id, busy_indicators[user_id])
        except Exception:
            pass  # Ignore deletion failures
        del busy_indicators[user_id]

def human_size(num_bytes):
    if not num_bytes or num_bytes <= 0:
        return "0 B"
    units = ["B", "KB", "MB", "GB", "TB"]
    size = float(num_bytes)
    i = 0
    while size >= 1024 and i < len(units) - 1:
        size /= 1024.0
        i += 1
    return f"{size:.2f} {units[i]}"

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
                    import re
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

def human_speed(bps):
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

def _fetch_indexer(indexer: str, query: str):
    """
    Query a single Jackett indexer with short timeouts.
    Returns (results_list, error_string_or_None, indexer_name)
    """
    try:
        if not JACKETT_API_KEY:
            return [], "JACKETT_API_KEY is empty", indexer

        url = f"{JACKETT_URL}/api/v2.0/indexers/{indexer}/results"
        params = {"apikey": JACKETT_API_KEY, "Query": query}
        r = requests.get(url, params=params, timeout=(CONNECT_TIMEOUT, READ_TIMEOUT))
        r.raise_for_status()
        data = r.json() if r.text else {}
        results = data.get("Results", []) or []

        # Annotate tracker name so we can display it
        for item in results:
            item["Tracker"] = item.get("Tracker") or indexer

        # Surface first indexer error if Jackett provided any
        err = None
        for idx in data.get("Indexers", []) or []:
            if idx.get("Error"):
                err = idx.get("Error")
                break
        return results, err, indexer

    except requests.exceptions.Timeout:
        return [], f"timeout after {READ_TIMEOUT}s", indexer
    except Exception as e:
        return [], str(e), indexer

def _dedupe(results):
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

def _ensure_dir(path: str):
    try:
        os.makedirs(path, exist_ok=True)
    except Exception:
        pass

def _update_downloads_txt(qbt_client):
    """Dump current torrents into downloads.txt in the bot's mounted folder."""
    try:
        _ensure_dir(BOT_DOWNLOADS_DIR)
        out_path = os.path.join(BOT_DOWNLOADS_DIR, "downloads.txt")
        with open(out_path, "w", encoding="utf-8") as f:
            for tor in qbt_client.torrents_info():
                line = f"{tor.name} | {tor.state} | {tor.progress*100:.1f}%\n"
                f.write(line)
    except Exception as e:
        print(f"⚠️ Failed to update downloads.txt: {e}")

def _download_torrent_via_jackett(link_url: str, retries: int = 3) -> tuple[bytes | None, str | None]:
    """
    Download the .torrent file CONTENT via Jackett link with retries.
    Returns (bytes_or_None, error_message_or_None).
    """
    if not link_url:
        return None, "No link URL provided"
    
    last_error = None
    for attempt in range(retries):
        try:
            # If link is not through Jackett, try to wrap it with Jackett proxy (best effort)
            # but generally the Link Jackett returns is already a /dl/... URL.
            resp = requests.get(link_url, timeout=(CONNECT_TIMEOUT, 30))
            if resp.ok and resp.content:
                ctype = resp.headers.get("Content-Type", "").lower()
                if "torrent" in ctype or resp.content.startswith(b"d8:announce"):
                    return resp.content, None
                # some trackers send application/octet-stream
                if "octet-stream" in ctype:
                    return resp.content, None
            last_error = f"Invalid response: status={resp.status_code}, content-type={resp.headers.get('Content-Type', 'unknown')}"
        except requests.exceptions.Timeout:
            last_error = f"Timeout after {30}s (attempt {attempt + 1}/{retries})"
        except requests.exceptions.ConnectionError:
            last_error = f"Connection error (attempt {attempt + 1}/{retries})"
        except Exception as e:
            last_error = f"Unexpected error: {str(e)} (attempt {attempt + 1}/{retries})"
        
        if attempt < retries - 1:
            time.sleep(1)  # Brief delay before retry
    
    return None, last_error

def _try_alternative_download_methods(chosen_result: dict, qbt_client, save_path: str) -> tuple[bool, str]:
    """
    Try alternative methods to download a torrent when magnet link fails.
    Returns (success: bool, message: str)
    """
    title = chosen_result.get("Title", "Unknown Title")
    
    # Method 1: Try torrent file download
    link = chosen_result.get("Link")
    if link:
        torrent_bytes, error = _download_torrent_via_jackett(link, retries=MAX_FALLBACK_ATTEMPTS)
        if torrent_bytes:
            try:
                qbt_client.torrents_add(torrent_files={"file.torrent": torrent_bytes}, save_path=save_path)
                return True, f"✅ Downloaded via .torrent file"
            except Exception as e:
                error = f"Failed to add torrent file to qBittorrent: {str(e)}"
        
        if error:
            print(f"⚠️ Torrent file download failed: {error}")
    
    # Method 2: Try to construct magnet from available info
    info_hash = chosen_result.get("InfoHash")
    if info_hash:
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
            
            qbt_client.torrents_add(urls=magnet, save_path=save_path)
            return True, f"✅ Downloaded via reconstructed magnet link"
            
        except Exception as e:
            print(f"⚠️ Reconstructed magnet failed: {str(e)}")
    
    # Method 3: Search for alternative sources (only if aggressive fallback is enabled)
    if ENABLE_AGGRESSIVE_FALLBACK:
        try:
            # Try to find the same torrent from other indexers
            alt_results, _ = search_jackett_extended(title, limit=10)
            for alt_result in alt_results:
                # Skip if it's the same result
                if alt_result.get("Link") == chosen_result.get("Link"):
                    continue
                    
                alt_magnet = alt_result.get("MagnetUri")
                if alt_magnet:
                    try:
                        qbt_client.torrents_add(urls=alt_magnet, save_path=save_path)
                        return True, f"✅ Found alternative source from {alt_result.get('Tracker', 'unknown tracker')}"
                    except Exception as e:
                        print(f"⚠️ Alternative magnet failed: {str(e)}")
                        continue
                
                # Try alternative torrent file
                alt_link = alt_result.get("Link")
                if alt_link:
                    alt_torrent_bytes, alt_error = _download_torrent_via_jackett(alt_link, retries=2)  # Fewer retries for alternatives
                    if alt_torrent_bytes:
                        try:
                            qbt_client.torrents_add(torrent_files={"file.torrent": alt_torrent_bytes}, save_path=save_path)
                            return True, f"✅ Found alternative .torrent file from {alt_result.get('Tracker', 'unknown tracker')}"
                        except Exception as e:
                            print(f"⚠️ Alternative torrent file failed: {str(e)}")
                            continue
        
        except Exception as e:
            print(f"⚠️ Alternative sources search failed: {str(e)}")
    
    failure_msg = "❌ All download methods failed - no magnet link, torrent file download failed"
    if ENABLE_AGGRESSIVE_FALLBACK:
        failure_msg += ", and no alternative sources found"
    else:
        failure_msg += " (set ENABLE_AGGRESSIVE_FALLBACK=true for more alternatives)"
    
    return False, failure_msg

def _find_started_torrent(qbt_client, infohash, title_hint):
    """
    Try to find the torrent we just added, preferring infohash, else newest by added_on,
    else name contains title_hint.
    """
    try:
        if infohash:
            ts = qbt_client.torrents_info(hashes=infohash)
            if ts:
                return ts[0]
        ts = qbt_client.torrents_info()
        if not ts:
            return None
        if title_hint:
            candidates = [t for t in ts if title_hint.lower() in (t.name or "").lower()]
            if candidates:
                return max(candidates, key=lambda t: getattr(t, "added_on", 0) or 0)
        return max(ts, key=lambda t: getattr(t, "added_on", 0) or 0)
    except Exception:
        return None

def search_jackett_fast(query: str, limit: int = RESULT_LIMIT):
    """
    Hit a short list of popular indexers in parallel with short timeouts.
    Stop as soon as we collect 'limit' results.
    """
    indexers = [i for i in JACKETT_INDEXERS.split(",") if i]
    if not indexers:
        raise Exception("No indexers configured (JACKETT_INDEXERS is empty)")

    merged = []
    errs = []
    workers = min(MAX_WORKERS, max(1, len(indexers)))

    with ThreadPoolExecutor(max_workers=workers) as ex:
        futures = {ex.submit(_fetch_indexer, idx, query): idx for idx in indexers}
        for f in as_completed(futures):
            results, err, idx = f.result()
            if err:
                errs.append((idx, err))
            if results:
                merged.extend(results)
                merged = sort_results_by_seeders(merged)
                merged = _dedupe(merged)
                if len(merged) >= limit:
                    for fut in futures.keys():
                        if not fut.done():
                            fut.cancel()
                    break

    return merged[:limit], errs

def search_jackett_extended(query: str, limit: int = RESULT_LIMIT * 2):
    """
    Extended search that tries more indexers if initial search yields poor results.
    This is used as a fallback when we need more/better torrent options.
    """
    # First try the fast search
    results, errs = search_jackett_fast(query, limit)
    
    # If we got good results (multiple results with decent seeders), return them
    good_results = [r for r in results if r.get("Seeders", 0) > 0]
    if len(good_results) >= 3:
        return results, errs
    
    # If results are poor, try additional indexers (if available)
    # Common additional indexers that might not be in the fast list
    additional_indexers = [
        "1337x", "rarbg", "thepiratebay", "kickasstorrents", 
        "torrentgalaxy", "glodls", "magnetdl", "btdiggg"
    ]
    
    # Filter out indexers we already tried
    current_indexers = set(JACKETT_INDEXERS.split(","))
    new_indexers = [idx for idx in additional_indexers if idx not in current_indexers]
    
    if new_indexers:
        print(f"⚠️ Expanding search to additional indexers: {', '.join(new_indexers[:4])}")
        
        workers = min(MAX_WORKERS, max(1, len(new_indexers[:4])))  # Limit to 4 additional
        with ThreadPoolExecutor(max_workers=workers) as ex:
            futures = {ex.submit(_fetch_indexer, idx, query): idx for idx in new_indexers[:4]}
            for f in as_completed(futures):
                new_results, err, idx = f.result()
                if err:
                    errs.append((idx, err))
                if new_results:
                    results.extend(new_results)
        
        # Re-sort and dedupe the combined results
        results = sort_results_by_seeders(results)
        results = _dedupe(results)
    
    return results[:limit], errs

def search_jackett_rich(query: str, bot=None, message=None, limit: int = RICH_MODE_LIMIT):
    """
    Rich search that queries ALL available indexers for comprehensive results.
    Includes progress updates via busy indicator.
    """
    # Try to get all actually available indexers from Jackett
    available_indexers, error = check_available_indexers()
    
    if error:
        print(f"⚠️ Cannot get indexers from Jackett API: {error}")
        print(f"⚠️ Falling back to configured indexers: {JACKETT_INDEXERS}")
        
        # Fallback to configured indexers + extended list
        indexers = [i.strip() for i in JACKETT_INDEXERS.split(",") if i.strip()]
        
        # Add more from the ALL_INDEXERS list as fallback
        for idx in ALL_INDEXERS:
            if idx not in indexers:
                indexers.append(idx)
        
        # If we still have no indexers, fail
        if not indexers:
            raise Exception(f"Cannot get available indexers from Jackett and no fallback configured: {error}")
            
    else:
        if not available_indexers:
            print("⚠️ No configured indexers found in Jackett, using fallback list")
            indexers = [i.strip() for i in JACKETT_INDEXERS.split(",") if i.strip()]
        else:
            # Use all available indexers for rich mode
            indexers = [idx["id"] for idx in available_indexers]
    
    print(f"🔍 Rich mode using {len(indexers)} indexers: {', '.join(indexers[:10])}{'...' if len(indexers) > 10 else ''}")

    merged = []
    errs = []
    completed_indexers = 0
    
    # Use more workers for rich mode but cap it to avoid overwhelming
    workers = min(8, max(4, len(indexers) // 3))

    with ThreadPoolExecutor(max_workers=workers) as ex:
        # Submit all indexer searches
        future_to_indexer = {ex.submit(_fetch_indexer, idx, query): idx for idx in indexers}
        
        for future in as_completed(future_to_indexer):
            indexer = future_to_indexer[future]
            completed_indexers += 1
            
            try:
                results, err, idx = future.result()
                if err:
                    errs.append((idx, err))
                if results:
                    merged.extend(results)
                
                # Update progress if we have bot and message
                if bot and message:
                    update_busy_indicator(
                        bot, message, 
                        current_indexer=indexer,
                        total_indexers=len(indexers),
                        found_results=len(merged)
                    )
                
            except Exception as e:
                errs.append((indexer, str(e)))
        
        # Sort, dedupe and limit results
        merged = sort_results_by_seeders(merged)
        merged = _dedupe(merged)

    return merged[:limit], errs

def check_available_indexers():
    """
    Check which indexers are actually available and working in Jackett.
    This helps diagnose why bot results differ from desktop.
    """
    try:
        if not JACKETT_API_KEY:
            return [], "JACKETT_API_KEY is empty"
        
        # Get list of configured indexers from Jackett
        url = f"{JACKETT_URL}/api/v2.0/indexers"
        params = {"apikey": JACKETT_API_KEY}
        
        print(f"🔍 Checking Jackett indexers at: {url}")
        
        r = requests.get(url, params=params, timeout=(CONNECT_TIMEOUT, READ_TIMEOUT))
        print(f"📡 Response status: {r.status_code}")
        print(f"📄 Response headers: {dict(r.headers)}")
        print(f"📝 Response content length: {len(r.content)}")
        print(f"🔤 First 200 chars of response: {r.text[:200]}")
        
        r.raise_for_status()
        
        if not r.text.strip():
            return [], "Empty response from Jackett API"
        
        try:
            indexers = r.json()
        except ValueError as e:
            return [], f"Invalid JSON response: {str(e)}. Response: {r.text[:500]}"
        
        if not isinstance(indexers, list):
            return [], f"Expected list of indexers, got: {type(indexers)}. Response: {str(indexers)[:200]}"
        
        available = []
        for indexer in indexers:
            if isinstance(indexer, dict) and indexer.get("configured", False):
                name = indexer.get("id", "unknown")
                title = indexer.get("title", name)
                available.append({"id": name, "title": title})
        
        print(f"✅ Found {len(available)} configured indexers: {[i['id'] for i in available[:10]]}")
        
        return available, None
        
    except requests.exceptions.Timeout:
        return [], f"Timeout connecting to Jackett at {JACKETT_URL}"
    except requests.exceptions.ConnectionError:
        return [], f"Cannot connect to Jackett at {JACKETT_URL}"
    except requests.exceptions.HTTPError as e:
        return [], f"HTTP error from Jackett: {e.response.status_code} - {e.response.text[:200]}"
    except Exception as e:
        return [], f"Unexpected error: {str(e)}"

def test_indexer_performance(query="ubuntu", limit=3):
    """
    Test performance of individual indexers for diagnostic purposes.
    Shows which indexers return the most results and highest seeders.
    """
    try:
        # First, test the Jackett connection and API
        report = [f"🔍 Jackett Connection Test:"]
        report.append(f"URL: {JACKETT_URL}")
        report.append(f"API Key: {'***' + JACKETT_API_KEY[-4:] if len(JACKETT_API_KEY) > 4 else 'NOT SET'}")
        report.append("=" * 50)
        
        available_indexers, error = check_available_indexers()
        
        if error:
            report.append(f"❌ Jackett API Error: {error}")
            report.append("\n💡 Possible solutions:")
            report.append("• Check JACKETT_URL environment variable")
            report.append("• Check JACKETT_API_KEY environment variable")  
            report.append("• Verify Jackett is running and accessible")
            report.append("• Check Jackett logs for errors")
            
            # Try testing with configured indexers instead
            report.append(f"\n🔄 Testing with configured indexers: {JACKETT_INDEXERS}")
            indexers_to_test = [{"id": i.strip(), "title": i.strip()} for i in JACKETT_INDEXERS.split(",") if i.strip()]
        else:
            if not available_indexers:
                report.append("⚠️ No configured indexers found in Jackett")
                report.append("💡 Configure some indexers in your Jackett web interface")
                return "\n".join(report)
            else:
                report.append(f"✅ Found {len(available_indexers)} configured indexers")
                indexers_to_test = available_indexers
        
        if not indexers_to_test:
            report.append("❌ No indexers available to test")
            return "\n".join(report)
        
        report.append(f"\n🧪 Testing {len(indexers_to_test)} indexers with query: '{query}'")
        report.append("=" * 50)
        
        results_by_indexer = {}
        errors = []
        
        # Test each indexer individually
        for indexer_info in indexers_to_test[:15]:  # Test first 15 to avoid spam
            indexer_id = indexer_info["id"]
            try:
                results, err, _ = _fetch_indexer(indexer_id, query)
                if err:
                    errors.append(f"{indexer_id}: {err}")
                else:
                    # Get top result seeder count
                    top_seeders = max([get_seeders_count(r) for r in results], default=0)
                    results_by_indexer[indexer_id] = {
                        "count": len(results),
                        "top_seeders": top_seeders,
                        "title": indexer_info["title"]
                    }
                    report.append(f"✅ {indexer_id}: {len(results)} results, top: {top_seeders} seeders")
            except Exception as e:
                errors.append(f"{indexer_id}: {str(e)}")
                report.append(f"❌ {indexer_id}: {str(e)}")
        
        if results_by_indexer:
            # Sort by effectiveness (results count + top seeders)
            sorted_indexers = sorted(
                results_by_indexer.items(), 
                key=lambda x: (x[1]["count"], x[1]["top_seeders"]), 
                reverse=True
            )
            
            report.append(f"\n📊 Best Performing Indexers:")
            report.append("=" * 30)
            
            for indexer_id, data in sorted_indexers[:5]:
                title = data["title"]
                count = data["count"]
                seeders = data["top_seeders"]
                report.append(f"🏆 {indexer_id}: {count} results, {seeders} max seeders")
        
        if errors:
            report.append(f"\n❌ Failed Indexers ({len(errors)}):")
            report.append("=" * 25)
            for error in errors[:8]:
                report.append(f"   {error}")
        
        report.append(f"\n� Current Configuration:")
        report.append(f"• Normal mode uses: {JACKETT_INDEXERS}")
        report.append(f"• Rich mode uses: ALL available indexers")
        report.append(f"• Timeouts: {CONNECT_TIMEOUT}s connect, {READ_TIMEOUT}s read")
        
        return "\n".join(report)
        
    except Exception as e:
        return f"❌ Diagnostics failed: {str(e)}\n\nPlease check your Jackett configuration and network connectivity."

def get_all_available_indexers():
    """
    Get list of all indexers that could be available via Jackett.
    This is used for rich mode searches.
    """
    return ALL_INDEXERS.copy()
    """
    Get list of all indexers that could be available via Jackett.
    This is used for rich mode searches.
    """
    return ALL_INDEXERS.copy()
    """
    Extended search that tries more indexers if initial search yields poor results.
    This is used as a fallback when we need more/better torrent options.
    """
    # First try the fast search
    results, errs = search_jackett_fast(query, limit)
    
    # If we got good results (multiple results with decent seeders), return them
    good_results = [r for r in results if r.get("Seeders", 0) > 0]
    if len(good_results) >= 3:
        return results, errs
    
    # If results are poor, try additional indexers (if available)
    # Common additional indexers that might not be in the fast list
    additional_indexers = [
        "1337x", "rarbg", "thepiratebay", "kickasstorrents", 
        "torrentgalaxy", "glodls", "magnetdl", "btdiggg"
    ]
    
    # Filter out indexers we already tried
    current_indexers = set(JACKETT_INDEXERS.split(","))
    new_indexers = [idx for idx in additional_indexers if idx not in current_indexers]
    
    if new_indexers:
        print(f"⚠️ Expanding search to additional indexers: {', '.join(new_indexers[:4])}")
        
        workers = min(MAX_WORKERS, max(1, len(new_indexers[:4])))  # Limit to 4 additional
        with ThreadPoolExecutor(max_workers=workers) as ex:
            futures = {ex.submit(_fetch_indexer, idx, query): idx for idx in new_indexers[:4]}
            for f in as_completed(futures):
                new_results, err, idx = f.result()
                if err:
                    errs.append((idx, err))
                if new_results:
                    results.extend(new_results)
        
        # Re-sort and dedupe the combined results
        results = sorted(results, key=lambda x: x.get("Seeders", 0), reverse=True)
        results = _dedupe(results)
    
    return results[:limit], errs


# --------------- Telegram glue ---------------

def start_search(bot, message, folder, query, rich_mode=False):
    try:
        # Create busy indicator
        search_type = "rich" if rich_mode else "normal"
        create_busy_indicator(bot, message, search_type)
        
        bot.send_chat_action(message.chat.id, "typing")
        
        if rich_mode:
            # Rich mode: search all available indexers
            results, idx_errors = search_jackett_rich(query, bot, message, limit=RICH_MODE_LIMIT)
            search_mode_label = f"🔍 Rich search results ({len(results)} from all indexers):"
        else:
            # Normal mode: fast search with fallback to extended if needed
            results, idx_errors = search_jackett_fast(query, limit=RESULT_LIMIT)
            
            # If we didn't get good results, try extended search
            if len(results) < 3 or all(get_seeders_count(r) == 0 for r in results[:3]):
                update_busy_indicator(bot, message, found_results=len(results))
                results, idx_errors = search_jackett_extended(query, limit=RESULT_LIMIT)
            
            search_mode_label = f"🔍 Top {len(results)} results (seeders ↓):"
        
        # Remove busy indicator
        remove_busy_indicator(bot, message)

        if not results:
            msg = "❌ No torrents found."
            if idx_errors:
                err_lines = [f"• {name}: {err.splitlines()[0][:120]}" for name, err in idx_errors[:3]]
                msg += "\n⚠️ Some indexers errored:\n" + "\n".join(err_lines)
            if not rich_mode:
                msg += "\n\n💡 Try: /t <query> rich for comprehensive search across all indexers"
                msg += "\n💡 Run /tdiag to check indexer status"
            else:
                msg += "\n\n💡 Try different search terms or check if your indexers are working."
                msg += "\n💡 Run /tdiag to diagnose indexer issues"
            bot.reply_to(message, msg)
            return

        # Use user id as cache key so callbacks match reliably
        user_id = message.from_user.id
        
        # Ensure final results are properly sorted by seeders (descending)
        results = sort_results_by_seeders(results)
        
        search_cache[user_id] = {"results": results, "folder": folder, "rich_mode": rich_mode}

        # Enhanced result display with quality indicators
        lines = [search_mode_label]
        if rich_mode:
            lines.append("🌟 Comprehensive search across all available indexers")
        
        for i, res in enumerate(results, start=1):
            title = res.get("Title", "Unknown Title")
            seeders = get_seeders_count(res)  # Use robust seeder counting
            size = human_size(res.get("Size", 0))
            tracker = res.get("Tracker") or res.get("TrackerId") or ""
            
            # Add quality indicators
            quality_indicator = ""
            if seeders >= 100:
                quality_indicator = " 🔥"  # Hot torrent
            elif seeders >= 10:
                quality_indicator = " ⭐"  # Good torrent
            elif seeders > 0:
                quality_indicator = " ✅"  # Available
            else:
                quality_indicator = " ⚠️"  # No seeders
            
            # Check if magnet is available
            magnet_indicator = " 🧲" if res.get("MagnetUri") else ""
            torrent_indicator = " 📁" if res.get("Link") else ""
            
            ttag = f" • 🏷 {tracker}" if tracker else ""
            lines.append(f"\n{i}. {title}{quality_indicator}{magnet_indicator}{torrent_indicator}\n   🌱 {seeders} | 💾 {size}{ttag}")

        markup = types.InlineKeyboardMarkup()
        # Create rows of buttons (max 5 per row for readability)
        button_rows = []
        current_row = []
        
        for i, res in enumerate(results):
            btn = types.InlineKeyboardButton(f"{i+1} (🌱 {get_seeders_count(res)})", callback_data=f"torrent_{i}")
            current_row.append(btn)
            
            if len(current_row) == 5 or i == len(results) - 1:
                button_rows.append(current_row)
                current_row = []
        
        for row in button_rows:
            markup.row(*row)

        result_msg = "\n".join(lines)
        if len(result_msg) > 4000:  # Telegram message limit
            result_msg = result_msg[:3900] + "\n\n... (truncated)"
        
        bot.send_message(message.chat.id, result_msg, reply_markup=markup)

    except Exception as e:
        remove_busy_indicator(bot, message)
        bot.reply_to(message, f"❌ Torrent search error: {e}")
        print(f"Error in start_search: {e}")  # Log for debugging

def handle_selection(bot, call):
    try:
        user_id = call.from_user.id
        if user_id not in search_cache:
            bot.answer_callback_query(call.id, "⚠️ No active search")
            return

        data = search_cache.pop(user_id)
        results = data["results"]
        folder = data["folder"]

        idx = int(call.data.split("_")[1])
        if idx >= len(results):
            bot.answer_callback_query(call.id, "⚠️ Invalid choice")
            return

        chosen = results[idx]
        title = chosen.get("Title", "Unknown Title")

        # Connect to qBittorrent first
        qbt = qbittorrentapi.Client(
            host=QBIT_HOST, port=QBIT_PORT, username=QBIT_USER, password=QBIT_PASS
        )
        qbt.auth_log_in()

        save_path = QBIT_SAVE_ROOT if not folder else f"{QBIT_SAVE_ROOT}/{folder}"
        
        # Enhanced fallback mechanism
        download_success = False
        download_message = ""
        
        # Method 1: Try magnet link first (preferred method)
        magnet = chosen.get("MagnetUri")
        if magnet:
            try:
                qbt.torrents_add(urls=magnet, save_path=save_path)
                download_success = True
                download_message = "✅ Downloaded via magnet link"
            except Exception as e:
                print(f"⚠️ Magnet link failed: {str(e)}")
                download_message = f"⚠️ Magnet link failed: {str(e)}"
        
        # Method 2-4: Try alternative methods if magnet failed or wasn't available
        if not download_success:
            bot.send_message(call.message.chat.id, f"🔄 Magnet link not available or failed, trying alternative methods for: {title}")
            download_success, download_message = _try_alternative_download_methods(chosen, qbt, save_path)
        
        if not download_success:
            bot.answer_callback_query(call.id, "❌ All download methods failed")
            bot.send_message(call.message.chat.id, f"❌ Failed to download: {title}\n{download_message}")
            return

        # Try to resolve the torrent we just added for a richer "started" message
        infohash = extract_infohash_from_magnet(magnet) if magnet else None
        time.sleep(2)  # brief moment for qBittorrent to register
        tor = _find_started_torrent(qbt, infohash, title)

        # Remove buttons
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)

        if tor:
            started_msg = (
                f"🚀 Download started\n"
                f"{download_message}\n"
                f"• Name: {tor.name}\n"
                f"• Save: {folder or 'default'} ({save_path})\n"
                f"• State: {tor.state}\n"
                f"• Progress: {tor.progress*100:.1f}%\n"
                f"• DL: {human_speed(getattr(tor, 'dlspeed', 0))} | ETA: {format_eta(getattr(tor, 'eta', -1))}"
            )
        else:
            started_msg = (
                f"🚀 Download started\n"
                f"{download_message}\n"
                f"• Name: {title}\n"
                f"• Save: {folder or 'default'} ({save_path})"
            )

        bot.send_message(call.message.chat.id, started_msg)

        # Update downloads.txt in the bot's mounted directory
        _update_downloads_txt(qbt)

    except qbittorrentapi.LoginFailed as e:
        bot.send_message(call.message.chat.id, f"❌ Torrent add error: qBittorrent login failed: {e}")
    except qbittorrentapi.APIConnectionError as e:
        bot.send_message(call.message.chat.id, f"❌ Torrent add error: cannot reach qBittorrent: {e}")
    except qbittorrentapi.Forbidden403Error as e:
        bot.send_message(call.message.chat.id, f"❌ Torrent add error: WebUI auth/CSRF issue: {e}")
    except qbittorrentapi.TorrentFileError as e:
        bot.send_message(call.message.chat.id, f"❌ Torrent add error: Invalid torrent file: {e}")
    except qbittorrentapi.UnsupportedMediaType415Error as e:
        bot.send_message(call.message.chat.id, f"❌ Torrent add error: Unsupported file format: {e}")
    except Exception as e:
        error_msg = f"❌ Torrent add error: {type(e).__name__}: {e}"
        bot.send_message(call.message.chat.id, error_msg)
        print(f"Unexpected error in handle_selection: {error_msg}")  # Log for debugging
