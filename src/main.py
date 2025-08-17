"""Main application entry point following SOLID principles with dependency injection."""

import asyncio
import logging
import os
import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent))

from src.config.settings import AppConfig
from src.core.torrent_service import TorrentService
from src.core.command_handler import CommandHandlerService
from src.integrations.qbittorrent_client import QBittorrentClient
from src.integrations.jackett_client import JackettSearchProvider
from src.utils.telegram_bot import TelegramBotAdapter, NotificationService


class Application:
    """Main application class following Dependency Inversion Principle."""
    
    def __init__(self, config: AppConfig):
        self._config = config
        self._logger = self._setup_logging()
        
        # Initialize dependencies following dependency injection pattern
        self._torrent_client = QBittorrentClient(config.qbittorrent)
        self._search_provider = JackettSearchProvider(config.jackett)
        self._telegram_bot = TelegramBotAdapter(config.telegram)
        self._notification_service = NotificationService(self._telegram_bot)
        
        # Initialize services
        self._torrent_service = TorrentService(
            torrent_client=self._torrent_client,
            search_provider=self._search_provider,
            notification_service=self._notification_service,
            config=config
        )
        
        self._command_handler = CommandHandlerService(
            bot=self._telegram_bot,
            torrent_service=self._torrent_service,
            config=config
        )
    
    def _setup_logging(self) -> logging.Logger:
        """Setup application logging."""
        logging.basicConfig(
            level=getattr(logging, self._config.log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler('torrent_bot.log')
            ]
        )
        
        # Set specific log levels for external libraries
        logging.getLogger('aiohttp').setLevel(logging.WARNING)
        logging.getLogger('urllib3').setLevel(logging.WARNING)
        
        return logging.getLogger(__name__)
    
    async def start(self) -> None:
        """Start the application."""
        try:
            self._logger.info("Starting Torrent Bot Application...")
            
            # Validate configuration
            errors = self._config.validate()
            if errors:
                self._logger.error(f"Configuration errors: {errors}")
                return
            
            # Test connections
            self._logger.info("Testing connections...")
            
            # Test qBittorrent connection
            if not await self._torrent_client.connect():
                self._logger.error("Failed to connect to qBittorrent")
                return
            else:
                self._logger.info("✅ qBittorrent connection successful")
            
            # Test Jackett connection
            if not await self._search_provider.is_available():
                self._logger.warning("⚠️ Jackett connection failed - search functionality may be limited")
            else:
                self._logger.info("✅ Jackett connection successful")
            
            # Setup Telegram bot handlers
            self._setup_telegram_handlers()
            
            # Start background tasks
            tasks = []
            
            # Start download monitoring
            monitor_task = asyncio.create_task(
                self._torrent_service.monitor_downloads(),
                name="download_monitor"
            )
            tasks.append(monitor_task)
            
            # Start Telegram bot
            bot_task = asyncio.create_task(
                self._telegram_bot.start_polling(),
                name="telegram_bot"
            )
            tasks.append(bot_task)
            
            self._logger.info("🚀 Torrent Bot is running!")
            self._logger.info(f"📁 Download path: {self._config.download.default_path}")
            self._logger.info(f"👥 Authorized users: {len(self._config.telegram.allowed_users)}")
            
            # Wait for all tasks to complete
            await asyncio.gather(*tasks, return_exceptions=True)
            
        except KeyboardInterrupt:
            self._logger.info("Received interrupt signal, shutting down...")
        except Exception as e:
            self._logger.error(f"Application error: {e}")
        finally:
            await self.shutdown()
    
    def _setup_telegram_handlers(self) -> None:
        """Setup Telegram bot message handlers."""
        async def message_handler(update):
            """Handle incoming messages."""
            try:
                if update.message and update.message.text:
                    # Parse command and arguments
                    text = update.message.text.strip()
                    args = text.split()
                    
                    # Create command context
                    from src.core.command_handler import CommandContext
                    context = CommandContext(
                        chat_id=update.message.chat_id,
                        user_id=update.message.from_user.id,
                        message_id=update.message.message_id,
                        text=text,
                        args=args
                    )
                    
                    # Handle the command
                    await self._command_handler.handle_command(context)
                    
            except Exception as e:
                self._logger.error(f"Error handling message: {e}")
        
        # Add message handler to bot
        self._telegram_bot.add_handler(message_handler, "message")
    
    async def shutdown(self) -> None:
        """Gracefully shutdown the application."""
        self._logger.info("Shutting down application...")
        
        try:
            # Stop Telegram bot
            await self._telegram_bot.stop_polling()
            
            # Disconnect from qBittorrent
            await self._torrent_client.disconnect()
            
            # Close search provider
            await self._search_provider.close()
            
            self._logger.info("Application shutdown complete")
            
        except Exception as e:
            self._logger.error(f"Error during shutdown: {e}")


async def main():
    """Main entry point."""
    try:
        # Load configuration from environment
        config = AppConfig.from_env()
        
        # Create and start application
        app = Application(config)
        await app.start()
        
    except Exception as e:
        logging.error(f"Failed to start application: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Set event loop policy for Windows
    if sys.platform.startswith('win'):
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    # Run the application
    asyncio.run(main())
