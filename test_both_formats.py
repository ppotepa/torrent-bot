#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from universal_flags import parse_universal_flags, validate_command_flags, convert_flags_to_legacy

print("=== Testing Flag Parsing ===")

print("\n1. NEW format: /t guns flac:[all]")
query1, flags1, errors1 = parse_universal_flags('/t guns flac:[all]', 't')
valid_flags1, val_errors1 = validate_command_flags(flags1, 't')
legacy1 = convert_flags_to_legacy(valid_flags1, 't')
print(f"Query: {repr(query1)}")
print(f"Flags: {flags1}")
print(f"all_mode: {legacy1.get('all_mode', False)}")

print("\n2. OLD format: /t guns flac all")
query2, flags2, errors2 = parse_universal_flags('/t guns flac all', 't')
valid_flags2, val_errors2 = validate_command_flags(flags2, 't')
legacy2 = convert_flags_to_legacy(valid_flags2, 't')
print(f"Query: {repr(query2)}")
print(f"Flags: {flags2}")
print(f"all_mode: {legacy2.get('all_mode', False)}")

print("\n3. Query analysis:")
words = query2.split()
print(f"OLD query words: {words}")
print(f"Contains 'all': {'all' in words}")
