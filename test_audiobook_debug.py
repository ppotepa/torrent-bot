#!/usr/bin/env python3
"""
Test script to debug the audiobook TTS issue
"""

import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class MockMessage:
    def __init__(self, text, user_id=123456, chat_id=123456):
        self.text = text
        self.chat = MockChat(chat_id)
        self.from_user = MockUser(user_id)
        
class MockChat:
    def __init__(self, chat_id):
        self.id = chat_id

class MockUser:
    def __init__(self, user_id):
        self.id = user_id
        self.username = "test_user"

class MockBot:
    def send_message(self, chat_id, text, parse_mode=None):
        print(f"[BOT SEND] Chat {chat_id}: {text}")
        return MockMessage("status", 0, chat_id)
    
    def edit_message_text(self, text, chat_id, message_id, parse_mode=None):
        print(f"[BOT EDIT] Chat {chat_id}: {text}")
    
    def reply_to(self, message, text):
        print(f"[BOT REPLY] {text}")

def test_audiobook_command():
    """Test the audiobook command with the exact text that failed"""
    try:
        print("🔍 Starting audiobook debug test...")
        
        # Import the audiobook module
        from plugins import audiobook
        print("✅ Audiobook module imported successfully")
        
        # Create mock objects
        message = MockMessage("/ab test tesktu")  # Shorter text to avoid potential issues
        bot = MockBot()
        
        print(f"📝 Testing with message: {message.text}")
        
        # Try to call the audiobook function
        print("🎭 Calling handle_audiobook_command...")
        
        # Add more debugging
        print(f"📋 Function object: {audiobook.handle_audiobook_command}")
        print(f"📋 Message type: {type(message)}")
        print(f"📋 Bot type: {type(bot)}")
        
        audiobook.handle_audiobook_command(message, bot)
        print("✅ Function completed successfully")
        
    except Exception as e:
        print(f"❌ Error occurred: {e}")
        print(f"❌ Error type: {type(e)}")
        import traceback
        print("🔍 Full traceback:")
        traceback.print_exc()

if __name__ == "__main__":
    test_audiobook_command()
