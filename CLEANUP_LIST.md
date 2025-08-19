# 🗂️ LISTA PLIKÓW DO USUNIĘCIA - AUDIOBOOK PLUGIN

## 📋 **ANALIZA ŚCIEŻEK WYKONANIA**

### **🎯 GŁÓWNE ŚCIEŻKI WYKONANIA BOTA:**

1. **Nowy system (src/plugins/audiobook_tts.py)** - NIEUŻYWANY
2. **Główny system (src/bot.py → plugins/audiobook.py)** - UŻYWANY  
3. **Profile system (plugins/audiobook/enhanced_command_parser.py + profile_synthesizer.py)** - UŻYWANY

### **📁 PLIKI UŻYWANE PRZEZ BOTA:**

#### **Core files (ZACHOWAĆ):**
```
plugins/audiobook.py                     # Główny handler
plugins/audiobook/__init__.py           # Package init
plugins/audiobook/enhanced_command_parser.py  # Parser komend
plugins/audiobook/profile_synthesizer.py      # Profile system
plugins/audiobook/voice_profiles.py           # Voice profiles manager
plugins/audiobook/voice_profiles/profiles.json # Profile config
```

#### **Voice cloning system (ZACHOWAĆ):**
```
plugins/audiobook/polish_voice_converter.py   # Voice cloning pipeline
plugins/audiobook/enhanced_piper_tts.py       # Enhanced Piper TTS
plugins/audiobook/simple_speaker_embedding.py # Speaker embedding
plugins/audiobook/simple_speaker_embedding.pt # Trained embedding
plugins/audiobook/voice_samples/*.wav         # Reference samples
plugins/audiobook/voice_profiles/reference_samples/*.wav # Reference samples
```

#### **Models (ZACHOWAĆ):**
```
plugins/audiobook/models/tts/piper/           # Piper TTS models
plugins/audiobook/models/tts/pl_PL-gosia-medium.onnx  # Polish model
plugins/audiobook/models/tts/pl_PL-gosia-medium.onnx.json
```

#### **Engines (CZĘŚCIOWO ZACHOWAĆ):**
```
plugins/audiobook/engines/__init__.py         # ZACHOWAĆ
plugins/audiobook/engines/base_engine.py     # ZACHOWAĆ
plugins/audiobook/engines/voice_cloning_engine.py # ZACHOWAĆ (używany)
plugins/audiobook/engines/openvoice_engine.py     # ZACHOWAĆ (importowany)
plugins/audiobook/engines/gtts_engine.py          # ZACHOWAĆ (fallback)
plugins/audiobook/engines/pyttsx3_engine.py       # ZACHOWAĆ (fallback)
```

#### **Utils (ZACHOWAĆ):**
```
plugins/audiobook/utils/__init__.py           # Package init
plugins/audiobook/utils/language_detection.py # Language detection
```

---

## 🗑️ **PLIKI DO USUNIĘCIA**

### **1. 📊 Test i debug pliki (42 plików):**

#### **Test pliki główne:**
```
plugins/audiobook/demo_profiles.py
plugins/audiobook/final_system_test.py  
plugins/audiobook/final_test.py
plugins/audiobook/quality_test.py
plugins/audiobook/simple_manager_test.py
plugins/audiobook/simple_test.py
plugins/audiobook/test_bot_integration.py
plugins/audiobook/test_profile_system.py
plugins/audiobook/test_system.py
plugins/audiobook/ultimate_test.py
```

#### **Wygenerowane pliki testowe:**
```
plugins/audiobook/debug_voice_test.wav
plugins/audiobook/demo_expressive.wav
plugins/audiobook/demo_fast.wav
plugins/audiobook/demo_female.wav
plugins/audiobook/demo_natural.wav
plugins/audiobook/demo_pawel.wav
plugins/audiobook/ultimate_test_fast.wav
plugins/audiobook/ultimate_test_natural.wav
plugins/audiobook/ultimate_test_pawel.wav
```

#### **Katalog debug:**
```
plugins/audiobook/debug/                  # CAŁY KATALOG
├── debug_audiobook_plugin.py
├── debug_audiobook_storage.py
├── debug_language_detection.py
└── debug_voices.py
```

#### **Katalog tests:**
```
plugins/audiobook/tests/                  # CAŁY KATALOG
├── outputs/
│   ├── test_main.wav
│   ├── test_piper_voice_cloning_engine.wav
│   └── test_voice_cloning.wav
├── test_direct_polish_tts.py
├── test_openvoice.py
└── test_voice_cloning_integration.py
```

### **2. 📚 Dokumentacja (14 plików):**
```
plugins/audiobook/docs/                   # CAŁY KATALOG
├── AUDIOBOOK_AUTO_DETECTION_SUMMARY.md
├── AUDIOBOOK_FIXES_COMPLETE.md
├── AUDIOBOOK_PLUGIN_DOCUMENTATION.md
├── AUDIOBOOK_SUMMARY.md
├── ELEVENLABS_INTEGRATION.md
├── ELEVENLABS_SUMMARY.md
├── OPENVOICE_INTEGRATION_COMPLETE.md
├── OPENVOICE_INTEGRATION_GUIDE.md
├── OPENVOICE_STATUS.md
├── POLISH_COMMAND_FIXED.md
├── POLISH_TTS_PIPELINE_COMPLETE.md
├── POLISH_TTS_SETUP.md
└── VOICE_MESSAGE_INTEGRATION.md

plugins/audiobook/README.md
plugins/audiobook/PROFILE_SYSTEM_GUIDE.md
plugins/audiobook/ROBOTYCZNY_DZWIEK_ANALIZA.md
plugins/audiobook/SYSTEM_READY.md
```

