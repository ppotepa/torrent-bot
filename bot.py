import os
import telebot
from telebot import types  # noqa

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Loaded environment variables from .env file")
except ImportError:
    print("⚠️ python-dotenv not installed, using system environment variables only")

# import plugins
from plugins import youtube, facebook, torrent, downloads, sysinfo

# import download monitor
from plugins.torrent.download_monitor import start_download_monitoring, stop_download_monitoring, get_download_monitor

# --- Token ---
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
if not TOKEN or ":" not in TOKEN:
    raise ValueError("Invalid TELEGRAM_BOT_TOKEN env var (must contain a colon).")
bot = telebot.TeleBot(TOKEN)

# Notification function for download completions
def send_download_notification(message_text: str):
    """Send download completion notification to admin user."""
    try:
        # Get admin user ID (you can configure this via environment variable)
        admin_user_id = os.getenv("ADMIN_USER_ID", "").strip()
        
        if admin_user_id:
            bot.send_message(admin_user_id, message_text, parse_mode="Markdown")
            print(f"📨 Sent notification to admin user: {admin_user_id}")
        else:
            print("⚠️ No ADMIN_USER_ID configured, cannot send notifications")
            print(f"📋 Would send: {message_text[:100]}...")
    except Exception as e:
        print(f"❌ Error sending download notification: {e}")

# Start download monitoring
try:
    start_download_monitoring(send_download_notification)
    print("🔍 Download completion monitoring started")
except Exception as e:
    print(f"⚠️ Could not start download monitoring: {e}")

# --- Welcome & Help ---
@bot.message_handler(commands=["start", "help"])
def send_welcome(message):
    text = (
        "👋 Welcome to the Media Bot!\n\n"
        "Available commands:\n"
        "• /dl <url>:[flags] [folder] — download from YouTube or Facebook\n"
        "   Flags: [force], [notify], [silent], [background]\n"
        "   Example: /dl https://youtube.com/watch?v=123:[notify,background]\n"
        "• /t <query>:[flags] — search torrents via Jackett\n"
        "   Flags: [all], [rich], [music], [notify], [silent]\n"
        "   Examples:\n"
        "   ◦ /t ubuntu:[all] — Exhaustive search across ALL indexers\n"
        "   ◦ /t music album:[rich,notify] — Rich search with notification\n"
        "   ◦ /t song:[music] — Music-focused search\n"
        "• /tdiag — run torrent indexer diagnostics\n"
        "• /qdiag — diagnose qBittorrent connection and settings\n"
        "• /monitor:[flags] — download completion monitor\n"
        "   Flags: [start], [stop], [status]\n"
        "• /monitor_check — force check for completed downloads\n"
        "• /d [filter] — list qBittorrent downloads (filters: active, completed, seeding, paused, errored)\n"
        "• /si:[flags] — display system information\n"
        "   Flags: [detailed], [brief], [cpu], [memory], [disk], [network]\n\n"
        "📌 You can also just paste a link and I'll detect the right plugin.\n\n"
        "� **New Flag System:**\n"
        "   • Flags go at the end in square brackets: command query:[flag1,flag2]\n"
        "   • Each command has its own specific flags\n"
        "   • Some flags are mutually exclusive (all/rich/music for torrents)\n"
        "   • Use without flags for default behavior\n"
        "�🔄 Enhanced torrent fallback system:\n"
        "   • Tries magnet links first\n"
        "   • Falls back to .torrent files\n"
        "   • Reconstructs magnets from hash\n"
        "   • Searches alternative sources\n"
        "   • Visual quality indicators (🔥⭐✅⚠️🧲📁)\n"
    )
    bot.reply_to(message, text)

