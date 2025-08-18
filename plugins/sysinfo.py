#!/usr/bin/env python3
"""
System info plugin - Basic stub implementation
"""

def handle_sysinfo_command(message, bot):
    """Handle system info commands"""
    bot.send_message(message.chat.id, "System info plugin not yet implemented")

def register_sysinfo_commands():
    """Register system info commands"""
    return {
        'sysinfo': {
            'handler': handle_sysinfo_command,
            'description': 'Show system information'
        }
    }