### **3. 🏗️ Legacy i nieużywane komponenty (8 plików):**

#### **Legacy engines:**
```
plugins/audiobook/legacy/                 # CAŁY KATALOG
├── enhanced_local_tts.py
├── enhanced_tts_engine.py
├── openvoice_engine.py
├── piper_voice_cloning_engine.py
├── polish_tts_engine.py
├── simple_polish_tts.py
└── sync_polish_tts.py
```

#### **Nieużywane komponenty:**
```
plugins/audiobook/enhanced_handler.py    # Nieużywany handler
plugins/audiobook/tts_manager.py         # Nieużywany manager
plugins/audiobook/piper_tts.py           # Zastąpiony przez enhanced_piper_tts.py
```

### **4. 🎓 Training i tools (nieużywane) (całe katalogi):**

#### **Training system:**
```
plugins/audiobook/training/              # CAŁY KATALOG
└── voice_training/
    ├── __pycache__/
    ├── automation.py
    ├── cache/
    ├── finetune.txt
    ├── models/
    ├── OpenVoice/                       # Duplikat external/OpenVoice
    ├── openvoice.txt
    ├── output/
    ├── polish_pipeline/
    ├── prepare_sample.py
    ├── README.md
    ├── ref_samples/
    ├── samples/
    ├── setup_embedding.py
    └── train_custom_voice.py
```

#### **Tools:**
```
plugins/audiobook/tools/                 # CAŁY KATALOG
├── extract_speaker_embedding.py
└── prepare_voice_samples.py
```

### **5. 🔬 External (częściowo nieużywane):**

#### **OpenVoice (nieużywany w obecnej implementacji):**
```
plugins/audiobook/external/              # CAŁY KATALOG (36 plików)
└── OpenVoice/
    ├── demo_part1.ipynb
    ├── demo_part2.ipynb
    ├── demo_part3.ipynb
    ├── docs/
    ├── LICENSE
    ├── openvoice/                       # Pełna implementacja OpenVoice
    ├── README.md
    ├── requirements.txt
    ├── resources/
    └── setup.py
```

### **6. 📦 Examples i requirements:**
```
plugins/audiobook/examples/              # CAŁY KATALOG
├── demo_audiobook.txt
├── demo_polish_tts.py
└── demo_tts.py

plugins/audiobook/requirements/          # CAŁY KATALOG
├── requirements_openvoice_fixed.txt
└── requirements_openvoice.txt
```

### **7. 🔧 Utils nieużywane:**
```
plugins/audiobook/utils/enhanced_flag_parser.py  # Nieużywany
```

---

## 📊 **PODSUMOWANIE USUWANIA**

### **📈 Statystyki:**
- **Pliki do usunięcia**: ~120+ plików
- **Katalogi do usunięcia**: 8 katalogów
- **Szacowany rozmiar**: ~200MB+ (głównie modele OpenVoice)
- **Pozostanie**: ~25 plików podstawowych

### **🎯 Korzyści po usunięciu:**
1. **Mniejszy rozmiar**: Redukcja o ~80% rozmiaru
2. **Przejrzystość**: Tylko używane pliki
3. **Łatwiejsze utrzymanie**: Brak martwego kodu
4. **Szybsze wyszukiwanie**: Mniej plików do przeszukania

### **⚠️ UWAGI PRZED USUNIĘCIEM:**

1. **Backup**: Stwórz kopię zapasową przed usunięciem
2. **OpenVoice**: Może być przydatny w przyszłości dla prawdziwego voice cloning
3. **Training**: Może być potrzebny do retrenowania modelu
4. **Tests**: Przydatne do debugowania problemów

---

## 🚀 **KOLEJNOŚĆ USUWANIA (ZALECANA):**

### **Faza 1 - Bezpieczne (można usunąć od razu):**
```bash
# Test pliki i wygenerowane audio
rm plugins/audiobook/*.wav
rm -rf plugins/audiobook/debug/
rm -rf plugins/audiobook/tests/
rm plugins/audiobook/*test*.py
rm plugins/audiobook/demo_profiles.py
```

### **Faza 2 - Dokumentacja:**
```bash
rm -rf plugins/audiobook/docs/
rm plugins/audiobook/*.md
```

### **Faza 3 - Legacy i nieużywane:**
```bash
rm -rf plugins/audiobook/legacy/
rm plugins/audiobook/enhanced_handler.py
rm plugins/audiobook/tts_manager.py
rm plugins/audiobook/piper_tts.py
rm plugins/audiobook/utils/enhanced_flag_parser.py
```

### **Faza 4 - Training i tools (opcjonalnie):**
```bash
rm -rf plugins/audiobook/training/
rm -rf plugins/audiobook/tools/
rm -rf plugins/audiobook/examples/
rm -rf plugins/audiobook/requirements/
```

### **Faza 5 - OpenVoice (zachować do decyzji):**
```bash
# OPCJONALNIE - może być przydatny w przyszłości
# rm -rf plugins/audiobook/external/
```

---

**Data analizy**: 19 sierpnia 2025  
**Status**: Lista gotowa do implementacji
