#!/usr/bin/env python3
"""
Piper Voice Cloning Engine - Polish TTS with voice cloning integration for audiobook plugin
"""

import os
import logging
from typing import Optional, Dict, Any

# Enhanced logging integration
try:
    from enhanced_logging import get_logger
    logger = get_logger("piper_voice_cloning")
except ImportError:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("piper_voice_cloning")

# Import our Polish voice conversion pipeline
try:
    from polish_voice_converter import get_voice_converter
    PIPER_VOICE_CLONING_AVAILABLE = True
    logger.info("Piper Voice Cloning pipeline available")
except ImportError as e:
    PIPER_VOICE_CLONING_AVAILABLE = False
    logger.warning(f"Piper Voice Cloning not available: {e}")

class PiperVoiceCloningTTS:
    """Polish TTS with voice cloning using Piper + voice processing"""
    
    def __init__(self):
        self.voice_converter = None
        self.available = False
        self._initialize()
        
    def _initialize(self):
        """Initialize the voice conversion pipeline"""
        if not PIPER_VOICE_CLONING_AVAILABLE:
            logger.warning("Piper Voice Cloning dependencies not available")
            return
            
        try:
            self.voice_converter = get_voice_converter()
            if self.voice_converter.is_available():
                self.available = True
                logger.info("Piper Voice Cloning TTS initialized successfully")
            else:
                logger.warning("Piper Voice Cloning pipeline not available")
                
        except Exception as e:
            logger.error(f"Failed to initialize Piper Voice Cloning: {e}")
            self.available = False
    
    def is_available(self) -> bool:
        """Check if Piper Voice Cloning is available"""
        return self.available
    
    def convert_text_to_speech(self, text: str, output_path: str, language: str = "polish", voice_type: str = "female") -> bool:
        """
        Convert text to speech using Piper TTS with voice cloning
        
        Args:
            text: Text to convert
            output_path: Path to save audio file
            language: Language (supports 'polish' primarily)
            voice_type: Voice type (ignored - uses user's voice)
            
        Returns:
            bool: True if successful
        """
        if not self.available:
            logger.error("Piper Voice Cloning not available")
            return False
            
        try:
            logger.info(f"Converting {len(text)} chars to speech with voice cloning")
            logger.info(f"Language: {language}, Voice: {voice_type}")
            
            # Use our Polish voice conversion pipeline
            success = self.voice_converter.synthesize_with_voice_cloning(text, output_path)
            
            if success:
                # Verify file was created
                if os.path.exists(output_path):
                    file_size = os.path.getsize(output_path)
                    logger.info(f"Piper Voice Cloning success: {file_size} bytes created")
                    return True
                else:
                    logger.error("Piper Voice Cloning reported success but no file created")
                    return False
            else:
                logger.error("Piper Voice Cloning synthesis failed")
                return False
                
        except Exception as e:
            logger.error(f"Piper Voice Cloning conversion error: {e}")
            return False
    
    def get_info(self) -> Dict[str, Any]:
        """Get engine information"""
        return {
            "name": "Piper Voice Cloning",
            "available": self.available,
            "language_support": ["polish"],
            "quality": "Premium (Voice Cloned)",
            "voice_types": ["user_voice"],
            "description": "Polish TTS with voice cloning using Piper + voice processing"
        }

# Global instance
_piper_voice_cloning_instance = None

def get_piper_voice_cloning_tts() -> PiperVoiceCloningTTS:
    """Get global Piper Voice Cloning TTS instance"""
    global _piper_voice_cloning_instance
    if _piper_voice_cloning_instance is None:
        _piper_voice_cloning_instance = PiperVoiceCloningTTS()
    return _piper_voice_cloning_instance

def is_piper_voice_cloning_available() -> bool:
    """Check if Piper Voice Cloning is available"""
    return PIPER_VOICE_CLONING_AVAILABLE and get_piper_voice_cloning_tts().is_available()

if __name__ == "__main__":
    # Test Piper Voice Cloning TTS
    print("🎭 Test Piper Voice Cloning TTS Engine")
    print("=" * 50)
    
    engine = get_piper_voice_cloning_tts()
    
    print("Engine Info:")
    for key, value in engine.get_info().items():
        print(f"  {key}: {value}")
    
    if engine.is_available():
        print("\n🧪 Testing conversion...")
        test_text = "Witaj! To jest test polskiego systemu TTS z klonowaniem głosu dla audiobook plugin."
        output_file = "test_piper_voice_cloning_engine.wav"
        
        success = engine.convert_text_to_speech(test_text, output_file, "polish", "female")
        
        if success:
            print("✅ Test conversion successful!")
            if os.path.exists(output_file):
                file_size = os.path.getsize(output_file)
                print(f"✅ File created: {output_file} ({file_size} bytes)")
            else:
                print("❌ File not found despite success")
        else:
            print("❌ Test conversion failed")
    else:
        print("❌ Piper Voice Cloning not available")
