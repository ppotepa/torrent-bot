"""
Telegram bot handlers for torrent functionality.
Manages user interactions and UI components.
"""

import time
try:
    import qbittorrentapi
    from telebot import types
except ImportError as e:
    print(f"Warning: Missing dependency: {e}")
    # Define placeholder for development
    class types:
        class InlineKeyboardMarkup:
            def __init__(self): pass
            def row(self, *args): pass
        class InlineKeyboardButton:
            def __init__(self, text, callback_data): pass

from .config import config
from .utils import get_seeders_count, human_size, human_speed, format_eta, extract_infohash_from_magnet
from .busy_indicator import BusyIndicator
from .search_service import SearchService
from .qbittorrent_client import QBittorrentClient
from .fallback_manager import FallbackManager
from .download_monitor import get_download_monitor


def start_search(bot, message, folder, query, rich_mode=False, all_mode=False, music_mode=False):
    """Handle torrent search requests from Telegram."""
    try:
        # Create busy indicator
        if all_mode:
            search_type = "all"
        elif music_mode:
            search_type = "music"
        elif rich_mode:
            search_type = "rich"
        else:
            search_type = "normal"
            
        BusyIndicator.create(bot, message, search_type)
        
        bot.send_chat_action(message.chat.id, "typing")
        
        # Initialize services
        search_service = SearchService()
        
        # Perform search
        results, idx_errors, search_type = search_service.search(query, rich_mode, all_mode, music_mode, bot, message)
        
        # Remove busy indicator
        BusyIndicator.remove(bot, message)

        if not results:
            msg = "❌ No torrents found."
            if idx_errors:
                err_lines = [f"• {name}: {err.splitlines()[0][:120]}" for name, err in idx_errors[:3]]
                msg += "\n⚠️ Some indexers errored:\n" + "\n".join(err_lines)
            if not rich_mode and not all_mode and not music_mode:
                msg += "\n\n💡 Try: /t <query> rich for comprehensive search across configured indexers"
                msg += "\n💡 Try: /t <query> all for exhaustive search across ALL indexers"
                msg += "\n🎵 Try: /t <query> music for music-focused search"
                msg += "\n💡 Run /tdiag to check indexer status"
            elif music_mode:
                msg += "\n\n💡 Try: /t <query> rich or /t <query> all for broader search"
                msg += "\n💡 Try different artist/album names or check if music indexers are working."
                msg += "\n💡 Run /tdiag to diagnose indexer issues"
            elif rich_mode:
                msg += "\n\n💡 Try: /t <query> all for even more comprehensive search"
                msg += "\n🎵 Try: /t <query> music for music-focused results"
                msg += "\n💡 Try different search terms or check if your indexers are working."
                msg += "\n💡 Run /tdiag to diagnose indexer issues"
            else:  # all_mode
                msg += "\n\n💡 This was the most comprehensive search possible."
                msg += "\n💡 Try different search terms or check your Jackett configuration."
                msg += "\n💡 Run /tdiag to diagnose indexer issues"
            bot.reply_to(message, msg)
            return

        # Cache results for user selection
        user_id = message.from_user.id
        search_service.cache_results(user_id, results, folder, rich_mode, all_mode, music_mode)

        # Generate search results message
        search_mode_label = _get_search_mode_label(rich_mode, all_mode, music_mode, len(results))
        result_msg = _format_search_results(results, search_mode_label, rich_mode, all_mode, music_mode)
        
        # Create selection buttons
        markup = _create_selection_markup(results)
        
        bot.send_message(message.chat.id, result_msg, reply_markup=markup)

    except Exception as e:
        BusyIndicator.remove(bot, message)
        bot.reply_to(message, f"❌ Torrent search error: {e}")
        print(f"Error in start_search: {e}")  # Log for debugging


def handle_selection(bot, call):
    """Handle torrent selection callbacks from Telegram."""
    try:
        user_id = call.from_user.id
        search_service = SearchService()
        data = search_service.get_cached_results(user_id)
        
        if not data:
            bot.answer_callback_query(call.id, "⚠️ No active search")
            return

        results = data["results"]
        folder = data["folder"]

        idx = int(call.data.split("_")[1])
        if idx >= len(results):
            bot.answer_callback_query(call.id, "⚠️ Invalid choice")
            return

        chosen = results[idx]
        title = chosen.get("Title", "Unknown Title")

        # Initialize clients
        qbt_client = QBittorrentClient()
        fallback_manager = FallbackManager(qbt_client, search_service.jackett_client)

        save_path = config.QBIT_SAVE_ROOT if not folder else f"{config.QBIT_SAVE_ROOT}/{folder}"
        
        # Try to download the torrent
        download_success, download_message = _attempt_download(chosen, qbt_client, fallback_manager, save_path, call)
        
        if not download_success:
            bot.answer_callback_query(call.id, "❌ All download methods failed")
            bot.send_message(call.message.chat.id, f"❌ Failed to download: {title}\n{download_message}")
            return

        # Send intermediate message about fallback methods if magnet failed
        magnet = chosen.get("MagnetUri")
        if not magnet or "Downloaded via magnet link" not in download_message:
            bot.send_message(call.message.chat.id, f"🔄 Trying alternative download methods for: {title}")

        # Find the started torrent and send success message
        _send_download_success_message(bot, call, chosen, qbt_client, folder, save_path, download_message)

        # Auto-start download monitor if not already running (and if enabled)
        if config.AUTO_START_MONITOR:
            try:
                monitor = get_download_monitor()
                if not monitor.is_running():
                    # Get the bot callback function to send notifications
                    def notification_callback(message):
                        try:
                            # Send notification to the user who initiated the download
                            bot.send_message(call.message.chat.id, message)
                        except Exception as e:
                            print(f"Failed to send notification: {e}")
                    
                    monitor.start(notification_callback)
                    bot.send_message(call.message.chat.id, "🔔 Download monitor started automatically - you'll get notified when downloads complete!")
                else:
                    print("Monitor already running, skipping auto-start")
            except Exception as e:
                print(f"Failed to auto-start monitor: {e}")
                # Don't fail the download if monitor can't start

        # Update downloads.txt
        qbt_client.update_downloads_txt()

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
        print(f"Unexpected error in handle_selection: {error_msg}")


