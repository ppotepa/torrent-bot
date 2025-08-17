#!/usr/bin/env python3
"""Test the new command-specific flag parser."""

from flag_parser import parse_command_flags, get_usage_message

def test_torrent_command():
    print("=== Testing Torrent Command (/t) ===")
    
    # Test valid flags
    query, flags = parse_command_flags("/t ubuntu:[all,notify]", "t")
    print(f"Query: '{query}', Flags: {flags}")
    assert query == "ubuntu"
    assert flags['all_mode'] == True
    assert flags['notify'] == True
    
    # Test conflicting flags
    query, flags = parse_command_flags("/t ubuntu:[all,rich]", "t")
    print(f"Query: '{query}', Flags: {flags}")
    assert 'errors' in flags
    
    # Test no flags
    query, flags = parse_command_flags("/t ubuntu", "t")
    print(f"Query: '{query}', Flags: {flags}")
    assert query == "ubuntu"
    assert flags['all_mode'] == False
    
    print("✅ Torrent command tests passed!\n")

def test_download_command():
    print("=== Testing Download Command (/dl) ===")
    
    # Test valid flags
    query, flags = parse_command_flags("/dl file.torrent:[force,background]", "dl")
    print(f"Query: '{query}', Flags: {flags}")
    assert query == "file.torrent"
    assert flags['force'] == True
    assert flags['background'] == True
    
    # Test invalid flag
    query, flags = parse_command_flags("/dl file.torrent:[all]", "dl")
    print(f"Query: '{query}', Flags: {flags}")
    assert 'errors' in flags
    
    print("✅ Download command tests passed!\n")

def test_sysinfo_command():
    print("=== Testing System Info Command (/si) ===")
    
    # Test valid flags
    query, flags = parse_command_flags("/si:[detailed]", "si")
    print(f"Query: '{query}', Flags: {flags}")
    assert query == ""
    assert flags['detailed'] == True
    
    # Test conflicting flags
    query, flags = parse_command_flags("/si:[detailed,brief]", "si")
    print(f"Query: '{query}', Flags: {flags}")
    assert 'errors' in flags
    
    print("✅ System info command tests passed!\n")

def test_monitor_command():
    print("=== Testing Monitor Command (/monitor) ===")
    
    # Test valid flags
    query, flags = parse_command_flags("/monitor:[start]", "monitor")
    print(f"Query: '{query}', Flags: {flags}")
    assert query == ""
    assert flags['start'] == True
    
    # Test conflicting flags
    query, flags = parse_command_flags("/monitor:[start,stop]", "monitor")
    print(f"Query: '{query}', Flags: {flags}")
    assert 'errors' in flags
    
    print("✅ Monitor command tests passed!\n")

def test_usage_messages():
    print("=== Testing Usage Messages ===")
    
    usage_t = get_usage_message("t")
    print("Torrent usage message:")
    print(usage_t)
    print()
    
    usage_dl = get_usage_message("dl")
    print("Download usage message:")
    print(usage_dl)
    print()
    
    usage_si = get_usage_message("si")
    print("System info usage message:")
    print(usage_si)
    print()
    
    print("✅ Usage message tests passed!\n")

if __name__ == "__main__":
    test_torrent_command()
    test_download_command()
    test_sysinfo_command()
    test_monitor_command()
    test_usage_messages()
    print("🎉 All tests passed!")
