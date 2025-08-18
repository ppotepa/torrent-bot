#!/usr/bin/env python3

"""
Debug language detection scoring
"""

import sys
import os
import re

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def debug_language_detection(text: str):
    """Debug version of language detection showing scoring details"""
    
    text_lower = text.lower()
    
    # Check for Polish diacritics first
    polish_diacritics = re.findall(r'[ąćęłńóśźż]', text_lower)
    if polish_diacritics:
        print(f"🔥 DIACRITICS FOUND: {polish_diacritics} → POLISH")
        return 'pl'
    
    # Simplified word lists for debugging
    polish_indicators = ['a', 'i', 'w', 'z', 'na', 'do', 'od', 'po', 'za', 'przez', 'jak', 'co', 'nie', 'tak', 'że', 'się', 'jest', 'bardzo', 'może', 'już', 'tylko', 'też', 'gdzie', 'kiedy', 'który', 'która', 'które', 'wiem', 'wiesz', 'oznacza']
    english_indicators = ['the', 'and', 'a', 'to', 'in', 'is', 'you', 'that', 'it', 'he', 'was', 'for', 'on', 'are', 'as', 'with', 'his', 'they', 'i', 'at', 'be', 'this', 'have', 'from', 'or', 'one', 'had', 'by', 'but', 'not', 'what', 'all', 'were', 'we', 'when', 'your', 'can', 'said', 'there', 'each', 'which', 'she', 'do', 'how', 'their', 'if', 'will', 'up']
    
    polish_score = 0
    english_score = 0
    
    polish_matches = []
    english_matches = []
    
    # Polish scoring
    for indicator in polish_indicators:
        if len(indicator) == 1:  # Single characters
            count = text_lower.count(indicator) * 2
            if count > 0:
                polish_matches.append(f"'{indicator}' x{count//2} (single char)")
                polish_score += count
        else:  # Words
            matches = len(re.findall(r'\b' + re.escape(indicator) + r'\b', text_lower))
            if matches > 0:
                polish_matches.append(f"'{indicator}' x{matches}")
                polish_score += matches
    
    # English scoring
    for indicator in english_indicators:
        matches = len(re.findall(r'\b' + re.escape(indicator) + r'\b', text_lower))
        if matches > 0:
            english_matches.append(f"'{indicator}' x{matches}")
            english_score += matches
    
    print(f"📝 Text: '{text}'")
    print(f"🇵🇱 Polish matches: {polish_matches}")
    print(f"🇺🇸 English matches: {english_matches}")
    print(f"📊 Scores: Polish={polish_score}, English={english_score}")
    
    result = 'pl' if polish_score > english_score else 'en'
    print(f"🎯 Result: {result}")
    return result

def test_debug():
    test_cases = [
        "Hello, how are you today?",
        "My name is John Smith", 
        "I live in New York City",
        "Artur, wiesz co to oznacza?",
        "Dzień dobry, jak się masz?",
        "ą",
        "English text with ą"
    ]
    
    for text in test_cases:
        print("=" * 60)
        debug_language_detection(text)
        print()

if __name__ == "__main__":
    test_debug()
