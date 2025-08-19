#!/usr/bin/env python3
"""
Language Detection Utilities
Detects language from text content
"""

import re
import logging
from typing import Tuple

logger = logging.getLogger(__name__)

class LanguageDetector:
    """Simple rule-based language detection"""
    
    # Polish characters and common words
    POLISH_CHARS = set('ąćęłńóśźżĄĆĘŁŃÓŚŹŻ')
    POLISH_WORDS = {
        'bardzo', 'jest', 'może', 'można', 'będzie', 'tylko', 'przez', 'oraz', 'które', 'można',
        'także', 'także', 'między', 'został', 'została', 'zostało', 'zostały', 'będą', 'będzie',
        'nie', 'tak', 'ale', 'lub', 'oraz', 'czy', 'gdy', 'jak', 'że', 'się', 'na', 'do', 'za',
        'pod', 'nad', 'przed', 'po', 'bez', 'dla', 'od', 'przy', 'wraz', 'według', 'podczas'
    }
    
    # English indicators
    ENGLISH_WORDS = {
        'the', 'and', 'that', 'have', 'for', 'not', 'with', 'you', 'this', 'but', 'his', 'from',
        'they', 'she', 'her', 'been', 'than', 'its', 'who', 'did', 'get', 'may', 'him', 'old', 
        'see', 'now', 'way', 'could', 'people', 'my', 'than', 'first', 'water', 'been', 'call',
        'made', 'long', 'down', 'day', 'did', 'get', 'come', 'man', 'over', 'think', 'also',
        'back', 'after', 'use', 'two', 'how', 'our', 'work', 'first', 'well', 'way', 'even',
        'new', 'want', 'because', 'any', 'these', 'give', 'day', 'most', 'us'
    }
    
    @classmethod
    def detect_language(cls, text: str, confidence_threshold: float = 0.6) -> Tuple[str, float]:
        """
        Detect language from text
        
        Args:
            text: Text to analyze
            confidence_threshold: Minimum confidence to return result
            
        Returns:
            (language, confidence) - ('polish', 'english', or 'unknown', confidence_score)
        """
        
        if not text or len(text.strip()) < 3:
            return 'unknown', 0.0
        
        text_lower = text.lower()
        words = re.findall(r'\b\w+\b', text_lower)
        
        if not words:
            return 'unknown', 0.0
        
        # Check for Polish characters
        polish_char_count = sum(1 for char in text if char in cls.POLISH_CHARS)
        polish_char_ratio = polish_char_count / len(text) if text else 0
        
        # Check for Polish words
        polish_word_count = sum(1 for word in words if word in cls.POLISH_WORDS)
        polish_word_ratio = polish_word_count / len(words) if words else 0
        
        # Check for English words
        english_word_count = sum(1 for word in words if word in cls.ENGLISH_WORDS)
        english_word_ratio = english_word_count / len(words) if words else 0
        
        # Calculate scores
        polish_score = (polish_char_ratio * 0.4) + (polish_word_ratio * 0.6)
        english_score = english_word_ratio
        
        # Boost Polish score if we have Polish characters
        if polish_char_count > 0:
            polish_score += 0.3
        
        # Determine language
        if polish_score > english_score and polish_score >= confidence_threshold:
            confidence = min(polish_score, 1.0)
            logger.debug(f"Language detected: Polish (confidence: {confidence:.2f})")
            return 'polish', confidence
        elif english_score > polish_score and english_score >= confidence_threshold:
            confidence = min(english_score, 1.0)
            logger.debug(f"Language detected: English (confidence: {confidence:.2f})")
            return 'english', confidence
        else:
            # If both scores are low, default to English
            if len(words) > 5:  # Only for longer texts
                logger.debug(f"Language uncertain (PL: {polish_score:.2f}, EN: {english_score:.2f}), defaulting to English")
                return 'english', 0.5
            else:
                logger.debug(f"Language unknown (PL: {polish_score:.2f}, EN: {english_score:.2f})")
                return 'unknown', 0.0

def detect_language_simple(text: str) -> str:
    """Simple wrapper for language detection"""
    language, confidence = LanguageDetector.detect_language(text)
    
    # If confidence is too low, default to English
    if confidence < 0.3:
        return 'english'
    
    return language
