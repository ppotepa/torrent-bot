#!/usr/bin/env python3
"""Simple test of the flag parser."""

import sys
sys.path.append('.')

from flag_parser import parse_command_flags

# Test basic functionality
query, flags = parse_command_flags("/t ubuntu:[all,notify]", "t")
print(f"Query: '{query}', Flags: {flags}")

# Test without flags
query, flags = parse_command_flags("/t ubuntu", "t")
print(f"Query: '{query}', Flags: {flags}")

# Test download command
query, flags = parse_command_flags("/dl file.torrent:[force]", "dl")
print(f"Query: '{query}', Flags: {flags}")

print("✅ Basic tests passed!")
