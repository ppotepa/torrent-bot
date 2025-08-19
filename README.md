# 🤖 Advanced Telegram Bot with Reflection-Based Plugin System

A modern, extensible Telegram bot built with Python featuring automatic plugin discovery, C#-style attributes, and comprehensive command management.

## ✨ Features

- 🔍 **Reflection-Based Plugin System** - Automatic plugin discovery and registration
- 🎯 **C#-Style Attributes** - Use decorators like `@command`, `@callback_query` for clean code
- 🔐 **Permission System** - Built-in user/admin/owner access control
- 📊 **Rich Command Help** - Automatic help generation with examples and usage
- ⚡ **Task Management** - Startup, shutdown, and periodic tasks
- 🎭 **Multiple TTS Engines** - OpenVoice, voice cloning, gTTS, pyttsx3
- 📥 **YouTube Downloader** - Download videos/audio with yt-dlp
- 🔍 **Torrent Search** - Search and download via qBittorrent + Jackett
- 📊 **System Monitoring** - CPU, memory, disk, network stats
- 🛠️ **Advanced Help System** - Detailed command documentation

## 🚀 Quick Start

### Option 1: Docker (Recommended)
```bash
# Development mode (fastest rebuilds)
docker-build.bat --dev
docker-compose -f docker-compose.yaml -f docker-compose.dev.yaml up

# Production mode
docker-build.bat
docker-compose up -d
```

### Option 2: Local Installation
```bash
git clone https://github.com/your-repo/torrent-bot.git
cd torrent-bot
cd src
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
# Create .env file
TELEGRAM_BOT_TOKEN=your_bot_token_here
ADMIN_USER_IDS=your_user_id
OWNER_USER_IDS=your_user_id

# Optional: Configure external services
QBITTORRENT_URL=http://localhost:8080
QBITTORRENT_USER=admin
QBITTORRENT_PASS=adminadmin
JACKETT_URL=http://localhost:9117
JACKETT_API_KEY=your_jackett_api_key
```

### 3. Run the Bot
```bash
python main.py
```

## 📦 Plugin System

### Creating a Plugin

```python
from core import PluginBase, plugin_info, command, CommandScope, PermissionLevel

@plugin_info(
    name="My Plugin",
    version="1.0.0",
    author="Your Name",
    description="My awesome plugin",
    enabled=True
)
class MyPlugin(PluginBase):
    def get_plugin_description(self) -> str:
        return "Detailed description of plugin functionality"
    
    @command(
        name="hello",
        aliases=["hi", "greet"],
        description="Say hello to the user",
        usage="/hello [name]",
        examples=["/hello", "/hello John"],
        category="General"
    )
    def hello_command(self, message):
        args = message.text.split()[1:]
        name = args[0] if args else "World"
        self.bot.reply_to(message, f"Hello, {name}! 👋")
```

### Available Decorators

- `@command` - Define bot commands
- `@callback_query` - Handle inline button callbacks  
- `@message_handler` - Handle specific message types
- `@startup_task` - Run code when plugin starts
- `@shutdown_task` - Run code when plugin stops
- `@periodic_task` - Run code periodically

## 🎯 Built-in Plugins

### System Info Plugin
```bash
/sysinfo          # Show system information
/sysinfo brief    # Brief system stats
/sysinfo detailed # Detailed system info
/uptime          # System uptime
```

### YouTube Downloader Plugin
```bash
/youtube <url>                    # Download video
/youtube <url> audio              # Download audio only
/youtube <url> video 720p         # Download 720p video
/ytinfo <url>                     # Get video information
```

### Audiobook TTS Plugin
```bash
/audiobook Hello world            # Convert text to speech
/audiobook Text:profile           # Use specific voice profile
/audiobook [engine,lang] Text     # Specify engine and language
/tts_engines                      # Show available engines
```

### Torrent Search Plugin
   ```bash
/torrent <query>                  # Search torrents
/torrent <query> [rich]           # Rich results with buttons
/torrent <query> [all]            # Search all indexers
/downloads                        # Show active downloads
/tdiag                           # Torrent diagnostics
```

### Help System Plugin
```bash
/help_cmd <command>               # Detailed command help
/commands                         # List all commands
/commands <category>              # List commands by category
/plugin_info <plugin>             # Show plugin information
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `TELEGRAM_BOT_TOKEN` | Bot token from @BotFather | Yes |
| `ADMIN_USER_IDS` | Comma-separated admin user IDs | No |
| `OWNER_USER_IDS` | Comma-separated owner user IDs | No |
| `QBITTORRENT_URL` | qBittorrent Web UI URL | No |
| `QBITTORRENT_USER` | qBittorrent username | No |
| `QBITTORRENT_PASS` | qBittorrent password | No |
| `JACKETT_URL` | Jackett API URL | No |
| `JACKETT_API_KEY` | Jackett API key | No |

### Permission Levels

- **USER** - Anyone can use the command
- **ADMIN** - Only users in `ADMIN_USER_IDS`
- **OWNER** - Only users in `OWNER_USER_IDS`

## 🏗️ Architecture

```
src/
├── core/                     # Core plugin system
│   ├── attributes.py         # Decorator attributes
│   ├── plugin_base.py        # Base plugin class
│   ├── plugin_registry.py    # Plugin discovery
│   └── __init__.py
├── plugins/                  # Plugin modules
│   ├── system_info.py
│   ├── youtube_downloader.py
│   ├── audiobook_tts.py
│   ├── torrent_search.py
│   ├── help_system.py
│   └── __init__.py
├── main.py                   # Main application
└── requirements.txt
```

## 🔄 Migration from Old System

The new reflection-based system replaces the old manual command registration:

**Old System:**
```python
# Manual imports and handler registration
from plugins import youtube, torrent, audiobook

@bot.message_handler(commands=['youtube'])
def youtube_handler(message):
    youtube.handle_command(message, bot)
```

**New System:**
```python
# Automatic discovery and registration
# Just create plugin with @command decorators
# Everything else is handled automatically
```

## 🧪 Testing

```bash
cd src
python -m pytest tests/
```

## 📊 Monitoring

The bot includes comprehensive logging and monitoring:

- **System Stats** - CPU, memory, disk usage
- **Plugin Status** - Loaded plugins and their health
- **Command Usage** - Track command execution
- **Error Handling** - Detailed error logging

Use `/status` (admin only) to see current bot status.

## 🤝 Contributing

1. **Fork the repository**
2. **Create a new plugin** following the plugin system documentation
3. **Add tests** for your plugin
4. **Submit a pull request**

See [PLUGIN_SYSTEM.md](docs/PLUGIN_SYSTEM.md) for detailed plugin development guide.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- [Plugin Development Guide](docs/PLUGIN_SYSTEM.md)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [pyTelegramBotAPI Documentation](https://github.com/eternnoir/pyTelegramBotAPI)

## 🆘 Support

- Open an issue for bugs or feature requests
- Check the [Plugin System Documentation](docs/PLUGIN_SYSTEM.md) for development help
- Use `/help_cmd <command>` in the bot for command-specific help

---

Made with ❤️ using Python and the power of reflection!