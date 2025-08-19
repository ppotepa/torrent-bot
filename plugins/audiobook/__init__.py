#!/usr/bin/env python3
"""
Audiobook Plugin Package
Complete TTS system with voice cloning capabilities
"""

# Import main components
from .engines import VoiceCloningEngine, OpenVoiceEngine, GTTSEngine, Pyttsx3Engine
from .tts_manager import TTSEngineManager
from .utils import LanguageDetector, detect_language_simple

# Import main functions from parent audiobook.py module
import sys
import os
parent_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, parent_dir)

try:
    # Import the main audiobook functions
    import importlib.util
    audiobook_path = os.path.join(parent_dir, 'audiobook.py')
    spec = importlib.util.spec_from_file_location("audiobook_main", audiobook_path)
    audiobook_main = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(audiobook_main)
    
    # Export main functions
    handle_audiobook_command = audiobook_main.handle_audiobook_command
    handle_audiobook_file = audiobook_main.handle_audiobook_file
    show_audiobook_help = audiobook_main.show_audiobook_help
    convert_text_to_speech = audiobook_main.convert_text_to_speech
    
except Exception as e:
    # Fallback if import fails
    def handle_audiobook_command(*args, **kwargs):
        raise ImportError(f"Could not import main audiobook module: {e}")
    def handle_audiobook_file(*args, **kwargs):
        raise ImportError(f"Could not import main audiobook module: {e}")
    def show_audiobook_help(*args, **kwargs):
        raise ImportError(f"Could not import main audiobook module: {e}")
    def convert_text_to_speech(*args, **kwargs):
        raise ImportError(f"Could not import main audiobook module: {e}")

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
