"""Telegram bot adapter and notification service implementations."""

import asyncio
import logging
from typing import Any, Callable, Optional, List
from telegram import Update, Bot
from telegram.ext import Application, MessageHandler, filters, ContextTypes

from ..interfaces.telegram_bot import ITelegramBot, BotMessage, INotificationService
from ..interfaces.search_provider import SearchResult
from ..config.settings import TelegramConfig


class TelegramBotAdapter(ITelegramBot):
    """Telegram bot adapter implementation using python-telegram-bot."""
    
    def __init__(self, config: TelegramConfig):
        self._config = config
        self._bot = Bot(token=config.bot_token)
        self._application: Optional[Application] = None
        self._handlers: List[Callable] = []
        self._logger = logging.getLogger(__name__)
    
    async def send_message(self, message: BotMessage) -> bool:
        """Send a message."""
        try:
            await self._bot.send_message(
                chat_id=message.chat_id,
                text=message.text,
                reply_to_message_id=message.reply_to_message_id,
                parse_mode=message.parse_mode,
                reply_markup=message.reply_markup
            )
            return True
            
        except Exception as e:
            self._logger.error(f"Error sending message: {e}")
            return False
    
    async def edit_message(self, chat_id: int, message_id: int, text: str, reply_markup: Any = None) -> bool:
        """Edit an existing message."""
        try:
            await self._bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=text,
                reply_markup=reply_markup
            )
            return True
            
        except Exception as e:
            self._logger.error(f"Error editing message: {e}")
            return False
    
    async def delete_message(self, chat_id: int, message_id: int) -> bool:
        """Delete a message."""
        try:
            await self._bot.delete_message(chat_id=chat_id, message_id=message_id)
            return True
            
        except Exception as e:
            self._logger.error(f"Error deleting message: {e}")
            return False
    
    def add_handler(self, handler: Callable, filter_type: str = "message") -> None:
        """Add a message handler."""
        self._handlers.append(handler)
    
    async def start_polling(self) -> None:
        """Start bot polling."""
        try:
            # Create application
            self._application = Application.builder().token(self._config.bot_token).build()
            
            # Add handlers
            for handler_func in self._handlers:
                message_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, self._create_update_handler(handler_func))
                command_handler = MessageHandler(filters.COMMAND, self._create_update_handler(handler_func))
                
                self._application.add_handler(message_handler)
                self._application.add_handler(command_handler)
            
            self._logger.info("Starting Telegram bot polling...")
            
            # Start polling
            await self._application.initialize()
            await self._application.start()
            await self._application.updater.start_polling()
            
            # Keep running
            await self._application.updater.idle()
            
        except Exception as e:
            self._logger.error(f"Error in bot polling: {e}")
    
    async def stop_polling(self) -> None:
        """Stop bot polling."""
        try:
            if self._application:
                await self._application.updater.stop()
                await self._application.stop()
                await self._application.shutdown()
            
            self._logger.info("Telegram bot polling stopped")
            
        except Exception as e:
            self._logger.error(f"Error stopping bot: {e}")
    
    def _create_update_handler(self, handler_func: Callable):
        """Create an update handler wrapper."""
        async def update_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
            try:
                await handler_func(update)
            except Exception as e:
                self._logger.error(f"Error in update handler: {e}")
        
        return update_handler


class NotificationService(INotificationService):
    """Notification service implementation."""
    
    def __init__(self, bot: ITelegramBot):
        self._bot = bot
        self._logger = logging.getLogger(__name__)
    
    async def notify_download_started(self, torrent_name: str, chat_id: int) -> None:
        """Notify when download starts."""
        message = BotMessage(
            chat_id=chat_id,
            text=f"⬇️ **Download Started**\n\n📁 {torrent_name}",
            parse_mode="Markdown"
        )
        await self._bot.send_message(message)
    
    async def notify_download_completed(self, torrent_name: str, chat_id: int) -> None:
        """Notify when download completes."""
        message = BotMessage(
            chat_id=chat_id,
            text=f"✅ **Download Completed**\n\n📁 {torrent_name}",
            parse_mode="Markdown"
        )
        await self._bot.send_message(message)
    
    async def notify_download_failed(self, torrent_name: str, error: str, chat_id: int) -> None:
        """Notify when download fails."""
        message = BotMessage(
            chat_id=chat_id,
            text=f"❌ **Download Failed**\n\n📁 {torrent_name}\n🚨 Error: {error}",
            parse_mode="Markdown"
        )
        await self._bot.send_message(message)
    
    async def notify_search_results(self, results: List[SearchResult], chat_id: int) -> None:
        """Notify with search results."""
        if not results:
            message = BotMessage(
                chat_id=chat_id,
                text="❌ No search results found."
            )
            await self._bot.send_message(message)
            return
        
        # Format results
        results_text = f"🔍 **Search Results** ({len(results)} found)\n\n"
        
        for i, result in enumerate(results[:10], 1):
            size_mb = result.size / (1024 * 1024) if result.size > 0 else 0
            results_text += f"**{i}.** {result.title[:50]}{'...' if len(result.title) > 50 else ''}\n"
            results_text += f"📏 {size_mb:.1f} MB | 🌱 {result.seeders}S/{result.leechers}L\n"
            results_text += f"🏷️ {result.category} | 📅 {result.published_date}\n\n"
        
        if len(results) > 10:
            results_text += f"... and {len(results) - 10} more results.\n"
        
        message = BotMessage(
            chat_id=chat_id,
            text=results_text,
            parse_mode="Markdown"
        )
        await self._bot.send_message(message)
