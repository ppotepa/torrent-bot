#!/usr/bin/env python3
"""
Simple Test for TTS Components
"""

import os
import sys
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

# Add paths
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.extend([current_dir, os.path.dirname(current_dir), os.path.dirname(os.path.dirname(current_dir))])

def test_components():
    """Test individual components"""
    print("🧪 Testing TTS Components")
    print("=" * 40)
    
    # Test language detection
    try:
        print("\n1. Testing Language Detection...")
        sys.path.append('utils')
        from utils.language_detection import detect_language_simple
        
        test_texts = [
            "Hello, this is English text",
            "Witaj świecie! To jest polski tekst",
            "Jak się masz? Bardzo dobrze!"
        ]
        
        for text in test_texts:
            lang = detect_language_simple(text)
            print(f"   '{text[:30]}...' -> {lang}")
        
        print("✅ Language detection working")
        
    except Exception as e:
        print(f"❌ Language detection failed: {e}")
    
    # Test base engine
    try:
        print("\n2. Testing Base Engine...")
        sys.path.append('engines')
        from engines.base_engine import BaseTTSEngine
        
        class TestEngine(BaseTTSEngine):
            def __init__(self):
                super().__init__()
                self.name = "Test Engine"
                
            def is_available(self):
                return True
                
            def convert(self, text, output_path, language='english', voice_type='female'):
                return True, "Test conversion"
        
        engine = TestEngine()
        print(f"   Engine: {engine.name}")
        print(f"   Available: {engine.is_available()}")
        print(f"   Supports Polish: {engine.supports_language('polish')}")
        
        print("✅ Base engine working")
        
    except Exception as e:
        print(f"❌ Base engine failed: {e}")
    
    # Test voice cloning engine
    try:
        print("\n3. Testing Voice Cloning Engine...")
        
        # Check if voice cloning files exist
        root_dir = os.path.dirname(current_dir)
        voice_converter_path = os.path.join(root_dir, 'polish_voice_converter.py')
        
        if os.path.exists(voice_converter_path):
            print(f"   ✅ Found voice converter: {voice_converter_path}")
            
            # Try importing
            sys.path.append(root_dir)
            from polish_voice_converter import PolishVoiceConverter
            
            converter = PolishVoiceConverter()
            print(f"   ✅ Voice converter initialized")
            
            # Test conversion
            test_text = "Test komunikat audio"
            output_path = "test_voice_cloning.wav"
            
            print(f"   Testing: '{test_text}'")
            success, result = converter.synthesize_with_voice_cloning(test_text, output_path)
            
            if success:
                file_size = os.path.getsize(output_path) if os.path.exists(output_path) else 0
                print(f"   ✅ Voice cloning successful: {file_size} bytes")
            else:
                print(f"   ❌ Voice cloning failed: {result}")
                
        else:
            print(f"   ❌ Voice converter not found at: {voice_converter_path}")
            
    except Exception as e:
        print(f"   ❌ Voice cloning test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_components()
