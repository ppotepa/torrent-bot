#!/usr/bin/env python3
"""
Simple TTS Manager Test
"""

import os
import sys
import logging

# Setup paths
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
sys.path.extend([current_dir, root_dir])

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_voice_cloning():
    """Test voice cloning directly"""
    print("🎭 Testing Voice Cloning System")
    print("=" * 40)
    
    try:
        # Import voice converter
        from polish_voice_converter import PolishVoiceConverter
        
        # Create converter
        converter = PolishVoiceConverter()
        print("✅ Voice converter initialized")
        
        # Test conversion
        test_texts = [
            "Witaj świecie!",
            "To jest test polskiego systemu głosowego.",
            "Jak się masz? Wszystko w porządku?"
        ]
        
        for i, text in enumerate(test_texts):
            output_path = f"test_voice_{i+1}.wav"
            print(f"\n📝 Converting: '{text}'")
            
            success = converter.synthesize_with_voice_cloning(text, output_path)
            
            if success:
                if os.path.exists(output_path):
                    file_size = os.path.getsize(output_path)
                    print(f"   ✅ Success: {file_size} bytes -> {output_path}")
                else:
                    print(f"   ❌ Success reported but file missing: {output_path}")
            else:
                print(f"   ❌ Failed to convert text")
        
        print(f"\n🎧 Voice cloning test completed!")
        
    except Exception as e:
        print(f"💥 Voice cloning test failed: {e}")
        import traceback
        traceback.print_exc()

def test_language_detection():
    """Test language detection"""
    print("\n🔍 Testing Language Detection")
    print("=" * 30)
    
    try:
        # Import language detection
        sys.path.append('utils')
        from utils.language_detection import detect_language_simple, LanguageDetector
        
        test_cases = [
            ("Hello world, how are you?", "english"),
            ("Witaj świecie, jak się masz?", "polish"),
            ("Dzień dobry, bardzo miło mi Cię poznać!", "polish"),
            ("Good morning, nice to meet you!", "english"),
            ("Czy wszystko w porządku?", "polish"),
            ("Is everything okay?", "english")
        ]
        
        print("Testing simple detection:")
        for text, expected in test_cases:
            detected = detect_language_simple(text)
            status = "✅" if detected == expected else "❌"
            print(f"   {status} '{text[:30]}...' -> {detected} (expected: {expected})")
        
        print("\nTesting detailed detection:")
        for text, expected in test_cases[:3]:
            language, confidence = LanguageDetector.detect_language(text)
            print(f"   '{text[:30]}...' -> {language} (confidence: {confidence:.2f})")
        
    except Exception as e:
        print(f"💥 Language detection test failed: {e}")

if __name__ == "__main__":
    test_language_detection()
    test_voice_cloning()
