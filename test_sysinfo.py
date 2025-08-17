#!/usr/bin/env python3
"""
Test script for system information formatting.
This helps verify that the /si command will work without Telegram API errors.
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from plugins.sysinfo import get_system_info, format_system_info

def test_sysinfo():
    """Test the system info gathering and formatting."""
    try:
        print("🔍 Testing system information gathering...")
        
        # Get system information
        info = get_system_info()
        
        # Format the information
        formatted_info = format_system_info(info)
        
        # Check for common problematic characters in Markdown (not relevant for HTML)
        # Since we're using HTML parsing now, most characters are safe
        markdown_chars = ['*', '_', '[', ']', '`', '\\']
        html_issues = []
        
        # Check for unescaped HTML characters that could cause issues
        if '&' in formatted_info and '&amp;' not in formatted_info:
            html_issues.append('unescaped &')
        if '<' in formatted_info and not ('<b>' in formatted_info or '<i>' in formatted_info or '<code>' in formatted_info):
            html_issues.append('unescaped <')
        if '>' in formatted_info and not ('</b>' in formatted_info or '</i>' in formatted_info or '</code>' in formatted_info):
            html_issues.append('unescaped >')
        
        print("✅ System info gathered successfully")
        print(f"📏 Formatted message length: {len(formatted_info)} characters")
        
        if html_issues:
            print(f"⚠️ Found HTML parsing issues: {html_issues}")
        else:
            print("✅ No HTML parsing issues found")
        
        # Check for Markdown characters (informational only since we use HTML)
        found_markdown = []
        for char in markdown_chars:
            if char in formatted_info:
                found_markdown.append(char)
        
        if found_markdown:
            print(f"ℹ️ Found Markdown characters (OK with HTML parsing): {found_markdown}")
        else:
            print("ℹ️ No Markdown characters found")
        
        # Check message length
        if len(formatted_info) > 4096:
            print("⚠️ Message exceeds Telegram's 4096 character limit")
        else:
            print("✅ Message length is within Telegram limits")
        
        print("\n" + "="*50)
        print("📄 FULL FORMATTED OUTPUT:")
        print("="*50)
        print(formatted_info)
        print("="*50)
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing system info: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_sysinfo()
    sys.exit(0 if success else 1)
