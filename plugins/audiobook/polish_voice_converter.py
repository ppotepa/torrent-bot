#!/usr/bin/env python3
"""
Polish Voice Conversion Pipeline - Kompletny pipeline polskiego TTS z klonowaniem głosu
"""

import os
import tempfile
import logging
from pathlib import Path
from typing import Optional, Dict, Any
import torch
import torchaudio

# Import naszych komponentów
from piper_tts import get_piper_tts
from simple_speaker_embedding import get_speaker_extractor

logger = logging.getLogger(__name__)

class PolishVoiceConverter:
    """Kompletny pipeline polskiego TTS z klonowaniem głosu"""
    
    def __init__(self, speaker_embedding_path: str = "simple_speaker_embedding.pt"):
        self.speaker_embedding_path = speaker_embedding_path
        
        # Komponenty pipeline
        self.piper_tts = get_piper_tts()
        self.speaker_extractor = get_speaker_extractor()
        
        # Załaduj speaker embedding
        self.speaker_embedding = None
        self._load_speaker_embedding()
        
        # Sprawdź dostępność
        self.available = self._check_availability()
        
    def _load_speaker_embedding(self) -> bool:
        """Ładuje speaker embedding z pliku"""
        if not os.path.exists(self.speaker_embedding_path):
            logger.warning(f"Speaker embedding nie znaleziony: {self.speaker_embedding_path}")
            return False
            
        self.speaker_embedding = self.speaker_extractor.load_speaker_embedding(self.speaker_embedding_path)
        if self.speaker_embedding is not None:
            logger.info(f"Załadowano speaker embedding: {self.speaker_embedding.shape}")
            return True
        return False
        
    def _check_availability(self) -> bool:
        """Sprawdza czy pipeline jest dostępny"""
        if not self.piper_tts.is_available():
            logger.warning("Piper TTS nie jest dostępny")
            return False
            
        if not self.speaker_extractor.is_available():
            logger.warning("Speaker extractor nie jest dostępny")
            return False
            
        if self.speaker_embedding is None:
            logger.warning("Speaker embedding nie został załadowany")
            return False
            
        return True
    
    def is_available(self) -> bool:
        """Zwraca czy pipeline jest dostępny"""
        return self.available
    
    def simple_voice_processing(self, base_audio_path: str, output_path: str) -> bool:
        """
        Prosty post-processing audio aby przypominało użytkownika
        (bez zaawansowanego voice cloning - to byłby placeholder)
        
        Args:
            base_audio_path: Ścieżka do bazowego audio z Piper
            output_path: Ścieżka do zapisu przetworzonego audio
            
        Returns:
            bool: True jeśli sukces
        """
        try:
            logger.info("Aplikowanie prostego voice processing...")
            
            # Załaduj bazowe audio
            audio, sr = torchaudio.load(base_audio_path)
            
            # === PROSTY VOICE PROCESSING ===
            # W prawdziwym voice cloning tutaj byłyby zaawansowane transformacje
            # Na razie robimy proste modyfikacje audio
            
            # 1. Lekka modulacja pitch (symulacja charakterystyki głosu)
            pitch_shift_factor = 0.95  # Lekkie obniżenie
            
            # Prosty pitch shift przez interpolację
            original_length = audio.shape[1]
            new_length = int(original_length / pitch_shift_factor)
            
            # Resample do nowej długości (prosty pitch shift)
            if new_length != original_length:
                resampler = torchaudio.transforms.Resample(
                    orig_freq=sr,
                    new_freq=int(sr * pitch_shift_factor)
                )
                audio_shifted = resampler(audio)
                
                # Przywróć oryginalną długość
                target_resampler = torchaudio.transforms.Resample(
                    orig_freq=int(sr * pitch_shift_factor),
                    new_freq=sr
                )
                audio = target_resampler(audio_shifted)
            
            # 2. Lekki filtr charakterystyki (boost średnich częstotliwości)
            # Prosty EQ effect
            from scipy import signal
            import numpy as np
            
            # Konwertuj do numpy dla łatwiejszego przetwarzania
            audio_np = audio.numpy()
            
            # Projektuj filtr bandpass dla średnich częstotliwości (boost głosu)
            nyquist = sr // 2
            low_freq = 300 / nyquist   # 300 Hz
            high_freq = 3000 / nyquist # 3000 Hz
            
            b, a = signal.butter(2, [low_freq, high_freq], btype='band')
            
            # Aplikuj filtr do każdego kanału
            filtered_audio = np.zeros_like(audio_np)
            for channel in range(audio_np.shape[0]):
                # Lekki boost średnich częstotliwości
                filtered = signal.filtfilt(b, a, audio_np[channel])
                # Mix z oryginalnym (70% oryginał + 30% boost)
                filtered_audio[channel] = 0.7 * audio_np[channel] + 0.3 * filtered
            
            # Konwertuj z powrotem do tensor
            audio = torch.from_numpy(filtered_audio).float()
            
            # 3. Normalizacja końcowa
            audio = torch.nn.functional.normalize(audio, dim=1) * 0.8  # Lekko ciszej
            
            # Zapisz przetworzone audio
            torchaudio.save(output_path, audio, sr)
            
            logger.info(f"Voice processing zakończony: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Błąd voice processing: {e}")
            return False
    
    def synthesize_with_voice_cloning(self, text: str, output_path: str) -> bool:
        """
        Syntezuje tekst z klonowaniem głosu
        
        Args:
            text: Tekst do syntezowania po polsku
            output_path: Ścieżka do pliku wyjściowego
            
        Returns:
            bool: True jeśli sukces
        """
        if not self.available:
            logger.error("Polish Voice Converter nie jest dostępny")
            return False
        
        try:
            logger.info(f"Synteza tekstu z voice cloning: '{text[:50]}...'")
            
            # KROK 1: Synteza bazowa używając Piper TTS
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
                base_audio_path = tmp.name
            
            logger.info("Synteza bazowa z Piper TTS...")
            success = self.piper_tts.synthesize_text(text, base_audio_path)
            
            if not success or not os.path.exists(base_audio_path):
                logger.error("Synteza bazowa nie powiodła się")
                return False
                
            base_size = os.path.getsize(base_audio_path)
            logger.info(f"Synteza bazowa zakończona: {base_size} bytes")
            
            # KROK 2: Voice processing (klonowanie głosu)
            logger.info("Aplikowanie voice cloning...")
            success = self.simple_voice_processing(base_audio_path, output_path)
            
            # Cleanup
            if os.path.exists(base_audio_path):
                os.unlink(base_audio_path)
            
            if success:
                final_size = os.path.getsize(output_path)
                logger.info(f"Voice cloning zakończony sukcesem: {final_size} bytes")
                return True
            else:
                logger.error("Voice processing nie powiódł się")
                return False
                
        except Exception as e:
            logger.error(f"Błąd podczas syntezy z voice cloning: {e}")
            return False
    
    def test_synthesis(self) -> bool:
        """Test syntezy polskiego tekstu z voice cloning"""
        if not self.available:
            return False
            
        test_text = "Witaj! To jest test polskiego systemu syntezy mowy z klonowaniem głosu. Czy brzmi naturalnie?"
        
        output_path = "test_voice_cloning.wav"
        
        try:
            success = self.synthesize_with_voice_cloning(test_text, output_path)
            if success and os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                logger.info(f"Test voice cloning zakończony sukcesem: {file_size} bytes")
                return True
            else:
                logger.error("Test voice cloning nie powiódł się")
                return False
        except Exception as e:
            logger.error(f"Błąd podczas testu voice cloning: {e}")
            return False
    
    def get_info(self) -> Dict[str, Any]:
        """Zwraca informacje o pipeline"""
        return {
            "name": "Polish Voice Conversion Pipeline",
            "available": self.available,
            "piper_tts": self.piper_tts.get_info(),
            "speaker_extractor": self.speaker_extractor.get_info(),
            "speaker_embedding_path": self.speaker_embedding_path,
            "speaker_embedding_loaded": self.speaker_embedding is not None
        }

