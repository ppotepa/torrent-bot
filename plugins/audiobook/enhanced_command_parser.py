#!/usr/bin/env python3
"""
Enhanced Command Parser - Ulepszone parsowanie komend z obsługą profili głosowych
Obsługuje składnię: /ab [text]:[profile] oraz /ab [flags] text
"""

import re
import logging
from typing import Tuple, Dict, Any, Optional

logger = logging.getLogger(__name__)

def parse_audiobook_command(command_text: str) -> Tuple[str, Optional[str], Dict[str, Any]]:
    """
    Parsuje komendę audiobook z obsługą profili głosowych
    
    Obsługiwane formaty:
    - /ab Hello world:pawel                    # Text z profilem
    - /ab Cześć jak się masz:natural          # Text z profilem natural
    - /ab [polish,male] Hello world           # Text z flagami
    - /ab Hello world                         # Text bez profilu (auto-detect)
    
    Args:
        command_text: Pełny tekst komendy
        
    Returns:
        Tuple[text, profile_id, flags]: (tekst do syntezy, ID profilu, flagi)
    """
    try:
        logger.info(f"🔍 Parsing command: {command_text}")
        
        # Usuń prefix komendy
        text = command_text.strip()
        if text.startswith('/ab'):
            text = text[3:].strip()
        
        flags = {}
        profile_id = None
        
        # === METODA 1: Składnia [text]:[profile] ===
        # Sprawdź czy jest dwukropek wskazujący na profil
        if ':' in text:
            # Znajdź ostatni dwukropek (może być w tekście)
            parts = text.rsplit(':', 1)
            if len(parts) == 2:
                potential_text = parts[0].strip()
                potential_profile = parts[1].strip().lower()
                
                # Sprawdź czy to wygląda na profil (krótkie słowo bez spacji)
                if potential_profile and len(potential_profile) <= 20 and ' ' not in potential_profile:
                    text = potential_text
                    profile_id = potential_profile
                    logger.info(f"🎭 Wykryto profil z dwukropka: '{profile_id}'")
        
        # === METODA 2: Składnia z flagami [flags] ===
        if not profile_id:
            # Sprawdź flagi w nawiasach kwadratowych - poprawiony regex
            bracket_pattern = r'\[([^\]]+)\]'
            matches = re.findall(bracket_pattern, text)
            
            if matches:
                for match in matches:
                    flag_values = [v.strip().lower() for v in match.split(',')]
                    
                    for value in flag_values:
                        # Profile detection (nowe - sprawdź czy to nazwa profilu)
                        if value in ['pawel', 'natural', 'expressive', 'fast', 'female']:
                            profile_id = value
                            logger.info(f"🎭 Wykryto profil z flag: '{profile_id}'")
                        # Language detection
                        elif value in ['eng', 'english', 'en']:
                            flags['language'] = 'english'
                        elif value in ['pl', 'polish', 'polski']:
                            flags['language'] = 'polish'
                        # Voice type detection
                        elif value in ['male', 'female', 'british', 'young']:
                            flags['voice_type'] = value
                        # Engine detection
                        elif value in ['openvoice', 'auto', 'gtts', 'enhanced_sapi', 'pyttsx3']:
                            flags['engine'] = value
                        # Legacy voice cloning detection
                        elif value in ['piper_voice_cloning', 'voice_cloning']:
                            profile_id = 'pawel'  # Map to Paweł profile
                
                # Usuń flagi z tekstu
                text = re.sub(bracket_pattern, '', text).strip()
        
        # === AUTO-DETECTION ===
        if not profile_id:
            # Auto-wykrywanie języka i sugerowanie profilu
            if _detect_polish(text):
                profile_id = 'pawel'  # Domyślnie Twój głos dla polskiego
                logger.info(f"🇵🇱 Wykryto polski - użycie profilu 'pawel'")
            else:
                profile_id = 'natural'  # Naturalny dla angielskiego
                logger.info(f"🇬🇧 Wykryto angielski - użycie profilu 'natural'")
        
        logger.info(f"📋 Parsed: text='{text[:50]}...', profile='{profile_id}', flags={flags}")
        return text, profile_id, flags
        
    except Exception as e:
        logger.error(f"Błąd parsowania komendy: {e}")
        # Fallback
        clean_text = command_text.replace('/ab', '').strip()
        return clean_text, 'natural', {}

def _detect_polish(text: str) -> bool:
    """Wykrywa czy tekst jest polski"""
    if not text:
        return False
    
    polish_chars = set('ąćęłńóśźżĄĆĘŁŃÓŚŹŻ')
    polish_words = [
        'jest', 'być', 'mieć', 'w', 'na', 'z', 'do', 'że', 'się', 'nie', 'jak',
        'co', 'ja', 'ty', 'on', 'ona', 'my', 'wy', 'oni', 'to', 'ten', 'ta'
    ]
    
    # Sprawdź polskie znaki
    if any(char in polish_chars for char in text):
        return True
    
    # Sprawdź polskie słowa
    words = text.lower().split()
    polish_word_count = sum(1 for word in words if word in polish_words)
    
    # Jeśli >30% słów to polskie słowa
    if len(words) > 0 and polish_word_count / len(words) > 0.3:
        return True
    
    return False

def parse_universal_flags(text):
    """Legacy wrapper dla kompatybilności"""
    parsed_text, profile_id, flags = parse_audiobook_command(text)
    
    # Konwertuj profil na engine dla legacy systemu
    if profile_id:
        if profile_id == 'pawel':
            flags['engine'] = 'piper_voice_cloning'
        else:
            flags['engine'] = 'enhanced_piper'
        flags['profile'] = profile_id
    
    return flags, parsed_text

def apply_default_flags(flags, command):
    """Apply default flags for audiobook commands"""
    defaults = {
        'file_type': 'inline',
        'language': 'polish',  # Domyślnie polski
        'voice_type': 'male',  # Domyślnie męski (Twój głos)
        'engine': 'auto',
        'profile': 'pawel'  # Domyślnie Twój profil
    }
    defaults.update(flags)
    return defaults

# Example usage and tests
if __name__ == "__main__":
    test_commands = [
        "/ab Cześć jak się masz:pawel",
        "/ab Hello world:natural",
        "/ab [polish,male] Witaj świecie", 
        "/ab [pawel] Jak się masz?",
        "/ab Dzień dobry",
        "/ab Hello there",
        "/ab Text with colon: but no profile after",
        "/ab [voice_cloning] Legacy command"
    ]
    
    for cmd in test_commands:
        text, profile, flags = parse_audiobook_command(cmd)
        print(f"Input: {cmd}")
        print(f"  Text: '{text}'")
        print(f"  Profile: '{profile}'")
        print(f"  Flags: {flags}")
        print()
