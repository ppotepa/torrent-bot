"""
Main Telegram Bot Application
Uses reflection-based plugin system with automatic command discovery
"""

import os
import sys
import asyncio
import signal
import logging
from pathlib import Path

# Add src directory to path
src_path = Path(__file__).parent
sys.path.insert(0, str(src_path))

import telebot
from core import PluginRegistry

# Enhanced logging system
try:
    from enhanced_logging import get_logger
    logger = get_logger("torrent-bot")
except ImportError:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger("torrent-bot")

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
    logger.info("Loaded environment variables from .env file")
except ImportError:
    logger.warning("python-dotenv not installed, using system environment variables only")

class TelegramBot:
    """Main Telegram Bot class with reflection-based plugin system"""
    
    def __init__(self):
        """Initialize the bot and plugin system"""
        
        # Validate token
        self.token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
        if not self.token or ":" not in self.token:
            raise ValueError("Invalid TELEGRAM_BOT_TOKEN env var (must contain a colon).")
        
        # Create bot instance
        self.bot = telebot.TeleBot(self.token)
        logger.info("Telegram bot initialized")
        
        # Initialize plugin registry
        self.plugin_registry = PluginRegistry(
            bot=self.bot,
            plugins_directory=str(src_path / "plugins"),
            logger=logger
        )
        
        # Setup signal handlers for graceful shutdown
        self._setup_signal_handlers()
        
        # Bot state
        self.running = False
    
    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(sig, frame):
            logger.info('🛑 Shutdown signal received, stopping bot...')
            self.stop()
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def start(self):
        """Start the bot and all plugins"""
        try:
            logger.info("🚀 Starting Telegram Bot...")
            
            # Discover and register plugins
            logger.info("🔍 Discovering plugins...")
            self.plugin_registry.discover_plugins()
            
            # Get plugin info
            plugins_info = self.plugin_registry.get_plugin_info()
            logger.info(f"📦 Loaded {len(plugins_info)} plugins:")
            for name, info in plugins_info.items():
                logger.info(f"   • {name} v{info['version']} - {info['description']}")
            
            # Run startup tasks
            logger.info("⚡ Running plugin startup tasks...")
            await self.plugin_registry.run_startup_tasks()
            
            # Register Telegram handlers
            logger.info("📡 Registering Telegram handlers...")
            self.plugin_registry.register_telegram_handlers()
            
            # Register built-in commands
            self._register_builtin_commands()
            
            # Set plugin registry reference for help system
            help_plugin = self.plugin_registry.plugins.get("Help System")
            if help_plugin:
                help_plugin.set_plugin_registry(self.plugin_registry)
            
            # Start periodic tasks
            logger.info("⏰ Starting periodic tasks...")
            self.plugin_registry.start_periodic_tasks()
            
            # Log system info
            admin_users = self.plugin_registry.admin_users
            owner_users = self.plugin_registry.owner_users
            
            logger.info(f"👤 Admin users: {admin_users}")
            logger.info(f"👑 Owner users: {owner_users}")
            logger.info(f"📊 Commands registered: {len(self.plugin_registry.commands)}")
            
            self.running = True
            logger.info("✅ Bot started successfully - ready to receive commands")
            
            # Start polling
            self.bot.infinity_polling(
                timeout=10,
                long_polling_timeout=5,
                none_stop=True,
                interval=1
            )
            
        except Exception as e:
            logger.critical(f"Failed to start bot: {e}", exc_info=True)
            raise
    
    async def stop(self):
        """Stop the bot gracefully"""
        try:
            logger.info("🛑 Stopping bot...")
            self.running = False
            
            # Stop polling
            try:
                self.bot.stop_polling()
            except:
                pass
            
            # Run shutdown tasks
            logger.info("🔄 Running shutdown tasks...")
            await self.plugin_registry.run_shutdown_tasks()
            
            logger.info("✅ Bot stopped successfully")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
        finally:
            # Force exit
            import sys
            sys.exit(0)
    
    def _register_builtin_commands(self):
        """Register built-in bot commands"""
        
        @self.bot.message_handler(commands=['start', 'help'])
        def send_welcome(message):
            """Send welcome message with available commands"""
            try:
                help_text = self._generate_help_text()
                self.bot.reply_to(message, help_text, parse_mode="Markdown")
            except Exception as e:
                logger.error(f"Welcome command failed: {e}")
                self.bot.reply_to(message, "❌ Error generating help message")
        
        @self.bot.message_handler(commands=['plugins'])
        def show_plugins(message):
            """Show loaded plugins information"""
            try:
                # Check if user has permission
                user_id = message.from_user.id
                if (user_id not in self.plugin_registry.admin_users and 
                    user_id not in self.plugin_registry.owner_users):
                    self.bot.reply_to(message, "❌ You don't have permission to view plugins")
                    return
                
                plugins_text = self._generate_plugins_text()
                self.bot.send_message(message.chat.id, plugins_text, parse_mode="Markdown")
                
            except Exception as e:
                logger.error(f"Plugins command failed: {e}")
                self.bot.reply_to(message, f"❌ Error: {e}")
        
        @self.bot.message_handler(commands=['status'])
        def show_status(message):
            """Show bot status"""
            try:
                # Check if user has permission
                user_id = message.from_user.id
                if (user_id not in self.plugin_registry.admin_users and 
                    user_id not in self.plugin_registry.owner_users):
                    self.bot.reply_to(message, "❌ You don't have permission to view status")
                    return
                
                status_text = self._generate_status_text()
                self.bot.send_message(message.chat.id, status_text, parse_mode="Markdown")
                
            except Exception as e:
                logger.error(f"Status command failed: {e}")
                self.bot.reply_to(message, f"❌ Error: {e}")
        
        logger.info("✅ Built-in commands registered")
    
    def _generate_help_text(self) -> str:
        """Generate help text with all available commands"""
        help_text = "🤖 **Welcome to the Enhanced Telegram Bot!**\n\n"
        help_text += "This bot uses a modern reflection-based plugin system with automatic command discovery.\n\n"
        
        # Group commands by category
        categories = {}
        processed_commands = set()
        
        for cmd_name, cmd_data in self.plugin_registry.commands.items():
            # Skip aliases (only show main command)
            if cmd_data['name'] in processed_commands:
                continue
            
            category = cmd_data['category']
            if category not in categories:
                categories[category] = []
            
            categories[category].append(cmd_data)
            processed_commands.add(cmd_data['name'])
        
        # Add built-in commands
        if "System" not in categories:
            categories["System"] = []
        
        categories["System"].extend([
            {"name": "start", "description": "Show this help message"},
            {"name": "plugins", "description": "Show loaded plugins (admin only)"},
            {"name": "status", "description": "Show bot status (admin only)"}
        ])
        
        # Generate help for each category
        for category, commands in categories.items():
            help_text += f"**{category} Commands:**\n"
            
            for cmd in commands:
                help_text += f"• `/{cmd['name']}` - {cmd['description']}\n"
                
                # Add usage if available
                if cmd.get('usage'):
                    help_text += f"  Usage: `{cmd['usage']}`\n"
                
                # Add examples if available
                if cmd.get('examples') and len(cmd['examples']) > 0:
                    help_text += f"  Example: `{cmd['examples'][0]}`\n"
            
            help_text += "\n"
        
        help_text += "💡 **Tips:**\n"
        help_text += "• Use `/command` to see specific command help\n"
        help_text += "• Commands support various flags and options\n"
        help_text += "• Bot automatically detects and handles different content types\n\n"
        
        help_text += "🔧 **System Features:**\n"
        help_text += "• Reflection-based plugin architecture\n"
        help_text += "• Automatic command discovery\n"
        help_text += "• Permission-based access control\n"
        help_text += "• Rich error handling and logging\n"
        help_text += "• Hot-pluggable extensions"
        
        return help_text
    
    def _generate_plugins_text(self) -> str:
        """Generate plugins information text"""
        plugins_info = self.plugin_registry.get_plugin_info()
        
        plugins_text = f"📦 **Loaded Plugins ({len(plugins_info)})**\n\n"
        
        for name, info in plugins_info.items():
            plugins_text += f"**{name}** v{info['version']}\n"
            plugins_text += f"👤 Author: {info['author']}\n"
            plugins_text += f"📝 Description: {info['description']}\n"
            
            if info['dependencies']:
                deps_str = ', '.join(info['dependencies'])
                plugins_text += f"📚 Dependencies: {deps_str}\n"
            
            plugins_text += f"✅ Enabled: {'Yes' if info['enabled'] else 'No'}\n\n"
        
        # Add command statistics
        commands_count = len(self.plugin_registry.commands)
        callbacks_count = len(self.plugin_registry._callback_queries)
        handlers_count = len(self.plugin_registry._message_handlers)
        
        plugins_text += f"📊 **Statistics:**\n"
        plugins_text += f"• Commands: {commands_count}\n"
        plugins_text += f"• Callback handlers: {callbacks_count}\n"
        plugins_text += f"• Message handlers: {handlers_count}\n"
        plugins_text += f"• Startup tasks: {len(self.plugin_registry._startup_tasks)}\n"
        plugins_text += f"• Periodic tasks: {len(self.plugin_registry._periodic_tasks)}"
        
        return plugins_text
    
    def _generate_status_text(self) -> str:
        """Generate bot status text"""
        import psutil
        import platform
        from datetime import datetime
        
        status_text = "🤖 **Bot Status**\n\n"
        
        # Bot info
        status_text += f"**Bot State:** {'🟢 Running' if self.running else '🔴 Stopped'}\n"
        status_text += f"**Python:** {platform.python_version()}\n"
        status_text += f"**Platform:** {platform.system()} {platform.release()}\n\n"
        
        # System resources
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        
        status_text += f"**System Resources:**\n"
        status_text += f"• CPU: {cpu_percent:.1f}%\n"
        status_text += f"• Memory: {memory.percent:.1f}% ({memory.used // (1024**2)} MB used)\n\n"
        
        # Plugin statistics
        plugins_count = len(self.plugin_registry.get_plugin_info())
        commands_count = len(self.plugin_registry.commands)
        
        status_text += f"**Plugin System:**\n"
        status_text += f"• Plugins loaded: {plugins_count}\n"
        status_text += f"• Commands registered: {commands_count}\n"
        status_text += f"• Admin users: {len(self.plugin_registry.admin_users)}\n"
        status_text += f"• Owner users: {len(self.plugin_registry.owner_users)}\n\n"
        
        # Environment
        status_text += f"**Environment:**\n"
        status_text += f"• Working directory: {os.getcwd()}\n"
        status_text += f"• Plugins directory: {self.plugin_registry.plugins_directory}\n"
        
        return status_text


def main():
    """Main entry point"""
    try:
        # Create and start bot
        bot = TelegramBot()
        
        # Run the bot
        if sys.platform == "win32":
            # Windows doesn't support asyncio.run with signal handlers
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(bot.start())
            finally:
                loop.close()
        else:
            # Unix systems
            asyncio.run(bot.start())
            
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.critical(f"Bot crashed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