# --- Torrent search (/t and /torrents) ---
@bot.message_handler(commands=["t", "torrent", "torrents"])
def cmd_torrent(message):
    from universal_flags import parse_universal_flags, validate_command_flags, convert_flags_to_legacy
    
    def get_torrent_usage():
        """Get usage message for torrent commands."""
        return (
            "⚠️ Usage: `/t <search query>:[flags]`\n\n"
            "📋 **Available Flags:**\n"
            "• `all` - Exhaustive search across ALL indexers\n"
            "• `rich` - Comprehensive search across configured indexers\n"
            "• `music` - Focused search across music indexers\n"
            "• `notify` - Send notification when download completes\n"
            "• `silent` - Disable notifications\n\n"
            "📝 **Examples:**\n"
            "• `/t ubuntu:[all]` - Search with all indexers\n"
            "• `/t ubuntu:[rich,notify]` - Rich search with notification\n"
            "• `/t ubuntu:[music]` - Music-focused search\n"
            "• `/t ubuntu` - Normal search (no flags)\n\n"
            "⚡ **Note:** Search mode flags (all, rich, music) are mutually exclusive"
        )
    
    # Parse command and extract flags using universal parser
    query, flags_list, parse_errors = parse_universal_flags(message.text, "t")
    valid_flags, validation_errors = validate_command_flags(flags_list, "t")
    legacy_flags = convert_flags_to_legacy(valid_flags, "t")
    
    # Check if we have a valid query
    if not query.strip():
        bot.reply_to(message, get_torrent_usage(), parse_mode="Markdown")
        return
    
    # Show any flag parsing errors
    all_errors = parse_errors + validation_errors
    if all_errors:
        error_msg = "⚠️ Flag parsing errors:\n" + "\n".join(f"• {err}" for err in all_errors)
        bot.reply_to(message, error_msg)
        # Continue processing with valid flags
    
    # Extract flags for the torrent module
    rich_mode = legacy_flags.get('rich_mode', False)
    all_mode = legacy_flags.get('all_mode', False)
    music_mode = legacy_flags.get('music_mode', False)
    notify = legacy_flags.get('notify', False)
    
    # no folder support in this shorthand; pass None
    torrent.start_search(bot, message, folder=None, query=query, rich_mode=rich_mode, all_mode=all_mode, music_mode=music_mode, notify=notify)

@bot.callback_query_handler(func=lambda call: call.data.startswith("torrent_"))
def callback_torrent(call):
    torrent.handle_selection(bot, call)

# --- Torrent diagnostics ---
@bot.message_handler(commands=["tdiag", "torrent_diag"])
def cmd_torrent_diag(message):
    try:
        bot.send_chat_action(message.chat.id, "typing")
        bot.send_message(message.chat.id, "🔍 Running torrent indexer diagnostics...")
        
        # Run diagnostic test
        report = torrent.test_indexer_performance()
        
        # Split long messages to avoid Telegram limits
        if len(report) > 4000:
            parts = [report[i:i+3900] for i in range(0, len(report), 3900)]
            for i, part in enumerate(parts):
                if i == 0:
                    bot.send_message(message.chat.id, part)
                else:
                    bot.send_message(message.chat.id, f"📊 Diagnostics (part {i+1}):\n{part}")
        else:
            bot.send_message(message.chat.id, report)
            
    except Exception as e:
        bot.reply_to(message, f"❌ Diagnostics failed: {e}")

# --- qBittorrent diagnostics ---
@bot.message_handler(commands=["qdiag", "qbittorrent_diag"])
def cmd_qbittorrent_diag(message):
    try:
        bot.send_chat_action(message.chat.id, "typing")
        bot.send_message(message.chat.id, "🔍 Running qBittorrent diagnostics...")
        
        # Import the qBittorrent client
        from plugins.torrent.qbittorrent_client import QBittorrentClient
        qbit_client = QBittorrentClient()
        
        # Run diagnostic test
        report = qbit_client.diagnose_connection()
        
        # Split long messages to avoid Telegram limits
        if len(report) > 4000:
            parts = [report[i:i+3900] for i in range(0, len(report), 3900)]
            for i, part in enumerate(parts):
                if i == 0:
                    bot.send_message(message.chat.id, part)
                else:
                    bot.send_message(message.chat.id, f"🔍 qBittorrent (part {i+1}):\n{part}")
        else:
            bot.send_message(message.chat.id, report)
            
    except Exception as e:
        bot.reply_to(message, f"❌ qBittorrent diagnostics error: {e}")

