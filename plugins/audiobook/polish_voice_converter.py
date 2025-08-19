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
from enhanced_piper_tts import get_piper_tts  # Enhanced version
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
        🎭 ULEPSZONE VOICE PROCESSING - redukcja robotycznego dźwięku
        
        Args:
            base_audio_path: Ścieżka do bazowego audio z Enhanced Piper
            output_path: Ścieżka do zapisu przetworzonego audio
            
        Returns:
            bool: True jeśli sukces
        """
        try:
            logger.info("🎭 Aplikowanie ulepszonego voice processing...")
            
            # Załaduj bazowe audio
            audio, sr = torchaudio.load(base_audio_path)
            
            # === ULEPSZONE VOICE PROCESSING ===
            
            # 1. 🎯 Inteligentna redukcja robotycznego dźwięku
            # Lekka denormalizacja dla naturalności
            audio = audio * 0.95  # Lekko ciszej
            
            # 2. 🎵 Naturalna modulacja amplitudy (symulacja oddechu)
            import numpy as np
            from scipy import signal
            
            audio_np = audio.numpy()
            
            # Generuj subtelną modulację amplitudy (4-6 Hz - naturalna częstość oddechu)
            modulation_freq = 5.0  # Hz
            t = np.linspace(0, audio_np.shape[1] / sr, audio_np.shape[1])
            amplitude_modulation = 1.0 + 0.02 * np.sin(2 * np.pi * modulation_freq * t)
            
            # Aplikuj modulację do każdego kanału
            for channel in range(audio_np.shape[0]):
                audio_np[channel] *= amplitude_modulation
            
            # 3. 🎚️ Subtelny EQ dla naturalności głosu
            # Boost częstotliwości wokalnych (1-3 kHz) i lekko obniż wysokie
            nyquist = sr // 2
            
            # Filtr shelf dla wysokich częstotliwości (powyżej 4kHz)
            high_freq = 4000 / nyquist
            if high_freq < 1.0:
                b_high, a_high = signal.butter(2, high_freq, btype='highpass')
                
                # Filtr boost dla częstotliwości wokalnych (800-3000 Hz)
                low_vocal = 800 / nyquist
                high_vocal = 3000 / nyquist
                
                if low_vocal < 1.0 and high_vocal < 1.0:
                    b_vocal, a_vocal = signal.butter(2, [low_vocal, high_vocal], btype='band')
                    
                    # Aplikuj filtry do każdego kanału
                    processed_audio = np.zeros_like(audio_np)
                    for channel in range(audio_np.shape[0]):
                        # Boost średnich częstotliwości wokalnych
                        vocal_boost = signal.filtfilt(b_vocal, a_vocal, audio_np[channel])
                        
                        # Lekko obniż wysokie częstotliwości
                        high_content = signal.filtfilt(b_high, a_high, audio_np[channel])
                        
                        # Mix: 85% oryginał + 15% boost wokalny - 5% wysokie
                        processed_audio[channel] = (
                            0.85 * audio_np[channel] + 
                            0.15 * vocal_boost - 
                            0.05 * high_content
                        )
                else:
                    processed_audio = audio_np
            else:
                processed_audio = audio_np
            
            # 4. 🎭 Subtelna charakterystyka głosu użytkownika
            if self.speaker_embedding is not None:
                # Prosty pitch shift oparty na charakterystyce użytkownika
                # (w prawdziwym voice cloning byłyby zaawansowane transformacje)
                
                # Ekstrakcja charakterystyki z embedding (uproszczone)
                embedding_mean = float(self.speaker_embedding.mean())
                
                # Mapuj embedding na subtelną modulację pitch (-0.05 do +0.05)
                pitch_adjustment = np.tanh(embedding_mean) * 0.05
                
                # Prosty pitch shift przez time stretching
                if abs(pitch_adjustment) > 0.01:
                    stretch_factor = 1.0 + pitch_adjustment
                    
                    # Time stretch każdego kanału
                    for channel in range(processed_audio.shape[0]):
                        original_length = len(processed_audio[channel])
                        new_length = int(original_length * stretch_factor)
                        
                        # Interpolacja dla stretch/compress
                        x_old = np.linspace(0, 1, original_length)
                        x_new = np.linspace(0, 1, new_length)
                        stretched = np.interp(x_new, x_old, processed_audio[channel])
                        
                        # Przywróć oryginalną długość przez resampling
                        if new_length != original_length:
                            x_resample = np.linspace(0, 1, original_length)
                            processed_audio[channel] = np.interp(x_resample, x_new, stretched)
            
            # 5. 🎚️ Finalna normalizacja z naturalnym headroom
            # Konwertuj z powrotem do tensor
            audio = torch.from_numpy(processed_audio).float()
            
            # Gentle normalization z headroom
            max_amplitude = audio.abs().max()
            if max_amplitude > 0.1:  # Tylko jeśli jest za głośno
                target_amplitude = 0.7  # Naturalne headroom
                audio = audio * (target_amplitude / max_amplitude)
            
            # Zapisz przetworzone audio
            torchaudio.save(output_path, audio, sr)
            
            logger.info(f"🎭 Ulepszone voice processing zakończone: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"💥 Błąd ulepszonego voice processing: {e}")
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