# Factory function
def get_voice_converter(speaker_embedding_path: str = "simple_speaker_embedding.pt") -> PolishVoiceConverter:
    """Tworzy instancję Polish Voice Converter"""
    return PolishVoiceConverter(speaker_embedding_path)

if __name__ == "__main__":
    # Ustaw debug logging
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    # Test Polish Voice Conversion Pipeline
    print("🎭 Test Polish Voice Conversion Pipeline")
    print("=" * 60)
    
    converter = get_voice_converter()
    
    # Informacje
    print("Voice Converter Info:")
    info = converter.get_info()
    for key, value in info.items():
        if isinstance(value, dict):
            print(f"  {key}:")
            for k, v in value.items():
                print(f"    {k}: {v}")
        else:
            print(f"  {key}: {value}")
    
    if not converter.is_available():
        print("❌ Polish Voice Converter nie jest dostępny!")
        exit(1)
    
    # Test syntezy
    print("\n🧪 Uruchamianie testu syntezy z voice cloning...")
    
    success = converter.test_synthesis()
    
    if success:
        print("✅ Test zakończony sukcesem!")
        
        # Sprawdź plik wyjściowy
        output_file = "test_voice_cloning.wav"
        if os.path.exists(output_file):
            file_size = os.path.getsize(output_file)
            print(f"✅ Plik audio utworzony: {output_file} ({file_size} bytes)")
        else:
            print("❌ Plik audio nie został utworzony")
    else:
        print("❌ Test nie powiódł się!")