# --- Download monitor commands ---
@bot.message_handler(commands=["monitor", "download_monitor"])
def cmd_download_monitor(message):
    from universal_flags import parse_universal_flags, validate_command_flags, convert_flags_to_legacy
    
    def get_monitor_usage():
        """Get usage message for monitor commands."""
        return (
            "⚠️ Usage: `/monitor` or `/monitor:[flags]`\n\n"
            "📋 **Available Flags:**\n"
            "• `start` - Start the download monitor\n"
            "• `stop` - Stop the download monitor\n"
            "• `status` - Show monitor status (default)\n"
            "• `force` - Force action even if already in that state\n\n"
            "📝 **Examples:**\n"
            "• `/monitor` - Show monitor status\n"
            "• `/monitor:[start]` - Start monitoring\n"
            "• `/monitor:[start,force]` - Force restart monitoring"
        )
    
    try:
        # Handle special case where flags are in the command itself
        command_text = message.text.strip()
        
        # Parse command and extract flags using universal parser
        query, flags_list, parse_errors = parse_universal_flags(command_text, "monitor")
        valid_flags, validation_errors = validate_command_flags(flags_list, "monitor")
        legacy_flags = convert_flags_to_legacy(valid_flags, "monitor")
        
        # Show any flag parsing errors
        all_errors = parse_errors + validation_errors
        if all_errors:
            error_msg = "⚠️ Flag parsing errors:\n" + "\n".join(f"• {err}" for err in all_errors)
            bot.reply_to(message, error_msg)
            # Continue processing with valid flags
        
        action = legacy_flags.get('action', 'status')
        force = legacy_flags.get('force', False)
        
        monitor = get_download_monitor()
        
        if action == 'start':
            if monitor.running and not force:
                bot.reply_to(message, "ℹ️ Download monitor is already running. Use /monitor:[start,force] to restart.")
            else:
                if force and monitor.running:
                    monitor.stop_monitoring()
                monitor.notification_callback = send_download_notification
                monitor.start_monitoring()
                bot.reply_to(message, "✅ Download monitor started")
        
        elif action == 'stop':
            if not monitor.running and not force:
                bot.reply_to(message, "ℹ️ Download monitor is not running")
            else:
                monitor.stop_monitoring()
                bot.reply_to(message, "✅ Download monitor stopped")
        
        else:  # status (default)
            status = monitor.get_monitor_status()
            bot.send_message(message.chat.id, f"```\n{status}\n```", parse_mode="Markdown")
            
    except Exception as e:
        bot.reply_to(message, f"❌ Monitor error: {e}")

@bot.message_handler(commands=["monitor_check", "force_check"])
def cmd_force_monitor_check(message):
    try:
        bot.send_chat_action(message.chat.id, "typing")
        monitor = get_download_monitor()
        result = monitor.force_check()
        bot.reply_to(message, result)
    except Exception as e:
        bot.reply_to(message, f"❌ Force check error: {e}")

@bot.message_handler(commands=["monitor_start"])
def cmd_start_monitor(message):
    try:
        monitor = get_download_monitor()
        if monitor.running:
            bot.reply_to(message, "ℹ️ Download monitor is already running")
        else:
            monitor.notification_callback = send_download_notification
            monitor.start_monitoring()
            bot.reply_to(message, "✅ Download monitor started")
    except Exception as e:
        bot.reply_to(message, f"❌ Error starting monitor: {e}")

@bot.message_handler(commands=["monitor_stop"])
def cmd_stop_monitor(message):
    try:
        monitor = get_download_monitor()
        if not monitor.running:
            bot.reply_to(message, "ℹ️ Download monitor is not running")
        else:
            monitor.stop_monitoring()
            bot.reply_to(message, "🛑 Download monitor stopped")
    except Exception as e:
        bot.reply_to(message, f"❌ Error stopping monitor: {e}")

# Graceful shutdown
import signal
import sys

def signal_handler(sig, frame):
    print('🛑 Shutting down bot...')
    try:
        stop_download_monitoring()
        print('✅ Download monitor stopped')
    except:
        pass
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# --- System Information ---
@bot.message_handler(commands=["si", "sysinfo", "system_info"])
def cmd_sysinfo(message):
    from universal_flags import parse_universal_flags, validate_command_flags, convert_flags_to_legacy
    
    def get_si_usage():
        """Get usage message for sysinfo commands."""
        return (
            "⚠️ Usage: `/si` or `/si:[flags]`\n\n"
            "📋 **Available Flags:**\n"
            "• `brief` - Show brief system information\n"
            "• `detailed` - Show detailed system information\n"
            "• `network` - Show network information\n"
            "• `storage` - Show storage information\n"
            "• `processes` - Show running processes\n\n"
            "📝 **Examples:**\n"
            "• `/si` - Default system info\n"
            "• `/si:[detailed]` - Detailed system information\n"
            "• `/si:[network,storage]` - Network and storage info only"
        )
    
    try:
        # Handle special case where flags are in the command itself
        command_text = message.text.strip()
        
        # Parse command and extract flags using universal parser
        query, flags_list, parse_errors = parse_universal_flags(command_text, "si")
        valid_flags, validation_errors = validate_command_flags(flags_list, "si")
        legacy_flags = convert_flags_to_legacy(valid_flags, "si")
        
        # Show any flag parsing errors
        all_errors = parse_errors + validation_errors
        if all_errors:
            error_msg = "⚠️ Flag parsing errors:\n" + "\n".join(f"• {err}" for err in all_errors)
            bot.reply_to(message, error_msg)
            # Continue processing with valid flags
        
        # For now, pass the detail level to the sysinfo module
        detail_level = legacy_flags.get('detail_level', 'normal')
        
        # Create a modified message object with detail level info
        if detail_level != 'normal':
            # For now, just call the normal sysinfo and add flag info
            sysinfo.handle_sysinfo_command(bot, message)
            if detail_level == 'brief':
                bot.send_message(message.chat.id, "ℹ️ Brief mode requested - showing condensed system info")
            elif detail_level == 'detailed':
                bot.send_message(message.chat.id, "ℹ️ Detailed mode requested - showing comprehensive system info")
            elif detail_level in ['cpu', 'memory', 'disk', 'network']:
                bot.send_message(message.chat.id, f"ℹ️ {detail_level.upper()}-only mode requested")
        else:
            sysinfo.handle_sysinfo_command(bot, message)
        
    except Exception as e:
        bot.reply_to(message, f"❌ System info failed: {e}")

