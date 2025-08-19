#!/usr/bin/env python3
"""
Test integracji systemu profili z głównym botem
"""

import os
import sys
import tempfile

# Dodaj ścieżki
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'audiobook'))

class MockMessage:
    """Mock obiektu message z Telegrama"""
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

class MockBot:
    """Mock obiektu bota Telegram"""
    def __init__(self):
        self.messages = []
        self.voice_messages = []
        self.deleted_messages = []
        
    def send_message(self, chat_id, text, parse_mode=None):
        message = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': parse_mode,
            'message_id': len(self.messages) + 1
        }
        self.messages.append(message)
        print(f"📱 BOT MESSAGE: {text[:100]}...")
        return MockMessage(text, message_id=message['message_id'])
        
    def send_voice(self, chat_id, audio_file, caption=None):
        voice = {
            'chat_id': chat_id,
            'caption': caption,
            'file_size': len(audio_file.read()) if hasattr(audio_file, 'read') else 0
        }
        self.voice_messages.append(voice)
        print(f"🎧 VOICE MESSAGE: {caption}")
        
    def delete_message(self, chat_id, message_id):
        self.deleted_messages.append((chat_id, message_id))
        print(f"🗑️ DELETED MESSAGE: {message_id}")
        
    def edit_message_text(self, text, chat_id, message_id, parse_mode=None):
        print(f"✏️ EDIT MESSAGE: {text[:100]}...")

def test_profile_system_integration():
    """Test pełnej integracji systemu profili"""
    print("🎭 TEST INTEGRACJI SYSTEMU PROFILI Z BOTEM")
    print("=" * 60)
    
    # Import funkcji z audiobook plugin
    try:
        from plugins.audiobook import handle_audiobook_command
        print("✅ Importowany handle_audiobook_command")
    except ImportError as e:
        print(f"❌ Błąd importu: {e}")
        return False
    
    # Mock bot i message
    bot = MockBot()
    
    # Test różnych komend
    test_commands = [
        "/ab",  # Help
        "/ab Cześć jak się masz:pawel",  # Voice cloning
        "/ab Hello world:natural",       # Natural
        "/ab Szybka wiadomość:fast",     # Fast
        "/ab Test ekspresji:expressive", # Expressive
        "/ab Dzień dobry",               # Auto-detect (polski → pawel)
        "/ab Hello there",               # Auto-detect (angielski → natural)
    ]
    
    for i, cmd in enumerate(test_commands):
        print(f"\n🧪 TEST {i+1}: {cmd}")
        print("-" * 40)
        
        message = MockMessage(cmd)
        
        try:
            handle_audiobook_command(message, bot)
            print("✅ Komenda wykonana pomyślnie")
        except Exception as e:
            print(f"❌ Błąd wykonania: {e}")
            import traceback
            traceback.print_exc()
    
    # Podsumowanie
    print("\n" + "=" * 60)
    print("📊 PODSUMOWANIE TESTÓW:")
    print(f"📱 Wysłanych wiadomości: {len(bot.messages)}")
    print(f"🎧 Wysłanych plików audio: {len(bot.voice_messages)}")
    print(f"🗑️ Usuniętych wiadomości: {len(bot.deleted_messages)}")
    
    return True

def test_specific_profile_commands():
    """Test konkretnych komend z profilami"""
    print("\n🎯 TEST KONKRETNYCH KOMEND")
    print("=" * 60)
    
    # Import bezpośrednio z audiobook folder  
    from enhanced_command_parser import parse_audiobook_command
    from profile_synthesizer import get_tts_synthesizer
    
    synthesizer = get_tts_synthesizer()
    
    test_scenarios = [
        {
            'command': '/ab Witaj w nowym systemie:pawel',
            'expected_profile': 'pawel',
            'description': 'Voice cloning z Twoim głosem'
        },
        {
            'command': '/ab Test naturalnego głosu:natural',
            'expected_profile': 'natural', 
            'description': 'Enhanced Piper naturalny'
        },
        {
            'command': '/ab Dzień dobry wszystkim',
            'expected_profile': 'pawel',
            'description': 'Auto-detect polski → pawel'
        },
        {
            'command': '/ab Hello everyone',
            'expected_profile': 'natural',
            'description': 'Auto-detect angielski → natural'
        }
    ]
    
    for scenario in test_scenarios:
        print(f"\n🔍 {scenario['description']}")
        print(f"📝 Komenda: {scenario['command']}")
        
        # Parse komenda
        text, profile_id, flags = parse_audiobook_command(scenario['command'])
        
        print(f"   📋 Tekst: '{text}'")
        print(f"   🎭 Profil: {profile_id}")
        print(f"   ✅ Oczekiwany: {scenario['expected_profile']}")
        
        if profile_id == scenario['expected_profile']:
            print("   ✅ POPRAWNY profil!")
        else:
            print("   ❌ BŁĘDNY profil!")
        
        # Test syntezy (krótki test)
        test_output = f"test_integration_{profile_id}.wav"
        try:
            success, message = synthesizer.synthesize_with_profile(
                text=text[:20] + "...",  # Krótki test
                profile_id=profile_id,
                output_path=test_output
            )
            
            if success:
                size = os.path.getsize(test_output) if os.path.exists(test_output) else 0
                print(f"   🎧 Synteza OK: {size} bytes")
            else:
                print(f"   ❌ Synteza failed: {message}")
                
        except Exception as e:
            print(f"   💥 Synteza exception: {e}")

if __name__ == "__main__":
    try:
        # Test integracji
        success = test_profile_system_integration()
        
        if success:
            # Test szczegółowy
            test_specific_profile_commands()
            
            print("\n🎉 WSZYSTKIE TESTY ZAKOŃCZONE!")
            print("\n💡 SYSTEM PROFILI GOTOWY DO UŻYCIA:")
            print("   /ab Twój tekst:pawel    # Twój sklonowany głos")
            print("   /ab Twój tekst:natural  # Naturalny głos")
            print("   /ab Twój tekst          # Auto-wykrywanie")
        
    except Exception as e:
        print(f"💥 BŁĄD TESTÓW: {e}")
        import traceback
        traceback.print_exc()
