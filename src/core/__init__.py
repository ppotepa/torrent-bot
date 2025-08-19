"""
Core module for the reflection-based Telegram bot plugin system
"""

from .attributes import (
    command, callback_query, message_handler, startup_task, shutdown_task, 
    periodic_task, plugin_info, CommandScope, PermissionLevel,
    get_command_metadata, get_plugin_metadata, is_command_method,
    is_callback_query_method, is_message_handler_method
)
from .plugin_base import PluginBase
from .plugin_registry import PluginRegistry

__all__ = [
    # Decorators (attributes)
    'command',
    'callback_query', 
    'message_handler',
    'startup_task',
    'shutdown_task',
    'periodic_task',
    'plugin_info',
    
    # Enums
    'CommandScope',
    'PermissionLevel',
    
    # Classes
    'PluginBase',
    'PluginRegistry',
    
    # Utility functions
    'get_command_metadata',
    'get_plugin_metadata',
    'is_command_method',
    'is_callback_query_method',
    'is_message_handler_method'
]
