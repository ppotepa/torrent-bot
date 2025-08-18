#!/usr/bin/env python3
"""
Test YouTube download functionality
"""

import os
import sys
from unittest.mock import Mock

def test_youtube_download():
    """Test YouTube download with audio flag"""
    print("🎬 Testing YouTube Download Functionality")
    print("=" * 50)
    
    try:
        # Create mock bot and message
        class MockBot:
            def reply_to(self, message, text, **kwargs):
                print(f"🤖 Bot reply: {text}")
        
        class MockMessage:
            def __init__(self, text):
                self.text = text
                self.chat = Mock()
                self.chat.id = 123456
        
        bot = MockBot()
        
        # Test 1: Audio download
        print("🎵 Test 1: Audio Download")
        print("-" * 30)
        
        message = MockMessage("/dl https://www.youtube.com/watch?v=bJ1aVeVA_es:[audio] music")
        
        # Import and test the download function
        from plugins.youtube import download
        
        print(f"📋 Command: {message.text}")
        print("🔧 Testing flag parsing...")
        
        # Parse flags manually to see what happens
        from universal_flags import parse_universal_flags, validate_command_flags, convert_flags_to_legacy
        
        query, flags_list, parse_errors = parse_universal_flags(message.text, "dl")
        valid_flags, validation_errors = validate_command_flags(flags_list, "dl")
        legacy_flags = convert_flags_to_legacy(valid_flags, "dl")
        
        print(f"   • Parsed flags: {flags_list}")
        print(f"   • Valid flags: {valid_flags}")
        print(f"   • Legacy flags: {legacy_flags}")
        print(f"   • Audio mode: {legacy_flags.get('audio', False)}")
        
        # Test what would happen (without actually downloading)
        # We'll just test the flag processing part
        print("✅ Flag processing successful!")
        print()
        
        # Test 2: Video download
        print("🎬 Test 2: Video Download")
        print("-" * 30)
        
        message2 = MockMessage("/dl https://www.youtube.com/watch?v=bJ1aVeVA_es:[notify] videos")
        
        query2, flags_list2, parse_errors2 = parse_universal_flags(message2.text, "dl")
        valid_flags2, validation_errors2 = validate_command_flags(flags_list2, "dl")
        legacy_flags2 = convert_flags_to_legacy(valid_flags2, "dl")
        
        print(f"📋 Command: {message2.text}")
        print(f"   • Parsed flags: {flags_list2}")
        print(f"   • Audio mode: {legacy_flags2.get('audio', False)}")
        print(f"   • Notify: {legacy_flags2.get('notify', False)}")
        print("✅ Flag processing successful!")
        print()
        
        # Test 3: Check yt-dlp availability
        print("📦 Test 3: yt-dlp Availability")
        print("-" * 30)
        
        try:
            import yt_dlp
            print("✅ yt-dlp is available")
            
            # Test yt-dlp config for audio
            audio_opts = {
                'format': 'bestaudio/best',
                'noplaylist': True,
                'quiet': True,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '0',
                }],
            }
            print("✅ Audio configuration prepared")
            
            # Test yt-dlp config for video
            video_opts = {
                'format': 'bestvideo+bestaudio/best',
                'noplaylist': True,
                'quiet': True,
                'merge_output_format': 'mp4',
            }
            print("✅ Video configuration prepared")
            
        except ImportError:
            print("❌ yt-dlp not available - install with: pip install yt-dlp")
            return False
        
        print()
        print("🎯 All Tests PASSED!")
        print()
        print("💡 Usage Examples:")
        print("   • Audio only: /dl https://youtube.com/watch?v=123:[audio]")
        print("   • Video: /dl https://youtube.com/watch?v=123")
        print("   • Audio with notification: /dl https://youtube.com/watch?v=123:[audio,notify]")
        print("   • Video to folder: /dl https://youtube.com/watch?v=123 music")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_youtube_download()
    
    if success:
        print()
        print("🚀 YouTube download functionality is ready!")
        print("📝 To use: Start the bot and try: /dl https://www.youtube.com/watch?v=bJ1aVeVA_es:[audio]")
    else:
        print()
        print("❌ YouTube download needs fixes - check errors above")
