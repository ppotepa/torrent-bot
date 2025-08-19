#!/usr/bin/env python3
"""
TTS Engines Package
All available TTS engines for the audiobook system
"""

from .base_engine import BaseTTSEngine
from .voice_cloning_engine import VoiceCloningEngine
from .openvoice_engine import OpenVoiceEngine
from .gtts_engine import GTTSEngine
from .pyttsx3_engine import Pyttsx3Engine

# Export all engines
__all__ = [
    'BaseTTSEngine',
    'VoiceCloningEngine',
    'OpenVoiceEngine', 
    'GTTSEngine',
    'Pyttsx3Engine'
]

# Available engines in priority order (0 = highest priority)
AVAILABLE_ENGINES = [
    VoiceCloningEngine,    # Priority 0 - Best quality
    OpenVoiceEngine,       # Priority 1 - Premium
    GTTSEngine,           # Priority 2 - Good
    Pyttsx3Engine         # Priority 3 - Basic fallback
]
