import os
from telebot import types
import qbittorrentapi

# ---- qBittorrent connection (override with envs if needed) ----
QBIT_HOST = os.getenv("QBIT_HOST", "qbittorrent")
QBIT_PORT = int(os.getenv("QBIT_PORT", "8080"))
QBIT_USER = os.getenv("QBIT_USER", "admin")
QBIT_PASS = os.getenv("QBIT_PASS", "adminadmin")

PAGE_SIZE = 10
_cache = {}  # chat_id -> {"items": [...], "page": 0, "filter": str|None}

# ---------- helpers ----------
def _human_size(n: int | float | None) -> str:
    if not n or n <= 0:
        return "0 B"
    units = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    n = float(n)
    while n >= 1024 and i < len(units) - 1:
        n /= 1024.0
        i += 1
    return f"{n:.2f} {units[i]}"

def _eta(sec: int | None) -> str:
    if sec is None or sec < 0 or sec > 365*24*3600:
        return ""
    m, s = divmod(int(sec), 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)
    if d:  return f"{d}d {h}h"
    if h:  return f"{h}h {m}m"
    if m:  return f"{m}m {s}s"
    return f"{s}s"

def _state_icon(state: str) -> str:
    s = (state or "").lower()
    if "error" in s: return ""
    if "paused" in s: return ""
    if "stalled" in s: return ""
    if "upload" in s or "seeding" in s: return ""
    if "queued" in s: return ""
    if "checking" in s: return ""
    if "meta" in s: return ""
    if "down" in s: return ""
    return ""

def _connect_qbt():
    try:
        client = qbittorrentapi.Client(
            host=QBIT_HOST, port=QBIT_PORT, username=QBIT_USER, password=QBIT_PASS
        )
        client.auth_log_in()
        return client
    except Exception as e:
        raise RuntimeError(
            f"Could not connect/login to qBittorrent at {QBIT_HOST}:{QBIT_PORT} "
            f"as '{QBIT_USER}'. Details: {e}"
        )

def _load_torrents(filter_key: str | None):
    client = _connect_qbt()
    tors = client.torrents_info()  # returns list of TorrentDictionary
    items = []
    for t in tors:
        # normalize fields safely
        name = getattr(t, "name", "(no name)")
        state = getattr(t, "state", "")
        progress = float(getattr(t, "progress", 0.0))  # 0..1
        dlspeed = int(getattr(t, "dlspeed", 0))
        upspeed = int(getattr(t, "upspeed", 0))
        eta = getattr(t, "eta", None)
        total_size = int(getattr(t, "size", getattr(t, "total_size", 0)))
        completed = int(total_size * progress) if total_size else 0
        save_path = getattr(t, "save_path", "")
        added_on = int(getattr(t, "added_on", 0))

        item = {
            "name": name,
            "state": state,
            "progress": progress,
            "dlspeed": dlspeed,
            "upspeed": upspeed,
            "eta": eta,
            "size": total_size,
            "completed": completed,
            "save_path": save_path,
            "added_on": added_on,
        }

        # optional filtering
        if filter_key:
            fk = filter_key.lower()
            s = state.lower()
            if fk in ("active", "downloading"):
                if not ("down" in s or (dlspeed > 0 and progress < 1.0)):
                    continue
            elif fk in ("completed", "done", "finished"):
                if progress < 0.999:
                    continue
            elif fk in ("seeding",):
                if not ("upload" in s or "seeding" in s):
                    continue
            elif fk in ("paused",):
                if "paused" not in s:
                    continue
            elif fk in ("errored", "error", "failed"):
                if "error" not in s:
                    continue
            # otherwise unknown filter -> no-op

        items.append(item)

    # sort newest first
    items.sort(key=lambda x: x.get("added_on", 0), reverse=True)
    return items

