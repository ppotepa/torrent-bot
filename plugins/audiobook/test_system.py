#!/usr/bin/env python3
"""
Test Script for Enhanced Audiobook System
"""

import os
import sys
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Add parent directories to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
grandparent_dir = os.path.dirname(parent_dir)
sys.path.extend([current_dir, parent_dir, grandparent_dir])

def test_audiobook_system():
    """Test the new audiobook system"""
    print("🧪 Testing Enhanced Audiobook System")
    print("=" * 50)
    
    try:
        # Import components directly
        from tts_manager import TTSEngineManager
        from utils.language_detection import detect_language_simple
        
        # Create TTS manager
        tts_manager = TTSEngineManager()
        print("✅ TTS Manager initialized")
        
        # Get engine status
        status = tts_manager.get_engine_status()
        print(f"\n📊 Engine Status:")
        print(f"   Total engines: {status['total_engines']}")
        print(f"   Available engines: {status['available_engines']}")
        
        print(f"\n🔧 Engine Details:")
        for engine in status['engines']:
            availability = "✅" if engine['available'] else "❌"
            print(f"   {availability} {engine['name']} (Priority {engine['priority']}) - {engine['quality']}")
            print(f"      Languages: {', '.join(engine['languages'])}")
        
        # Test text conversion
        test_text = "Witaj świecie! To jest test systemu audiobook."
        output_path = "test_output.wav"
        
        print(f"\n🎧 Testing conversion:")
        print(f"   Text: '{test_text}'")
        print(f"   Output: {output_path}")
        
        # Detect language
        detected_lang = detect_language_simple(test_text)
        print(f"   Detected language: {detected_lang}")
        
        success, message = tts_manager.convert_text(test_text, output_path, detected_lang)
        
        if success:
            print(f"✅ Conversion successful: {message}")
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                print(f"   File created: {file_size} bytes")
            else:
                print("❌ Output file not found")
        else:
            print(f"❌ Conversion failed: {message}")
        
    except Exception as e:
        print(f"💥 Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_audiobook_system()
