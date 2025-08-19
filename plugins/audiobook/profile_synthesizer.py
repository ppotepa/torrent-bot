#!/usr/bin/env python3
"""
Profile-based TTS Synthesizer - Syntezator TTS oparty na profilach głosowych
Integruje wszystkie dostępne silniki TTS z systemem profili
"""

import os
import tempfile
import logging
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
import torch

from voice_profiles import get_voice_profile_manager, get_profile_synthesis_params
from enhanced_piper_tts import get_piper_tts
from polish_voice_converter import PolishVoiceConverter

logger = logging.getLogger(__name__)

class ProfileBasedTTSSynthesizer:
    """Syntezator TTS oparty na profilach głosowych"""
    
    def __init__(self):
        self.profile_manager = get_voice_profile_manager()
        self.piper_tts = get_piper_tts()
        self.voice_converter = None
        self._initialize_voice_converter()
        
    def _initialize_voice_converter(self):
        """Inicjalizuje voice converter dla voice cloning"""
        try:
            # Sprawdź czy istnieje speaker embedding dla profilu Pawła
            embedding_path = Path(__file__).parent / "simple_speaker_embedding.pt"
            if embedding_path.exists():
                self.voice_converter = PolishVoiceConverter(str(embedding_path))
                if self.voice_converter.is_available():
                    logger.info("Voice Converter zainicjalizowany")
                else:
                    logger.warning("Voice Converter niedostępny")
            else:
                logger.warning(f"Speaker embedding nie znaleziony: {embedding_path}")
        except Exception as e:
            logger.error(f"Błąd inicjalizacji Voice Converter: {e}")
    
    def synthesize_with_profile(self, text: str, profile_id: str, output_path: str) -> Tuple[bool, str]:
        """
        Syntezuje mowę używając określonego profilu
        
        Args:
            text: Tekst do syntezy
            profile_id: ID profilu głosowego
            output_path: Ścieżka do zapisu audio
            
        Returns:
            Tuple[bool, str]: (sukces, opis wyniku)
        """
        try:
            # Pobierz parametry profilu
            params = get_profile_synthesis_params(profile_id)
            profile_type = params.get("type", "enhanced_piper")
            
            logger.info(f"🎭 Synteza z profilem '{profile_id}' (typ: {profile_type})")
            
            if profile_type == "voice_cloning":
                return self._synthesize_voice_cloning(text, params, output_path, profile_id)
            elif profile_type == "enhanced_piper":
                return self._synthesize_enhanced_piper(text, params, output_path, profile_id)
            else:
                return False, f"Nieznany typ profilu: {profile_type}"
                
        except Exception as e:
            error_msg = f"Błąd syntezy z profilem '{profile_id}': {e}"
            logger.error(error_msg)
            return False, error_msg
    
    def _synthesize_voice_cloning(self, text: str, params: Dict[str, Any], 
                                output_path: str, profile_id: str) -> Tuple[bool, str]:
        """Synteza z voice cloning"""
        if not self.voice_converter or not self.voice_converter.is_available():
            logger.warning("Voice Converter niedostępny, fallback do Enhanced Piper")
            return self._synthesize_enhanced_piper(text, params, output_path, profile_id)
        
        try:
            logger.info(f"🎭 Voice Cloning synteza dla profilu '{profile_id}'")
            
            # Użyj Enhanced Piper jako bazy
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                base_audio_path = temp_file.name
            
            # Synteza z Enhanced Piper (naturalne parametry)
            piper_params = {
                "noise_scale": 0.333,
                "length_scale": 1.1,
                "noise_w": 0.4,
                "sentence_silence": 0.1
            }
            
            success = self.piper_tts.convert_text_to_speech(
                text=text,
                output_path=base_audio_path,
                language="polish",
                voice_type=params.get("voice_type", "male"),
                parameters=piper_params
            )
            
            if not success:
                os.unlink(base_audio_path)
                return False, "Błąd bazowej syntezy Enhanced Piper"
            
            # Aplikuj voice cloning processing
            success = self.voice_converter.simple_voice_processing(
                base_audio_path, output_path
            )
            
            # Cleanup
            os.unlink(base_audio_path)
            
            if success:
                # Sprawdź rozmiar pliku
                if os.path.exists(output_path):
                    size = os.path.getsize(output_path)
                    return True, f"Voice Cloning sukces ({size} bytes) - profil '{profile_id}'"
                else:
                    return False, "Voice Cloning - brak pliku wyjściowego"
            else:
                return False, "Voice Cloning processing failed"
                
        except Exception as e:
            return False, f"Voice Cloning błąd: {e}"
    
    def _synthesize_enhanced_piper(self, text: str, params: Dict[str, Any], 
                                 output_path: str, profile_id: str) -> Tuple[bool, str]:
        """Synteza z Enhanced Piper"""
        try:
            logger.info(f"🎵 Enhanced Piper synteza dla profilu '{profile_id}'")
            
            # Użyj parametrów z profilu
            piper_params = params.get("parameters", {
                "noise_scale": 0.4,
                "length_scale": 1.05,
                "noise_w": 0.45,
                "sentence_silence": 0.08
            })
            
            success = self.piper_tts.convert_text_to_speech(
                text=text,
                output_path=output_path,
                language=params.get("language", "polish"),
                voice_type=params.get("voice_type", "male"),
                parameters=piper_params
            )
            
            if success:
                # Sprawdź rozmiar pliku
                if os.path.exists(output_path):
                    size = os.path.getsize(output_path)
                    quality = params.get("quality", "good").title()
                    return True, f"Enhanced Piper sukces ({size} bytes) - {quality} profil '{profile_id}'"
                else:
                    return False, "Enhanced Piper - brak pliku wyjściowego"
            else:
                return False, "Enhanced Piper conversion failed"
                
        except Exception as e:
            return False, f"Enhanced Piper błąd: {e}"
    
    def get_available_profiles(self) -> Dict[str, str]:
        """Zwraca dostępne profile"""
        return self.profile_manager.list_profiles()
    
    def get_profile_info(self, profile_id: str) -> str:
        """Zwraca informacje o profilu"""
        return self.profile_manager.get_profile_description(profile_id)
    
    def create_user_profile_from_samples(self, profile_id: str, name: str, 
                                       sample_paths: list, description: str = "") -> bool:
        """
        Tworzy profil użytkownika z próbek głosowych
        
        Args:
            profile_id: Unikalny ID profilu
            name: Nazwa profilu
            sample_paths: Lista ścieżek do próbek
            description: Opis profilu
            
        Returns:
            bool: True jeśli sukces
        """
        try:
            # Sprawdź czy próbki istnieją
            existing_samples = []
            for sample_path in sample_paths:
                if os.path.exists(sample_path):
                    existing_samples.append(sample_path)
                else:
                    logger.warning(f"Próbka nie istnieje: {sample_path}")
            
            if not existing_samples:
                logger.error("Brak dostępnych próbek głosowych")
                return False
            
            # Utwórz profil voice cloning
            success = self.profile_manager.create_voice_cloning_profile(
                profile_id=profile_id,
                name=name,
                reference_samples=existing_samples,
                description=description or f"Profil voice cloning: {name}",
                parameters={
                    "voice_strength": 1.0,
                    "naturalness": 0.9,
                    "clarity": 0.8,
                    "emotional_tone": "neutral"
                }
            )
            
            if success:
                logger.info(f"Utworzono profil użytkownika: {profile_id}")
                return True
            else:
                logger.error(f"Błąd tworzenia profilu: {profile_id}")
                return False
                
        except Exception as e:
            logger.error(f"Błąd tworzenia profilu z próbek: {e}")
            return False

# Global instance
_tts_synthesizer = None

def get_tts_synthesizer() -> ProfileBasedTTSSynthesizer:
    """Zwraca globalną instancję syntezatora TTS"""
    global _tts_synthesizer
    if _tts_synthesizer is None:
        _tts_synthesizer = ProfileBasedTTSSynthesizer()
    return _tts_synthesizer

def synthesize_with_profile(text: str, profile_id: str, output_path: str) -> Tuple[bool, str]:
    """Szybka funkcja do syntezy z profilem"""
    return get_tts_synthesizer().synthesize_with_profile(text, profile_id, output_path)

def list_available_profiles() -> Dict[str, str]:
    """Szybka funkcja do listowania profili"""
    return get_tts_synthesizer().get_available_profiles()

def get_profile_description(profile_id: str) -> str:
    """Szybka funkcja do opisu profilu"""
    return get_tts_synthesizer().get_profile_info(profile_id)
