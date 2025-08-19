#!/usr/bin/env python3
"""
Demo script to test OpenVoice TTS functionality
"""

import os
import sys
import tempfile

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def demo_tts():
    """Demo the TTS functionality"""
    print("🎵 OpenVoice TTS Demo")
    print("=" * 40)
    
    try:
        from plugins.audiobook import convert_text_to_speech
        
        # Test texts
        tests = [
            {
                "text": "Hello! Welcome to the OpenVoice text-to-speech demo. This is a premium quality voice synthesis system.",
                "language": "english",
                "voice": "female",
                "name": "English Female"
            },
            {
                "text": "This is a demonstration of the male voice option with enhanced audio quality.",
                "language": "english", 
                "voice": "male",
                "name": "English Male"
            },
            {
                "text": "Cześć! To jest demonstracja polskiego systemu syntezy mowy z technologią OpenVoice.",
                "language": "polish",
                "voice": "female", 
                "name": "Polish Female"
            }
        ]
        
        print(f"Testing {len(tests)} voice configurations...\n")
        
        for i, test in enumerate(tests, 1):
            print(f"Test {i}: {test['name']}")
            print(f"Text: {test['text'][:50]}...")
            
            # Create temp file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
                output_path = tmp.name
            
            # Convert to speech
            success, error_msg = convert_text_to_speech(
                text=test['text'],
                language=test['language'],
                output_path=output_path,
                voice_type=test['voice'],
                engine='auto'  # Uses OpenVoice if available
            )
            
            if success and os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                print(f"✅ Success! Generated {file_size:,} bytes")
                print(f"   File: {output_path}")
                
                # Keep the file for testing
                new_name = f"demo_{test['language']}_{test['voice']}.wav"
                final_path = os.path.join(os.path.dirname(__file__), "audiobooks", new_name)
                os.makedirs(os.path.dirname(final_path), exist_ok=True)
                
                try:
                    import shutil
                    shutil.move(output_path, final_path)
                    print(f"   Saved as: {final_path}")
                except:
                    pass
                    
            else:
                print(f"❌ Failed: {error_msg}")
            
            print()
        
        print("🎉 Demo completed!")
        print("Check the 'audiobooks' folder for generated files.")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    demo_tts()