def _build_page_text(items, page: int, filter_key: str | None):
    total = len(items)
    if total == 0:
        return " No torrents found."
    start = page * PAGE_SIZE
    end = min(start + PAGE_SIZE, total)
    hdr = f" qBittorrent downloads  {total} total"
    if filter_key:
        hdr += f" (filter: {filter_key})"
    lines = [hdr]

    for idx, it in enumerate(items[start:end], start=start + 1):
        pct = f"{it['progress']*100:.1f}%"
        icon = _state_icon(it["state"])
        line = (
            f"\n{idx}. {icon} {it['name']}\n"
            f"    {it['state']} ({pct})\n"
            f"     {_human_size(it['dlspeed'])}/s   {_human_size(it['upspeed'])}/s  | ETA {_eta(it['eta'])}\n"
            f"    {_human_size(it['completed'])} / {_human_size(it['size'])}\n"
            f"    {it['save_path']}"
        )
        lines.append(line)
    return "\n".join(lines)

def _pagination_markup(total: int, page: int):
    if total <= PAGE_SIZE:
        return None
    markup = types.InlineKeyboardMarkup()
    buttons = []
    if page > 0:
        buttons.append(types.InlineKeyboardButton(" Prev", callback_data=f"dlpage:{page-1}"))
    if (page + 1) * PAGE_SIZE < total:
        buttons.append(types.InlineKeyboardButton("Next ", callback_data=f"dlpage:{page+1}"))
    if buttons:
        markup.row(*buttons)
    return markup

def _delete_completed_torrents():
    """Delete all fully completed torrents from qBittorrent."""
    client = _connect_qbt()
    tors = client.torrents_info()
    
    deleted_count = 0
    deleted_names = []
    
    for t in tors:
        progress = float(getattr(t, "progress", 0.0))  # 0..1
        state = getattr(t, "state", "").lower()
        name = getattr(t, "name", "(no name)")
        hash_value = getattr(t, "hash", "")
        
        # Consider torrent completed if progress is 100% 
        if progress >= 0.999:  # Use 0.999 to account for floating point precision
            try:
                # Delete torrent and its files
                client.torrents_delete(delete_files=True, torrent_hashes=hash_value)
                deleted_count += 1
                deleted_names.append(name)
                print(f" Deleted completed torrent: {name}")
            except Exception as e:
                print(f" Failed to delete torrent {name}: {e}")
    
    return deleted_count, deleted_names

# ---------- exposed API ----------
def show(bot, message):
    """Entry point for /d [optional filter]"""
    try:
        parts = message.text.strip().split(" ", 1)
        filter_key = parts[1].strip() if len(parts) > 1 else None

        # Handle special "clear" command
        if filter_key and filter_key.lower() == "clear":
            bot.send_message(message.chat.id, " Clearing all completed torrents...")
            
            deleted_count, deleted_names = _delete_completed_torrents()
            
            if deleted_count == 0:
                response = " No completed torrents to clear."
            else:
                response = f" Successfully cleared {deleted_count} completed torrent(s):\n\n"
                # Show first few names, truncate if too many
                shown_names = deleted_names[:5]
                for name in shown_names:
                    response += f" {name}\n"
                
                if len(deleted_names) > 5:
                    response += f"\n... and {len(deleted_names) - 5} more"
            
            bot.send_message(message.chat.id, response)
            return

        items = _load_torrents(filter_key)
        _cache[message.chat.id] = {"items": items, "page": 0, "filter": filter_key}

        text = _build_page_text(items, 0, filter_key)
        markup = _pagination_markup(len(items), 0)
        bot.send_message(message.chat.id, text, reply_markup=markup)

    except Exception as e:
        bot.reply_to(message, f" Downloads error: {e}")

def handle_page(bot, call):
    """Handle inline pagination callback"""
    try:
        chat_id = call.message.chat.id
        payload = _cache.get(chat_id)
        if not payload:
            bot.answer_callback_query(call.id, "No data to paginate.")
            return

        # page index from callback payload
        page = int(call.data.split(":")[1])
        payload["page"] = page

        items = payload["items"]
        filter_key = payload["filter"]

        text = _build_page_text(items, page, filter_key)
        markup = _pagination_markup(len(items), page)

        bot.edit_message_text(
            text, chat_id, call.message.message_id, reply_markup=markup
        )
        bot.answer_callback_query(call.id)

    except Exception as e:
        bot.answer_callback_query(call.id, f"Error: {e}")
