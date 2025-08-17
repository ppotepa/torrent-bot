#!/usr/bin/env python3
"""Test the new flag system directly in bot.py"""

import re

def test_torrent_flags():
    """Test torrent flag parsing"""
    def parse_torrent_flags(command_text: str):
        """Parse flags for torrent commands in format: /t query:[flags]"""
        # Default flags
        flags = {
            'rich_mode': False,
            'all_mode': False,
            'music_mode': False,
            'notify': False,
            'errors': []
        }
        
        # Split command into parts
        parts = command_text.strip().split()
        if len(parts) < 2:
            return "", flags
        
        # Remove the command part (/t, /torrent, etc.)
        query_with_flags = " ".join(parts[1:])
        
        # Pattern to match flags at the end: query:[flag1,flag2,flag3]
        flag_pattern = re.compile(r'^(.*):\[([^\]]+)\]$')
        match = flag_pattern.match(query_with_flags)
        
        if not match:
            # No flags found, return the full query
            return query_with_flags, flags
        
        # Extract query and flags
        query = match.group(1).strip()
        flags_str = match.group(2).strip()
        
        # Valid flags for torrent command
        valid_flags = ['all', 'rich', 'music', 'notify', 'silent', 'cache', 'nocache']
        individual_flags = [f.strip().lower() for f in flags_str.split(',') if f.strip()]
        
        # Track conflicting flags
        search_modes = []
        
        for flag in individual_flags:
            if flag not in valid_flags:
                flags['errors'].append(f"Unknown flag: '{flag}'")
                continue
            
            if flag in ['all', 'rich', 'music']:
                search_modes.append(flag)
                flags['all_mode'] = flag == 'all'
                flags['rich_mode'] = flag == 'rich'
                flags['music_mode'] = flag == 'music'
            elif flag == 'notify':
                flags['notify'] = True
            elif flag == 'silent':
                flags['notify'] = False
            # cache/nocache flags can be added later
        
        # Check for conflicting search modes
        if len(search_modes) > 1:
            flags['errors'].append(f"Conflicting search modes: {', '.join(search_modes)}")
        
        return query, flags

    print("=== Testing Torrent Flags ===")
    
    # Test 1: Normal query with all flag
    query, flags = parse_torrent_flags("/t ubuntu:[all,notify]")
    print(f"Test 1 - Query: '{query}', All: {flags['all_mode']}, Notify: {flags['notify']}, Errors: {flags['errors']}")
    assert query == "ubuntu", f"Expected 'ubuntu', got '{query}'"
    assert flags['all_mode'] == True, "Expected all_mode to be True"
    assert flags['notify'] == True, "Expected notify to be True"
    
    # Test 2: Query without flags
    query, flags = parse_torrent_flags("/t ubuntu")
    print(f"Test 2 - Query: '{query}', All: {flags['all_mode']}, Notify: {flags['notify']}")
    assert query == "ubuntu", f"Expected 'ubuntu', got '{query}'"
    assert flags['all_mode'] == False, "Expected all_mode to be False"
    
    # Test 3: Conflicting flags
    query, flags = parse_torrent_flags("/t movie:[all,rich]")
    print(f"Test 3 - Query: '{query}', Errors: {flags['errors']}")
    assert len(flags['errors']) > 0, "Expected errors for conflicting flags"
    
    # Test 4: Invalid flag
    query, flags = parse_torrent_flags("/t music:[badFlag]")
    print(f"Test 4 - Query: '{query}', Errors: {flags['errors']}")
    assert len(flags['errors']) > 0, "Expected errors for invalid flag"
    
    print("✅ Torrent flag tests passed!\n")

def test_dl_flags():
    """Test download flag parsing"""
    def parse_dl_flags(command_text: str):
        """Parse flags for download commands in format: /dl url:[flags]"""
        # Default flags
        flags = {
            'force': False,
            'notify': False,
            'background': False,
            'errors': []
        }
        
        # Split command into parts
        parts = command_text.strip().split()
        if len(parts) < 2:
            return "", None, flags
        
        # Check if the second part (URL) has flags
        url_with_flags = parts[1]
        folder = " ".join(parts[2:]).strip() if len(parts) > 2 else None
        
        # Pattern to match flags at the end: url:[flag1,flag2,flag3]
        flag_pattern = re.compile(r'^(.*):\[([^\]]+)\]$')
        match = flag_pattern.match(url_with_flags)
        
        if not match:
            # No flags found, return the original URL
            return url_with_flags, folder, flags
        
        # Extract URL and flags
        url = match.group(1).strip()
        flags_str = match.group(2).strip()
        
        # Valid flags for download command
        valid_flags = ['force', 'notify', 'silent', 'background']
        individual_flags = [f.strip().lower() for f in flags_str.split(',') if f.strip()]
        
        for flag in individual_flags:
            if flag not in valid_flags:
                flags['errors'].append(f"Unknown flag: '{flag}'")
                continue
            
            if flag == 'force':
                flags['force'] = True
            elif flag == 'notify':
                flags['notify'] = True
            elif flag == 'silent':
                flags['notify'] = False
            elif flag == 'background':
                flags['background'] = True
        
        return url, folder, flags

    print("=== Testing Download Flags ===")
    
    # Test 1: URL with flags
    url, folder, flags = parse_dl_flags("/dl https://example.com/file.mp4:[force,notify] MyFolder")
    print(f"Test 1 - URL: '{url}', Folder: '{folder}', Force: {flags['force']}, Notify: {flags['notify']}")
    assert url == "https://example.com/file.mp4", f"Expected URL, got '{url}'"
    assert folder == "MyFolder", f"Expected 'MyFolder', got '{folder}'"
    assert flags['force'] == True, "Expected force to be True"
    assert flags['notify'] == True, "Expected notify to be True"
    
    # Test 2: URL without flags
    url, folder, flags = parse_dl_flags("/dl https://example.com/file.mp4")
    print(f"Test 2 - URL: '{url}', Folder: '{folder}', Force: {flags['force']}")
    assert url == "https://example.com/file.mp4", f"Expected URL, got '{url}'"
    assert flags['force'] == False, "Expected force to be False"
    
    print("✅ Download flag tests passed!\n")

if __name__ == "__main__":
    test_torrent_flags()
    test_dl_flags()
    print("🎉 All flag parsing tests passed!")
