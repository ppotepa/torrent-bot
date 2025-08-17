#!/usr/bin/env python3
"""
Test script for the flag parser module.
Tests the new flag format parsing functionality.
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flag_parser import FlagParser, parse_command_flags, get_usage_message


def test_flag_parsing():
    """Test the flag parsing functionality."""
    print("🧪 Testing Flag Parser...")
    print("=" * 50)
    
    parser = FlagParser()
    
    test_cases = [
        # (input, expected_query, expected_flags)
        ("/t ubuntu:[all,notify]", "ubuntu", {'search_mode': 'all', 'notify': True}),
        ("/t ubuntu:[rich]", "ubuntu", {'search_mode': 'rich', 'notify': False}),
        ("/t ubuntu:[music,notify]", "ubuntu", {'search_mode': 'music', 'notify': True}),
        ("/t ubuntu", "ubuntu", {'search_mode': 'normal', 'notify': False}),
        ("/t ubuntu linux iso:[all]", "ubuntu linux iso", {'search_mode': 'all', 'notify': False}),
        ("/t game of thrones:[rich,notify]", "game of thrones", {'search_mode': 'rich', 'notify': True}),
        ("/t :[all]", ":[all]", {'search_mode': 'normal', 'notify': False}),  # Edge case - no pattern match
        ("/t ubuntu:[invalid,rich]", "ubuntu", {'search_mode': 'rich', 'notify': False}),  # Invalid flag
        ("/t ubuntu:[all,rich]", "ubuntu", {'search_mode': 'rich', 'notify': False}),  # Multiple search modes
    ]
    
    all_passed = True
    
    for i, (input_text, expected_query, expected_partial_flags) in enumerate(test_cases, 1):
        print(f"\n🔬 Test {i}: {input_text}")
        
        try:
            query, flags_dict = parser.parse_command(input_text)
            
            # Check query
            if query != expected_query:
                print(f"❌ Query mismatch. Expected: '{expected_query}', Got: '{query}'")
                all_passed = False
                continue
            
            # Check key flags
            query_passed = True
            for key, expected_value in expected_partial_flags.items():
                if flags_dict.get(key) != expected_value:
                    print(f"❌ Flag mismatch for '{key}'. Expected: {expected_value}, Got: {flags_dict.get(key)}")
                    query_passed = False
                    all_passed = False
            
            if query_passed:
                print(f"✅ Passed - Query: '{query}', Flags: {flags_dict}")
            
            # Test legacy conversion
            legacy_flags = parser.get_legacy_flags(flags_dict)
            print(f"🔄 Legacy format: {legacy_flags}")
            
            # Show any errors
            if flags_dict.get('errors'):
                print(f"⚠️ Errors: {flags_dict['errors']}")
            
        except Exception as e:
            print(f"❌ Exception: {e}")
            all_passed = False
    
    print("\n" + "=" * 50)
    
    # Test convenience function
    print("\n🧪 Testing convenience function...")
    query, legacy_flags = parse_command_flags("/t ubuntu:[all,notify]")
    print(f"Query: '{query}'")
    print(f"Legacy flags: {legacy_flags}")
    
    # Test usage message
    print("\n📖 Usage message:")
    print(get_usage_message())
    
    if all_passed:
        print("\n✅ All flag parsing tests passed!")
        return True
    else:
        print("\n❌ Some flag parsing tests failed!")
        return False


if __name__ == "__main__":
    success = test_flag_parsing()
    sys.exit(0 if success else 1)
