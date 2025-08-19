"""
Help System Plugin - Provides detailed help for commands and plugins
"""

from typing import Optional

from core import PluginBase, plugin_info, command, CommandScope, PermissionLevel


@plugin_info(
    name="Help System",
    version="1.0.0",
    author="TorrentBot",
    description="Advanced help system with detailed command information",
    enabled=True
)
class HelpSystemPlugin(PluginBase):
    """Plugin that provides detailed help for commands and plugins"""
    
    def __init__(self, bot, logger=None):
        super().__init__(bot, logger)
        self.plugin_registry = None  # Will be set by the main bot
    
    def get_plugin_description(self) -> str:
        return "Provides detailed help information for all commands and plugins"
    
    def set_plugin_registry(self, registry):
        """Set reference to plugin registry (called by main bot)"""
        self.plugin_registry = registry
    
    @command(
        name="help_cmd",
        aliases=["h", "man"],
        description="Get detailed help for a specific command",
        usage="/help_cmd <command_name>",
        examples=[
            "/help_cmd torrent",
            "/help_cmd audiobook",
            "/h sysinfo"
        ],
        category="Help"
    )
    def help_command(self, message):
        """Show detailed help for a specific command"""
        try:
            args = message.text.split()[1:]
            
            if not args:
                self.bot.reply_to(message,
                    "❓ **Command Help**\n\n"
                    "Usage: `/help_cmd <command_name>`\n\n"
                    "Examples:\n"
                    "• `/help_cmd torrent` - Help for torrent command\n"
                    "• `/help_cmd audiobook` - Help for audiobook command\n\n"
                    "💡 Use `/start` for general help or `/commands` to list all commands",
                    parse_mode="Markdown"
                )
                return
            
            command_name = args[0].lower()
            
            # Remove leading slash if present
            if command_name.startswith('/'):
                command_name = command_name[1:]
            
            if not self.plugin_registry:
                self.bot.reply_to(message, "❌ Help system not properly initialized")
                return
            
            # Find command
            help_text = self.plugin_registry.get_command_help(command_name)
            
            if help_text:
                # Add plugin information
                if command_name in self.plugin_registry.commands:
                    cmd_data = self.plugin_registry.commands[command_name]
                    plugin_name = cmd_data['plugin']
                    plugin_instance = cmd_data['plugin_instance']
                    plugin_info = plugin_instance.plugin_info
                    
                    help_text += f"\n\n**Plugin:** {plugin_name} v{plugin_info['version']}"
                    if plugin_info['author']:
                        help_text += f"\n**Author:** {plugin_info['author']}"
                
                self.bot.send_message(message.chat.id, help_text, parse_mode="Markdown")
            else:
                # Suggest similar commands
                similar_commands = self._find_similar_commands(command_name)
                
                error_text = f"❌ Command `/{command_name}` not found"
                
                if similar_commands:
                    error_text += f"\n\n💡 **Did you mean:**\n"
                    for cmd in similar_commands[:3]:
                        error_text += f"• `/{cmd}`\n"
                
                error_text += f"\n\n📋 Use `/commands` to see all available commands"
                
                self.bot.reply_to(message, error_text, parse_mode="Markdown")
        
        except Exception as e:
            self.logger.error(f"Help command failed: {e}")
            self.bot.reply_to(message, f"❌ Error getting help: {e}")
    
    @command(
        name="commands",
        aliases=["list", "cmds"],
        description="List all available commands organized by category",
        usage="/commands [category]",
        examples=[
            "/commands",
            "/commands Media",
            "/commands System"
        ],
        category="Help"
    )
    def list_commands(self, message):
        """List all available commands"""
        try:
            args = message.text.split()[1:]
            filter_category = args[0] if args else None
            
            if not self.plugin_registry:
                self.bot.reply_to(message, "❌ Help system not properly initialized")
                return
            
            # Group commands by category
            categories = {}
            processed_commands = set()
            
            for cmd_name, cmd_data in self.plugin_registry.commands.items():
                # Skip aliases (only show main command)
                if cmd_data['name'] in processed_commands:
                    continue
                
                category = cmd_data['category']
                
                # Filter by category if specified
                if filter_category and category.lower() != filter_category.lower():
                    continue
                
                if category not in categories:
                    categories[category] = []
                
                categories[category].append(cmd_data)
                processed_commands.add(cmd_data['name'])
            
            if not categories:
                if filter_category:
                    self.bot.reply_to(message, f"❌ No commands found in category: {filter_category}")
                else:
                    self.bot.reply_to(message, "❌ No commands available")
                return
            
            # Generate commands list
            commands_text = "📋 **Available Commands**\n\n"
            
            if filter_category:
                commands_text = f"📋 **{filter_category} Commands**\n\n"
            
            for category, commands in sorted(categories.items()):
                if not filter_category:
                    commands_text += f"**{category}:**\n"
                
                for cmd in sorted(commands, key=lambda x: x['name']):
                    commands_text += f"• `/{cmd['name']}`"
                    
                    # Add aliases if any
                    if cmd['aliases']:
                        aliases_str = ', '.join(f"`/{alias}`" for alias in cmd['aliases'])
                        commands_text += f" ({aliases_str})"
                    
                    commands_text += f" - {cmd['description']}\n"
                
                commands_text += "\n"
            
            # Add footer
            commands_text += "💡 **Tips:**\n"
            commands_text += "• Use `/help_cmd <command>` for detailed help\n"
            commands_text += "• Use `/commands <category>` to filter by category\n"
            
            if not filter_category:
                # Show available categories
                category_list = ', '.join(f"`{cat}`" for cat in sorted(categories.keys()))
                commands_text += f"• **Categories:** {category_list}"
            
            # Split message if too long
            if len(commands_text) > 4000:
                parts = [commands_text[i:i+3900] for i in range(0, len(commands_text), 3900)]
                for i, part in enumerate(parts):
                    if i == 0:
                        self.bot.send_message(message.chat.id, part, parse_mode="Markdown")
                    else:
                        self.bot.send_message(message.chat.id, f"📋 Commands (part {i+1}):\n{part}", parse_mode="Markdown")
            else:
                self.bot.send_message(message.chat.id, commands_text, parse_mode="Markdown")
        
        except Exception as e:
            self.logger.error(f"List commands failed: {e}")
            self.bot.reply_to(message, f"❌ Error listing commands: {e}")
    
    @command(
        name="plugin_info",
        aliases=["pinfo"],
        description="Show information about a specific plugin",
        usage="/plugin_info <plugin_name>",
        examples=[
            "/plugin_info System Info",
            "/plugin_info Audiobook TTS"
        ],
        category="Help"
    )
    def plugin_info_command(self, message):
        """Show information about a specific plugin"""
        try:
            args = message.text.split()[1:]
            
            if not args:
                self.bot.reply_to(message,
                    "❓ **Plugin Information**\n\n"
                    "Usage: `/plugin_info <plugin_name>`\n\n"
                    "💡 Use `/plugins` to see all loaded plugins",
                    parse_mode="Markdown"
                )
                return
            
            plugin_name = ' '.join(args)
            
            if not self.plugin_registry:
                self.bot.reply_to(message, "❌ Help system not properly initialized")
                return
            
            # Find plugin
            plugins_info = self.plugin_registry.get_plugin_info()
            
            if plugin_name not in plugins_info:
                # Try to find similar plugin names
                similar_plugins = []
                for name in plugins_info.keys():
                    if plugin_name.lower() in name.lower():
                        similar_plugins.append(name)
                
                error_text = f"❌ Plugin `{plugin_name}` not found"
                
                if similar_plugins:
                    error_text += f"\n\n💡 **Did you mean:**\n"
                    for plugin in similar_plugins[:3]:
                        error_text += f"• `{plugin}`\n"
                
                self.bot.reply_to(message, error_text, parse_mode="Markdown")
                return
            
            # Get plugin info
            plugin_info = plugins_info[plugin_name]
            plugin_instance = self.plugin_registry.plugins[plugin_name]
            
            info_text = f"📦 **{plugin_name}**\n\n"
            info_text += f"**Version:** {plugin_info['version']}\n"
            
            if plugin_info['author']:
                info_text += f"**Author:** {plugin_info['author']}\n"
            
            info_text += f"**Description:** {plugin_info['description']}\n"
            info_text += f"**Enabled:** {'Yes' if plugin_info['enabled'] else 'No'}\n"
            
            if plugin_info['dependencies']:
                deps_str = ', '.join(f"`{dep}`" for dep in plugin_info['dependencies'])
                info_text += f"**Dependencies:** {deps_str}\n"
            
            # Get plugin commands
            plugin_commands = []
            for cmd_name, cmd_data in self.plugin_registry.commands.items():
                if cmd_data['plugin'] == plugin_name and cmd_name == cmd_data['name']:
                    plugin_commands.append(cmd_name)
            
            if plugin_commands:
                info_text += f"\n**Commands ({len(plugin_commands)}):**\n"
                for cmd in sorted(plugin_commands):
                    info_text += f"• `/{cmd}`\n"
            
            # Get additional info from plugin
            try:
                additional_info = plugin_instance.get_plugin_description()
                if additional_info:
                    info_text += f"\n**Details:** {additional_info}"
            except:
                pass
            
            self.bot.send_message(message.chat.id, info_text, parse_mode="Markdown")
        
        except Exception as e:
            self.logger.error(f"Plugin info command failed: {e}")
            self.bot.reply_to(message, f"❌ Error getting plugin info: {e}")
    
    def _find_similar_commands(self, command_name: str) -> list:
        """Find commands similar to the given name"""
        if not self.plugin_registry:
            return []
        
        similar_commands = []
        command_lower = command_name.lower()
        
        for cmd_name, cmd_data in self.plugin_registry.commands.items():
            # Skip aliases
            if cmd_name != cmd_data['name']:
                continue
            
            cmd_lower = cmd_name.lower()
            
            # Exact substring match
            if command_lower in cmd_lower or cmd_lower in command_lower:
                similar_commands.append(cmd_name)
            # Similar length and some common characters
            elif (abs(len(command_lower) - len(cmd_lower)) <= 2 and
                  len(set(command_lower) & set(cmd_lower)) >= min(len(command_lower), len(cmd_lower)) // 2):
                similar_commands.append(cmd_name)
        
        return similar_commands[:5]  # Return max 5 suggestions

