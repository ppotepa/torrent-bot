#!/usr/bin/env python3
"""
Enhanced Audiobook Handler
Integrates the new modular TTS system with existing audiobook functionality
"""

import os
import logging
from typing import Optional, Tuple
from .tts_manager import TTSEngineManager
from .utils import detect_language_simple

logger = logging.getLogger(__name__)

class EnhancedAudiobookHandler:
    """Enhanced audiobook handler with modular TTS system"""
    
    def __init__(self):
        self.tts_manager = TTSEngineManager()
        logger.info("🎧 Enhanced Audiobook Handler initialized")
    
    def convert_text_to_speech(self, text: str, output_path: str, 
                             language: Optional[str] = None, 
                             voice_type: str = 'female',
                             preferred_engine: Optional[str] = None) -> Tuple[bool, str]:
        """
        Convert text to speech using the best available engine
        
        Args:
            text: Text to convert
            output_path: Output file path
            language: Language ('english' or 'polish', auto-detect if None)
            voice_type: Voice type ('male' or 'female')
            preferred_engine: Preferred engine name
            
        Returns:
            (success, message)
        """
        
        # Auto-detect language if not specified
        if language is None:
            language = detect_language_simple(text)
            logger.info(f"🔍 Auto-detected language: {language}")
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Convert using TTS manager
        success, message = self.tts_manager.convert_text(
            text=text,
            output_path=output_path,
            language=language,
            voice_type=voice_type,
            preferred_engine=preferred_engine
        )
        
        return success, message
    
    def get_engine_status(self) -> dict:
        """Get status of all TTS engines"""
        return self.tts_manager.get_engine_status()
    
    def get_available_engines(self):
        """Get list of available engines"""
        return self.tts_manager.get_available_engines()

# Global instance for backward compatibility
_handler_instance = None

def get_audiobook_handler() -> EnhancedAudiobookHandler:
    """Get singleton audiobook handler instance"""
    global _handler_instance
    if _handler_instance is None:
        _handler_instance = EnhancedAudiobookHandler()
    return _handler_instance

# Legacy functions for backward compatibility (to be updated)
def handle_audiobook_command(message, update, context):
    """Legacy audiobook command handler - will be updated"""
    # This will be updated to use the new system
    try:
        # Import the old handler for now
        import sys
        sys.path.append('../..')
        from plugins.audiobook.audiobook_handler import handle_audiobook_command as old_handler
        return old_handler(message, update, context)
    except Exception as e:
        logger.error(f"Legacy handler failed: {e}")
        return False, str(e)

def handle_audiobook_file(message, update, context):
    """Legacy audiobook file handler - will be updated"""
    # This will be updated to use the new system
    try:
        # Import the old handler for now
        import sys
        sys.path.append('../..')
        from plugins.audiobook.audiobook_handler import handle_audiobook_file as old_handler
        return old_handler(message, update, context)
    except Exception as e:
        logger.error(f"Legacy file handler failed: {e}")
        return False, str(e)

def show_audiobook_help():
    """Show audiobook help - will be updated"""
    help_text = """
🎧 **Enhanced Audiobook System**

**Commands:**
• `/audiobook` - Convert text to speech
• Send text files - Auto-convert to audiobook

**Features:**
• 🎭 Voice cloning with your voice samples
• 🌍 Automatic language detection (Polish/English)
• 🔄 Multiple TTS engines with fallback
• 📱 High-quality audio output

**Engines Available:**
1. **Voice Cloning** (Priority 0) - Your voice with Polish TTS
2. **OpenVoice Premium** (Priority 1) - High quality
3. **Google TTS** (Priority 2) - Good quality  
4. **Pyttsx3 Local** (Priority 3) - Basic fallback

**Usage:**
```
/audiobook Hello, this is a test message
```

The system automatically:
- Detects language (Polish/English)
- Selects best available engine
- Falls back if primary engine fails
- Creates high-quality audio files
    """
    return help_text
