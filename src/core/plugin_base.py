"""
Base Plugin Class - Provides reflection capabilities and standardized interface
for all Telegram bot plugins
"""

import inspect
import logging
from typing import Dict, List, Any, Optional, Type, Callable
from abc import ABC, abstractmethod

from .attributes import (
    get_command_metadata, get_plugin_metadata,
    is_command_method, is_callback_query_method, is_message_handler_method,
    is_startup_task_method, is_shutdown_task_method, is_periodic_task_method
)


class PluginBase(ABC):
    """
    Base class for all bot plugins. Uses reflection to automatically
    discover commands, handlers, and tasks defined with attributes.
    """
    
    def __init__(self, bot, logger: Optional[logging.Logger] = None):
        """
        Initialize plugin with bot instance and optional logger
        
        Args:
            bot: Telegram bot instance
            logger: Logger instance (will create one if not provided)
        """
        self.bot = bot
        self.logger = logger or logging.getLogger(self.__class__.__name__)
        self._commands: Dict[str, Dict[str, Any]] = {}
        self._callback_queries: List[Dict[str, Any]] = []
        self._message_handlers: List[Dict[str, Any]] = []
        self._startup_tasks: List[Dict[str, Any]] = []
        self._shutdown_tasks: List[Dict[str, Any]] = []
        self._periodic_tasks: List[Dict[str, Any]] = []
        
        # Automatically discover all decorated methods
        self._discover_methods()
    
    def _discover_methods(self):
        """
        Use reflection to discover all methods decorated with plugin attributes
        """
        for name, method in inspect.getmembers(self, predicate=inspect.ismethod):
            # Skip private methods and inherited methods from base classes
            if name.startswith('_') or not hasattr(method, '__func__'):
                continue
            
            func = method.__func__
            
            # Discover commands
            if is_command_method(func):
                cmd_metadata = get_command_metadata(func)
                if cmd_metadata:
                    cmd_name = cmd_metadata['name']
                    # Replace the handler with the bound method
                    cmd_metadata['handler'] = method
                    self._commands[cmd_name] = cmd_metadata
                    
                    # Also register aliases
                    for alias in cmd_metadata['aliases']:
                        # Create a copy for aliases to avoid reference issues
                        alias_metadata = cmd_metadata.copy()
                        alias_metadata['handler'] = method  # Ensure bound method for aliases too
                        self._commands[alias] = alias_metadata
                    
                    self.logger.info(f"Discovered command: /{cmd_name}")
            
            # Discover callback query handlers
            if is_callback_query_method(func):
                callback_metadata = {
                    'pattern': func._callback_pattern,
                    'description': func._callback_description,
                    'handler': method
                }
                self._callback_queries.append(callback_metadata)
                self.logger.info(f"Discovered callback query: {func._callback_pattern}")
            
            # Discover message handlers
            if is_message_handler_method(func):
                handler_metadata = {
                    'content_types': func._handler_content_types,
                    'regexp': func._handler_regexp,
                    'func_filter': func._handler_filter,
                    'description': func._handler_description,
                    'handler': method  # Already using bound method - good!
                }
                self._message_handlers.append(handler_metadata)
                self.logger.info(f"Discovered message handler: {func._handler_description}")
            
            # Discover startup tasks
            if is_startup_task_method(func):
                task_metadata = {
                    'priority': func._startup_priority,
                    'handler': method
                }
                self._startup_tasks.append(task_metadata)
                self.logger.info(f"Discovered startup task: {name}")
            
            # Discover shutdown tasks
            if is_shutdown_task_method(func):
                task_metadata = {
                    'priority': func._shutdown_priority,
                    'handler': method
                }
                self._shutdown_tasks.append(task_metadata)
                self.logger.info(f"Discovered shutdown task: {name}")
            
            # Discover periodic tasks
            if is_periodic_task_method(func):
                task_metadata = {
                    'interval': func._task_interval,
                    'description': func._task_description,
                    'handler': method
                }
                self._periodic_tasks.append(task_metadata)
                self.logger.info(f"Discovered periodic task: {name} ({func._task_interval}s)")
        
        # Sort tasks by priority
        self._startup_tasks.sort(key=lambda x: x['priority'])
        self._shutdown_tasks.sort(key=lambda x: x['priority'])
    
    @property
    def plugin_info(self) -> Dict[str, Any]:
        """Get plugin metadata"""
        return get_plugin_metadata(self.__class__)
    
    @property 
    def commands(self) -> Dict[str, Dict[str, Any]]:
        """Get all discovered commands"""
        return self._commands.copy()
    
    @property
    def callback_queries(self) -> List[Dict[str, Any]]:
        """Get all discovered callback query handlers"""
        return self._callback_queries.copy()
    
    @property
    def message_handlers(self) -> List[Dict[str, Any]]:
        """Get all discovered message handlers"""
        return self._message_handlers.copy()
    
    @property
    def startup_tasks(self) -> List[Dict[str, Any]]:
        """Get all discovered startup tasks"""
        return self._startup_tasks.copy()
    
    @property
    def shutdown_tasks(self) -> List[Dict[str, Any]]:
        """Get all discovered shutdown tasks"""
        return self._shutdown_tasks.copy()
    
    @property
    def periodic_tasks(self) -> List[Dict[str, Any]]:
        """Get all discovered periodic tasks"""
        return self._periodic_tasks.copy()
    
    def get_command_help(self, command_name: str) -> Optional[str]:
        """
        Get help text for a specific command
        
        Args:
            command_name: Name of the command (without /)
            
        Returns:
            Formatted help text or None if command not found
        """
        if command_name not in self._commands:
            return None
        
        cmd = self._commands[command_name]
        help_text = f"**/{cmd['name']}**"
        
        if cmd['aliases']:
            aliases_str = ', '.join(f"/{alias}" for alias in cmd['aliases'])
            help_text += f" (aliases: {aliases_str})"
        
        if cmd['description']:
            help_text += f"\n{cmd['description']}"
        
        if cmd['usage']:
            help_text += f"\n\n**Usage:** `{cmd['usage']}`"
        
        if cmd['examples']:
            help_text += f"\n\n**Examples:**\n"
            for example in cmd['examples']:
                help_text += f"• `{example}`\n"
        
        if cmd['flags']:
            flags_str = ', '.join(f"`{flag}`" for flag in cmd['flags'])
            help_text += f"\n**Supported flags:** {flags_str}"
        
        return help_text
    
    def get_all_commands_help(self) -> str:
        """
        Get help text for all commands in this plugin
        
        Returns:
            Formatted help text for all commands
        """
        plugin_info = self.plugin_info
        help_text = f"**{plugin_info['name']} Plugin**"
        
        if plugin_info['description']:
            help_text += f"\n{plugin_info['description']}"
        
        if plugin_info['version']:
            help_text += f"\n*Version: {plugin_info['version']}*"
        
        help_text += "\n\n**Commands:**\n"
        
        # Group commands by category
        categories: Dict[str, List[Dict[str, Any]]] = {}
        processed_commands = set()
        
        for cmd_name, cmd_data in self._commands.items():
            # Skip aliases (only show main command)
            if cmd_data['name'] in processed_commands:
                continue
            
            category = cmd_data['category']
            if category not in categories:
                categories[category] = []
            
            categories[category].append(cmd_data)
            processed_commands.add(cmd_data['name'])
        
        for category, commands in categories.items():
            if len(categories) > 1:
                help_text += f"\n**{category}:**\n"
            
            for cmd in commands:
                help_text += f"• `/{cmd['name']}` - {cmd['description']}\n"
        
        return help_text
    
    async def run_startup_tasks(self):
        """Run all startup tasks in priority order"""
        self.logger.info(f"Running {len(self._startup_tasks)} startup tasks for {self.plugin_info['name']}")
        
        for task in self._startup_tasks:
            try:
                self.logger.debug(f"Running startup task: {task['handler'].__name__}")
                await self._run_task_safely(task['handler'])
            except Exception as e:
                self.logger.error(f"Startup task {task['handler'].__name__} failed: {e}")
    
    async def run_shutdown_tasks(self):
        """Run all shutdown tasks in priority order"""
        self.logger.info(f"Running {len(self._shutdown_tasks)} shutdown tasks for {self.plugin_info['name']}")
        
        for task in self._shutdown_tasks:
            try:
                self.logger.debug(f"Running shutdown task: {task['handler'].__name__}")
                await self._run_task_safely(task['handler'])
            except Exception as e:
                self.logger.error(f"Shutdown task {task['handler'].__name__} failed: {e}")
    
    async def _run_task_safely(self, task_method):
        """Run a task method safely, handling both sync and async methods"""
        if inspect.iscoroutinefunction(task_method):
            await task_method()
        else:
            task_method()
    
    @abstractmethod
    def get_plugin_description(self) -> str:
        """
        Get a description of what this plugin does.
        This method must be implemented by all plugins.
        """
        pass
    
    def is_enabled(self) -> bool:
        """Check if plugin is enabled"""
        return self.plugin_info.get('enabled', True)
    
    def validate_dependencies(self) -> List[str]:
        """
        Validate that all required dependencies are available
        
        Returns:
            List of missing dependencies (empty if all are available)
        """
        missing_deps = []
        
        for dep in self.plugin_info.get('dependencies', []):
            try:
                __import__(dep)
            except ImportError:
                missing_deps.append(dep)
        
        return missing_deps
