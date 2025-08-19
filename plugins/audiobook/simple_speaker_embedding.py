#!/usr/bin/env python3
"""
Simple Speaker Embedding - Prosty ekstraktor cech głosu bez OpenVoice
"""

import os
import torch
import torchaudio
import numpy as np
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
import glob

logger = logging.getLogger(__name__)

class SimpleSpeakerEmbedding:
    """Prosty ekstraktor cech głosu używający MFCC i statystyki"""
    
    def __init__(self):
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.sample_rate = 22050
        self.n_mfcc = 13
        self.n_fft = 2048
        self.hop_length = 512
        
        # MFCC transform
        self.mfcc_transform = torchaudio.transforms.MFCC(
            sample_rate=self.sample_rate,
            n_mfcc=self.n_mfcc,
            melkwargs={
                'n_fft': self.n_fft,
                'hop_length': self.hop_length,
                'n_mels': 40,
                'f_min': 20,
                'f_max': self.sample_rate // 2
            }
        )
        
        self.available = True
        
    def is_available(self) -> bool:
        """Zwraca czy ekstraktor jest dostępny"""
        return self.available
    
    def extract_features(self, audio_path: str) -> Optional[torch.Tensor]:
        """
        Ekstraktuje cechy MFCC z pliku audio
        
        Args:
            audio_path: Ścieżka do pliku audio
            
        Returns:
            Tensor z cechami MFCC lub None w przypadku błędu
        """
        try:
            # Załaduj audio
            audio, sr = torchaudio.load(audio_path)
            
            # Konwersja do mono jeśli stereo
            if audio.shape[0] > 1:
                audio = torch.mean(audio, dim=0, keepdim=True)
            
            # Resample jeśli potrzeba
            if sr != self.sample_rate:
                resampler = torchaudio.transforms.Resample(sr, self.sample_rate)
                audio = resampler(audio)
            
            # Ekstraktuj MFCC
            mfcc = self.mfcc_transform(audio)
            
            return mfcc
            
        except Exception as e:
            logger.error(f"Błąd ekstrakcji cech z {audio_path}: {e}")
            return None
    
    def compute_statistics(self, mfcc: torch.Tensor) -> torch.Tensor:
        """
        Oblicza statystyki z cech MFCC
        
        Args:
            mfcc: Cechy MFCC [channels, n_mfcc, time]
            
        Returns:
            Wektor statystyk
        """
        # Uśrednij kanały jeśli są
        if mfcc.dim() == 3:
            mfcc = torch.mean(mfcc, dim=0)  # [n_mfcc, time]
        
        # Oblicz statystyki dla każdego współczynnika MFCC
        mean = torch.mean(mfcc, dim=1)  # [n_mfcc]
        std = torch.std(mfcc, dim=1)    # [n_mfcc]
        min_vals = torch.min(mfcc, dim=1)[0]  # [n_mfcc]
        max_vals = torch.max(mfcc, dim=1)[0]  # [n_mfcc]
        
        # Skewness i kurtosis (przybliżone)
        centered = mfcc - mean.unsqueeze(1)
        skewness = torch.mean(centered**3, dim=1) / (std**3 + 1e-8)
        kurtosis = torch.mean(centered**4, dim=1) / (std**4 + 1e-8)
        
        # Połącz wszystkie statystyki
        features = torch.cat([mean, std, min_vals, max_vals, skewness, kurtosis])
        
        return features
    
    def extract_speaker_embedding(self, audio_paths: List[str], output_path: str) -> bool:
        """
        Ekstraktuje speaker embedding z próbek audio
        
        Args:
            audio_paths: Lista ścieżek do plików audio z referencyjnym głosem
            output_path: Ścieżka do zapisu embedding
            
        Returns:
            bool: True jeśli sukces
        """
        try:
            logger.info(f"Ekstrakcja speaker embedding z {len(audio_paths)} próbek...")
            
            all_features = []
            
            for audio_path in audio_paths:
                if not os.path.exists(audio_path):
                    logger.warning(f"Plik nie istnieje: {audio_path}")
                    continue
                    
                logger.info(f"Przetwarzanie próbki: {audio_path}")
                
                # Ekstraktuj cechy MFCC
                mfcc = self.extract_features(audio_path)
                if mfcc is None:
                    continue
                
                # Oblicz statystyki
                features = self.compute_statistics(mfcc)
                all_features.append(features)
            
            if not all_features:
                logger.error("Brak prawidłowych próbek audio")
                return False
            
            # Uśrednij cechy ze wszystkich próbek
            speaker_embedding = torch.mean(torch.stack(all_features), dim=0)
            
            # Normalizacja
            speaker_embedding = torch.nn.functional.normalize(speaker_embedding, dim=0)
            
            # Zapisz embedding
            torch.save(speaker_embedding, output_path)
            
            logger.info(f"Speaker embedding zapisany: {output_path}")
            logger.info(f"Kształt embedding: {speaker_embedding.shape}")
            
            return True
            
        except Exception as e:
            logger.error(f"Błąd podczas ekstrakcji speaker embedding: {e}")
            return False
    
    def load_speaker_embedding(self, embedding_path: str) -> Optional[torch.Tensor]:
        """Ładuje zapisany speaker embedding"""
        try:
            if not os.path.exists(embedding_path):
                logger.error(f"Embedding nie istnieje: {embedding_path}")
                return None
                
            embedding = torch.load(embedding_path, map_location=self.device)
            logger.info(f"Załadowano speaker embedding: {embedding.shape}")
            return embedding
            
        except Exception as e:
            logger.error(f"Błąd ładowania embedding: {e}")
            return None
    
    def get_info(self) -> Dict[str, Any]:
        """Zwraca informacje o ekstraktorze"""
        return {
            "name": "Simple Speaker Embedding (MFCC-based)",
            "available": self.available,
            "device": self.device,
            "sample_rate": self.sample_rate,
            "n_mfcc": self.n_mfcc,
            "feature_dimension": self.n_mfcc * 6  # mean, std, min, max, skew, kurt
        }

