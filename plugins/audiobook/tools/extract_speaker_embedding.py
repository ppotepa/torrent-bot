#!/usr/bin/env python3
"""
Speaker Embedding Extraction - Ekstrakcja cech głosu dla OpenVoice
"""

import os
import torch
import torchaudio
import numpy as np
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
import glob

# OpenVoice imports
try:
    from openvoice import se_extractor
    from openvoice.api import ToneColorConverter
    OPENVOICE_AVAILABLE = True
except ImportError:
    OPENVOICE_AVAILABLE = False

logger = logging.getLogger(__name__)

class SpeakerEmbeddingExtractor:
    """Ekstraktor cech głosu używający OpenVoice"""
    
    def __init__(self, openvoice_dir="models/openvoice"):
        self.openvoice_dir = Path(openvoice_dir)
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        
        # Ścieżki do modeli OpenVoice
        self.ckpt_converter = self.openvoice_dir / "converter"
        
        # Speaker embedding extractor
        self.se_extractor = None
        self.tone_converter = None
        
        # Sprawdź dostępność
        self.available = self._check_availability()
        
    def _check_availability(self) -> bool:
        """Sprawdza czy OpenVoice jest dostępny"""
        if not OPENVOICE_AVAILABLE:
            logger.warning("OpenVoice nie jest zainstalowany")
            return False
            
        if not self.ckpt_converter.exists():
            logger.warning(f"Converter model nie znaleziony: {self.ckpt_converter}")
            return False
            
        return True
    
    def is_available(self) -> bool:
        """Zwraca czy ekstraktor jest dostępny"""
        return self.available
    
    def initialize_models(self) -> bool:
        """Inicjalizuje modele OpenVoice"""
        if not self.available:
            return False
            
        try:
            # Inicjalizacja tone converter
            logger.info("Inicjalizacja OpenVoice ToneColorConverter...")
            self.tone_converter = ToneColorConverter(f'{self.ckpt_converter}/config.json', device=self.device)
            self.tone_converter.load_ckpt(f'{self.ckpt_converter}/checkpoint.pth')
            
            # Inicjalizacja speaker embedding extractor
            logger.info("Inicjalizacja Speaker Embedding Extractor...")
            
            return True
            
        except Exception as e:
            logger.error(f"Błąd inicjalizacji modeli OpenVoice: {e}")
            return False
    
    def extract_speaker_embedding(self, audio_paths: List[str], output_path: str) -> bool:
        """
        Ekstraktuje speaker embedding z próbek audio
        
        Args:
            audio_paths: Lista ścieżek do plików audio z referencyjnym głosem
            output_path: Ścieżka do zapisu embedding
            
        Returns:
            bool: True jeśli sukces
        """
        if not self.available:
            logger.error("Speaker embedding extractor nie jest dostępny")
            return False
            
        if not self.tone_converter:
            if not self.initialize_models():
                return False
        
        try:
            logger.info(f"Ekstrakcja speaker embedding z {len(audio_paths)} próbek...")
            
            # Załaduj wszystkie próbki audio
            audio_tensors = []
            sample_rates = []
            
            for audio_path in audio_paths:
                if not os.path.exists(audio_path):
                    logger.warning(f"Plik nie istnieje: {audio_path}")
                    continue
                    
                logger.info(f"Ładowanie próbki: {audio_path}")
                audio, sr = torchaudio.load(audio_path)
                
                # Konwersja do mono jeśli stereo
                if audio.shape[0] > 1:
                    audio = torch.mean(audio, dim=0, keepdim=True)
                
                audio_tensors.append(audio)
                sample_rates.append(sr)
            
            if not audio_tensors:
                logger.error("Brak prawidłowych próbek audio")
                return False
            
            # Sprawdź czy wszystkie próbki mają ten sam sample rate
            if len(set(sample_rates)) > 1:
                logger.warning(f"Różne sample rates: {sample_rates}, używam pierwszego")
            
            target_sr = sample_rates[0]
            
            # Połącz wszystkie próbki
            if len(audio_tensors) > 1:
                # Dopasuj długości (padding/trimming)
                max_length = max(audio.shape[1] for audio in audio_tensors)
                padded_tensors = []
                
                for audio in audio_tensors:
                    if audio.shape[1] < max_length:
                        # Padding z zerami
                        pad_size = max_length - audio.shape[1]
                        audio = torch.nn.functional.pad(audio, (0, pad_size))
                    elif audio.shape[1] > max_length:
                        # Trim do max_length
                        audio = audio[:, :max_length]
                    padded_tensors.append(audio)
                
                # Uśrednij wszystkie próbki
                combined_audio = torch.mean(torch.stack(padded_tensors), dim=0)
            else:
                combined_audio = audio_tensors[0]
            
            # Zapisz połączone audio do tymczasowego pliku
            temp_audio_path = output_path.replace('.pt', '_combined.wav')
            torchaudio.save(temp_audio_path, combined_audio, target_sr)
            
            logger.info(f"Połączone audio zapisane: {temp_audio_path}")
            logger.info(f"Kształt: {combined_audio.shape}, Sample rate: {target_sr}")
            
            # Ekstraktuj speaker embedding używając OpenVoice
            logger.info("Ekstrakcja speaker embedding...")
            reference_speaker_embedding = se_extractor.get_se(
                temp_audio_path, 
                self.tone_converter, 
                vad=True  # Voice Activity Detection
            )
            
            # Zapisz embedding
            torch.save(reference_speaker_embedding, output_path)
            
            # Cleanup
            if os.path.exists(temp_audio_path):
                os.unlink(temp_audio_path)
            
            logger.info(f"Speaker embedding zapisany: {output_path}")
            logger.info(f"Kształt embedding: {reference_speaker_embedding.shape}")
            
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
            "name": "OpenVoice Speaker Embedding Extractor",
            "available": self.available,
            "device": self.device,
            "openvoice_dir": str(self.openvoice_dir),
            "converter_path": str(self.ckpt_converter)
        }

# Factory function
def get_speaker_extractor(openvoice_dir="models/openvoice") -> SpeakerEmbeddingExtractor:
    """Tworzy instancję speaker embedding extractor"""
    return SpeakerEmbeddingExtractor(openvoice_dir)

if __name__ == "__main__":
    # Ustaw debug logging
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    # Test Speaker Embedding Extractor
    print("🎙️ Test Speaker Embedding Extractor")
    print("=" * 50)
    
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
            output_embedding = "speaker_embedding.pt"
            success = extractor.extract_speaker_embedding(audio_files, output_embedding)
            
            if success:
                print("✅ Test zakończony sukcesem!")
                
                # Test ładowania
                embedding = extractor.load_speaker_embedding(output_embedding)
                if embedding is not None:
                    print(f"✅ Speaker embedding załadowany: {embedding.shape}")
                else:
                    print("❌ Błąd ładowania embedding")
            else:
                print("❌ Test nie powiódł się!")
        else:
            print("❌ Brak próbek głosu w katalogu voice_samples/")
    else:
        print("❌ Katalog voice_samples/ nie istnieje!")
