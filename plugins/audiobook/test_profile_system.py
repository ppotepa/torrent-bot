#!/usr/bin/env python3
"""
Test systemu profili głosowych - sprawdza nową składnię /ab [text]:[profile]
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_command_parser import parse_audiobook_command
from voice_profiles import get_voice_profile_manager
from profile_synthesizer import get_tts_synthesizer
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_command_parsing():
    """Testuje parsowanie komend z profilami"""
    print("🔍 TESTOWANIE PARSOWANIA KOMEND Z PROFILAMI\n")
    
    test_commands = [
        "/ab Cześć jak się masz:pawel",
        "/ab Hello world:natural", 
        "/ab Dzień dobry:fast",
        "/ab Test ekspresji:expressive",
        "/ab Kobieta test:female",
        "/ab [polish,male] Witaj świecie",
        "/ab [pawel] Jak się masz?",
        "/ab Dzień dobry",  # Auto-detect
        "/ab Hello there",   # Auto-detect
        "/ab Text with colon: but no profile after",
        "/ab [voice_cloning] Legacy command"
    ]
    
    for cmd in test_commands:
        print(f"📝 Input: {cmd}")
        text, profile, flags = parse_audiobook_command(cmd)
        print(f"   Text: '{text}'")
        print(f"   Profile: '{profile}'")
        print(f"   Flags: {flags}")
        print()

def test_profile_manager():
    """Testuje manager profili"""
    print("🎭 TESTOWANIE MANAGERA PROFILI\n")
    
    pm = get_voice_profile_manager()
    
    # Lista profili
    profiles = pm.list_profiles()
    print("📋 Dostępne profile:")
    for profile_id, name in profiles.items():
        print(f"  • {profile_id}: {name}")
    print()
    
    # Szczegóły profili
    for profile_id in ['pawel', 'natural', 'expressive', 'fast', 'female']:
        print(f"🎤 Profil '{profile_id}':")
        description = pm.get_profile_description(profile_id)
        print(f"   {description}")
        print()
        
        params = pm.get_synthesis_parameters(profile_id)
        print(f"   Parametry: {params}")
        print()

def test_synthesizer_init():
    """Testuje inicjalizację syntezatora"""
    print("🎵 TESTOWANIE INICJALIZACJI SYNTEZATORA\n")
    
    synthesizer = get_tts_synthesizer()
    
    # Sprawdź dostępne profile
    profiles = synthesizer.get_available_profiles()
    print("📋 Profile dostępne w syntezatorze:")
    for profile_id, name in profiles.items():
        print(f"  • {profile_id}: {name}")
    print()
    
    # Sprawdź info o profilach
    for profile_id in ['pawel', 'natural']:
        print(f"ℹ️ Info o profilu '{profile_id}':")
        info = synthesizer.get_profile_info(profile_id)
        print(f"   {info}")
        print()

def test_voice_synthesis():
    """Testuje syntezę z profilami"""
    print("🎤 TESTOWANIE SYNTEZY GŁOSU Z PROFILAMI\n")
    
    synthesizer = get_tts_synthesizer()
    test_text = "To jest test nowego systemu profili głosowych."
    
    test_profiles = ['pawel', 'natural', 'expressive', 'fast']
    
    for profile_id in test_profiles:
        print(f"🎭 Testowanie profilu '{profile_id}':")
        output_path = f"test_profile_{profile_id}.wav"
        
        try:
            success, message = synthesizer.synthesize_with_profile(
                text=test_text,
                profile_id=profile_id,
                output_path=output_path
            )
            
            if success:
                size = os.path.getsize(output_path) if os.path.exists(output_path) else 0
                print(f"   ✅ Sukces: {message}")
                print(f"   📊 Rozmiar: {size} bytes")
            else:
                print(f"   ❌ Błąd: {message}")
                
        except Exception as e:
            print(f"   💥 Exception: {e}")
        
        print()

def create_user_profile_test():
    """Testuje tworzenie profilu użytkownika z próbek"""
    print("👤 TESTOWANIE TWORZENIA PROFILU UŻYTKOWNIKA\n")
    
    synthesizer = get_tts_synthesizer()
    
    # Ścieżki do próbek
    sample_paths = [
        "voice_profiles/reference_samples/mowa.wav",
        "voice_profiles/reference_samples/mowa-2.wav"
    ]
    
    # Sprawdź czy próbki istnieją
    print("📁 Sprawdzanie próbek referencyjnych:")
    for path in sample_paths:
        exists = os.path.exists(path)
        size = os.path.getsize(path) if exists else 0
        print(f"   {path}: {'✅' if exists else '❌'} ({size} bytes)")
    print()
    
    # Utwórz profil
    success = synthesizer.create_user_profile_from_samples(
        profile_id="pawel_custom",
        name="Paweł Custom Voice",
        sample_paths=sample_paths,
        description="Niestandardowy profil oparty na próbkach głosu Pawła"
    )
    
    if success:
        print("✅ Profil użytkownika utworzony pomyślnie")
        
        # Test syntezy z nowym profilem
        test_text = "To jest test niestandardowego profilu głosowego."
        output_path = "test_custom_profile.wav"
        
        success, message = synthesizer.synthesize_with_profile(
            text=test_text,
            profile_id="pawel_custom",
            output_path=output_path
        )
        
        if success:
            size = os.path.getsize(output_path) if os.path.exists(output_path) else 0
            print(f"✅ Test syntezy: {message}")
            print(f"📊 Rozmiar pliku: {size} bytes")
        else:
            print(f"❌ Test syntezy failed: {message}")
    else:
        print("❌ Błąd tworzenia profilu użytkownika")

if __name__ == "__main__":
    print("🎭 TEST SYSTEMU PROFILI GŁOSOWYCH\n")
    print("=" * 60)
    
    try:
        test_command_parsing()
        print("=" * 60)
        
        test_profile_manager()
        print("=" * 60)
        
        test_synthesizer_init()
        print("=" * 60)
        
        test_voice_synthesis()
        print("=" * 60)
        
        create_user_profile_test()
        print("=" * 60)
        
        print("🎉 TESTY ZAKOŃCZONE")
        
    except Exception as e:
        print(f"💥 BŁĄD TESTÓW: {e}")
        import traceback
        traceback.print_exc()
