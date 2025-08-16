"""
Busy indicator management for showing search progress to users.
"""

# Cache: user_id → message_id
busy_indicators = {}


class BusyIndicator:
    """Manages busy indicators for search operations."""
    
    @staticmethod
    def create(bot, message, search_type="normal"):
        """Create and send a busy indicator message."""
        if search_type == "rich":
            busy_text = (
                "🔍 Rich search in progress...\n"
                "📡 Querying all available indexers\n"
                "⏳ This may take a moment"
            )
        elif search_type == "all":
            busy_text = (
                "🔍 ALL search in progress...\n"
                "🌐 Querying EVERY indexer on Jackett\n"
                "⏳ This will take longer but be comprehensive"
            )
        elif search_type == "music":
            busy_text = (
                "🎵 Music search in progress...\n"
                "🎧 Querying popular music indexers\n"
                "⏳ Finding the best music torrents"
            )
        else:
            busy_text = (
                "🔍 Searching torrents...\n"
                "⏳ Please wait"
            )
        
        busy_msg = bot.send_message(message.chat.id, busy_text)
        busy_indicators[message.from_user.id] = busy_msg.message_id
        return busy_msg

    @staticmethod
    def update(bot, message, current_indexer=None, total_indexers=None, found_results=0):
        """Update the busy indicator with progress."""
        user_id = message.from_user.id
        if user_id not in busy_indicators:
            return
        
        if current_indexer and total_indexers:
            progress_text = (
                f"🔍 Comprehensive search in progress...\n"
                f"📡 Searching: {current_indexer}\n"
                f"📊 Progress: {total_indexers - len([f for f in range(total_indexers) if f < total_indexers])}/{total_indexers} indexers\n"
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

    @staticmethod
    def remove(bot, message):
        """Remove the busy indicator."""
        user_id = message.from_user.id
        if user_id in busy_indicators:
            try:
                bot.delete_message(message.chat.id, busy_indicators[user_id])
            except Exception:
                pass  # Ignore deletion failures
            del busy_indicators[user_id]
