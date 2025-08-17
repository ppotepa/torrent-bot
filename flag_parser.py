"""
Flag parser module for handling command flags in the new format.
Supports flags at the end of commands in square brackets.

Each command has its own specific set of valid flags.

Example formats:
- /t ubuntu:[all,notify]
- /dl file.torrent:[force,silent]
- /si:[detailed]
- /monitor:[start]
"""

import re
from typing import Tuple, List, Dict, Any


class FlagParser:
    """Parser for command flags in square bracket format."""
    
    def __init__(self):
        # Define valid flags for each command
        self.command_flags = {
            't': ['all', 'rich', 'music', 'notify', 'silent', 'cache', 'nocache'],
            'torrent': ['all', 'rich', 'music', 'notify', 'silent', 'cache', 'nocache'],
            'torrents': ['all', 'rich', 'music', 'notify', 'silent', 'cache', 'nocache'],
            'dl': ['force', 'notify', 'silent', 'background'],
            'd': ['force', 'notify', 'silent'],
            'si': ['detailed', 'brief', 'cpu', 'memory', 'disk', 'network'],
            'sysinfo': ['detailed', 'brief', 'cpu', 'memory', 'disk', 'network'],
            'system_info': ['detailed', 'brief', 'cpu', 'memory', 'disk', 'network'],
            'monitor': ['start', 'stop', 'status', 'force'],
            'download_monitor': ['start', 'stop', 'status', 'force'],
            'tdiag': ['verbose', 'brief'],
            'qdiag': ['verbose', 'brief'],
        }
        
        # Pattern to match flags at the end: query:[flag1,flag2,flag3]
        self.flag_pattern = re.compile(r'^(.*):\[([^\]]+)\]$')
    
    def parse_command(self, command_text: str, command_name: str) -> Tuple[str, Dict[str, Any]]:
        """Parse command text to extract query and flags for a specific command."""
        # Split command into parts
        parts = command_text.strip().split()
        if len(parts) < 1:
            return "", self._get_default_flags(command_name)
        
        # Remove the command part (/t, /torrent, etc.)
        if len(parts) == 1:
            # Only command, no query
            return "", self._get_default_flags(command_name)
            
        query_with_flags = " ".join(parts[1:])
        
        # Check if there are flags at the end
        match = self.flag_pattern.match(query_with_flags)
        
        if not match:
            # No flags found, return the full query with default flags
            return query_with_flags, self._get_default_flags(command_name)
        
        # Extract query and flags
        query = match.group(1).strip()
        flags_str = match.group(2).strip()
        
        # Parse individual flags
        parsed_flags = self._parse_flags(flags_str, command_name)
        
        return query, parsed_flags
    
    def _get_default_flags(self, command_name: str) -> Dict[str, Any]:
        """Get default flags for a command."""
        defaults = {
            't': {'search_mode': 'normal', 'notify': False, 'use_cache': True},
            'torrent': {'search_mode': 'normal', 'notify': False, 'use_cache': True},
            'torrents': {'search_mode': 'normal', 'notify': False, 'use_cache': True},
            'dl': {'force': False, 'notify': False, 'background': False},
            'd': {'force': False, 'notify': False},
            'si': {'detail_level': 'normal'},
            'sysinfo': {'detail_level': 'normal'},
            'system_info': {'detail_level': 'normal'},
            'monitor': {'action': 'status'},
            'download_monitor': {'action': 'status'},
            'tdiag': {'verbose': False},
            'qdiag': {'verbose': False},
        }
        
        result = defaults.get(command_name, {})
        result['errors'] = []
        return result
    
    def _parse_flags(self, flags_str: str, command_name: str) -> Dict[str, Any]:
        """Parse the flags string into a dictionary for a specific command."""
        flags_dict = self._get_default_flags(command_name)
        
        # Get valid flags for this command
        valid_flags = self.command_flags.get(command_name, [])
        if not valid_flags:
            flags_dict['errors'].append(f"No flags supported for command '{command_name}'")
            return flags_dict
        
        # Split by comma and clean up
        individual_flags = [f.strip().lower() for f in flags_str.split(',') if f.strip()]
        
        for flag in individual_flags:
            if flag not in valid_flags:
                flags_dict['errors'].append(f"Unknown flag '{flag}' for command '{command_name}'")
                continue
            
            # Apply the flag based on command type
            self._apply_flag(flag, command_name, flags_dict)
        
        return flags_dict
    
    def _apply_flag(self, flag: str, command_name: str, flags_dict: Dict):
        """Apply a specific flag to the flags dictionary."""
        # Torrent command flags
        if command_name in ['t', 'torrent', 'torrents']:
            if flag in ['all', 'rich', 'music']:
                flags_dict['search_mode'] = flag
            elif flag == 'notify':
                flags_dict['notify'] = True
            elif flag == 'silent':
                flags_dict['notify'] = False
            elif flag == 'cache':
                flags_dict['use_cache'] = True
            elif flag == 'nocache':
                flags_dict['use_cache'] = False
        
        # Download command flags
        elif command_name in ['dl', 'd']:
            if flag == 'force':
                flags_dict['force'] = True
            elif flag == 'notify':
                flags_dict['notify'] = True
            elif flag == 'silent':
                flags_dict['notify'] = False
            elif flag == 'background':
                flags_dict['background'] = True
        
        # System info command flags
        elif command_name in ['si', 'sysinfo', 'system_info']:
            if flag == 'detailed':
                flags_dict['detail_level'] = 'detailed'
            elif flag == 'brief':
                flags_dict['detail_level'] = 'brief'
            elif flag in ['cpu', 'memory', 'disk', 'network']:
                flags_dict['detail_level'] = flag
        
        # Monitor command flags
        elif command_name in ['monitor', 'download_monitor']:
            if flag in ['start', 'stop', 'status']:
                flags_dict['action'] = flag
            elif flag == 'force':
                flags_dict['force'] = True
        
        # Diagnostic command flags
        elif command_name in ['tdiag', 'qdiag']:
            if flag == 'verbose':
                flags_dict['verbose'] = True
            elif flag == 'brief':
                flags_dict['verbose'] = False
    
    def get_legacy_flags(self, flags_dict: Dict[str, Any], command_name: str) -> Dict[str, bool]:
        """Convert new flag format to legacy boolean flags for compatibility."""
        if command_name in ['t', 'torrent', 'torrents']:
            search_mode = flags_dict.get('search_mode', 'normal')
            return {
                'rich_mode': search_mode == 'rich',
                'all_mode': search_mode == 'all', 
                'music_mode': search_mode == 'music',
                'notify': flags_dict.get('notify', False),
                'use_cache': flags_dict.get('use_cache', True)
            }
        elif command_name in ['dl', 'd']:
            return {
                'force': flags_dict.get('force', False),
                'notify': flags_dict.get('notify', False),
                'background': flags_dict.get('background', False)
            }
        elif command_name in ['si', 'sysinfo', 'system_info']:
            detail_level = flags_dict.get('detail_level', 'normal')
            return {
                'detailed': detail_level == 'detailed',
                'brief': detail_level == 'brief',
                'cpu_only': detail_level == 'cpu',
                'memory_only': detail_level == 'memory',
                'disk_only': detail_level == 'disk',
                'network_only': detail_level == 'network'
            }
        elif command_name in ['monitor', 'download_monitor']:
            return {
                'start': flags_dict.get('action') == 'start',
                'stop': flags_dict.get('action') == 'stop',
                'status': flags_dict.get('action') == 'status',
                'force': flags_dict.get('force', False)
            }
        else:
            return {}


