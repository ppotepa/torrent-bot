import os
imp@bot.message_handler(commands=["start", "help"])
def send_welcome(message):
    text = (
        "👋 Welcome to the Media Bot!\n\n"
        "Available commands:\n"
        "• /dl <url> [folder] — download from YouTube or Facebook\n"
        "   (best audio by default; add "video" at the end to force video if your plugin supports it)\n"
        "• /t <query> — search torrents via Jackett (top 5 with buttons)\n"
        "• /d [filter] — list qBittorrent downloads (filters: active, completed, seeding, paused, errored)\n\n"
        "📌 You can also just paste a link and I'll detect the right plugin.\n\n"
        "🔄 Enhanced torrent fallback system:\n"
        "   • Tries magnet links first\n"
        "   • Falls back to .torrent files\n"
        "   • Reconstructs magnets from hash\n"
        "   • Searches alternative sources\n"
        "   • Visual quality indicators (🔥⭐✅⚠️🧲📁)"
    )
    bot.reply_to(message, text)
from telebot import types  # noqa

# import plugins
from plugins import youtube, facebook, torrent, downloads

# --- Token ---
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
if not TOKEN or ":" not in TOKEN:
    raise ValueError("Invalid TELEGRAM_BOT_TOKEN env var (must contain a colon).")
bot = telebot.TeleBot(TOKEN)

# --- Welcome & Help ---
@bot.message_handler(commands=["start", "help"])
def send_welcome(message):
    text = (
        "👋 Welcome to the Media Bot!\n\n"
        "Available commands:\n"
        "• /dl <url> [folder] — download from YouTube or Facebook\n"
        "   (best audio by default; add “video” at the end to force video if your plugin supports it)\n"
        "• /t <query> — search torrents via Jackett (top 5 with buttons)\n"
        "• /d [filter] — list qBittorrent downloads (filters: active, completed, seeding, paused, errored)\n\n"
        "📌 You can also just paste a link and I’ll detect the right plugin."
    )
    bot.reply_to(message, text)

# --- Torrent search (/t and /torrents) ---
@bot.message_handler(commands=["t", "torrent", "torrents"])
def cmd_torrent(message):
    parts = message.text.split(maxsplit=1)
    query = parts[1] if len(parts) > 1 else None
    if not query:
        bot.reply_to(message, "⚠️ Usage: /t <search query>")
        return
    # no folder support in this shorthand; pass None
    torrent.start_search(bot, message, folder=None, query=query)

@bot.callback_query_handler(func=lambda call: call.data.startswith("torrent_"))
def callback_torrent(call):
    torrent.handle_selection(bot, call)

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
