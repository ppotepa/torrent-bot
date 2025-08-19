#!/usr/bin/env python3
"""
Audiobook Utilities Package
"""

from .language_detection import LanguageDetector, detect_language_simple

__all__ = [
    'LanguageDetector',
    'detect_language_simple'
]
