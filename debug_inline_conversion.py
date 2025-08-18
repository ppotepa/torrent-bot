#!/usr/bin/env python3

"""
Test specific inline audiobook conversion to trace the issue
"""

import os
import sys

# Add the current directory to Python path so we can import our modules  
sys.path.insert(0, os.getcwd())

def test_inline_conversion_detailed():
    """Test inline conversion with detailed logging"""
    print("🎯 Testing Inline Conversion Process")
    print("=" * 40)
    
    try:
        from plugins.audiobook import handle_audiobook_command, AUDIOBOOK_DIR
        from universal_flags import parse_universal_flags, validate_command_flags
        
        # Create mock message and bot
        class MockMessage:
            def __init__(self, text):
                self.text = text
                self.chat = MockChat()
                
        class MockChat:
            def __init__(self):
                self.id = 12345
        
        class MockBot:
            def __init__(self):
                self.messages = []
                self.audio_files = []
                
            def reply_to(self, message, text, parse_mode=None):
                print(f"📱 Bot Reply: {text}")
                self.messages.append(text)
                
            def send_audio(self, chat_id, audio, caption=None, title=None, performer=None):
                print(f"🎵 Bot Sending Audio: {audio}")
                print(f"   Caption: {caption}")
                self.audio_files.append(audio)
                
            def send_message(self, chat_id, text, parse_mode=None):
                print(f"📱 Bot Message: {text}")
                self.messages.append(text)
        
        # Test inline command
        test_command = "/ab Hello world this is a test inline conversion:[inline,eng]"
        print(f"📝 Test command: {test_command}")
        
        message = MockMessage(test_command)
        bot = MockBot()
        
        # Check directory before
        print(f"\n📁 Files before conversion:")
        if os.path.exists(AUDIOBOOK_DIR):
            files_before = os.listdir(AUDIOBOOK_DIR)
            print(f"   {files_before}")
        else:
            print("   Directory doesn't exist")
            files_before = []
        
        # Run the conversion
        print(f"\n🔄 Running conversion...")
        try:
            handle_audiobook_command(bot, message)
            print(f"✅ Conversion completed without errors")
        except Exception as e:
            print(f"❌ Conversion error: {e}")
            return False
        
        # Check directory after
        print(f"\n📁 Files after conversion:")
        if os.path.exists(AUDIOBOOK_DIR):
            files_after = os.listdir(AUDIOBOOK_DIR)
            print(f"   {files_after}")
            
            # Check for new files
            new_files = [f for f in files_after if f not in files_before]
            if new_files:
                print(f"✅ New files created: {new_files}")
                
                # Check file details
                for file in new_files:
                    file_path = os.path.join(AUDIOBOOK_DIR, file)
                    size = os.path.getsize(file_path)
                    print(f"   📄 {file}: {size} bytes")
                    
            else:
                print(f"❌ No new files created")
        else:
            print("   Directory still doesn't exist")
            files_after = []
        
        # Check bot responses
        print(f"\n📱 Bot responses ({len(bot.messages)}):")
        for i, msg in enumerate(bot.messages, 1):
            print(f"   {i}. {msg}")
        
        print(f"\n🎵 Audio files sent ({len(bot.audio_files)}):")
        for i, audio in enumerate(bot.audio_files, 1):
            print(f"   {i}. {audio}")
        
        return len(new_files) > 0 if 'new_files' in locals() else False
        
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_flag_parsing():
    """Test the flag parsing for inline commands"""
    print("\n🏷️ Testing Flag Parsing")
    print("=" * 25)
    
    try:
        from universal_flags import parse_universal_flags, validate_command_flags
        
        test_command = "/ab Hello world test:[inline,eng]"
        print(f"📝 Command: {test_command}")
        
        # Parse flags
        query, flags_list, parse_errors = parse_universal_flags(test_command, 'ab')
        print(f"📊 Parsed query: '{query}'")
        print(f"🏷️ Parsed flags: {flags_list}")
        
        if parse_errors:
            print(f"❌ Parse errors: {parse_errors}")
            return False
        
        # Validate flags
        valid_flags, validation_errors = validate_command_flags(flags_list, 'ab')
        print(f"✅ Valid flags: {valid_flags}")
        
        if validation_errors:
            print(f"❌ Validation errors: {validation_errors}")
            return False
        
        # Check inline detection
        has_inline = 'inline' in valid_flags
        print(f"📝 Inline mode detected: {has_inline}")
        
        return has_inline
        
    except Exception as e:
        print(f"❌ Flag parsing error: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Detailed Inline Conversion Test")
    print("=" * 45)
    
    # Test flag parsing first
    flag_test = test_flag_parsing()
    
    if flag_test:
        # Test conversion if flags work
        conversion_test = test_inline_conversion_detailed()
        
        print(f"\n{'=' * 45}")
        print("📊 Test Results:")
        print(f"   Flag Parsing: {'✅' if flag_test else '❌'}")
        print(f"   Conversion: {'✅' if conversion_test else '❌'}")
        
        if not conversion_test:
            print("\n💡 Possible issues:")
            print("   - TTS conversion failing silently")
            print("   - Files being created but cleaned up")
            print("   - Path issues in file creation")
            print("   - Permission problems")
            
    else:
        print("\n❌ Flag parsing failed - cannot test conversion")
