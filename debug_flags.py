import re

def debug_parsing():
    test_cases = [
        "/si:[detailed]",
        "/monitor:[start,force]",
    ]
    
    for test in test_cases:
        print(f"\n--- Debugging: {test} ---")
        
        # Extract command name properly
        parts = test.strip().split()
        full_command = parts[0][1:]  # Remove the '/'
        # Split on colon to get just the command part
        command_name = full_command.split(':')[0]
        print(f"Command name: '{command_name}'")
        
        if len(parts) < 2:
            query_with_flags = ""
        else:
            query_with_flags = " ".join(parts[1:])
        
        print(f"Query with flags: '{query_with_flags}'")
        
        # Check the patterns
        flags_only_pattern = re.compile(r'^:(\[[^\]]+\])$')
        match = flags_only_pattern.match(query_with_flags)
        print(f"Flags-only pattern match: {match}")
        
        if match:
            flags_part = match.group(1).strip()
            print(f"Flags part: '{flags_part}'")
            flags_str = flags_part[1:-1]  # Remove [ and ]
            print(f"Flags string: '{flags_str}'")
            flags_list = [f.strip().lower() for f in flags_str.split(',') if f.strip()]
            print(f"Flags list: {flags_list}")

if __name__ == "__main__":
    debug_parsing()
