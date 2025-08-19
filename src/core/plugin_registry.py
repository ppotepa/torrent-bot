"""
Plugin Registry - Automatic plugin discovery and registration system
Uses reflection to find and register all plugins with their commands
"""

import os
import sys
import importlib
import inspect
import logging
import asyncio
import threading
import time
from typing import Dict, List, Any, Optional, Type, Callable
from pathlib import Path

from .plugin_base import PluginBase
from .attributes import CommandScope, PermissionLevel


class PluginRegistry:
    """
    Central registry for managing all bot plugins.
    Automatically discovers and registers plugins using reflection.
    """
    
    def __init__(self, bot, plugins_directory: str = "src/plugins", logger: Optional[logging.Logger] = None):
        """
        Initialize plugin registry
        
        Args:
            bot: Telegram bot instance
            plugins_directory: Directory containing plugin modules
            logger: Logger instance
        """
        self.bot = bot
        self.plugins_directory = Path(plugins_directory)
        self.logger = logger or logging.getLogger(__name__)
        
        self._plugins: Dict[str, PluginBase] = {}
        self._commands: Dict[str, Dict[str, Any]] = {}
        self._callback_queries: List[Dict[str, Any]] = []
        self._message_handlers: List[Dict[str, Any]] = []
        self._startup_tasks: List[Dict[str, Any]] = []
        self._shutdown_tasks: List[Dict[str, Any]] = []
        self._periodic_tasks: List[Dict[str, Any]] = []
        self._periodic_task_threads: List[threading.Thread] = []
        
        # Admin and owner user IDs (loaded from environment)
        self.admin_users = self._load_admin_users()
        self.owner_users = self._load_owner_users()
    
    def _load_admin_users(self) -> List[int]:
        """Load admin user IDs from environment"""
        admin_ids = os.getenv("ADMIN_USER_IDS", "").strip()
        if not admin_ids:
            admin_id = os.getenv("ADMIN_USER_ID", "").strip()
            admin_ids = admin_id
        
        if admin_ids:
            try:
                return [int(uid.strip()) for uid in admin_ids.split(",") if uid.strip()]
            except ValueError as e:
                self.logger.error(f"Invalid admin user IDs: {e}")
        
        return []
    
    def _load_owner_users(self) -> List[int]:
        """Load owner user IDs from environment"""
        owner_ids = os.getenv("OWNER_USER_IDS", "").strip()
        if not owner_ids:
            owner_id = os.getenv("OWNER_USER_ID", "").strip()
            owner_ids = owner_id
        
        if owner_ids:
            try:
                return [int(uid.strip()) for uid in owner_ids.split(",") if uid.strip()]
            except ValueError as e:
                self.logger.error(f"Invalid owner user IDs: {e}")
        
        return []
    
    def discover_plugins(self):
        """
        Automatically discover all plugins in the plugins directory
        """
        self.logger.info(f"Discovering plugins in {self.plugins_directory}")
        
        if not self.plugins_directory.exists():
            self.logger.warning(f"Plugins directory does not exist: {self.plugins_directory}")
            return
        
        # Add plugins directory to Python path
        plugins_parent = str(self.plugins_directory.parent.absolute())
        if plugins_parent not in sys.path:
            sys.path.insert(0, plugins_parent)
        
        # Find all Python files in plugins directory
        plugin_files = []
        for root, dirs, files in os.walk(self.plugins_directory):
            # Skip __pycache__ and other hidden directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
            
            for file in files:
                if file.endswith('.py') and not file.startswith('_'):
                    plugin_files.append(Path(root) / file)
        
        # Import and register each plugin
        for plugin_file in plugin_files:
            try:
                self._import_and_register_plugin(plugin_file)
            except Exception as e:
                self.logger.error(f"Failed to load plugin {plugin_file}: {e}")
    
    def _import_and_register_plugin(self, plugin_file: Path):
        """
        Import a plugin file and register any plugin classes found
        
        Args:
            plugin_file: Path to the plugin Python file
        """
        # Convert file path to module name
        relative_path = plugin_file.relative_to(self.plugins_directory.parent)
        module_name = str(relative_path.with_suffix('')).replace(os.sep, '.')
        
        self.logger.debug(f"Importing plugin module: {module_name}")
        
        try:
            # Import the module
            module = importlib.import_module(module_name)
            
            # Find all classes that inherit from PluginBase
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if (issubclass(obj, PluginBase) and 
                    obj != PluginBase and 
                    obj.__module__ == module_name):
                    
                    self.logger.info(f"Found plugin class: {name}")
                    self._register_plugin_class(obj)
                    
        except Exception as e:
            self.logger.error(f"Error importing plugin {module_name}: {e}")
            raise
    
    def _register_plugin_class(self, plugin_class: Type[PluginBase]):
        """
        Register a plugin class
        
        Args:
            plugin_class: Plugin class to register
        """
        try:
            # Check if plugin is enabled
            plugin_metadata = plugin_class._plugin_name if hasattr(plugin_class, '_plugin_name') else plugin_class.__name__
            
            # Validate dependencies
            temp_plugin = plugin_class(self.bot, self.logger)
            missing_deps = temp_plugin.validate_dependencies()
            
            if missing_deps:
                self.logger.warning(f"Plugin {plugin_metadata} has missing dependencies: {missing_deps}")
                return
            
            if not temp_plugin.is_enabled():
                self.logger.info(f"Plugin {plugin_metadata} is disabled, skipping")
                return
            
            # Create plugin instance
            plugin_instance = plugin_class(self.bot, self.logger)
            plugin_name = plugin_instance.plugin_info['name']
            
            # Store plugin instance
            self._plugins[plugin_name] = plugin_instance
            
            # Register all commands from this plugin
            for cmd_name, cmd_data in plugin_instance.commands.items():
                if cmd_name in self._commands:
                    self.logger.warning(f"Command /{cmd_name} already registered, skipping")
                    continue
                
                self._commands[cmd_name] = {
                    **cmd_data,
                    'plugin': plugin_name,
                    'plugin_instance': plugin_instance
                }
                
                self.logger.info(f"Registered command: /{cmd_name} from {plugin_name}")
            
            # Register callback queries
            for callback_data in plugin_instance.callback_queries:
                self._callback_queries.append({
                    **callback_data,
                    'plugin': plugin_name,
                    'plugin_instance': plugin_instance
                })
            
            # Register message handlers
            for handler_data in plugin_instance.message_handlers:
                self._message_handlers.append({
                    **handler_data,
                    'plugin': plugin_name,
                    'plugin_instance': plugin_instance
                })
            
            # Register tasks
            for task_data in plugin_instance.startup_tasks:
                self._startup_tasks.append({
                    **task_data,
                    'plugin': plugin_name,
                    'plugin_instance': plugin_instance
                })
            
            for task_data in plugin_instance.shutdown_tasks:
                self._shutdown_tasks.append({
                    **task_data,
                    'plugin': plugin_name,
                    'plugin_instance': plugin_instance
                })
            
            for task_data in plugin_instance.periodic_tasks:
                self._periodic_tasks.append({
                    **task_data,
                    'plugin': plugin_name,
                    'plugin_instance': plugin_instance
                })
            
            self.logger.info(f"Successfully registered plugin: {plugin_name}")
            
        except Exception as e:
            self.logger.error(f"Error registering plugin {plugin_class.__name__}: {e}")
            raise
    
    def register_telegram_handlers(self):
        """
        Register all discovered commands and handlers with the Telegram bot
        """
        self.logger.info("Registering Telegram handlers")
        
        # Register command handlers
        for cmd_name, cmd_data in self._commands.items():
            # Skip aliases (already handled by main command)
            if cmd_name != cmd_data['name']:
                continue
            
            # Create list of all command variations (name + aliases)
            command_list = [cmd_data['name']] + cmd_data['aliases']
            
            # Create handler function with permission and scope checking
            def create_command_handler(cmd_info):
                def handler(message):
                    try:
                        # Check permissions
                        if not self._check_permissions(message, cmd_info['permission']):
                            self.bot.reply_to(message, "❌ You don't have permission to use this command.")
                            return
                        
                        # Check scope
                        if not self._check_scope(message, cmd_info['scope']):
                            scope_name = cmd_info['scope'].value
                            self.bot.reply_to(message, f"❌ This command can only be used in {scope_name} chats.")
                            return
                        
                        # Call the actual handler
                        cmd_info['handler'](message)
                        
                    except Exception as e:
                        self.logger.error(f"Error in command /{cmd_info['name']}: {e}")
                        self.bot.reply_to(message, f"❌ An error occurred: {e}")
                
                return handler
            
            # Register with telebot
            handler_func = create_command_handler(cmd_data)
            self.bot.message_handler(commands=command_list)(handler_func)
            
            self.logger.debug(f"Registered Telegram handler for: {command_list}")
        
        # Register callback query handlers
        for callback_data in self._callback_queries:
            def create_callback_handler(cb_info):
                def handler(call):
                    try:
                        cb_info['handler'](call)
                    except Exception as e:
                        self.logger.error(f"Error in callback query {cb_info['pattern']}: {e}")
                
                return handler
            
            handler_func = create_callback_handler(callback_data)
            self.bot.callback_query_handler(func=lambda call, pattern=callback_data['pattern']: 
                                          call.data and pattern in call.data)(handler_func)
        
        # Register message handlers
        for handler_data in self._message_handlers:
            def create_message_handler(handler_info):
                def handler(message):
                    try:
                        handler_info['handler'](message)
                    except Exception as e:
                        self.logger.error(f"Error in message handler: {e}")
                
                return handler
            
            handler_func = create_message_handler(handler_data)
            
            # Build handler arguments
            kwargs = {
                'content_types': handler_data['content_types']
            }
            
            if handler_data['regexp']:
                kwargs['regexp'] = handler_data['regexp']
            
            if handler_data['func_filter']:
                kwargs['func'] = handler_data['func_filter']
            
            self.bot.message_handler(**kwargs)(handler_func)
    
    def _check_permissions(self, message, required_permission: PermissionLevel) -> bool:
        """Check if user has required permissions"""
        user_id = message.from_user.id
        
        if required_permission == PermissionLevel.USER:
            return True
        elif required_permission == PermissionLevel.ADMIN:
            return user_id in self.admin_users or user_id in self.owner_users
        elif required_permission == PermissionLevel.OWNER:
            return user_id in self.owner_users
        
        return False
    
    def _check_scope(self, message, required_scope: CommandScope) -> bool:
        """Check if command is being used in correct scope"""
        if required_scope == CommandScope.ALL:
            return True
        
        chat_type = message.chat.type
        
        if required_scope == CommandScope.PRIVATE and chat_type == 'private':
            return True
        elif required_scope == CommandScope.GROUP and chat_type == 'group':
            return True
        elif required_scope == CommandScope.SUPERGROUP and chat_type == 'supergroup':
            return True
        elif required_scope == CommandScope.CHANNEL and chat_type == 'channel':
            return True
        
        return False
    
    async def run_startup_tasks(self):
        """Run all startup tasks from all plugins"""
        # Sort by priority
        self._startup_tasks.sort(key=lambda x: x['priority'])
        
        self.logger.info(f"Running {len(self._startup_tasks)} startup tasks")
        
        for task in self._startup_tasks:
            try:
                plugin_instance = task['plugin_instance']
                await plugin_instance._run_task_safely(task['handler'])
            except Exception as e:
                self.logger.error(f"Startup task from {task['plugin']} failed: {e}")
    
    async def run_shutdown_tasks(self):
        """Run all shutdown tasks from all plugins"""
        # Sort by priority
        self._shutdown_tasks.sort(key=lambda x: x['priority'])
        
        self.logger.info(f"Running {len(self._shutdown_tasks)} shutdown tasks")
        
        # Stop periodic tasks first
        self.stop_periodic_tasks()
        
        for task in self._shutdown_tasks:
            try:
                plugin_instance = task['plugin_instance']
                await plugin_instance._run_task_safely(task['handler'])
            except Exception as e:
                self.logger.error(f"Shutdown task from {task['plugin']} failed: {e}")
    
    def start_periodic_tasks(self):
        """Start all periodic tasks in separate threads"""
        self.logger.info(f"Starting {len(self._periodic_tasks)} periodic tasks")
        
        for task in self._periodic_tasks:
            thread = threading.Thread(
                target=self._run_periodic_task,
                args=(task,),
                daemon=True,
                name=f"PeriodicTask-{task['plugin']}-{task['handler'].__name__}"
            )
            thread.start()
            self._periodic_task_threads.append(thread)
    
    def _run_periodic_task(self, task):
        """Run a periodic task in a loop"""
        plugin_instance = task['plugin_instance']
        handler = task['handler']
        interval = task['interval']
        
        self.logger.debug(f"Started periodic task: {task['description']} ({interval}s)")
        
        while True:
            try:
                time.sleep(interval)
                
                # Run the task (handle both sync and async)
                if inspect.iscoroutinefunction(handler):
                    # Run async function in new event loop
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        loop.run_until_complete(handler())
                    finally:
                        loop.close()
                else:
                    handler()
                    
            except Exception as e:
                self.logger.error(f"Periodic task {task['description']} failed: {e}")
                # Continue running despite errors
    
    def stop_periodic_tasks(self):
        """Stop all periodic task threads"""
        self.logger.info("Stopping periodic tasks")
        # Note: We can't cleanly stop daemon threads, but they'll stop when main process exits
        self._periodic_task_threads.clear()
    
    def get_plugin_info(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all registered plugins"""
        return {name: plugin.plugin_info for name, plugin in self._plugins.items()}
    
    def get_command_help(self, command_name: str) -> Optional[str]:
        """Get help for a specific command"""
        if command_name not in self._commands:
            return None
        
        cmd_data = self._commands[command_name]
        plugin_instance = cmd_data['plugin_instance']
        return plugin_instance.get_command_help(command_name)
    
    def get_all_commands_help(self) -> str:
        """Get help for all commands organized by plugin"""
        help_text = "🤖 **Available Commands**\n\n"
        
        # Group commands by plugin
        plugins_commands: Dict[str, List[str]] = {}
        
        for cmd_name, cmd_data in self._commands.items():
            # Skip aliases
            if cmd_name != cmd_data['name']:
                continue
            
            plugin_name = cmd_data['plugin']
            if plugin_name not in plugins_commands:
                plugins_commands[plugin_name] = []
            
            plugins_commands[plugin_name].append(cmd_name)
        
        # Generate help for each plugin
        for plugin_name, commands in plugins_commands.items():
            plugin_instance = self._plugins[plugin_name]
            help_text += plugin_instance.get_all_commands_help() + "\n\n"
        
        return help_text
    
    @property
    def plugins(self) -> Dict[str, PluginBase]:
        """Get all registered plugins"""
        return self._plugins.copy()
    
    @property
    def commands(self) -> Dict[str, Dict[str, Any]]:
        """Get all registered commands"""
        return self._commands.copy()

