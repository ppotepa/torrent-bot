#!/usr/bin/env python3
"""
Pyttsx3 Local TTS Engine
"""

import os
import logging
from typing import Tuple
from .base_engine import BaseTTSEngine

logger = logging.getLogger(__name__)

class Pyttsx3Engine(BaseTTSEngine):
    """Pyttsx3 Local TTS Engine"""
    
    def __init__(self):
        super().__init__()
        self.name = "Pyttsx3 Local"
        self.quality = "Basic"
        self.priority = 3
        self.supported_languages = ['english', 'polish']
        
        # Try to import pyttsx3
        try:
            import pyttsx3
            self.pyttsx3 = pyttsx3
            logger.info("✅ Pyttsx3 Engine imported successfully")
        except ImportError as e:
            logger.warning(f"❌ Pyttsx3 not available: {e}")
            self.pyttsx3 = None
    
    def is_available(self) -> bool:
        """Check if pyttsx3 is available"""
        return self.pyttsx3 is not None
    
    def convert(self, text: str, output_path: str, language: str = 'english', 
               voice_type: str = 'female') -> Tuple[bool, str]:
        """Convert text using pyttsx3"""
        
        if not self.is_available():
            return False, "Pyttsx3 engine not available"
        
        try:
            logger.info(f"🔊 Pyttsx3: Converting '{text[:50]}...' to {output_path}")
            
            # Initialize pyttsx3 engine
            engine = self.pyttsx3.init()
            
            # Configure voice settings
            voices = engine.getProperty('voices')
            if voices:
                # Try to find appropriate voice
                for voice in voices:
                    if voice_type.lower() in voice.name.lower():
                        engine.setProperty('voice', voice.id)
                        break
                    elif language == 'polish' and ('polish' in voice.name.lower() or 'poland' in voice.name.lower()):
                        engine.setProperty('voice', voice.id)
                        break
            
            # Configure speech rate and volume
            engine.setProperty('rate', 150)  # Slower speech
            engine.setProperty('volume', 0.9)
            
            # Save to file
            engine.save_to_file(text, output_path)
            engine.runAndWait()
            
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                if file_size > 100:
                    logger.info(f"✅ Pyttsx3 successful: {file_size} bytes")
                    return True, f"Pyttsx3 success ({file_size} bytes)"
                else:
                    return False, f"Pyttsx3 created too small file ({file_size} bytes)"
            else:
                return False, "Pyttsx3 failed to create output file"
                
        except Exception as e:
            error_msg = f"Pyttsx3 conversion failed: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
