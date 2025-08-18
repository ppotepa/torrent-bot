#!/usr/bin/env python3
"""
Debug available TTS voices on the system
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    import pyttsx3
    
    print("🎭 Checking available TTS voices...")
    
    # Initialize pyttsx3
    try:
        engine = pyttsx3.init('sapi5')
        voices = engine.getProperty('voices')
        
        print(f"\n📢 Found {len(voices)} voices:")
        print("=" * 80)
        
        for i, voice in enumerate(voices):
            print(f"Voice {i+1}:")
            print(f"  ID: {voice.id}")
            print(f"  Name: {voice.name}")
            print(f"  Languages: {voice.languages}")
            print(f"  Gender: {getattr(voice, 'gender', 'Unknown')}")
            print(f"  Age: {getattr(voice, 'age', 'Unknown')}")
            print("-" * 40)
            
        # Check for Polish voices specifically
        polish_voices = []
        for voice in voices:
            if voice.languages:
                for lang in voice.languages:
                    if 'pl' in lang.lower() or 'polish' in lang.lower() or 'poland' in lang.lower():
                        polish_voices.append(voice)
                        break
                        
        print(f"\n🇵🇱 Polish voices found: {len(polish_voices)}")
        for voice in polish_voices:
            print(f"  - {voice.name} ({voice.id})")
            
        # Test voice setting
        print("\n🧪 Testing voice changes...")
        
        # Try setting different voices
        current_voice = engine.getProperty('voice')
        print(f"Current voice: {current_voice}")
        
        # Try to find a Polish voice or at least a different voice
        test_voice = None
        if polish_voices:
            test_voice = polish_voices[0]
            print(f"Setting to Polish voice: {test_voice.name}")
        elif len(voices) > 1:
            # Try second voice if available
            test_voice = voices[1]
            print(f"Setting to alternative voice: {test_voice.name}")
            
        if test_voice:
            try:
                engine.setProperty('voice', test_voice.id)
                new_voice = engine.getProperty('voice')
                print(f"Voice changed to: {new_voice}")
                print(f"Success: {new_voice == test_voice.id}")
            except Exception as e:
                print(f"Error changing voice: {e}")
                
    except Exception as e:
        print(f"Error initializing SAPI5: {e}")
        
except ImportError as e:
    print(f"Error importing pyttsx3: {e}")