# Factory function
def get_speaker_extractor() -> SimpleSpeakerEmbedding:
    """Tworzy instancję simple speaker embedding extractor"""
    return SimpleSpeakerEmbedding()

if __name__ == "__main__":
    # Ustaw debug logging
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    # Test Speaker Embedding Extractor
    print("🎙️ Test Simple Speaker Embedding Extractor")
    print("=" * 55)
    
    extractor = get_speaker_extractor()
    
    # Informacje
    print("Speaker Extractor Info:")
    for key, value in extractor.get_info().items():
        print(f"  {key}: {value}")
    
    if not extractor.is_available():
        print("❌ Speaker Embedding Extractor nie jest dostępny!")
        exit(1)
    
    # Test ekstrakcji
    print("\n🧪 Uruchamianie testu ekstrakcji...")
    
    # Znajdź próbki głosu
    voice_samples_dir = "voice_samples"
    if os.path.exists(voice_samples_dir):
        audio_files = glob.glob(os.path.join(voice_samples_dir, "reference_*.wav"))
        
        if audio_files:
            print(f"Znaleziono {len(audio_files)} próbek głosu:")
            for f in audio_files:
                print(f"  - {f}")
            
            # Ekstraktuj speaker embedding
            output_embedding = "simple_speaker_embedding.pt"
            success = extractor.extract_speaker_embedding(audio_files, output_embedding)
            
            if success:
                print("✅ Test zakończony sukcesem!")
                
                # Test ładowania
                embedding = extractor.load_speaker_embedding(output_embedding)
                if embedding is not None:
                    print(f"✅ Speaker embedding załadowany: {embedding.shape}")
                    print(f"✅ Wymiary: {embedding.numel()} elementów")
                else:
                    print("❌ Błąd ładowania embedding")
            else:
                print("❌ Test nie powiódł się!")
        else:
            print("❌ Brak próbek głosu w katalogu voice_samples/")
    else:
        print("❌ Katalog voice_samples/ nie istnieje!")
