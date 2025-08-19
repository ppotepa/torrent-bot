# 🔧 Reflection-Based Plugin System

## Overview

This Telegram bot uses a modern reflection-based plugin system inspired by C# attributes. Plugins are automatically discovered and registered using Python decorators that mimic C# attributes.

## 🏗️ Architecture

```
src/
├── core/                     # Core plugin system
│   ├── attributes.py         # Decorator attributes (like C# attributes)
│   ├── plugin_base.py        # Base plugin class
│   ├── plugin_registry.py    # Automatic plugin discovery
│   └── __init__.py
├── plugins/                  # Plugin modules
│   ├── system_info.py        # System information plugin
│   ├── youtube_downloader.py # YouTube downloader plugin
│   ├── audiobook_tts.py      # Text-to-speech plugin
│   ├── torrent_search.py     # Torrent search plugin
│   ├── help_system.py        # Advanced help system
│   └── __init__.py
├── main.py                   # Main bot application
└── requirements.txt
```

## 🎯 Key Features

- **Automatic Discovery**: Plugins are automatically found and loaded
- **C#-Style Attributes**: Use decorators like `@command`, `@callback_query`, etc.
- **Reflection-Based**: Commands and handlers are discovered using reflection
- **Permission System**: Built-in user/admin/owner permission levels
- **Scope Control**: Commands can be restricted to private/group/channel
- **Task System**: Startup, shutdown, and periodic tasks
- **Rich Help System**: Automatic help generation with examples
- **Error Handling**: Comprehensive error handling and logging

## 📝 Creating a Plugin

### 1. Basic Plugin Structure

```python
from core import PluginBase, plugin_info, command

@plugin_info(
    name="My Plugin",
    version="1.0.0",
    author="Your Name",
    description="Plugin description",
    dependencies=["requests"],  # Optional dependencies
    enabled=True
)
class MyPlugin(PluginBase):
    """My awesome plugin"""
    
    def get_plugin_description(self) -> str:
        return "Detailed description of what this plugin does"
    
    @command(
        name="mycommand",
        aliases=["mc", "my"],
        description="My awesome command",
        usage="/mycommand <parameter>",
        examples=["/mycommand hello", "/mycommand world"],
        flags=["flag1", "flag2"],
        category="General"
    )
    def my_command(self, message):
        """Handle my command"""
        self.bot.reply_to(message, "Hello from my plugin!")
```

### 2. Available Decorators (Attributes)

#### @command
```python
@command(
    name="command_name",           # Command name (required)
    aliases=["alias1", "alias2"],  # Alternative names
    description="Description",     # Short description
    usage="/command <args>",       # Usage syntax
    examples=["example1"],         # Usage examples
    flags=["flag1", "flag2"],      # Supported flags
    category="Category",           # Command category
    scope=CommandScope.ALL,        # Where command works
    permission=PermissionLevel.USER # Required permission
)
def my_command(self, message):
    pass
```

#### @callback_query
```python
@callback_query(
    pattern="my_callback_",        # Regex pattern to match
    description="Handle callbacks"  # Description
)
def my_callback(self, call):
    pass
```

#### @message_handler
```python
@message_handler(
    content_types=['text'],        # Content types to handle
    regexp=r"pattern",            # Regex pattern
    func_filter=lambda m: True,   # Custom filter function
    description="Handle messages"  # Description
)
def my_handler(self, message):
    pass
```

#### @startup_task
```python
@startup_task(priority=0)  # Lower numbers run first
def initialize_plugin(self):
    """Run when plugin starts"""
    self.logger.info("Plugin initialized!")
```

#### @shutdown_task
```python
@shutdown_task(priority=0)
def cleanup_plugin(self):
    """Run when plugin shuts down"""
    self.logger.info("Plugin cleaned up!")
```

#### @periodic_task
```python
@periodic_task(interval_seconds=60, description="Hourly task")
def hourly_task(self):
    """Run every 60 seconds"""
    self.logger.info("Periodic task executed!")
```

### 3. Permission Levels

```python
from core import PermissionLevel

# Available levels:
PermissionLevel.USER    # Anyone can use
PermissionLevel.ADMIN   # Only admin users
PermissionLevel.OWNER   # Only owner users
```

