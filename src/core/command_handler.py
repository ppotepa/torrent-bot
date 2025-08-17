"""Command handler service for processing Telegram commands."""

import logging
import re
from typing import List, Optional, Any, Dict
from dataclasses import dataclass

from ..interfaces.telegram_bot import ITelegramBot, BotMessage
from ..core.torrent_service import TorrentService, DownloadRequest
from ..config.settings import AppConfig


@dataclass
class CommandContext:
    """Context for command execution."""
    chat_id: int
    user_id: int
    message_id: int
    text: str
    args: List[str]


class CommandHandlerService:
    """Service for handling Telegram bot commands."""
    
    def __init__(
        self,
        bot: ITelegramBot,
        torrent_service: TorrentService,
        config: AppConfig
    ):
        self._bot = bot
        self._torrent_service = torrent_service
        self._config = config
        self._logger = logging.getLogger(__name__)
        
        # Register command handlers
        self._commands = {
            "/start": self._handle_start,
            "/help": self._handle_help,
            "/search": self._handle_search,
            "/download": self._handle_download,
            "/status": self._handle_status,
            "/list": self._handle_list,
            "/pause": self._handle_pause,
            "/resume": self._handle_resume,
            "/delete": self._handle_delete,
        }
    
    def is_authorized(self, user_id: int) -> bool:
        """Check if user is authorized to use the bot."""
        return user_id in self._config.telegram.allowed_users
    
    async def handle_command(self, context: CommandContext) -> None:
        """Handle incoming command."""
        if not self.is_authorized(context.user_id):
            await self._send_unauthorized_message(context.chat_id)
            return
        
        command = context.args[0] if context.args else ""
        handler = self._commands.get(command)
        
        if handler:
            try:
                await handler(context)
            except Exception as e:
                self._logger.error(f"Error handling command {command}: {e}")
                await self._send_error_message(context.chat_id, f"Error processing command: {e}")
        else:
            await self._handle_unknown_command(context)
    
    async def _handle_start(self, context: CommandContext) -> None:
        """Handle /start command."""
        message = BotMessage(
            chat_id=context.chat_id,
            text="🤖 Welcome to Torrent Bot!\n\nUse /help to see available commands."
        )
        await self._bot.send_message(message)
    
    async def _handle_help(self, context: CommandContext) -> None:
        """Handle /help command."""
        help_text = """
🤖 **Torrent Bot Commands**

🔍 **Search & Download:**
• `/search <query>` - Search for torrents
• `/download <magnet_link> [category]` - Download torrent

📊 **Status & Management:**
• `/status` - Show bot status
• `/list` - List active downloads
• `/pause <hash>` - Pause torrent
• `/resume <hash>` - Resume torrent
• `/delete <hash> [delete_files]` - Delete torrent

**Categories:** movies, tv, music, games, software, books, anime

**Examples:**
• `/search Inception 2010`
• `/download magnet:?xt=... movies`
• `/pause abc123def456`
• `/delete abc123def456 true`
        """
        
        message = BotMessage(
            chat_id=context.chat_id,
            text=help_text,
            parse_mode="Markdown"
        )
        await self._bot.send_message(message)
    
    async def _handle_search(self, context: CommandContext) -> None:
        """Handle /search command."""
        if len(context.args) < 2:
            message = BotMessage(
                chat_id=context.chat_id,
                text="❌ Usage: `/search <query>`",
                parse_mode="Markdown"
            )
            await self._bot.send_message(message)
            return
        
        query = " ".join(context.args[1:])
        
        # Send searching message
        searching_message = BotMessage(
            chat_id=context.chat_id,
            text=f"🔍 Searching for: `{query}`...",
            parse_mode="Markdown"
        )
        await self._bot.send_message(searching_message)
        
        # Perform search
        results = await self._torrent_service.search_torrents(query)
        
        if not results:
            message = BotMessage(
                chat_id=context.chat_id,
                text="❌ No torrents found."
            )
            await self._bot.send_message(message)
            return
        
        # Format results (show top 10)
        results_text = f"🔍 **Search Results for:** `{query}`\n\n"
        
        for i, result in enumerate(results[:10], 1):
            size_mb = result.size / (1024 * 1024)
            results_text += f"**{i}.** {result.title}\n"
            results_text += f"📏 Size: {size_mb:.1f} MB\n"
            results_text += f"🌱 Seeds: {result.seeders} | 📥 Peers: {result.leechers}\n"
            results_text += f"🏷️ Category: {result.category}\n"
            results_text += f"🔗 `/download_magnet_{i}`\n\n"
        
        if len(results) > 10:
            results_text += f"... and {len(results) - 10} more results.\n"
        
        message = BotMessage(
            chat_id=context.chat_id,
            text=results_text,
            parse_mode="Markdown"
        )
        await self._bot.send_message(message)
        
        # Store search results for quick download (this would need a temporary storage)
        # For now, we'll just show the magnet links in a simplified way
    
    async def _handle_download(self, context: CommandContext) -> None:
        """Handle /download command."""
        if len(context.args) < 2:
            message = BotMessage(
                chat_id=context.chat_id,
                text="❌ Usage: `/download <magnet_link> [category]`",
                parse_mode="Markdown"
            )
            await self._bot.send_message(message)
            return
        
        magnet_link = context.args[1]
        category = context.args[2] if len(context.args) > 2 else ""
        
        # Validate magnet link
        if not magnet_link.startswith("magnet:"):
            message = BotMessage(
                chat_id=context.chat_id,
                text="❌ Invalid magnet link. Must start with `magnet:`",
                parse_mode="Markdown"
            )
            await self._bot.send_message(message)
            return
        
        # Send downloading message
        downloading_message = BotMessage(
            chat_id=context.chat_id,
            text=f"⬇️ Adding torrent to downloads...",
        )
        await self._bot.send_message(downloading_message)
        
        # Create download request
        request = DownloadRequest(
            magnet_link=magnet_link,
            category=category,
            chat_id=context.chat_id
        )
        
        # Download torrent
        result = await self._torrent_service.download_torrent(request)
        
        if result.success:
            message = BotMessage(
                chat_id=context.chat_id,
                text=f"✅ Torrent added successfully!\n🏷️ Category: {category or 'default'}",
            )
        else:
            message = BotMessage(
                chat_id=context.chat_id,
                text=f"❌ Failed to add torrent: {result.message}",
            )
        
        await self._bot.send_message(message)
    
    async def _handle_status(self, context: CommandContext) -> None:
        """Handle /status command."""
        active_downloads = await self._torrent_service.get_active_downloads()
        
        status_text = "📊 **Bot Status**\n\n"
        status_text += f"🔄 Active Downloads: {len(active_downloads)}\n"
        status_text += f"💾 Download Path: `{self._config.download.default_path}`\n"
        status_text += f"🔍 Search Provider: {self._config.search.fallback_providers[0] if self._config.search.fallback_providers else 'None'}\n"
        
        message = BotMessage(
            chat_id=context.chat_id,
            text=status_text,
            parse_mode="Markdown"
        )
        await self._bot.send_message(message)
    
    async def _handle_list(self, context: CommandContext) -> None:
        """Handle /list command."""
        active_downloads = await self._torrent_service.get_active_downloads()
        
        if not active_downloads:
            message = BotMessage(
                chat_id=context.chat_id,
                text="📭 No active downloads."
            )
            await self._bot.send_message(message)
            return
        
        list_text = "📥 **Active Downloads:**\n\n"
        
        for torrent in active_downloads:
            progress_bar = self._create_progress_bar(torrent.progress)
            list_text += f"**{torrent.name[:30]}{'...' if len(torrent.name) > 30 else ''}**\n"
            list_text += f"{progress_bar} {torrent.progress:.1f}%\n"
            list_text += f"📊 Status: {torrent.status}\n"
            list_text += f"⬇️ {self._format_speed(torrent.download_speed)} | ⬆️ {self._format_speed(torrent.upload_speed)}\n"
            list_text += f"🔑 Hash: `{torrent.hash[:8]}...`\n\n"
        
        message = BotMessage(
            chat_id=context.chat_id,
            text=list_text,
            parse_mode="Markdown"
        )
        await self._bot.send_message(message)
    
    async def _handle_pause(self, context: CommandContext) -> None:
        """Handle /pause command."""
        if len(context.args) < 2:
            message = BotMessage(
                chat_id=context.chat_id,
                text="❌ Usage: `/pause <torrent_hash>`",
                parse_mode="Markdown"
            )
            await self._bot.send_message(message)
            return
        
        torrent_hash = context.args[1]
        success = await self._torrent_service.pause_torrent(torrent_hash, context.chat_id)
        
        if success:
            message = BotMessage(
                chat_id=context.chat_id,
                text=f"⏸️ Torrent paused: `{torrent_hash[:8]}...`",
                parse_mode="Markdown"
            )
        else:
            message = BotMessage(
                chat_id=context.chat_id,
                text=f"❌ Failed to pause torrent: `{torrent_hash[:8]}...`",
                parse_mode="Markdown"
            )
        
        await self._bot.send_message(message)
    
    async def _handle_resume(self, context: CommandContext) -> None:
        """Handle /resume command."""
        if len(context.args) < 2:
            message = BotMessage(
                chat_id=context.chat_id,
                text="❌ Usage: `/resume <torrent_hash>`",
                parse_mode="Markdown"
            )
            await self._bot.send_message(message)
            return
        
        torrent_hash = context.args[1]
        success = await self._torrent_service.resume_torrent(torrent_hash, context.chat_id)
        
        if success:
            message = BotMessage(
                chat_id=context.chat_id,
                text=f"▶️ Torrent resumed: `{torrent_hash[:8]}...`",
                parse_mode="Markdown"
            )
        else:
            message = BotMessage(
                chat_id=context.chat_id,
                text=f"❌ Failed to resume torrent: `{torrent_hash[:8]}...`",
                parse_mode="Markdown"
            )
        
        await self._bot.send_message(message)
    
    async def _handle_delete(self, context: CommandContext) -> None:
        """Handle /delete command."""
        if len(context.args) < 2:
            message = BotMessage(
                chat_id=context.chat_id,
                text="❌ Usage: `/delete <torrent_hash> [true/false]`",
                parse_mode="Markdown"
            )
            await self._bot.send_message(message)
            return
        
        torrent_hash = context.args[1]
        delete_files = len(context.args) > 2 and context.args[2].lower() == "true"
        
        success = await self._torrent_service.delete_torrent(torrent_hash, delete_files, context.chat_id)
        
        if success:
            files_text = "and files" if delete_files else "only"
            message = BotMessage(
                chat_id=context.chat_id,
                text=f"🗑️ Torrent deleted ({files_text}): `{torrent_hash[:8]}...`",
                parse_mode="Markdown"
            )
        else:
            message = BotMessage(
                chat_id=context.chat_id,
                text=f"❌ Failed to delete torrent: `{torrent_hash[:8]}...`",
                parse_mode="Markdown"
            )
        
        await self._bot.send_message(message)
    
    async def _handle_unknown_command(self, context: CommandContext) -> None:
        """Handle unknown commands."""
        message = BotMessage(
            chat_id=context.chat_id,
            text="❓ Unknown command. Use /help to see available commands."
        )
        await self._bot.send_message(message)
    
    async def _send_unauthorized_message(self, chat_id: int) -> None:
        """Send unauthorized access message."""
        message = BotMessage(
            chat_id=chat_id,
            text="🚫 Unauthorized access. Contact the administrator."
        )
        await self._bot.send_message(message)
    
    async def _send_error_message(self, chat_id: int, error: str) -> None:
        """Send error message."""
        message = BotMessage(
            chat_id=chat_id,
            text=f"❌ Error: {error}"
        )
        await self._bot.send_message(message)
    
    def _create_progress_bar(self, progress: float, length: int = 10) -> str:
        """Create a text progress bar."""
        filled = int(progress / 100 * length)
        bar = "█" * filled + "░" * (length - filled)
        return f"[{bar}]"
    
    def _format_speed(self, speed_bytes: int) -> str:
        """Format speed in human readable format."""
        if speed_bytes < 1024:
            return f"{speed_bytes} B/s"
        elif speed_bytes < 1024 * 1024:
            return f"{speed_bytes / 1024:.1f} KB/s"
        else:
            return f"{speed_bytes / (1024 * 1024):.1f} MB/s"
