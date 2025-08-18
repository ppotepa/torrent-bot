"""
Universal flag parser that finds the last colon followed by square brackets.
This ensures that URLs with colons (like http://example.com:8080) are handled correctly.
"""

import re
from typing import Tuple, Dict, List, Any

def parse_universal_flags(command_text: str, command_name: str = None) -> Tuple[str, List[str], List[str]]:
    """
    Universal flag parser that finds the LAST colon followed by square brackets.
    
    Args:
        command_text: Full command text (e.g., "/t http://site:8080/search:[all,notify]")
        command_name: Optional command name for validation
    
    Returns:
        Tuple of (query, flags_list, errors_list)
        - query: The search query without flags
        - flags_list: List of individual flags found
        - errors_list: List of parsing errors
    """
    
    # Special case: check if flags are in the command itself (e.g., /si:[detailed])
    if ':' in command_text and command_text.count(' ') == 0:
        # Single token with colon, might be /command:[flags]
        command_flag_pattern = re.compile(r'^/([^:]+):(\[[^\]]+\])$')
        match = command_flag_pattern.match(command_text)
        if match:
            extracted_command = match.group(1)
            flags_part = match.group(2).strip()
            flags_str = flags_part[1:-1]  # Remove [ and ]
            flags_list = [f.strip().lower() for f in flags_str.split(',') if f.strip()]
            return "", flags_list, []
    
    # Split command into parts
    parts = command_text.strip().split()
    if len(parts) < 2:
        return "", [], []
    
    # Remove the command part (/t, /dl, etc.)
    query_with_flags = " ".join(parts[1:])
    
    # Special handling for different command types
    if command_name in ['dl', 'd']:
        # For download commands, flags can be in the URL part: /dl url:[flags] folder
        # We need to check if the first argument (URL) has flags
        if len(parts) >= 2:
            url_part = parts[1]
            folder_parts = parts[2:] if len(parts) > 2 else []
            
            # Check if URL has flags
            url_flag_pattern = re.compile(r'^(.*):(\[[^\]]+\])$')
            match = url_flag_pattern.match(url_part)
            
            if match:
                url = match.group(1).strip()
                flags_part = match.group(2).strip()
                folder = " ".join(folder_parts) if folder_parts else ""
                query = f"{url} {folder}".strip()
                
                # Extract flags
                flags_str = flags_part[1:-1]  # Remove [ and ]
                flags_list = [f.strip().lower() for f in flags_str.split(',') if f.strip()]
                return query, flags_list, []
            else:
                # No flags in URL, return full query
                return query_with_flags, [], []
    
    elif command_name in ['si', 'sysinfo', 'system_info', 'monitor', 'download_monitor']:
        # For commands that can have flags without a query: /si:[detailed], /monitor:[start]
        # Check if the entire arguments part is just flags
        flags_only_pattern = re.compile(r'^:(\[[^\]]+\])$')
        match = flags_only_pattern.match(query_with_flags)
        
        if match:
            flags_part = match.group(1).strip()
            flags_str = flags_part[1:-1]  # Remove [ and ]
            flags_list = [f.strip().lower() for f in flags_str.split(',') if f.strip()]
            return "", flags_list, []
        else:
            # Try the normal pattern as well for cases like /si system info:[detailed]
            last_colon_pattern = re.compile(r'^(.*):(\[[^\]]+\])$')
            match = last_colon_pattern.match(query_with_flags)
            
            if match:
                query = match.group(1).strip()
                flags_part = match.group(2).strip()
                flags_str = flags_part[1:-1]  # Remove [ and ]
                flags_list = [f.strip().lower() for f in flags_str.split(',') if f.strip()]
                return query, flags_list, []
    
    # Default pattern for most commands: find the LAST occurrence of :[flags] pattern
    last_colon_pattern = re.compile(r'^(.*):(\[[^\]]+\])$')
    match = last_colon_pattern.match(query_with_flags)
    
    if not match:
        # No flags found, return the full query
        return query_with_flags, [], []
    
    # Extract query and flags
    query = match.group(1).strip()
    flags_part = match.group(2).strip()
    
    # Remove the square brackets and split by comma
    flags_str = flags_part[1:-1]  # Remove [ and ]
    flags_list = [f.strip().lower() for f in flags_str.split(',') if f.strip()]
    
    return query, flags_list, []

