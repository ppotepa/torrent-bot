#!/usr/bin/env python3

"""
Test script for Facebook audio download functionality
"""

import os
import sys
import tempfile
import shutil

# Add the current directory to Python path so we can import our modules
sys.path.insert(0, os.getcwd())

from universal_flags import parse_universal_flags, validate_command_flags

def test_facebook_flag_parsing():
    """Test that audio flags are parsed correctly for Facebook downloads"""
    print("🧪 Testing Facebook audio flag parsing...")
    
    test_cases = [
        {
            'input': '/dl https://facebook.com/video:[audio]',
            'expected_mode': 'audio',
            'description': 'Audio flag in URL'
        },
        {
            'input': '/dl https://facebook.com/video test_folder',
            'expected_mode': 'video', 
            'description': 'No audio flag - should default to video'
        },
        {
            'input': '/dl https://facebook.com/video:[audio] my_folder',
            'expected_mode': 'audio',
            'description': 'Audio flag with folder'
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n  Test {i}: {case['description']}")
        print(f"    Input: {case['input']}")
        
        query, flags_list, parse_errors = parse_universal_flags(case['input'], 'dl')
        valid_flags, validation_errors = validate_command_flags(flags_list, 'dl')
        
        if parse_errors:
            print(f"    ❌ Parse errors: {parse_errors}")
            continue
            
        if validation_errors:
            print(f"    ❌ Validation errors: {validation_errors}")
            continue
            
        mode = "audio" if "audio" in valid_flags else "video"
        
        if mode == case['expected_mode']:
            print(f"    ✅ Correctly detected mode: {mode}")
        else:
            print(f"    ❌ Expected {case['expected_mode']}, got {mode}")
            
        print(f"    📝 Valid flags: {valid_flags}")
        print(f"    📝 All flags found: {flags_list}")

def test_facebook_import():
    """Test that the Facebook plugin can be imported and has the right functions"""
    print("\n🧪 Testing Facebook plugin import...")
    
    try:
        from plugins import facebook
        print("  ✅ Facebook plugin imported successfully")
        
        # Check for required functions
        if hasattr(facebook, 'download'):
            print("  ✅ download() function found")
        else:
            print("  ❌ download() function missing")
            
        if hasattr(facebook, 'run'):
            print("  ✅ run() function found")
        else:
            print("  ❌ run() function missing")
            
    except ImportError as e:
        print(f"  ❌ Failed to import Facebook plugin: {e}")

def test_mp3_config():
    """Test that yt-dlp configuration is correct for MP3 output"""
    print("\n🧪 Testing MP3 configuration...")
    
    try:
        from plugins.facebook import run
        import inspect
        
        # Get the source code to check the configuration
        source = inspect.getsource(run)
        
        if "'preferredcodec': 'mp3'" in source:
            print("  ✅ MP3 codec configuration found")
        else:
            print("  ❌ MP3 codec configuration missing")
            
        if "FFmpegExtractAudio" in source:
            print("  ✅ FFmpeg audio extraction configured")
        else:
            print("  ❌ FFmpeg audio extraction missing")
            
        if "'preferredquality': '0'" in source:
            print("  ✅ Best quality setting found")
        else:
            print("  ❌ Quality setting missing or incorrect")
            
    except Exception as e:
        print(f"  ❌ Error checking MP3 configuration: {e}")

if __name__ == "__main__":
    print("🔍 Facebook Audio Download Test Suite")
    print("=" * 50)
    
    test_facebook_flag_parsing()
    test_facebook_import()
    test_mp3_config()
    
    print("\n" + "=" * 50)
    print("✅ Test suite completed!")
    print("\nTo test with a real Facebook video:")
    print("  /dl https://facebook.com/watch?v=VIDEO_ID:[audio]")
    print("  - This should download as MP3 audio")
    print("  - The permission error should be resolved")
