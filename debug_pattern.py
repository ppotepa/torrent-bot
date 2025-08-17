#!/usr/bin/env python3
"""Test the current flag parsing with edge cases"""

import re

def test_current_pattern():
    # Current pattern from bot.py
    flag_pattern = re.compile(r'^(.*):\[([^\]]+)\]$')
    
    test_cases = [
        "/t ubuntu:[all,notify]",
        "/t ubuntu server 20.04:[all,notify]", 
        "/t http://example.com:8080/search:[rich]",
        "/t complex:query:with:colons:[music,notify]",
        "/t simple query",
        "/t query:[badFormat",
        "/t query:notSquareBrackets",
        "/t :[flags]",  # empty query
    ]
    
    print("=== Testing Current Pattern ===")
    for test in test_cases:
        # Simulate the parsing from bot.py
        parts = test.strip().split()
        if len(parts) < 2:
            query_with_flags = ""
        else:
            query_with_flags = " ".join(parts[1:])
        
        match = flag_pattern.match(query_with_flags)
        
        if match:
            query = match.group(1).strip()
            flags_str = match.group(2).strip()
            print(f"✅ '{test}' -> Query: '{query}', Flags: '{flags_str}'")
        else:
            print(f"❌ '{test}' -> No match (query: '{query_with_flags}')")
    
    print("\n=== Testing Better Pattern (Last Colon) ===")
    # Better pattern that finds the LAST colon followed by square brackets
    better_pattern = re.compile(r'^(.*):(\[[^\]]+\])$')
    
    for test in test_cases:
        parts = test.strip().split()
        if len(parts) < 2:
            query_with_flags = ""
        else:
            query_with_flags = " ".join(parts[1:])
        
        match = better_pattern.match(query_with_flags)
        
        if match:
            full_match = match.group(0)
            query_part = match.group(1).strip()
            flags_part = match.group(2).strip()
            flags_str = flags_part[1:-1]  # Remove [ and ]
            print(f"✅ '{test}' -> Query: '{query_part}', Flags: '{flags_str}'")
        else:
            print(f"❌ '{test}' -> No match (query: '{query_with_flags}')")

if __name__ == "__main__":
    test_current_pattern()