def validate_command_flags(flags_list: List[str], command_name: str) -> Tuple[List[str], List[str]]:
    """
    Validate flags for a specific command.
    
    Args:
        flags_list: List of flags to validate
        command_name: Command name (t, dl, si, monitor, etc.)
    
    Returns:
        Tuple of (valid_flags, errors)
    """
    
    # Define valid flags for each command
    valid_flags_map = {
        't': ['all', 'rich', 'music', 'notify', 'silent', 'cache', 'nocache'],
        'torrent': ['all', 'rich', 'music', 'notify', 'silent', 'cache', 'nocache'],
        'torrents': ['all', 'rich', 'music', 'notify', 'silent', 'cache', 'nocache'],
        'dl': ['force', 'notify', 'silent', 'background', 'audio'],
        'd': ['force', 'notify', 'silent', 'audio'],
        'si': ['detailed', 'brief', 'cpu', 'memory', 'disk', 'network'],
        'sysinfo': ['detailed', 'brief', 'cpu', 'memory', 'disk', 'network'],
        'system_info': ['detailed', 'brief', 'cpu', 'memory', 'disk', 'network'],
        'monitor': ['start', 'stop', 'status', 'force'],
        'download_monitor': ['start', 'stop', 'status', 'force'],
    }
    
    # Define mutually exclusive flag groups
    exclusive_groups_map = {
        't': [['all', 'rich', 'music'], ['notify', 'silent'], ['cache', 'nocache']],
        'torrent': [['all', 'rich', 'music'], ['notify', 'silent'], ['cache', 'nocache']],
        'torrents': [['all', 'rich', 'music'], ['notify', 'silent'], ['cache', 'nocache']],
        'dl': [['notify', 'silent']],
        'd': [['notify', 'silent']],
        'si': [['detailed', 'brief'], ['cpu', 'memory', 'disk', 'network']],
        'sysinfo': [['detailed', 'brief'], ['cpu', 'memory', 'disk', 'network']],
        'system_info': [['detailed', 'brief'], ['cpu', 'memory', 'disk', 'network']],
        'monitor': [['start', 'stop']],
        'download_monitor': [['start', 'stop']],
    }
    
    valid_flags = valid_flags_map.get(command_name, [])
    exclusive_groups = exclusive_groups_map.get(command_name, [])
    
    errors = []
    validated_flags = []
    
    # Check if flags are valid
    for flag in flags_list:
        if flag not in valid_flags:
            errors.append(f"Unknown flag '{flag}' for command '{command_name}'")
        else:
            validated_flags.append(flag)
    
    # Check for mutually exclusive flags
    for group in exclusive_groups:
        found_in_group = [f for f in validated_flags if f in group]
        if len(found_in_group) > 1:
            errors.append(f"Conflicting flags: {', '.join(found_in_group)} are mutually exclusive")
    
    return validated_flags, errors

def convert_flags_to_legacy(flags_list: List[str], command_name: str) -> Dict[str, Any]:
    """
    Convert flag list to legacy format expected by existing code.
    
    Args:
        flags_list: List of validated flags
        command_name: Command name
    
    Returns:
        Dictionary with legacy flag format
    """
    
    if command_name in ['t', 'torrent', 'torrents']:
        result = {
            'rich_mode': 'rich' in flags_list,
            'all_mode': 'all' in flags_list,
            'music_mode': 'music' in flags_list,
            'notify': 'notify' in flags_list and 'silent' not in flags_list,
            'use_cache': 'nocache' not in flags_list  # Default to True unless nocache is specified
        }
    elif command_name in ['dl', 'd']:
        result = {
            'force': 'force' in flags_list,
            'notify': 'notify' in flags_list and 'silent' not in flags_list,
            'background': 'background' in flags_list,
            'audio': 'audio' in flags_list
        }
    elif command_name in ['si', 'sysinfo', 'system_info']:
        # Determine detail level
        if 'detailed' in flags_list:
            detail_level = 'detailed'
        elif 'brief' in flags_list:
            detail_level = 'brief'
        elif any(f in flags_list for f in ['cpu', 'memory', 'disk', 'network']):
            # Find which specific component was requested
            for comp in ['cpu', 'memory', 'disk', 'network']:
                if comp in flags_list:
                    detail_level = comp
                    break
        else:
            detail_level = 'normal'
        
        result = {
            'detailed': detail_level == 'detailed',
            'brief': detail_level == 'brief',
            'cpu_only': detail_level == 'cpu',
            'memory_only': detail_level == 'memory',
            'disk_only': detail_level == 'disk',
            'network_only': detail_level == 'network',
            'detail_level': detail_level
        }
    elif command_name in ['monitor', 'download_monitor']:
        # Determine action
        if 'start' in flags_list:
            action = 'start'
        elif 'stop' in flags_list:
            action = 'stop'
        else:
            action = 'status'  # default
        
        result = {
            'start': action == 'start',
            'stop': action == 'stop',
            'status': action == 'status',
            'force': 'force' in flags_list,
            'action': action
        }
    else:
        result = {}
    
    return result

# Example usage and test
if __name__ == "__main__":
    test_cases = [
        "/t ubuntu:[all,notify]",
        "/t ubuntu server 20.04:[all,notify]", 
        "/t http://example.com:8080/search:[rich]",
        "/t complex:query:with:colons:[music,notify]",
        "/dl https://youtube.com/watch?v=123:[force,background] MyFolder",
        "/si:[detailed]",
        "/monitor:[start,force]",
    ]
    
    for test in test_cases:
        print(f"\n--- Testing: {test} ---")
        
        # Extract command name properly
        full_command = test.split()[0][1:]  # Remove the '/' and get first part
        command_name = full_command.split(':')[0]  # Handle cases like 'si:[flags]'
        
        # Parse flags
        query, flags_list, parse_errors = parse_universal_flags(test, command_name)
        print(f"Query: '{query}'")
        print(f"Raw flags: {flags_list}")
        
        # Validate flags
        valid_flags, validation_errors = validate_command_flags(flags_list, command_name)
        print(f"Valid flags: {valid_flags}")
        
        # Convert to legacy format
        legacy_flags = convert_flags_to_legacy(valid_flags, command_name)
        print(f"Legacy format: {legacy_flags}")
        
        # Show any errors
        all_errors = parse_errors + validation_errors
        if all_errors:
            print(f"Errors: {all_errors}")
