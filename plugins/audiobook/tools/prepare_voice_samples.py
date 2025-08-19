#!/usr/bin/env python3
"""
Skrypt do przygotowania próbek głosu dla voice cloning
Konwertuje próbki do odpowiedniego formatu i przygotowuje je dla OpenVoice
"""

import os
import sys
import librosa
import soundfile as sf
import numpy as np
import noisereduce as nr
from pathlib import Path
import logging

# Konfiguracja logowania
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Parametry docelowe dla OpenVoice
TARGET_SAMPLE_RATE = 22050
TARGET_CHANNELS = 1  # mono
TARGET_DTYPE = np.float32

class VoiceSamplePreprocessor:
    """Klasa do preprocessing próbek głosu"""
    
    def __init__(self, input_dir=".", output_dir="voice_samples"):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
    def analyze_audio_file(self, file_path):
        """Analizuje parametry pliku audio"""
        try:
            # Załaduj audio używając librosa
            audio, sr = librosa.load(file_path, sr=None)
            duration = len(audio) / sr
            
            # Analizuj używając soundfile dla dokładnych informacji
            with sf.SoundFile(file_path) as f:
                frames = f.frames
                samplerate = f.samplerate
                channels = f.channels
                subtype = f.subtype
                
            info = {
                'file_path': str(file_path),
                'duration': duration,
                'sample_rate': samplerate,
                'channels': channels,
                'frames': frames,
                'subtype': subtype,
                'dtype': audio.dtype,
                'shape': audio.shape,
                'min_val': np.min(audio),
                'max_val': np.max(audio),
                'rms': np.sqrt(np.mean(audio**2))
            }
            
            return info, audio, sr
            
        except Exception as e:
            logger.error(f"Błąd podczas analizy {file_path}: {e}")
            return None, None, None
    
    def preprocess_audio(self, audio, sr):
        """Preprocessing audio - noise reduction, normalizacja"""
        try:
            # 1. Konwersja do mono jeśli stereo
            if len(audio.shape) > 1:
                audio = librosa.to_mono(audio)
            
            # 2. Resample do docelowej częstotliwości
            if sr != TARGET_SAMPLE_RATE:
                audio = librosa.resample(audio, orig_sr=sr, target_sr=TARGET_SAMPLE_RATE)
                sr = TARGET_SAMPLE_RATE
            
            # 3. Noise reduction
            audio_denoised = nr.reduce_noise(y=audio, sr=sr, prop_decrease=0.8)
            
            # 4. Normalizacja głośności do -20dB
            # Oblicz RMS i ustaw docelowy poziom
            current_rms = np.sqrt(np.mean(audio_denoised**2))
            target_rms = 0.1  # odpowiada około -20dB
            
            if current_rms > 0:
                audio_normalized = audio_denoised * (target_rms / current_rms)
            else:
                audio_normalized = audio_denoised
            
            # 5. Clipping protection
            audio_normalized = np.clip(audio_normalized, -1.0, 1.0)
            
            # 6. Trim silence na początku i końcu
            audio_trimmed, _ = librosa.effects.trim(audio_normalized, top_db=20)
            
            return audio_trimmed.astype(TARGET_DTYPE)
            
        except Exception as e:
            logger.error(f"Błąd podczas preprocessing: {e}")
            return None
    
    def process_sample(self, input_path, output_name):
        """Przetwarza pojedynczą próbkę głosu"""
        logger.info(f"Przetwarzanie: {input_path}")
        
        # Analiza pliku wejściowego
        info, audio, sr = self.analyze_audio_file(input_path)
        if audio is None:
            return False
        
        logger.info(f"Oryginalny plik:")
        logger.info(f"  - Czas trwania: {info['duration']:.2f}s")
        logger.info(f"  - Sample rate: {info['sample_rate']}Hz")
        logger.info(f"  - Kanały: {info['channels']}")
        logger.info(f"  - Format: {info['subtype']}")
        logger.info(f"  - RMS: {info['rms']:.4f}")
        
        # Preprocessing
        processed_audio = self.preprocess_audio(audio, sr)
        if processed_audio is None:
            return False
        
        # Zapisz przetworzony plik
        output_path = self.output_dir / f"{output_name}.wav"
        sf.write(output_path, processed_audio, TARGET_SAMPLE_RATE, subtype='PCM_16')
        
        # Analiza po przetworzeniu
        final_duration = len(processed_audio) / TARGET_SAMPLE_RATE
        final_rms = np.sqrt(np.mean(processed_audio**2))
        
        logger.info(f"Przetworzony plik:")
        logger.info(f"  - Czas trwania: {final_duration:.2f}s")
        logger.info(f"  - Sample rate: {TARGET_SAMPLE_RATE}Hz")
        logger.info(f"  - Kanały: 1 (mono)")
        logger.info(f"  - RMS: {final_rms:.4f}")
        logger.info(f"  - Zapisano: {output_path}")
        
        return True
    
    def find_voice_samples(self):
        """Szuka próbek głosu w różnych lokalizacjach"""
        possible_locations = [
            "voice_training/ref_samples/",
            "src/voice-model/",
            "."
        ]
        
        found_files = []
        
        for location in possible_locations:
            location_path = Path(location)
            if location_path.exists():
                for pattern in ["mowa*.wav", "voice*.wav", "sample*.wav"]:
                    files = list(location_path.glob(pattern))
                    found_files.extend(files)
        
        # Usuń duplikaty
        unique_files = list(set(found_files))
        return unique_files
    
    def process_all_samples(self):
        """Przetwarza wszystkie znalezione próbki głosu"""
        logger.info("🎵 Rozpoczynam preprocessing próbek głosu dla voice cloning")
        logger.info("=" * 60)
        
        # Znajdź próbki
        voice_files = self.find_voice_samples()
        
        if not voice_files:
            logger.error("❌ Nie znaleziono żadnych próbek głosu!")
            return False
        
        logger.info(f"✅ Znaleziono {len(voice_files)} próbek głosu:")
        for file in voice_files:
            logger.info(f"  - {file}")
        
        # Przetwórz każdą próbkę
        processed_count = 0
        for i, file_path in enumerate(voice_files):
            output_name = f"reference_{i+1}"
            if self.process_sample(file_path, output_name):
                processed_count += 1
                logger.info("✅ Przetwarzanie zakończone pomyślnie\n")
            else:
                logger.error("❌ Błąd podczas przetwarzania\n")
        
        logger.info("=" * 60)
        logger.info(f"🎉 Preprocessing zakończony!")
        logger.info(f"   Przetworzono: {processed_count}/{len(voice_files)} próbek")
        logger.info(f"   Lokalizacja: {self.output_dir}")
        
        # Lista przetworzonych plików
        processed_files = list(self.output_dir.glob("reference_*.wav"))
        logger.info(f"   Pliki gotowe do użycia:")
        for file in processed_files:
            logger.info(f"     - {file.name}")
        
        return processed_count > 0

def main():
    """Główna funkcja"""
    preprocessor = VoiceSamplePreprocessor()
    success = preprocessor.process_all_samples()
    
    if success:
        print("\n🎯 Następne kroki:")
        print("1. Sprawdź jakość przetworzonych plików w folderze 'voice_samples/'")
        print("2. Uruchom ekstrakcję speaker embedding")
        print("3. Zainstaluj polski TTS (XTTS lub Piper)")
        return 0
    else:
        print("\n❌ Preprocessing nie powiódł się!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
