#!/usr/bin/env python3
"""
Base TTS Engine Interface
"""

from abc import ABC, abstractmethod
from typing import Tuple

class BaseTTSEngine(ABC):
    """Base class for all TTS engines"""
    
    def __init__(self):
        self.name = "Base TTS Engine"
        self.quality = "Unknown"
        self.priority = 99
        self.supported_languages = ['english']
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if engine is available and functional"""
        pass
    
    @abstractmethod
    def convert(self, text: str, output_path: str, language: str = 'english', 
               voice_type: str = 'female') -> Tuple[bool, str]:
        """Convert text to speech. Returns (success, message)"""
        pass
    
    def get_info(self) -> dict:
        """Get engine information"""
        return {
            'name': self.name,
            'quality': self.quality,
            'priority': self.priority,
            'supported_languages': self.supported_languages,
            'available': self.is_available()
        }
    
    def supports_language(self, language: str) -> bool:
        """Check if engine supports given language"""
        return language.lower() in [lang.lower() for lang in self.supported_languages]