def _get_search_mode_label(rich_mode: bool, all_mode: bool, music_mode: bool, result_count: int) -> str:
    """Generate search mode label for results."""
    if all_mode:
        return f"🌐 ALL search results ({result_count} from EVERY indexer):"
    elif music_mode:
        return f"🎵 Music search results ({result_count} from music indexers):"
    elif rich_mode:
        return f"🔍 Rich search results ({result_count} from all configured indexers):"
    else:
        return f"🔍 Top {result_count} results (seeders ↓):"


def _format_search_results(results: list, search_mode_label: str, rich_mode: bool, all_mode: bool, music_mode: bool = False) -> str:
    """Format search results for display."""
    lines = [search_mode_label]
    if all_mode:
        lines.append("🌐 Exhaustive search across ALL indexers on Jackett")
    elif music_mode:
        lines.append("🎵 Focused search across popular music indexers")
    elif rich_mode:
        lines.append("🌟 Comprehensive search across all available indexers")
    
    for i, res in enumerate(results, start=1):
        title = res.get("Title", "Unknown Title")
        seeders = get_seeders_count(res)
        size = human_size(res.get("Size", 0))
        tracker = res.get("Tracker") or res.get("TrackerId") or ""
        
        # Add quality indicators
        quality_indicator = _get_quality_indicator(seeders)
        
        # Check if magnet/torrent file is available
        magnet_indicator = " 🧲" if res.get("MagnetUri") else ""
        torrent_indicator = " 📁" if res.get("Link") else ""
        
        ttag = f" • 🏷 {tracker}" if tracker else ""
        lines.append(f"\n{i}. {title}{quality_indicator}{magnet_indicator}{torrent_indicator}\n   🌱 {seeders} | 💾 {size}{ttag}")

    result_msg = "\n".join(lines)
    if len(result_msg) > 4000:  # Telegram message limit
        result_msg = result_msg[:3900] + "\n\n... (truncated)"
    
    return result_msg


def _get_quality_indicator(seeders: int) -> str:
    """Get quality indicator emoji based on seeder count."""
    if seeders >= 100:
        return " 🔥"  # Hot torrent
    elif seeders >= 10:
        return " ⭐"  # Good torrent
    elif seeders > 0:
        return " ✅"  # Available
    else:
        return " ⚠️"  # No seeders


def _create_selection_markup(results: list) -> types.InlineKeyboardMarkup:
    """Create inline keyboard markup for torrent selection."""
    markup = types.InlineKeyboardMarkup()
    button_rows = []
    current_row = []
    
    for i, res in enumerate(results):
        btn = types.InlineKeyboardButton(
            f"{i+1} (🌱 {get_seeders_count(res)})", 
            callback_data=f"torrent_{i}"
        )
        current_row.append(btn)
        
        if len(current_row) == 5 or i == len(results) - 1:
            button_rows.append(current_row)
            current_row = []
    
    for row in button_rows:
        markup.row(*row)
    
    return markup


def _attempt_download(chosen_result: dict, qbt_client: QBittorrentClient, fallback_manager: FallbackManager, save_path: str, call) -> tuple[bool, str]:
    """Attempt to download torrent using various methods."""
    # Method 1: Try magnet link first (preferred method)
    magnet = chosen_result.get("MagnetUri")
    if magnet:
        if qbt_client.add_torrent_magnet(magnet, save_path):
            return True, "✅ Downloaded via magnet link"
    
    # Method 2-4: Try alternative methods if magnet failed or wasn't available
    title = chosen_result.get("Title", "Unknown Title")
    # Note: We can't send intermediate messages from here since we don't have bot reference
    # The fallback message will be included in the final result
    
    return fallback_manager.try_alternative_download_methods(chosen_result, save_path)


def _send_download_success_message(bot, call, chosen_result: dict, qbt_client: QBittorrentClient, folder: str, save_path: str, download_message: str):
    """Send download success message with torrent details."""
    title = chosen_result.get("Title", "Unknown Title")
    magnet = chosen_result.get("MagnetUri")
    
    # Try to find the started torrent for richer information
    infohash = extract_infohash_from_magnet(magnet) if magnet else None
    time.sleep(2)  # brief moment for qBittorrent to register
    tor = qbt_client.find_started_torrent(infohash, title)

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
