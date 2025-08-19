#!/usr/bin/env python3
"""
Google Text-to-Speech (gTTS) Engine
"""

import os
import logging
from typing import Tuple
from .base_engine import BaseTTSEngine

logger = logging.getLogger(__name__)

class GTTSEngine(BaseTTSEngine):
    """Google Text-to-Speech Engine"""
    
    def __init__(self):
        super().__init__()
        self.name = "Google TTS"
        self.quality = "Good"
        self.priority = 2
        self.supported_languages = ['english', 'polish']
        
        # Try to import gTTS
        try:
            from gtts import gTTS
            self.tts_class = gTTS
            logger.info("✅ gTTS Engine imported successfully")
        except ImportError as e:
            logger.warning(f"❌ gTTS not available: {e}")
            self.tts_class = None
    
    def is_available(self) -> bool:
        """Check if gTTS is available"""
        return self.tts_class is not None
    
    def convert(self, text: str, output_path: str, language: str = 'english', 
               voice_type: str = 'female') -> Tuple[bool, str]:
        """Convert text using gTTS"""
        
        if not self.is_available():
            return False, "gTTS engine not available"
        
        try:
            logger.info(f"🌐 gTTS: Converting '{text[:50]}...' to {output_path}")
            
            # Map languages
            lang_code = 'en' if language == 'english' else 'pl'
            
            # Create gTTS instance
            tts = self.tts_class(text=text, lang=lang_code, slow=False)
            
            # Save to file
            tts.save(output_path)
            
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                if file_size > 100:
                    logger.info(f"✅ gTTS successful: {file_size} bytes")
                    return True, f"gTTS success ({file_size} bytes)"
                else:
                    return False, f"gTTS created too small file ({file_size} bytes)"
            else:
                return False, "gTTS failed to create output file"
                
        except Exception as e:
            error_msg = f"gTTS conversion failed: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
