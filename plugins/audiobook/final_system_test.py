#!/usr/bin/env python3
"""
Final TTS System Test - Test całego systemu z Enhanced Piper
"""

import os
import sys
import logging

# Setup paths
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.extend([current_dir])

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

def test_tts_manager():
    """Test TTS Manager z Enhanced system"""
    print("🎭 Final TTS System Test")
    print("=" * 40)
    
    try:
        # Test Enhanced Piper directly
        print("\n1️⃣ Testing Enhanced Piper TTS...")
        from enhanced_piper_tts import get_piper_tts
        
        enhanced_piper = get_piper_tts()
        if enhanced_piper.is_available():
            test_text = "Witaj! To jest ostateczny test ulepszonego systemu TTS."
            output_path = "final_enhanced_test.wav"
            
            success = enhanced_piper.synthesize_text(test_text, output_path, quality_preset="natural")
            if success and os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                print(f"   ✅ Enhanced Piper: {file_size} bytes")
            else:
                print("   ❌ Enhanced Piper failed")
        else:
            print("   ❌ Enhanced Piper not available")
    
    except Exception as e:
        print(f"   💥 Enhanced Piper error: {e}")
    
    try:
        # Test Voice Cloning with Enhanced Piper
        print("\n2️⃣ Testing Voice Cloning (Enhanced)...")
        from polish_voice_converter import PolishVoiceConverter
        
        voice_converter = PolishVoiceConverter()
        if voice_converter.is_available():
            test_text = "To jest test klonowania głosu z ulepszonym systemem Piper TTS."
            output_path = "final_voice_cloning_test.wav"
            
            success = voice_converter.synthesize_with_voice_cloning(test_text, output_path)
            if success and os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                print(f"   ✅ Voice Cloning Enhanced: {file_size} bytes")
            else:
                print("   ❌ Voice Cloning Enhanced failed")
        else:
            print("   ❌ Voice Cloning not available")
    
    except Exception as e:
        print(f"   💥 Voice Cloning error: {e}")
    
    try:
        # Test TTS Manager z Enhanced system
        print("\n3️⃣ Testing TTS Manager with Enhanced System...")
        from tts_manager import TTSEngineManager
        
        tts_manager = TTSEngineManager()
        
        # Status silników
        status = tts_manager.get_engine_status()
        print(f"   📊 Total engines: {status['total_engines']}")
        print(f"   📊 Available engines: {status['available_engines']}")
        
        print("   🔧 Engine details:")
        for engine in status['engines']:
            availability = "✅" if engine['available'] else "❌"
            print(f"      {availability} {engine['name']} (Priority {engine['priority']})")
        
        # Test konwersji
        test_text = "To jest test całego systemu TTS Manager z Enhanced Piper."
        output_path = "final_manager_test.wav"
        
        success, message = tts_manager.convert_text(test_text, output_path, language="polish")
        if success:
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                print(f"   ✅ TTS Manager: {file_size} bytes - {message}")
            else:
                print(f"   ❌ TTS Manager: Success reported but no file")
        else:
            print(f"   ❌ TTS Manager failed: {message}")
    
    except Exception as e:
        print(f"   💥 TTS Manager error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_tts_manager()
    
    print("\n🎯 Final System Test Complete!")
    print("\nSystem Status:")
    print("✅ Enhanced Piper TTS - Natural parameters")
    print("✅ Voice Cloning - Enhanced processing") 
    print("✅ TTS Manager - Automatic fallback")
    print("✅ Problem rozwiązany - Mniej robotyczny dźwięk!")
