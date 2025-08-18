#!/usr/bin/env python3

"""
Debug script to test audiobook plugin functions directly
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

# Import the audiobook plugin functions
from plugins.audiobook import convert_inline_text, convert_text_to_speech, detect_language

class MockBot:
    """Mock bot for testing"""
    def __init__(self):
        self.messages = []
    
    def reply_to(self, message, text):
        print(f"📤 Bot reply: {text}")
        self.messages.append(text)
    
    def send_voice(self, chat_id, audio_file, caption=None, duration=None):
        print(f"🎙️ Bot sending VOICE MESSAGE: {caption}")

class MockMessage:
    """Mock message for testing"""
    def __init__(self, text, user_id=12345, chat_id=67890):
        self.text = text
        self.from_user = MockUser(user_id)
        self.chat = MockChat(chat_id)

class MockUser:
    def __init__(self, user_id):
        self.id = user_id

class MockChat:
    def __init__(self, chat_id):
        self.id = chat_id

def test_simple_ab_command():
    """Test simple /ab command like user reported"""
    print("🧪 Testing simple /ab command that's failing...")
    
    bot = MockBot()
    message = MockMessage("/ab Hello world, this is a test")
    
    try:
        # Import the handle function
        from plugins.audiobook import handle_audiobook_command
        
        print("📝 Calling handle_audiobook_command...")
        handle_audiobook_command(bot, message)
        
        print("✅ Command completed successfully")
        
    except Exception as e:
        print(f"❌ Error in handle_audiobook_command: {e}")
        import traceback
        traceback.print_exc()

def test_enhanced_flag():
    """Test enhanced flag specifically"""
    print("\n🧪 Testing enhanced flag...")
    
    bot = MockBot()
    message = MockMessage("/ab Hello world --enhanced_sapi")
    
    try:
        from plugins.audiobook import handle_audiobook_command
        
        print("📝 Calling handle_audiobook_command with enhanced flag...")
        handle_audiobook_command(bot, message)
        
        print("✅ Enhanced flag command completed successfully")
        
    except Exception as e:
        print(f"❌ Error with enhanced flag: {e}")
        import traceback
        traceback.print_exc()

def test_detect_language():
    """Test language detection"""
    print("\n🧪 Testing language detection...")
    
    try:
        test_texts = [
            "Hello world, this is a test",
            "Witaj świecie, to jest test",
            "Good morning everyone"
        ]
        
        for text in test_texts:
            detected = detect_language(text)
            print(f"Text: '{text}' -> Language: {detected}")
            
    except Exception as e:
        print(f"❌ Error in language detection: {e}")
        import traceback
        traceback.print_exc()

def test_direct_convert():
    """Test direct convert_text_to_speech function"""
    print("\n🧪 Testing convert_text_to_speech directly...")
    
    try:
        os.makedirs('audiobooks', exist_ok=True)
        output_path = 'audiobooks/debug_test.mp3'
        
        success = convert_text_to_speech(
            text="Hello world, this is a test",
            language="en",
            output_path=output_path,
            voice_type="female",
            engine="enhanced_sapi"
        )
        
        print(f"Direct conversion result: {success}")
        if os.path.exists(output_path):
            print(f"✅ File created: {os.path.getsize(output_path)} bytes")
        
    except Exception as e:
        print(f"❌ Error in direct conversion: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🔍 Audiobook Plugin Debug Tests")
    print("=" * 50)
    
    test_detect_language()
    test_direct_convert()
    test_simple_ab_command()
    test_enhanced_flag()
    
    print("\n🏁 Debug tests completed")