Configure admin/owner users via environment variables:
```bash
ADMIN_USER_IDS=123456789,987654321
OWNER_USER_IDS=123456789
```

### 4. Command Scopes

```python
from core import CommandScope

CommandScope.ALL         # Works everywhere
CommandScope.PRIVATE     # Only in private chats
CommandScope.GROUP       # Only in groups
CommandScope.SUPERGROUP  # Only in supergroups
CommandScope.CHANNEL     # Only in channels
```

## 🔄 Plugin Lifecycle

1. **Discovery**: Plugin files are automatically scanned
2. **Import**: Plugin classes are imported and validated
3. **Registration**: Commands and handlers are registered
4. **Startup**: Startup tasks are executed in priority order
5. **Runtime**: Commands and handlers respond to messages
6. **Shutdown**: Shutdown tasks are executed on bot stop

## 📊 Advanced Features

### Error Handling
```python
@command(name="example")
def example_command(self, message):
    try:
        # Your code here
        pass
    except Exception as e:
        self.logger.error(f"Command failed: {e}")
        self.bot.reply_to(message, f"❌ Error: {e}")
```

### Accessing Plugin Registry
```python
def some_method(self, message):
    # Access other plugins
    registry = self.bot._plugin_registry  # If needed
    other_plugin = registry.plugins.get("Other Plugin")
```

### Custom Initialization
```python
def __init__(self, bot, logger=None):
    super().__init__(bot, logger)
    # Custom initialization
    self.my_data = {}
    self.config = self._load_config()
```

## 🧪 Testing Your Plugin

### 1. Create Test File
```python
# tests/test_my_plugin.py
import pytest
from unittest.mock import Mock
from src.plugins.my_plugin import MyPlugin

def test_my_plugin():
    bot_mock = Mock()
    plugin = MyPlugin(bot_mock)
    
    # Test plugin info
    assert plugin.plugin_info['name'] == "My Plugin"
    
    # Test command discovery
    assert 'mycommand' in plugin.commands
```

### 2. Run Tests
```bash
cd src
python -m pytest tests/
```

## 🚀 Deployment

### 1. Environment Setup
```bash
# Required
TELEGRAM_BOT_TOKEN=your_bot_token

# Optional
ADMIN_USER_IDS=123456789,987654321
OWNER_USER_IDS=123456789
```

### 2. Install Dependencies
```bash
pip install -r src/requirements.txt
```

### 3. Run Bot
```bash
cd src
python main.py
```

## 🔧 Configuration

### Environment Variables
- `TELEGRAM_BOT_TOKEN` - Bot token (required)
- `ADMIN_USER_IDS` - Comma-separated admin user IDs
- `OWNER_USER_IDS` - Comma-separated owner user IDs
- Plugin-specific variables (see individual plugin docs)

### Plugin Configuration
Each plugin can have its own configuration via environment variables or config files.

## 📚 Examples

See the included plugins for complete examples:
- `system_info.py` - System monitoring commands
- `youtube_downloader.py` - Media downloading with progress
- `audiobook_tts.py` - Text-to-speech with multiple engines
- `torrent_search.py` - Torrent search with callback buttons
- `help_system.py` - Advanced help system

## 🐛 Debugging

### Enable Debug Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Plugin Status
Use `/plugins` command to see loaded plugins and their status.

### Command Help
Use `/help_cmd <command>` for detailed command information.

## 🔄 Migration from Old System

The new system is designed to be a complete replacement for the old manual command registration system. Key improvements:

1. **No more manual imports** - Plugins are auto-discovered
2. **No more manual handlers** - Use decorators instead
3. **Better error handling** - Automatic try/catch with logging
4. **Permission system** - Built-in user access control
5. **Rich help system** - Automatic help generation
6. **Task management** - Startup/shutdown/periodic tasks

## 🤝 Contributing

1. Follow the plugin structure outlined above
2. Use proper type hints
3. Include comprehensive docstrings
4. Add examples in command decorators
5. Handle errors gracefully
6. Write tests for your plugins

