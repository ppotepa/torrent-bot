#!/usr/bin/env python3
"""
Demo systemu profili - testuje różne składnie komend
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_command_parser import parse_audiobook_command
from profile_synthesizer import get_tts_synthesizer

def demo_voice_profiles():
    """Demo różnych profili głosowych"""
    print("🎭 DEMO SYSTEMU PROFILI GŁOSOWYCH")
    print("=" * 50)
    
    synthesizer = get_tts_synthesizer()
    
    # Test różnych profili z tym samym tekstem
    test_text = "Witaj! To jest demo nowego systemu profili głosowych."
    
    profiles_to_test = [
        ("pawel", "🎭 Twój sklonowany głos"),
        ("natural", "🎵 Naturalny Enhanced Piper"),
        ("expressive", "🎪 Ekspresyjny styl"),
        ("fast", "⚡ Szybka synteza"),
        ("female", "👩 Kobieca wersja")
    ]
    
    for profile_id, description in profiles_to_test:
        print(f"\n{description}")
        print(f"📝 Komenda: /ab {test_text}:{profile_id}")
        
        output_path = f"demo_{profile_id}.wav"
        
        success, message = synthesizer.synthesize_with_profile(
            text=test_text,
            profile_id=profile_id,
            output_path=output_path
        )
        
        if success:
            size = os.path.getsize(output_path) if os.path.exists(output_path) else 0
            print(f"✅ Sukces: {size} bytes")
            print(f"📊 {message}")
        else:
            print(f"❌ Błąd: {message}")
    
    print("\n" + "=" * 50)
    print("🎤 PLIKI AUDIO UTWORZONE:")
    
    for profile_id, _ in profiles_to_test:
        output_path = f"demo_{profile_id}.wav"
        if os.path.exists(output_path):
            size = os.path.getsize(output_path)
            print(f"  🎧 {output_path} - {size:,} bytes")

def demo_command_syntax():
    """Demo różnych składni komend"""
    print("\n🔍 DEMO SKŁADNI KOMEND")
    print("=" * 50)
    
    test_commands = [
        "/ab Cześć jak się masz:pawel",  # Dwukropek z profilem
        "/ab Hello world:natural",       # Angielski z naturalnym
        "/ab [pawel] Jak leci?",         # Flagi z profilem
        "/ab [polish,male] Witaj świecie",  # Flagi tradycyjne
        "/ab Dzień dobry",               # Auto-detect (polski → pawel)
        "/ab Hello there",               # Auto-detect (angielski → natural)
    ]
    
    for cmd in test_commands:
        print(f"\n📝 {cmd}")
        text, profile, flags = parse_audiobook_command(cmd)
        print(f"   → Tekst: '{text}'")
        print(f"   → Profil: {profile}")
        if flags:
            print(f"   → Flagi: {flags}")

if __name__ == "__main__":
    try:
        demo_command_syntax()
        demo_voice_profiles()
        
        print("\n🎉 DEMO ZAKOŃCZONE!")
        print("\n💡 INSTRUKCJE DLA UŻYTKOWNIKA:")
        print("1. Użyj komendy: /ab Twój tekst:pawel")
        print("2. Lub po prostu: /ab Twój tekst (auto-wybór)")
        print("3. Dostępne profile: pawel, natural, expressive, fast, female")
        print("4. Profile pawel używa Twojego sklonowanego głosu!")
        
    except Exception as e:
        print(f"💥 Błąd demo: {e}")
        import traceback
        traceback.print_exc()
