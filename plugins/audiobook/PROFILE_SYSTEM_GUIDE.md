# 🎭 System Profili Głosowych - Instrukcja Użytkownika

## 📋 Wprowadzenie

Nowy system profili głosowych umożliwia łatwą syntezę mowy z różnymi charakterystykami głosu, w tym z klonowaniem Twojego własnego głosu opartym na próbkach `mowa.wav` i `mowa-2.wav`.

## 🎤 Dostępne Profile

### 🎭 pawel (Twój głos - PREMIUM)
- **Typ**: Voice Cloning z Enhanced Piper
- **Jakość**: Premium (największe pliki ~300-400KB)
- **Opis**: Sklonowany głos oparty na Twoich próbkach głosowych
- **Cechy**: Najbardziej naturalny, największa podobność do Twojego głosu

### 🎵 natural (Naturalny)
- **Typ**: Enhanced Piper TTS
- **Jakość**: High (~150-180KB)
- **Opis**: Wysoka jakość bez klonowania głosu
- **Cechy**: Naturalny polski męski głos, zredukowana robotyczność

### 🎪 expressive (Ekspresyjny)
- **Typ**: Enhanced Piper TTS
- **Jakość**: High (~160-190KB)
- **Opis**: Ekspresyjny styl z większą emocjonalnością
- **Cechy**: Więcej ekspresji i modulacji głosu

### ⚡ fast (Szybki)
- **Typ**: Enhanced Piper TTS
- **Jakość**: Good (~130-160KB)
- **Opis**: Szybka synteza z dobrą jakością
- **Cechy**: Przyspieszony, kompaktowy

### 👩 female (Kobieca)
- **Typ**: Enhanced Piper TTS
- **Jakość**: High (~150-180KB)
- **Opis**: Naturalny kobiecy głos polski
- **Cechy**: Żeńska wersja naturalnego głosu

## 📝 Składnia Komend

### 1. **Składnia z dwukropkiem (ZALECANA)**
```
/ab Twój tekst:profil
```

**Przykłady:**
```
/ab Cześć jak się masz:pawel          # Twój sklonowany głos
/ab Hello world:natural               # Naturalny głos
/ab Dzień dobry wszystkim:expressive  # Ekspresyjny styl
/ab Szybka informacja:fast            # Szybka synteza
/ab Witam serdecznie:female           # Kobieci głos
```

### 2. **Auto-wykrywanie języka**
```
/ab Twój tekst
```

**Logika:**
- Tekst polski → automatycznie profil `pawel` (Twój głos)
- Tekst angielski → automatycznie profil `natural`

**Przykłady:**
```
/ab Dzień dobry                       # → profil 'pawel'
/ab Hello there                       # → profil 'natural'
```

### 3. **Składnia z flagami**
```
/ab [profil] Twój tekst
/ab [flagi] Twój tekst
```

**Przykłady:**
```
/ab [pawel] Jak się masz?            # Bezpośredni wybór profilu
/ab [voice_cloning] Legacy command    # Mapuje na profil 'pawel'
/ab [polish,male] Witaj świecie       # Tradycyjne flagi
```

## 🎯 Zalecenia Użycia

### 💎 **Dla najwyższej jakości**
```
/ab Twój polski tekst:pawel
```
- Używa Twojego sklonowanego głosu
- Najlepsze rezultaty dla polskiego tekstu
- Rozmiar pliku: ~300-400KB

### ⚡ **Dla szybkości**
```
/ab Szybka wiadomość:fast
```
- Mniejsze pliki (~130-160KB)  
- Szybsza synteza
- Nadal dobra jakość

### 🎪 **Dla ekspresji**
```
/ab Ważna wiadomość z emocjami:expressive
```
- Więcej modulacji głosu
- Ekspresyjniejszy styl
- Idealny dla ważnych komunikatów

### 👩 **Dla różnorodności**
```
/ab Komunikat od asystentki:female
```
- Żeński głos polski
- Naturalna intonacja
- Alternatywa dla męskiego głosu

## 📊 Porównanie Wydajności

| Profil | Typ | Jakość | Rozmiar | Czas | Naturalność |
|--------|-----|--------|---------|------|-------------|
| **pawel** | Voice Cloning | Premium | ~350KB | Długi | ⭐⭐⭐⭐⭐ |
| **natural** | Enhanced Piper | High | ~170KB | Średni | ⭐⭐⭐⭐ |
| **expressive** | Enhanced Piper | High | ~180KB | Średni | ⭐⭐⭐⭐ |
| **fast** | Enhanced Piper | Good | ~150KB | Szybki | ⭐⭐⭐ |
| **female** | Enhanced Piper | High | ~170KB | Średni | ⭐⭐⭐⭐ |

## 🔧 Rozwiązywanie Problemów

### ❌ "Profile system not available"
- Sprawdź czy pliki są w folderze `plugins/audiobook/`
- Uruchom ponownie bota

### ❌ "Voice Converter niedostępny"  
- Sprawdź czy istnieje `simple_speaker_embedding.pt`
- Sprawdź czy próbki `mowa.wav` i `mowa-2.wav` są dostępne

### ❌ "Enhanced Piper TTS nie jest dostępny"
- Sprawdź czy folder `models/tts/` istnieje
- Sprawdź czy `piper.exe` i `pl_PL-gosia-medium.onnx` są dostępne

## 🎉 Przykłady Kompleksowe

```bash
# 🎭 Sklonowany głos (najlepsza jakość)
/ab Witam wszystkich na dzisiejszym spotkaniu:pawel

# 🎵 Naturalny głos (szybko + dobra jakość)  
/ab Informuję o zakończeniu prac:natural

# 🎪 Ekspresyjny styl (ważne komunikaty)
/ab UWAGA! Ważna informacja dla wszystkich:expressive

# ⚡ Szybka synteza (krótkie wiadomości)
/ab OK, zrobione:fast

# 👩 Kobieci głos (różnorodność)
/ab Miłego dnia życzę:female

# 🌍 Auto-wykrywanie
/ab Dzień dobry              # → pawel (polski)
/ab Hello there              # → natural (angielski)
```

## 💡 Wskazówki

1. **Dla polskiego tekstu zawsze używaj profilu `pawel`** - to Twój sklonowany głos!
2. **Profile `natural` i `expressive`** są idealne jako alternatywy
3. **Profil `fast`** dla szybkich testów i krótkich wiadomości
4. **Profil `female`** dla różnorodności głosów
5. **Składnia z dwukropkiem** (`tekst:profil`) jest najłatwiejsza w użyciu

## 🔄 Historia Zmian

- **v1.0**: Podstawowy system profili
- **v1.1**: Dodano auto-wykrywanie języka
- **v1.2**: Ulepszone parametry Enhanced Piper (redukcja robotyczności)
- **v1.3**: Integracja z Voice Cloning opartym na Twoich próbkach głosowych