# --- Downloader ---
@bot.message_handler(commands=["dl"])
def cmd_dl(message):
    from universal_flags import parse_universal_flags, validate_command_flags, convert_flags_to_legacy
    
    def get_dl_usage():
        """Get usage message for download commands."""
        return (
            "⚠️ Usage: `/dl <url>:[flags] [folder]`\n\n"
            "📋 **Available Flags:**\n"
            "• `force` - Force download even if file exists\n"
            "• `notify` - Send notification when download completes\n"
            "• `silent` - Disable notifications\n"
            "• `background` - Download in background\n\n"
            "📝 **Examples:**\n"
            "• `/dl https://example.com/file.mp4:[notify]` - Download with notification\n"
            "• `/dl https://example.com/file.mp4:[force,background]` - Force download in background\n"
            "• `/dl https://example.com/file.mp4` - Normal download (no flags)"
        )
    
    try:
        # Parse command and extract flags using universal parser
        query, flags_list, parse_errors = parse_universal_flags(message.text, "dl")
        valid_flags, validation_errors = validate_command_flags(flags_list, "dl")
        legacy_flags = convert_flags_to_legacy(valid_flags, "dl")
        
        # For download commands, the query contains "url folder", we need to extract them
        parts = query.strip().split()
        if not parts:
            bot.reply_to(message, get_dl_usage(), parse_mode="Markdown")
            return
        
        url = parts[0]
        folder = " ".join(parts[1:]).strip() if len(parts) > 1 else None
        
        # Show any flag parsing errors
        all_errors = parse_errors + validation_errors
        if all_errors:
            error_msg = "⚠️ Flag parsing errors:\n" + "\n".join(f"• {err}" for err in all_errors)
            bot.reply_to(message, error_msg)
            # Continue processing with valid flags
        
        # Auto-detect plugin
        u = url.lower()
        if "youtube.com" in u or "youtu.be" in u:
            # your youtube plugin should implement download(bot, message, url, folder)
            youtube.download(bot, message, url, folder)
        elif "facebook.com" in u or "fb.watch" in u:
            facebook.download(bot, message, url, folder)
        else:
            bot.reply_to(message, f"❌ No plugin available for this URL: {url}")

    except Exception as e:
        bot.reply_to(message, f"❌ Error: {e}")

# --- Downloads list (/d) with pagination ---
@bot.message_handler(commands=["d"])
def handle_downloads(message):
    downloads.show(bot, message)

@bot.callback_query_handler(func=lambda call: call.data.startswith("dlpage:"))
def handle_downloads_pagination(call):
    downloads.handle_page(bot, call)

# --- Fallback: echo links ---
@bot.message_handler(func=lambda m: m.text and ("http://" in m.text or "https://" in m.text))
def handle_links(message):
    url = message.text.strip()
    u = url.lower()
    if "youtube.com" in u or "youtu.be" in u:
        youtube.download(bot, message, url, None)
    elif "facebook.com" in u or "fb.watch" in u:
        facebook.download(bot, message, url, None)
    else:
        bot.reply_to(message, f"❌ No plugin available for this URL: {url}")

# --- Run bot ---
if __name__ == "__main__":
    print("🤖 Bot started...")
    bot.infinity_polling()
