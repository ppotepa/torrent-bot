# 🎧 Enhanced Audiobook Plugin

Kompletny system TTS (Text-to-Speech) z funkcjami klonowania głosu dla bota Telegram.

## 📁 Struktura

```
plugins/audiobook/
├── engines/                    # Silniki TTS
│   ├── __init__.py            # Eksporty silników
│   ├── base_engine.py         # Bazowa klasa silnika
│   ├── voice_cloning_engine.py # Silnik klonowania głosu (Priorytet 0)
│   ├── openvoice_engine.py    # OpenVoice Premium (Priorytet 1)
│   ├── gtts_engine.py         # Google TTS (Priorytet 2)
│   └── pyttsx3_engine.py      # Pyttsx3 Local (Priorytet 3)
├── utils/                     # Narzędzia pomocnicze
│   ├── __init__.py
│   └── language_detection.py  # Wykrywanie języka
├── models/                    # Modele TTS
│   └── tts/piper/            # Model Piper TTS
├── voice_samples/             # Próbki głosu użytkownika
├── tts_manager.py             # Główny menedżer silników
├── enhanced_handler.py        # Ulepszony handler
├── polish_voice_converter.py  # Konwerter z klonowaniem głosu
├── piper_tts.py              # Wrapper dla Piper TTS
├── simple_speaker_embedding.py # Ekstrakcja cech głosu
└── simple_speaker_embedding.pt # Model embeddings głosu
```

## 🎭 Funkcje

### 1. **Voice Cloning (Priorytet 0)**
- Używa Twojego głosu do generowania naturalnych komunikatów
- Technologia: Piper TTS + Speaker Embedding + Voice Processing
- Języki: Polski, Angielski
- Jakość: **Najwyższa** - naturalny głos użytkownika

### 2. **OpenVoice Premium (Priorytet 1)**
- Wysokiej jakości synteza głosu
- Różne głosy i style
- Języki: Polski, Angielski
- Jakość: **Premium**

### 3. **Google TTS (Priorytet 2)**
- Niezawodna synteza przez API Google
- Dobra jakość dźwięku
- Języki: Polski, Angielski  
- Jakość: **Dobra**

### 4. **Pyttsx3 Local (Priorytet 3)**
- Lokalna synteza bez internetu
- Podstawowa jakość
- Fallback dla innych silników
- Jakość: **Podstawowa**

## 🔄 System Fallback

System automatycznie wybiera najlepszy dostępny silnik:

1. **Voice Cloning** → Jeśli dostępny, używa klonowania głosu
2. **OpenVoice** → Jeśli Voice Cloning niedostępny
3. **Google TTS** → Jeśli OpenVoice niedostępny  
4. **Pyttsx3** → Ostateczny fallback

## 🌍 Wykrywanie Języka

System automatycznie wykrywa język tekstu:
- **Polski**: Wykrywa polskie znaki (ą, ć, ę, ł, ń, ó, ś, ź, ż) i słowa
- **Angielski**: Wykrywa angielskie słowa i struktury
- **Fallback**: Domyślnie angielski dla nieznanych tekstów

## 📊 Status Testów

### ✅ Funkcjonujące Komponenty
- [x] **Voice Cloning**: 117KB-260KB plików audio
- [x] **Language Detection**: Podstawowe wykrywanie
- [x] **Modular Architecture**: Sistem priorytetów silników
- [x] **File Management**: Automatyczne tworzenie folderów
- [x] **Error Handling**: Graceful fallback między silnikami

### ⚠️ Znane Problemy
- **Memory Issue**: Voice processing może mieć problemy z pamięcią dla długich tekstów
- **Language Detection**: Wymaga poprawy dla tekstów polskich
- **Relative Imports**: Niektóre moduły wymagają absolute imports

## 🚀 Użycie

### Podstawowe użycie:
```python
from plugins.audiobook import TTSEngineManager

# Inicjalizacja menedżera
tts = TTSEngineManager()

# Konwersja tekstu
success, message = tts.convert_text(
    text="Witaj świecie!",
    output_path="output.wav",
    language="polish"  # lub auto-detect
)
```

### Status silników:
```python
status = tts.get_engine_status()
print(f"Dostępne silniki: {status['available_engines']}")
```

## 📈 Plany Rozwoju

1. **Optymalizacja Voice Cloning**: Redukcja zużycia pamięci
2. **Lepsza Detekcja Języka**: Poprawa dokładności dla polskiego
3. **Więcej Głosów**: Dodanie różnych stylów głosu
4. **Cache System**: Buforowanie często używanych fraz
5. **Web Interface**: Panel kontrolny do zarządzania głosami

## 🛠️ Integracja z Botem

Plugin jest w pełni zintegrowany z głównym botem Telegram:
- Automatyczna konwersja wiadomości tekstowych
- Obsługa plików tekstowych (.txt)
- Inteligentny wybór języka
- Wysokiej jakości pliki audio

---

**Status**: ✅ **Działający** - Voice cloning przetestowany i funkcjonalny  
**Ostatnia aktualizacja**: 2024 - Reorganizacja modułowa
