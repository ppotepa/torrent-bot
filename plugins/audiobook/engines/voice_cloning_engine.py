#!/usr/bin/env python3
"""
Voice Cloning Engine - Piper TTS + Speaker Embedding
"""

import os
import logging
from typing import Tuple
from .base_engine import BaseTTSEngine

logger = logging.getLogger(__name__)

class VoiceCloningEngine(BaseTTSEngine):
    """Voice Cloning engine using Piper TTS + Voice Conversion"""
    
    def __init__(self):
        super().__init__()
        self.name = "Voice Cloning (YOUR VOICE!)"
        self.quality = "Premium Cloned"
        self.priority = 0  # Highest priority
        self.supported_languages = ['polish']
        
        # Import our voice cloning pipeline
        try:
            # Import from parent directory
            import sys
            sys.path.append('..')
            from polish_voice_converter import PolishVoiceConverter  # Uses Enhanced Piper
            self.converter = PolishVoiceConverter()
            self._available = self.converter.is_available() if self.converter else False
            logger.info("✅ Voice Cloning Engine initialized with Enhanced Piper TTS")
        except Exception as e:
            logger.error(f"❌ Voice Cloning Engine failed to initialize: {e}")
            self.converter = None
            self._available = False
    
    def is_available(self) -> bool:
        """Check if voice cloning is available"""
        if not self._available or not self.converter:
            return False
        
        return self.converter.is_available()
    
    def convert(self, text: str, output_path: str, language: str = 'polish', 
               voice_type: str = 'female') -> Tuple[bool, str]:
        """Convert text using voice cloning pipeline"""
        
        if not self.is_available():
            return False, "Voice Cloning engine not available (missing files or dependencies)"
        
        try:
            logger.info(f"🎭 Voice Cloning: Converting '{text[:50]}...' to {output_path}")
            
            # Use our voice conversion pipeline
            success = self.converter.synthesize_with_voice_cloning(text, output_path)
            
            if success and os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                if file_size > 100:
                    logger.info(f"✅ Voice Cloning successful: {file_size} bytes")
                    return True, f"Voice Cloning success with YOUR voice ({file_size} bytes)"
                else:
                    return False, f"Voice Cloning created too small file ({file_size} bytes)"
            else:
                return False, "Voice Cloning pipeline failed to create output file"
                
        except Exception as e:
            error_msg = f"Voice Cloning conversion failed: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
