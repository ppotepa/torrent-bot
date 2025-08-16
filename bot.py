import os
import telebot
from telebot import types  # noqa

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
        "• /dl <url> [folder] — download from YouTube or Facebook\n"
        "   (best audio by default; add \"video\" at the end to force video if your plugin supports it)\n"
        "• /t <query> [rich|all|music] — search torrents via Jackett\n"
        "   ◦ normal: Fast search across popular indexers (top 5 results)\n"
        "   ◦ rich: Comprehensive search across all configured indexers (top 15)\n"
        "   ◦ all: Exhaustive search across EVERY indexer on Jackett (top 25)\n"
        "   ◦ music: Focused search across popular music indexers (top 12)\n"
        "• /tdiag — run torrent indexer diagnostics\n"
        "• /qdiag — diagnose qBittorrent connection and settings\n"
        "• /monitor — check download completion monitor status\n"
        "• /monitor_check — force check for completed downloads\n"
        "• /d [filter] — list qBittorrent downloads (filters: active, completed, seeding, paused, errored)\n"
        "• /si — display comprehensive system information\n\n"
        "📌 You can also just paste a link and I'll detect the right plugin.\n\n"
        "🔄 Enhanced torrent fallback system:\n"
        "   • Tries magnet links first\n"
        "   • Falls back to .torrent files\n"
        "   • Reconstructs magnets from hash\n"
        "   • Searches alternative sources\n"
        "   • Visual quality indicators (🔥⭐✅⚠️🧲📁)\n"
        "   • Rich mode: /t <query> rich for comprehensive search\n"
        "   • Music mode: /t <query> music for music-focused results\n"
    )
    bot.reply_to(message, text)

# --- Torrent search (/t and /torrents) ---
@bot.message_handler(commands=["t", "torrent", "torrents"])
def cmd_torrent(message):
    parts = message.text.split()
    if len(parts) < 2:
        bot.reply_to(message, "⚠️ Usage: /t <search query> [rich|all|music]\n\n• rich: Comprehensive search across configured indexers\n• all: Exhaustive search across ALL indexers on Jackett\n🎵 music: Focused search across popular music indexers")
        return
    
    # Check for search mode flags
    rich_mode = False
    all_mode = False
    music_mode = False
    query_parts = parts[1:]
    
    if query_parts and query_parts[-1].lower() == "rich":
        rich_mode = True
        query_parts = query_parts[:-1]  # Remove "rich" from query
    elif query_parts and query_parts[-1].lower() == "all":
        all_mode = True
        query_parts = query_parts[:-1]  # Remove "all" from query
    elif query_parts and query_parts[-1].lower() == "music":
        music_mode = True
        query_parts = query_parts[:-1]  # Remove "music" from query
    
    query = " ".join(query_parts)
    if not query.strip():
        bot.reply_to(message, "⚠️ Usage: /t <search query> [rich|all|music]\n\n• rich: Comprehensive search across configured indexers\n• all: Exhaustive search across ALL indexers on Jackett\n🎵 music: Focused search across popular music indexers")
        return
    
    # no folder support in this shorthand; pass None
    torrent.start_search(bot, message, folder=None, query=query, rich_mode=rich_mode, all_mode=all_mode, music_mode=music_mode)

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
    try:
        monitor = get_download_monitor()
        status = monitor.get_monitor_status()
        bot.send_message(message.chat.id, f"```\n{status}\n```", parse_mode="Markdown")
    except Exception as e:
        bot.reply_to(message, f"❌ Monitor status error: {e}")

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
    try:
        sysinfo.handle_sysinfo_command(bot, message)
    except Exception as e:
        bot.reply_to(message, f"❌ System info failed: {e}")

# --- Downloader ---
@bot.message_handler(commands=["dl"])
def cmd_dl(message):
    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "⚠️ Usage: /dl <url> [folder]")
            return

        url = parts[1].strip()
        folder = " ".join(parts[2:]).strip() if len(parts) > 2 else None

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
