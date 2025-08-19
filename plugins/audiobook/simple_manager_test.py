#!/usr/bin/env python3
"""
Simple TTS Manager Test - bez relative imports
"""

import os
import sys
import logging

# Setup paths
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.extend([current_dir, 'engines', 'utils'])

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

def test_simple_manager():
    """Prosty test managera"""
    print("🎭 Simple Manager Test")
    print("=" * 30)
    
    try:
        # Import Enhanced Piper
        from enhanced_piper_tts import get_piper_tts
        
        # Prosty manager
        class SimpleTTSManager:
            def __init__(self):
                self.enhanced_piper = get_piper_tts()
                
            def convert_text(self, text, output_path, language='polish'):
                if self.enhanced_piper.is_available():
                    success = self.enhanced_piper.synthesize_text(text, output_path, quality_preset="natural")
                    if success:
                        return True, "Enhanced Piper TTS success"
                    else:
                        return False, "Enhanced Piper TTS failed"
                else:
                    return False, "No TTS engines available"
        
        # Test managera
        manager = SimpleTTSManager()
        
        test_text = "To jest test prostego managera z Enhanced Piper TTS."
        output_path = "simple_manager_test.wav"
        
        success, message = manager.convert_text(test_text, output_path)
        
        if success and os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            print(f"✅ Simple Manager: {file_size} bytes - {message}")
        else:
            print(f"❌ Simple Manager failed: {message}")
            
    except Exception as e:
        print(f"💥 Simple Manager error: {e}")

if __name__ == "__main__":
    test_simple_manager()
