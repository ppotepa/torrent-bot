#!/usr/bin/env python3
"""
OpenVoice Premium TTS Engine
"""

import os
import logging
from typing import Tuple
from .base_engine import BaseTTSEngine

logger = logging.getLogger(__name__)

class OpenVoiceEngine(BaseTTSEngine):
    """OpenVoice Premium TTS Engine"""
    
    def __init__(self):
        super().__init__()
        self.name = "OpenVoice Premium"
        self.quality = "Premium"
        self.priority = 1
        self.supported_languages = ['english', 'polish']
        
        # Try to import OpenVoice from parent directory
        try:
            import sys
            sys.path.append('..')
            from openvoice_engine import get_openvoice_tts, is_openvoice_available
            self.get_engine = get_openvoice_tts
            self.check_available = is_openvoice_available
            logger.info("✅ OpenVoice Engine imported successfully")
        except Exception as e:
            logger.warning(f"❌ OpenVoice not available: {e}")
            self.get_engine = None
            self.check_available = lambda: False
    
    def is_available(self) -> bool:
        """Check if OpenVoice is available"""
        if self.check_available:
            return self.check_available()
        return False
    
    def convert(self, text: str, output_path: str, language: str = 'english', 
               voice_type: str = 'female') -> Tuple[bool, str]:
        """Convert text using OpenVoice"""
        
        if not self.is_available():
            return False, "OpenVoice engine not available"
        
        try:
            logger.info(f"🎭 OpenVoice: Converting '{text[:50]}...' to {output_path}")
            
            engine_instance = self.get_engine()
            success = engine_instance.convert_text_to_speech(text, output_path, language, voice_type)
            
            if success and os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                if file_size > 100:
                    logger.info(f"✅ OpenVoice successful: {file_size} bytes")
                    return True, f"OpenVoice success ({file_size} bytes)"
                else:
                    return False, f"OpenVoice created too small file ({file_size} bytes)"
            else:
                return False, "OpenVoice failed to create output file"
                
        except Exception as e:
            error_msg = f"OpenVoice conversion failed: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
