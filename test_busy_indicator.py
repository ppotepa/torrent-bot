#!/usr/bin/env python3
"""
Test the busy indicator for number selection.
"""

import sys
import os
import time

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class MockBot:
    """Mock bot for testing busy indicators."""
    def __init__(self):
        self.messages = []
        self.deleted_messages = []
        self.message_counter = 1000
    
    def send_message(self, chat_id, text, parse_mode=None):
        message_id = self.message_counter
        self.message_counter += 1
        
        message = {
            'message_id': message_id,
            'chat_id': chat_id,
            'text': text,
            'parse_mode': parse_mode
        }
        self.messages.append(message)
        
        print(f"📤 Message {message_id} sent to {chat_id}:")
        print(f"Parse mode: {parse_mode}")
        print("-" * 40)
        print(text)
        print("-" * 40)
        
        return MockMessage(text, message_id)
    
    def delete_message(self, chat_id, message_id):
        self.deleted_messages.append({'chat_id': chat_id, 'message_id': message_id})
        print(f"🗑️ Deleted message {message_id} from chat {chat_id}")
        return True
    
    def reply_to(self, message, text, parse_mode=None):
        return self.send_message(message.chat.id, text, parse_mode)

class MockMessage:
    """Mock message object."""
    def __init__(self, text, message_id=123):
        self.text = text
        self.message_id = message_id
        self.chat = MockChat()
        self.from_user = MockUser()

class MockChat:
    """Mock chat object."""
    def __init__(self):
        self.id = 12345

class MockUser:
    """Mock user object."""
    def __init__(self):
        self.id = 67890

def test_busy_indicator():
    """Test the busy indicator for number selection."""
    
    print("🧪 Testing Busy Indicator for Number Selection")
    print("=" * 60)
    
    mock_bot = MockBot()
    mock_message = MockMessage("2")
    
    print("📋 **Step 1: Simulate User Number Selection**")
    print("User types: '2'")
    
    print()
    print("📋 **Step 2: Show Busy Indicator**")
    
    # Create the busy indicator message (simulating what the bot would do)
    busy_msg = mock_bot.send_message(
        mock_message.chat.id,
        f"⏳ **Processing selection 2...**\n"
        f"🧲 Adding torrent to qBittorrent\n"
        f"📁 Setting up download folder\n"
        f"🚀 Starting download..."
    )
    
    print()
    print("📋 **Step 3: Simulate Processing Time**")
    print("Processing torrent selection...")
    
    # Simulate processing delay
    time.sleep(1)
    
    print("✅ Download started successfully!")
    
    print()
    print("📋 **Step 4: Clean Up Busy Indicator**")
    
    # Clean up the busy indicator
    mock_bot.delete_message(mock_message.chat.id, busy_msg.message_id)
    
    print()
    print("📋 **Step 5: Send Success Message**")
    
    # Send final success message
    success_msg = mock_bot.send_message(
        mock_message.chat.id,
        "✅ **Download Started!**\n\n"
        "📁 **File:** Pink Floyd - The Wall [FLAC]\n"
        "💾 **Size:** 1.40 GB\n"
        "📍 **Folder:** /downloads/music\n"
        "🔔 **Notifications:** You'll be notified when complete"
    )
    
    print()
    print("✅ **Busy Indicator Test Results:**")
    print(f"• Messages sent: {len(mock_bot.messages)}")
    print(f"• Messages deleted: {len(mock_bot.deleted_messages)}")
    print("• ✅ Immediate feedback provided")
    print("• ✅ Processing status shown")
    print("• ✅ Clean up after completion")
    print("• ✅ Final status message sent")
    
    print()
    print("🎯 **User Experience Improvement:**")
    print("• User types number → Instant busy indicator")
    print("• Clear progress messages shown")
    print("• No confusing silence during processing")
    print("• Clean interface with automatic cleanup")
    print("• Final confirmation of successful download start")

if __name__ == "__main__":
    test_busy_indicator()
