"""
Plugin Attribute System - Python decorators that mimic C# attributes
for defining Telegram bot commands with metadata
"""

import functools
from typing import List, Dict, Any, Optional, Callable
from enum import Enum


class CommandScope(Enum):
    """Define where commands can be executed"""
    PRIVATE = "private"
    GROUP = "group" 
    SUPERGROUP = "supergroup"
    CHANNEL = "channel"
    ALL = "all"


class PermissionLevel(Enum):
    """Define permission levels for commands"""
    USER = "user"
    ADMIN = "admin"
    OWNER = "owner"


def command(
    name: str,
    aliases: Optional[List[str]] = None,
    description: str = "",
    usage: str = "",
    examples: Optional[List[str]] = None,
    scope: CommandScope = CommandScope.ALL,
    permission: PermissionLevel = PermissionLevel.USER,
    flags: Optional[List[str]] = None,
    category: str = "General"
):
    """
    Decorator that marks a method as a Telegram bot command (like C# [Command] attribute)
    
    Args:
        name: Command name (without /)
        aliases: Alternative command names
        description: Short description of what command does
        usage: Usage syntax
        examples: List of example usages
        scope: Where command can be used (private/group/etc)
        permission: Required permission level
        flags: Supported flags for this command
        category: Command category for organization
    """
    def decorator(func: Callable) -> Callable:
        # Store command metadata as function attributes
        func._is_command = True
        func._command_name = name
        func._command_aliases = aliases or []
        func._command_description = description
        func._command_usage = usage
        func._command_examples = examples or []
        func._command_scope = scope
        func._command_permission = permission
        func._command_flags = flags or []
        func._command_category = category
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


def callback_query(pattern: str, description: str = ""):
    """
    Decorator for callback query handlers (like C# [CallbackQuery] attribute)
    
    Args:
        pattern: Regex pattern to match callback data
        description: Description of what this callback handles
    """
    def decorator(func: Callable) -> Callable:
        func._is_callback_query = True
        func._callback_pattern = pattern
        func._callback_description = description
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


def message_handler(
    content_types: Optional[List[str]] = None,
    regexp: Optional[str] = None,
    func_filter: Optional[Callable] = None,
    description: str = ""
):
    """
    Decorator for message handlers (like C# [MessageHandler] attribute)
    
    Args:
        content_types: Types of content to handle (text, photo, document, etc.)
        regexp: Regular expression to match message text
        func_filter: Custom filter function
        description: Description of what this handler does
    """
    def decorator(func: Callable) -> Callable:
        func._is_message_handler = True
        func._handler_content_types = content_types or ['text']
        func._handler_regexp = regexp
        func._handler_filter = func_filter
        func._handler_description = description
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


def startup_task(priority: int = 0):
    """
    Decorator for methods that should run on bot startup (like C# [StartupTask] attribute)
    
    Args:
        priority: Execution priority (lower numbers run first)
    """
    def decorator(func: Callable) -> Callable:
        func._is_startup_task = True
        func._startup_priority = priority
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


def shutdown_task(priority: int = 0):
    """
    Decorator for methods that should run on bot shutdown (like C# [ShutdownTask] attribute)
    
    Args:
        priority: Execution priority (lower numbers run first)
    """
    def decorator(func: Callable) -> Callable:
        func._is_shutdown_task = True
        func._shutdown_priority = priority
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


def periodic_task(interval_seconds: int, description: str = ""):
    """
    Decorator for methods that should run periodically (like C# [PeriodicTask] attribute)
    
    Args:
        interval_seconds: How often to run the task
        description: Description of what this task does
    """
    def decorator(func: Callable) -> Callable:
        func._is_periodic_task = True
        func._task_interval = interval_seconds
        func._task_description = description
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


def plugin_info(
    name: str,
    version: str = "1.0.0",
    author: str = "",
    description: str = "",
    dependencies: Optional[List[str]] = None,
    enabled: bool = True
):
    """
    Class decorator for plugin metadata (like C# [PluginInfo] attribute)
    
    Args:
        name: Plugin display name
        version: Plugin version
        author: Plugin author
        description: Plugin description
        dependencies: Required dependencies
        enabled: Whether plugin is enabled by default
    """
    def decorator(cls):
        cls._plugin_name = name
        cls._plugin_version = version
        cls._plugin_author = author
        cls._plugin_description = description
        cls._plugin_dependencies = dependencies or []
        cls._plugin_enabled = enabled
        
        return cls
    return decorator


# Utility functions to extract metadata from decorated methods/classes

def get_command_metadata(func: Callable) -> Optional[Dict[str, Any]]:
    """Extract command metadata from a decorated function"""
    if not hasattr(func, '_is_command') or not func._is_command:
        return None
    
    return {
        'name': func._command_name,
        'aliases': func._command_aliases,
        'description': func._command_description,
        'usage': func._command_usage,
        'examples': func._command_examples,
        'scope': func._command_scope,
        'permission': func._command_permission,
        'flags': func._command_flags,
        'category': func._command_category,
        'handler': func
    }


def get_plugin_metadata(cls) -> Dict[str, Any]:
    """Extract plugin metadata from a decorated class"""
    return {
        'name': getattr(cls, '_plugin_name', cls.__name__),
        'version': getattr(cls, '_plugin_version', '1.0.0'),
        'author': getattr(cls, '_plugin_author', ''),
        'description': getattr(cls, '_plugin_description', ''),
        'dependencies': getattr(cls, '_plugin_dependencies', []),
        'enabled': getattr(cls, '_plugin_enabled', True)
    }


def is_command_method(func: Callable) -> bool:
    """Check if a method is decorated as a command"""
    return hasattr(func, '_is_command') and func._is_command


def is_callback_query_method(func: Callable) -> bool:
    """Check if a method is decorated as a callback query handler"""
    return hasattr(func, '_is_callback_query') and func._is_callback_query


def is_message_handler_method(func: Callable) -> bool:
    """Check if a method is decorated as a message handler"""
    return hasattr(func, '_is_message_handler') and func._is_message_handler


def is_startup_task_method(func: Callable) -> bool:
    """Check if a method is decorated as a startup task"""
    return hasattr(func, '_is_startup_task') and func._is_startup_task


def is_shutdown_task_method(func: Callable) -> bool:
    """Check if a method is decorated as a shutdown task"""
    return hasattr(func, '_is_shutdown_task') and func._is_shutdown_task


def is_periodic_task_method(func: Callable) -> bool:
    """Check if a method is decorated as a periodic task"""
    return hasattr(func, '_is_periodic_task') and func._is_periodic_task

