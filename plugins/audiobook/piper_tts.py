#!/usr/bin/env python3
"""
Piper TTS Wrapper - Interfejs Python dla Piper TTS z obsługą polskiego
"""

import os
import subprocess
import tempfile
import logging
from pathlib import Path
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class PiperTTS:
    """Wrapper dla Piper TTS - wysokiej jakości polish TTS"""
    
    def __init__(self, models_dir="models/tts"):
        self.models_dir = Path(models_dir)
        self.piper_exe = self.models_dir / "piper" / "piper.exe"
        
        # Polski model - jest bezpośrednio w models/tts/
        self.polish_model = self.models_dir / "pl_PL-gosia-medium.onnx"
        
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
    
    def synthesize_text(self, text: str, output_path: str, voice_type: str = "female") -> bool:
        """
        Syntezuje tekst do audio używając Piper TTS
        
        Args:
            text: Tekst do syntezowania
            output_path: Ścieżka do pliku wyjściowego
            voice_type: Typ głosu (obecnie ignorowany, Piper ma jeden model)
            
        Returns:
            bool: True jeśli sukces, False w przeciwnym razie
        """
        if not self.available:
            logger.error("Piper TTS nie jest dostępny")
            return False
            
        try:
            # Upewnij się że output_path jest bezwzględny
            output_path = os.path.abspath(output_path)
            
            # Komenda Piper względem katalogu z bibliotekami  
            cmd = [
                f".{os.path.sep}piper.exe",  # Względna ścieżka z kropką
                "--model", f"..{os.path.sep}pl_PL-gosia-medium.onnx",  # Model jest poziom wyżej
                "--output_file", output_path  # Bezwzględna ścieżka wyjścia
            ]
            
            logger.info(f"Uruchamianie Piper TTS: {' '.join(cmd)}")
            logger.info(f"Tekst do syntezy: '{text[:50]}...'")
            logger.info(f"Katalog roboczy: {self.piper_exe.parent}")
            
            # Uruchom Piper z katalogu zawierającego DLL
            result = subprocess.run(
                cmd,
                input=text,
                text=True,
                capture_output=True,
                timeout=30,
                cwd=str(self.piper_exe.parent),  # Katalog z piper.exe i DLL
                shell=True,  # Użyj shell
                encoding='utf-8'  # Ustaw kodowanie UTF-8
            )
            
            if result.returncode == 0:
                if os.path.exists(output_path):
                    file_size = os.path.getsize(output_path)
                    logger.info(f"Piper TTS sukces: {file_size} bytes")
                    return True
                else:
                    logger.error(f"Piper TTS: Brak pliku wyjściowego {output_path}")
                    logger.error(f"STDOUT: {result.stdout}")
                    logger.error(f"STDERR: {result.stderr}")
                    return False
            else:
                logger.error(f"Piper TTS błąd - kod: {result.returncode}")
                logger.error(f"STDOUT: {result.stdout}")
                logger.error(f"STDERR: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("Piper TTS timeout")
            return False
        except Exception as e:
            logger.error(f"Piper TTS wyjątek: {e}")
            return False
    
    def test_synthesis(self) -> bool:
        """Test syntezy polskiego tekstu"""
        if not self.available:
            return False
            
        test_text = "Witaj! To jest test polskiego systemu syntezy mowy Piper."
        
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
            output_path = tmp.name
            
        try:
            success = self.synthesize_text(test_text, output_path)
            if success and os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                logger.info(f"Test Piper TTS zakończony sukcesem: {file_size} bytes")
                os.unlink(output_path)  # Cleanup
                return True
            else:
                logger.error("Test Piper TTS nie powiódł się")
                return False
        except Exception as e:
            logger.error(f"Błąd podczas testu Piper TTS: {e}")
            return False
        finally:
            # Cleanup
            if os.path.exists(output_path):
                try:
                    os.unlink(output_path)
                except:
                    pass
    
    def get_info(self) -> Dict[str, Any]:
        """Zwraca informacje o Piper TTS"""
        return {
            "name": "Piper TTS",
            "available": self.available,
            "language": "Polish (pl_PL)",
            "model": "gosia-medium",
            "quality": "Medium",
            "piper_exe": str(self.piper_exe),
            "model_path": str(self.polish_model)
        }

# Factory function
def get_piper_tts(models_dir="models/tts") -> PiperTTS:
    """Tworzy instancję Piper TTS"""
    return PiperTTS(models_dir)

if __name__ == "__main__":
    # Ustaw debug logging
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    # Test Piper TTS
    print("🎵 Test Piper TTS")
    print("=" * 40)
    
    piper = get_piper_tts()
    info = piper.get_info()
    
    print(f"Piper TTS Info:")
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    if piper.is_available():
        print("\n🧪 Uruchamianie testu syntezy...")
        if piper.test_synthesis():
            print("✅ Test zakończony sukcesem!")
        else:
            print("❌ Test nie powiódł się!")
    else:
        print("\n❌ Piper TTS nie jest dostępny!")
        print("Sprawdź czy piper.exe i modele zostały pobrane poprawnie.")