# Global parser instance
flag_parser = FlagParser()


def parse_command_flags(command_text: str, command_name: str) -> Tuple[str, Dict[str, bool]]:
    """Convenience function to parse command flags and return legacy format."""
    query, flags_dict = flag_parser.parse_command(command_text, command_name)
    legacy_flags = flag_parser.get_legacy_flags(flags_dict, command_name)
    
    # Add error handling
    if flags_dict.get('errors'):
        legacy_flags['errors'] = flags_dict['errors']
    
    return query, legacy_flags


def get_usage_message(command_name: str) -> str:
    """Get the usage message for a specific command."""
    valid_flags = flag_parser.command_flags.get(command_name, [])
    
    if not valid_flags:
        return f"ℹ️ Command `/{command_name}` does not support flags."
    
    message = f"⚠️ Usage: `/{command_name} <query>:[flags]`\n\n"
    message += f"📋 **Available Flags for `/{command_name}`:**\n"
    
    for flag in valid_flags:
        message += f"• `{flag}`\n"
    
    message += f"\n📝 **Examples:**\n"
    if command_name in ['t', 'torrent', 'torrents']:
        message += f"• `/{command_name} ubuntu:[all]` - Search with all indexers\n"
        message += f"• `/{command_name} ubuntu:[rich,notify]` - Rich search with notification\n"
        message += f"• `/{command_name} ubuntu:[music]` - Music-focused search\n"
    elif command_name in ['dl', 'd']:
        message += f"• `/{command_name} file.torrent:[force]` - Force download\n"
        message += f"• `/{command_name} file.torrent:[notify,background]` - Download with notification in background\n"
    elif command_name in ['si', 'sysinfo', 'system_info']:
        message += f"• `/{command_name}:[detailed]` - Show detailed system info\n"
        message += f"• `/{command_name}:[cpu]` - Show only CPU info\n"
    elif command_name in ['monitor', 'download_monitor']:
        message += f"• `/{command_name}:[start]` - Start the monitor\n"
        message += f"• `/{command_name}:[stop]` - Stop the monitor\n"
    
    message += f"• `/{command_name} <query>` - Default behavior (no flags)\n"
    
    return message
