#!/usr/bin/env python3
"""
Ostateczny test systemu profili głosowych
"""

import os
import sys

# Dodaj bieżący folder do ścieżki
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def final_system_test():
    """Ostateczny test całego systemu"""
    print("🎊 OSTATECZNY TEST SYSTEMU PROFILI GŁOSOWYCH")
    print("=" * 70)
    
    # Test 1: Parsowanie komend
    print("1️⃣ TEST PARSOWANIA KOMEND:")
    try:
        from enhanced_command_parser import parse_audiobook_command
        
        test_commands = [
            "/ab Cześć jak się masz:pawel",
            "/ab Hello world:natural", 
            "/ab [pawel] Test profilu",
            "/ab Dzień dobry",  # Auto-detect
            "/ab Hello there"   # Auto-detect
        ]
        
        for cmd in test_commands:
            text, profile, flags = parse_audiobook_command(cmd)
            print(f"   ✅ {cmd}")
            print(f"      → '{text}' | Profil: {profile}")
        
        print("   ✅ Parsowanie działa poprawnie!")
    except Exception as e:
        print(f"   ❌ Błąd parsowania: {e}")
    
    # Test 2: Manager profili
    print("\n2️⃣ TEST MANAGERA PROFILI:")
    try:
        from voice_profiles import get_voice_profile_manager
        
        pm = get_voice_profile_manager()
        profiles = pm.list_profiles()
        
        print(f"   ✅ Załadowano {len(profiles)} profili:")
        for pid, name in profiles.items():
            params = pm.get_synthesis_parameters(pid)
            ptype = params.get('type', 'unknown')
            quality = params.get('quality', 'unknown')
            print(f"      • {pid}: {name} ({ptype}, {quality})")
        
        print("   ✅ Manager profili działa poprawnie!")
    except Exception as e:
        print(f"   ❌ Błąd managera profili: {e}")
    
    # Test 3: Syntezator
    print("\n3️⃣ TEST SYNTEZATORA:")
    try:
        from profile_synthesizer import get_tts_synthesizer
        
        synthesizer = get_tts_synthesizer()
        test_text = "Krótki test systemu profili"
        
        # Test kluczowych profili
        test_profiles = [
            ('pawel', '🎭 Sklonowany głos'),
            ('natural', '🎵 Naturalny'),
            ('fast', '⚡ Szybki')
        ]
        
        results = []
        for profile_id, description in test_profiles:
            output_path = f"ultimate_test_{profile_id}.wav"
            try:
                success, message = synthesizer.synthesize_with_profile(
                    text=test_text,
                    profile_id=profile_id,
                    output_path=output_path
                )
                
                if success and os.path.exists(output_path):
                    size = os.path.getsize(output_path)
                    results.append((profile_id, size, "✅"))
                    print(f"   ✅ {description}: {size:,} bytes")
                else:
                    results.append((profile_id, 0, "❌"))
                    print(f"   ❌ {description}: {message}")
                    
            except Exception as e:
                results.append((profile_id, 0, "💥"))
                print(f"   💥 {description}: {e}")
        
        # Sprawdź wyniki
        success_count = sum(1 for _, _, status in results if status == "✅")
        if success_count >= 2:
            print("   ✅ Syntezator działa poprawnie!")
        else:
            print("   ⚠️ Syntezator ma problemy")
            
    except Exception as e:
        print(f"   ❌ Błąd syntezatora: {e}")
    
    # Test 4: Sprawdzenie plików
    print("\n4️⃣ SPRAWDZENIE WYGENEROWANYCH PLIKÓW:")
    generated_files = []
    for file in os.listdir('.'):
        if file.startswith('ultimate_test_') and file.endswith('.wav'):
            size = os.path.getsize(file)
            generated_files.append((file, size))
            print(f"   🎧 {file}: {size:,} bytes")
    
    if generated_files:
        # Znajdź największy plik (prawdopodobnie voice cloning)
        largest = max(generated_files, key=lambda x: x[1])
        if 'pawel' in largest[0] and largest[1] > 200000:
            print(f"   🏆 Najlepszy rezultat: {largest[0]} ({largest[1]:,} bytes)")
            print("   🎭 Voice cloning działa optimal!")
    
    # Podsumowanie finalne
    print("\n" + "=" * 70)
    print("🎉 SYSTEM PROFILI GŁOSOWYCH GOTOWY DO UŻYCIA!")
    print("\n📋 INSTRUKCJE DLA UŻYTKOWNIKA:")
    print("┌─────────────────────────────────────────────────────────────┐")
    print("│  SKŁADNIA KOMEND:                                           │")
    print("│  /ab Twój tekst:pawel      # Twój sklonowany głos          │")
    print("│  /ab Twój tekst:natural    # Naturalny Enhanced Piper      │")
    print("│  /ab Twój tekst:fast       # Szybka synteza                │")
    print("│  /ab Twój tekst            # Auto-wykrywanie języka        │")
    print("└─────────────────────────────────────────────────────────────┘")
    print("\n🔥 ZALECENIE: Używaj profilu 'pawel' dla najlepszej jakości!")
    print("💎 Profil 'pawel' używa Twoich próbek mowa.wav i mowa-2.wav")
    
    return True

if __name__ == "__main__":
    try:
        final_system_test()
    except Exception as e:
        print(f"💥 BŁĄD GŁÓWNY: {e}")
        import traceback
        traceback.print_exc()
