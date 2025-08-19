#!/usr/bin/env python3
"""
Audiobook Plugin Package
Complete TTS system with voice cloning capabilities
"""

# Import main components
from .engines import VoiceCloningEngine, OpenVoiceEngine, GTTSEngine, Pyttsx3Engine
from .tts_manager import TTSEngineManager
from .utils import LanguageDetector, detect_language_simple

# Legacy audiobook handler (will be updated to use new system)
from .audiobook_handler import handle_audiobook_command, handle_audiobook_file, show_audiobook_help

# Main exports
__all__ = [
    'TTSEngineManager',
    'VoiceCloningEngine', 
    'OpenVoiceEngine',
    'GTTSEngine', 
    'Pyttsx3Engine',
    'LanguageDetector',
    'detect_language_simple',
    'handle_audiobook_command', 
    'handle_audiobook_file', 
    'show_audiobook_help'
]

# Version info
__version__ = "1.0.0"
