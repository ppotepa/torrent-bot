#!/usr/bin/env python3
"""
Voice Profiles System - System profili głosowych dla bot TTS
Umożliwia tworzenie i zarządzanie profilami syntezy głosu opartymi na próbkach referencyjnych
"""

import os
import json
import tempfile
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
import torch
import torchaudio

logger = logging.getLogger(__name__)

class VoiceProfileManager:
    """Manager profili głosowych"""
    
    def __init__(self, profiles_dir: str = "voice_profiles"):
        self.profiles_dir = Path(profiles_dir)
        self.profiles_dir.mkdir(exist_ok=True)
        
        # Profile configuration
        self.profiles_config_path = self.profiles_dir / "profiles.json"
        self.profiles = self._load_profiles()
        
        # Domyślne profile
        self._initialize_default_profiles()
        
    def _load_profiles(self) -> Dict[str, Dict[str, Any]]:
        """Ładuje konfigurację profili z pliku"""
        if self.profiles_config_path.exists():
            try:
                with open(self.profiles_config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Błąd ładowania profili: {e}")
        
        return {}
    
    def _save_profiles(self):
        """Zapisuje konfigurację profili do pliku"""
        try:
            with open(self.profiles_config_path, 'w', encoding='utf-8') as f:
                json.dump(self.profiles, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Błąd zapisu profili: {e}")
    
    def _initialize_default_profiles(self):
        """Inicjalizuje domyślne profile głosowe"""
        default_profiles = {
            "pawel": {
                "name": "Paweł (Twój głos)",
                "description": "Profil oparty na próbkach głosu Pawła",
                "type": "voice_cloning",
                "reference_samples": ["mowa.wav", "mowa-2.wav"],
                "speaker_embedding": "pawel_speaker_embedding.pt",
                "quality": "premium",
                "language": "polish",
                "voice_type": "male",
                "parameters": {
                    "voice_strength": 1.0,
                    "naturalness": 0.9,
                    "clarity": 0.8,
                    "emotional_tone": "neutral"
                }
            },
            "natural": {
                "name": "Naturalny Polski",
                "description": "Wysoka jakość TTS bez klonowania głosu",
                "type": "enhanced_piper",
                "quality": "high",
                "language": "polish",
                "voice_type": "male",
                "parameters": {
                    "noise_scale": 0.333,
                    "length_scale": 1.1,
                    "noise_w": 0.4,
                    "sentence_silence": 0.1
                }
            },
            "expressive": {
                "name": "Ekspresyjny Polski",
                "description": "Ekspresyjny styl z większą emocjonalnością",
                "type": "enhanced_piper",
                "quality": "high",
                "language": "polish",
                "voice_type": "male",
                "parameters": {
                    "noise_scale": 0.4,
                    "length_scale": 1.05,
                    "noise_w": 0.5,
                    "sentence_silence": 0.15
                }
            },
            "fast": {
                "name": "Szybki",
                "description": "Szybka synteza z dobrą jakością",
                "type": "enhanced_piper",
                "quality": "good",
                "language": "polish",
                "voice_type": "male",
                "parameters": {
                    "noise_scale": 0.5,
                    "length_scale": 0.9,
                    "noise_w": 0.3,
                    "sentence_silence": 0.05
                }
            },
            "female": {
                "name": "Kobieta Naturalna",
                "description": "Naturalny kobiecy głos polski",
                "type": "enhanced_piper",
                "quality": "high",
                "language": "polish",
                "voice_type": "female",
                "parameters": {
                    "noise_scale": 0.333,
                    "length_scale": 1.15,
                    "noise_w": 0.35,
                    "sentence_silence": 0.12
                }
            }
        }
        
        # Dodaj domyślne profile jeśli nie istnieją
        for profile_id, profile_data in default_profiles.items():
            if profile_id not in self.profiles:
                self.profiles[profile_id] = profile_data
                logger.info(f"Dodano domyślny profil: {profile_id}")
        
        self._save_profiles()
    
    def get_profile(self, profile_id: str) -> Optional[Dict[str, Any]]:
        """Pobiera profil po ID"""
        return self.profiles.get(profile_id)
    
    def list_profiles(self) -> Dict[str, str]:
        """Zwraca listę dostępnych profili z opisami"""
        return {
            profile_id: profile_data.get("name", profile_id)
            for profile_id, profile_data in self.profiles.items()
        }
    
    def get_profile_description(self, profile_id: str) -> str:
        """Zwraca szczegółowy opis profilu"""
        profile = self.get_profile(profile_id)
        if not profile:
            return f"❌ Profil '{profile_id}' nie istnieje"
        
        name = profile.get("name", profile_id)
        description = profile.get("description", "Brak opisu")
        quality = profile.get("quality", "unknown").title()
        language = profile.get("language", "unknown").title()
        voice_type = profile.get("voice_type", "unknown").title()
        profile_type = profile.get("type", "unknown")
        
        emoji = {
            "voice_cloning": "🎭",
            "enhanced_piper": "🎵",
            "openvoice": "🎤",
            "standard": "🔊"
        }.get(profile_type, "🎧")
        
        return f"{emoji} **{name}**\n📝 {description}\n⚙️ Typ: {profile_type}\n🌟 Jakość: {quality}\n🌍 Język: {language}\n👤 Głos: {voice_type}"
    
    def create_voice_cloning_profile(self, profile_id: str, name: str, reference_samples: List[str], 
                                   description: str = "", parameters: Optional[Dict] = None) -> bool:
        """
        Tworzy nowy profil voice cloning z próbek referencyjnych
        
        Args:
            profile_id: Unikalny identyfikator profilu
            name: Przyjazna nazwa profilu
            reference_samples: Lista ścieżek do próbek referencyjnych
            description: Opis profilu
            parameters: Dodatkowe parametry syntezy
            
        Returns:
            bool: True jeśli sukces
        """
        try:
            # Sprawdź czy próbki istnieją
            for sample in reference_samples:
                if not os.path.exists(sample):
                    logger.error(f"Próbka nie istnieje: {sample}")
                    return False
            
            # Utwórz profil
            profile_data = {
                "name": name,
                "description": description or f"Profil voice cloning: {name}",
                "type": "voice_cloning",
                "reference_samples": reference_samples,
                "speaker_embedding": f"{profile_id}_speaker_embedding.pt",
                "quality": "premium",
                "language": "polish",
                "voice_type": "male",  # Można wykryć automatycznie
                "parameters": parameters or {
                    "voice_strength": 1.0,
                    "naturalness": 0.9,
                    "clarity": 0.8,
                    "emotional_tone": "neutral"
                },
                "created_at": str(Path.cwd())
            }
            
            self.profiles[profile_id] = profile_data
            self._save_profiles()
            
            logger.info(f"Utworzono profil voice cloning: {profile_id}")
            return True
            
        except Exception as e:
            logger.error(f"Błąd tworzenia profilu voice cloning: {e}")
            return False
    
    def create_enhanced_piper_profile(self, profile_id: str, name: str, voice_type: str = "male",
                                    quality: str = "high", parameters: Optional[Dict] = None,
                                    description: str = "") -> bool:
        """
        Tworzy nowy profil Enhanced Piper TTS
        
        Args:
            profile_id: Unikalny identyfikator profilu
            name: Przyjazna nazwa profilu
            voice_type: Typ głosu (male/female)
            quality: Jakość (high/good/fast)
            parameters: Parametry syntezy
            description: Opis profilu
            
        Returns:
            bool: True jeśli sukces
        """
        try:
            # Domyślne parametry według jakości
            quality_presets = {
                "high": {
                    "noise_scale": 0.333,
                    "length_scale": 1.1,
                    "noise_w": 0.4,
                    "sentence_silence": 0.1
                },
                "good": {
                    "noise_scale": 0.4,
                    "length_scale": 1.05,
                    "noise_w": 0.45,
                    "sentence_silence": 0.08
                },
                "fast": {
                    "noise_scale": 0.5,
                    "length_scale": 0.9,
                    "noise_w": 0.3,
                    "sentence_silence": 0.05
                }
            }
            
            # Utwórz profil
            profile_data = {
                "name": name,
                "description": description or f"Profil Enhanced Piper: {name}",
                "type": "enhanced_piper",
                "quality": quality,
                "language": "polish",
                "voice_type": voice_type,
                "parameters": parameters or quality_presets.get(quality, quality_presets["good"]),
                "created_at": str(Path.cwd())
            }
            
            self.profiles[profile_id] = profile_data
            self._save_profiles()
            
            logger.info(f"Utworzono profil Enhanced Piper: {profile_id}")
            return True
            
        except Exception as e:
            logger.error(f"Błąd tworzenia profilu Enhanced Piper: {e}")
            return False
    
    def delete_profile(self, profile_id: str) -> bool:
        """Usuwa profil"""
        if profile_id in self.profiles:
            del self.profiles[profile_id]
            self._save_profiles()
            logger.info(f"Usunięto profil: {profile_id}")
            return True
        return False
    
    def get_synthesis_parameters(self, profile_id: str) -> Dict[str, Any]:
        """
        Zwraca parametry syntezy dla profilu
        
        Returns:
            Dict zawierający wszystkie potrzebne parametry do syntezy
        """
        profile = self.get_profile(profile_id)
        if not profile:
            # Fallback do domyślnego profilu
            logger.warning(f"Profil '{profile_id}' nie istnieje, używam 'natural'")
            profile = self.get_profile("natural")
            if not profile:
                # Ostateczny fallback
                return {
                    "type": "enhanced_piper",
                    "language": "polish",
                    "voice_type": "male",
                    "quality": "good",
                    "parameters": {
                        "noise_scale": 0.4,
                        "length_scale": 1.05,
                        "noise_w": 0.45,
                        "sentence_silence": 0.08
                    }
                }
        
        return {
            "type": profile.get("type", "enhanced_piper"),
            "language": profile.get("language", "polish"),
            "voice_type": profile.get("voice_type", "male"),
            "quality": profile.get("quality", "good"),
            "parameters": profile.get("parameters", {}),
            "reference_samples": profile.get("reference_samples", []),
            "speaker_embedding": profile.get("speaker_embedding")
        }

# Global instance
_voice_profile_manager = None

def get_voice_profile_manager() -> VoiceProfileManager:
    """Zwraca globalną instancję VoiceProfileManager"""
    global _voice_profile_manager
    if _voice_profile_manager is None:
        # Utwórz folder w plugins/audiobook
        profiles_dir = Path(__file__).parent / "voice_profiles"
        _voice_profile_manager = VoiceProfileManager(str(profiles_dir))
    return _voice_profile_manager

def list_available_profiles() -> Dict[str, str]:
    """Szybki dostęp do listy profili"""
    return get_voice_profile_manager().list_profiles()

def get_profile_synthesis_params(profile_id: str) -> Dict[str, Any]:
    """Szybki dostęp do parametrów syntezy"""
    return get_voice_profile_manager().get_synthesis_parameters(profile_id)
