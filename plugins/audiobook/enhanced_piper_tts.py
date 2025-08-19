#!/usr/bin/env python3
"""
Enhanced Piper TTS - Ulepszona wersja z naturalnymi parametrami dźwięku
"""

import os
import subprocess
import tempfile
import logging
from pathlib import Path
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class EnhancedPiperTTS:
    """Ulepszona wersja Piper TTS z naturalnymi parametrami audio"""
    
    def __init__(self, models_dir="models/tts"):
        self.models_dir = Path(models_dir)
        self.piper_exe = self.models_dir / "piper" / "piper.exe"
        self.polish_model = self.models_dir / "pl_PL-gosia-medium.onnx"
        
        # 🎯 ULEPSZONE PARAMETRY dla naturalnego dźwięku
        self.audio_params = {
            # Redukcja szumu generatora (domyślnie 0.667 → 0.333)
            'noise_scale': 0.333,
            
            # Wydłużenie fonemów dla płynności (domyślnie 1.0 → 1.1) 
            'length_scale': 1.1,
            
            # Redukcja szumu szerokości fonemów (domyślnie 0.8 → 0.4)
            'noise_w': 0.4,
            
            # Krótsze przerwy między zdaniami (domyślnie 0.2 → 0.1)
            'sentence_silence': 0.1
        }
        
        # Sprawdź dostępność
        self.available = self._check_availability()
        
    def _check_availability(self) -> bool:
        """Sprawdza czy Piper i polskie modele są dostępne"""
        if not self.piper_exe.exists():
            logger.warning(f"Piper executable nie znaleziony: {self.piper_exe}")
            return False
            
        if not self.polish_model.exists():
            logger.warning(f"Polski model nie znaleziony: {self.polish_model}")
            return False
            
        return True
    
    def is_available(self) -> bool:
        """Zwraca czy Piper TTS jest dostępny"""
        return self.available
    
    def synthesize_text(self, text: str, output_path: str, 
                       voice_type: str = "female", 
                       quality_preset: str = "natural") -> bool:
        """
        Syntezuje tekst do audio używając Enhanced Piper TTS
        
        Args:
            text: Tekst do syntezowania
            output_path: Ścieżka do pliku wyjściowego
            voice_type: Typ głosu (obecnie ignorowany)
            quality_preset: Preset jakości ('natural', 'fast', 'slow')
            
        Returns:
            bool: True jeśli sukces, False w przeciwnym razie
        """
        if not self.available:
            logger.error("Enhanced Piper TTS nie jest dostępny")
            return False
            
        try:
            # Wybierz parametry na podstawie presetu
            params = self._get_quality_params(quality_preset)
            
            # Upewnij się że output_path jest bezwzględny
            output_path = os.path.abspath(output_path)
            
            # 🎯 ULEPSZONA KOMENDA z naturalnymi parametrami
            cmd = [
                f".{os.path.sep}piper.exe",
                "--model", f"..{os.path.sep}pl_PL-gosia-medium.onnx",
                "--output_file", output_path,
                "--noise_scale", str(params['noise_scale']),
                "--length_scale", str(params['length_scale']), 
                "--noise_w", str(params['noise_w']),
                "--sentence_silence", str(params['sentence_silence'])
            ]
            
            logger.info(f"🎭 Enhanced Piper TTS ({quality_preset} preset)")
            logger.info(f"   Noise scale: {params['noise_scale']} (mniej robotyczny)")
            logger.info(f"   Length scale: {params['length_scale']} (płynniejszy)")
            logger.info(f"   Noise width: {params['noise_w']} (wyraźniejszy)")
            logger.info(f"   Sentence silence: {params['sentence_silence']}s")
            logger.info(f"   Tekst: '{text[:50]}...'")
            
            # Uruchom Enhanced Piper z naturalnymi parametrami
            result = subprocess.run(
                cmd,
                input=text,
                text=True,
                capture_output=True,
                timeout=30,
                cwd=str(self.piper_exe.parent),
                shell=True,
                encoding='utf-8'
            )
            
            if result.returncode == 0:
                if os.path.exists(output_path):
                    file_size = os.path.getsize(output_path)
                    logger.info(f"✅ Enhanced Piper TTS sukces: {file_size} bytes")
                    
                    # Log output dla debugging
                    if result.stdout:
                        for line in result.stdout.strip().split('\n'):
                            if 'Real-time factor' in line:
                                logger.info(f"   Performance: {line}")
                    
                    return True
                else:
                    logger.error(f"Enhanced Piper TTS: Brak pliku wyjściowego {output_path}")
                    logger.error(f"STDOUT: {result.stdout}")
                    logger.error(f"STDERR: {result.stderr}")
                    return False
            else:
                logger.error(f"Enhanced Piper TTS błąd - kod: {result.returncode}")
                logger.error(f"STDOUT: {result.stdout}")
                logger.error(f"STDERR: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("Enhanced Piper TTS timeout")
            return False
        except Exception as e:
            logger.error(f"Enhanced Piper TTS wyjątek: {e}")
            return False
    
    def convert_text_to_speech(self, text: str, output_path: str, 
                             language: str = "polish", voice_type: str = "male",
                             parameters: Optional[Dict] = None) -> bool:
        """
        Metoda kompatybilna ze starym interfejsem
        
        Args:
            text: Tekst do syntezowania
            output_path: Ścieżka do pliku wyjściowego  
            language: Język (obecnie ignorowany - zawsze polski)
            voice_type: Typ głosu (obecnie ignorowany)
            parameters: Parametry syntezy
            
        Returns:
            bool: True jeśli sukces
        """
        # Map parameters to quality preset
        if parameters:
            noise_scale = parameters.get('noise_scale', 0.333)
            if noise_scale <= 0.35:
                quality_preset = "natural"
            elif noise_scale <= 0.45:
                quality_preset = "expressive" 
            elif noise_scale <= 0.55:
                quality_preset = "fast"
            else:
                quality_preset = "slow"
        else:
            quality_preset = "natural"
        
        return self.synthesize_text(text, output_path, voice_type, quality_preset)
    
    def _get_quality_params(self, preset: str) -> Dict[str, float]:
        """Zwraca parametry jakości dla danego presetu"""
        
        presets = {
            'natural': {
                'noise_scale': 0.333,      # Bardzo mało szumu
                'length_scale': 1.1,       # Lekko wydłużone fonemy  
                'noise_w': 0.4,           # Mała wariancja szerokości
                'sentence_silence': 0.1    # Krótkie pauzy
            },
            'expressive': {
                'noise_scale': 0.4,        # Trochę więcej ekspresji
                'length_scale': 1.15,      # Bardziej wydłużone
                'noise_w': 0.5,           # Więcej wariacji
                'sentence_silence': 0.15   # Dłuższe pauzy dla dramatu
            },
            'fast': {
                'noise_scale': 0.5,        # Szybkie, ale czytelne
                'length_scale': 0.9,       # Krótsze fonemy
                'noise_w': 0.3,           # Mniej wariacji
                'sentence_silence': 0.05   # Bardzo krótkie pauzy
            },
            'slow': {
                'noise_scale': 0.2,        # Bardzo czyste
                'length_scale': 1.3,       # Bardzo wydłużone
                'noise_w': 0.3,           # Stabilne
                'sentence_silence': 0.3    # Długie pauzy
            }
        }
        
        return presets.get(preset, self.audio_params)
    
    def test_synthesis(self, quality_preset: str = "natural") -> bool:
        """Test syntezy polskiego tekstu z Enhanced parametrami"""
        if not self.available:
            return False
            
        test_text = "Witaj! To jest test ulepszonego polskiego systemu syntezy mowy z naturalnymi parametrami."
        
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
            output_path = tmp.name
            
        try:
            success = self.synthesize_text(test_text, output_path, quality_preset=quality_preset)
            if success and os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                logger.info(f"✅ Test Enhanced Piper TTS ({quality_preset}) zakończony sukcesem: {file_size} bytes")
                os.unlink(output_path)  # Cleanup
                return True
            else:
                logger.error("❌ Test Enhanced Piper TTS nie powiódł się")
                return False
        except Exception as e:
            logger.error(f"💥 Test Enhanced Piper TTS błąd: {e}")
            return False

# Fabryka dla kompatybilności wstecznej
def get_enhanced_piper_tts(models_dir="models/tts") -> EnhancedPiperTTS:
    """Factory function dla Enhanced Piper TTS"""
    return EnhancedPiperTTS(models_dir)

# Domyślna instancja
_enhanced_piper_instance = None

def get_piper_tts(models_dir="models/tts") -> EnhancedPiperTTS:
    """Zwraca singleton Enhanced Piper TTS instance"""
    global _enhanced_piper_instance
    if _enhanced_piper_instance is None:
        _enhanced_piper_instance = EnhancedPiperTTS(models_dir)
    return _enhanced_piper_instance

if __name__ == "__main__":
    # Test wszystkich presetów
    piper = EnhancedPiperTTS()
    
    if not piper.is_available():
        print("❌ Enhanced Piper TTS nie jest dostępny!")
        exit(1)
    
    presets = ['natural', 'expressive', 'fast', 'slow']
    
    for preset in presets:
        print(f"\n🧪 Testowanie preset: {preset}")
        success = piper.test_synthesis(preset)
        if success:
            print(f"✅ Preset {preset} działa!")
        else:
            print(f"❌ Preset {preset} nie działa!")
