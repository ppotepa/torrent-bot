#!/usr/bin/env python3
"""Test OpenVoice TTS setup"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_openvoice():
    print("Testing OpenVoice TTS setup...")
    
    # Test 1: Check dependencies
    try:
        from openvoice_engine import OPENVOICE_AVAILABLE, get_openvoice_tts
        print(f"✓ OpenVoice dependencies available: {OPENVOICE_AVAILABLE}")
    except ImportError as e:
        print(f"✗ Failed to import OpenVoice engine: {e}")
        return False
    
    # Test 2: Check audiobook plugin
    try:
        from plugins.audiobook import get_available_engines
        engines = get_available_engines()
        print(f"✓ Found {len(engines)} TTS engines:")
        for name, info in engines.items():
            print(f"  - {name}: {info['name']} ({info['quality']} quality, priority {info['priority']})")
    except ImportError as e:
        print(f"✗ Failed to import audiobook plugin: {e}")
        return False
    
    # Test 3: Create OpenVoice engine
    try:
        if OPENVOICE_AVAILABLE:
            engine = get_openvoice_tts()
            print("✓ OpenVoice engine created successfully")
        else:
            print("! OpenVoice not available, using fallback engines")
    except Exception as e:
        print(f"✗ Failed to create OpenVoice engine: {e}")
        return False
    
    # Test 4: Test TTS conversion
    try:
        from plugins.audiobook import convert_text_to_speech
        import tempfile
        
        test_text = "Hello, this is a test of the OpenVoice text-to-speech system."
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
            output_path = tmp.name
        
        success, error_msg = convert_text_to_speech(
            text=test_text,
            language='english',
            output_path=output_path,
            voice_type='female',
            engine='auto'
        )
        
        if success:
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                print(f"✓ TTS conversion successful! Generated {file_size} bytes")
                os.unlink(output_path)  # Clean up
            else:
                print("✗ TTS reported success but no file was created")
        else:
            print(f"✗ TTS conversion failed: {error_msg}")
    except Exception as e:
        print(f"✗ Error during TTS test: {e}")
        return False
    
    print("\n🎉 OpenVoice TTS setup test completed successfully!")
    return True

if __name__ == "__main__":
    test_openvoice()
