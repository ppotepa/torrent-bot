# 🎭 ElevenLabs Integration - Premium Audiobook Quality

## Overview
ElevenLabs integration brings studio-quality text-to-speech to the audiobook plugin, offering natural-sounding voices that dramatically improve the listening experience compared to traditional TTS engines.

## 🌟 Features

### ✅ Premium Quality
- **Natural Voices**: Human-like speech synthesis
- **Multiple Languages**: English, Polish, and other supported languages
- **Advanced Models**: eleven_multilingual_v2 model for best quality
- **Smart Chunking**: Automatic text splitting for long content

### ✅ Voice Options
- **Default Voices**: Carefully selected for each language
- **Gender Selection**: Male and female voice options
- **Accent Varieties**: British English, Young voices, and more
- **Quality Consistency**: Same voice across all content

### ✅ Smart Fallbacks
- **Automatic**: Falls back to gTTS or pyttsx3 if ElevenLabs unavailable
- **Priority System**: User can choose preferred engine
- **Error Recovery**: Graceful handling of API issues

## 🎯 Available Voices

### English Voices
```
default: Rachel    # High-quality female voice
male: Adam        # Natural male voice  
female: Rachel    # Same as default
british: Charlotte # British accent
young: Bella      # Younger sounding voice
```

### Polish Voices
```
default: Freya    # Good for Polish (multilingual)
male: Adam       # Male voice with Polish support
female: Freya    # Same as default
```

## 🚀 Usage Examples

### Basic Usage
```
/ab Hello world:[inline,eng,elevenlabs]           # English with ElevenLabs
/ab Witaj świecie:[inline,pl,elevenlabs]          # Polish with ElevenLabs
```

### Voice Selection
```
/ab Your story:[inline,eng,elevenlabs,female]     # Female voice
/ab Your story:[inline,eng,elevenlabs,male]       # Male voice
/ab Your story:[inline,eng,elevenlabs,british]    # British accent
/ab Your story:[inline,eng,elevenlabs,young]      # Young voice
```

### File Processing
```
/ab document.pdf:[pdf,eng,elevenlabs,female]      # PDF with female voice
/ab book.epub:[epub,polish,elevenlabs]            # EPUB in Polish
/ab notes.txt:[text,eng,elevenlabs,british]       # Text with British accent
```

### Engine Priority
```
/ab text:[inline,eng,elevenlabs]   # Force ElevenLabs first
/ab text:[inline,eng,gtts]         # Force Google TTS first  
/ab text:[inline,eng,pyttsx3]      # Force local TTS first
/ab text:[inline,eng]              # Auto-select (ElevenLabs → gTTS → pyttsx3)
```

## ⚙️ Setup Instructions

### 1. Get API Key
1. Visit [ElevenLabs.io](https://elevenlabs.io)
2. Sign up for an account
3. Go to **Profile → API Keys**
4. Create a new API key
5. Copy the key

### 2. Configure Environment
Add your API key to environment variables:

**Windows (PowerShell):**
```powershell
$env:ELEVENLABS_API_KEY='your_api_key_here'
```

**Windows (Command Prompt):**
```cmd
set ELEVENLABS_API_KEY=your_api_key_here
```

**Linux/Mac:**
```bash
export ELEVENLABS_API_KEY='your_api_key_here'
```

**Or add to .env file:**
```
ELEVENLABS_API_KEY=your_api_key_here
```

### 3. Install Dependencies
```bash
pip install elevenlabs pydub
```

### 4. Test Setup
```bash
python test_elevenlabs.py
```

## 🔧 Technical Details

### Character Limits
- **Short Text**: Up to 5,000 characters processed directly
- **Long Text**: Automatically split into chunks and concatenated
- **Quality**: No quality loss with chunking

### Audio Processing
- **Output Format**: High-quality MP3
- **Bitrate**: Optimized for speech clarity
- **Concatenation**: Seamless joining of multiple chunks
- **File Size**: Larger than basic TTS but much higher quality

### Error Handling
- **API Limits**: Automatic fallback to alternative engines
- **Network Issues**: Graceful retry and fallback
- **Invalid Keys**: Clear error messages and setup guidance
- **Rate Limiting**: Built-in handling for API rate limits

## 💰 Cost Considerations

### ElevenLabs Pricing
- **Free Tier**: 10,000 characters/month
- **Paid Plans**: Higher limits and additional features
- **Character Counting**: Only successful conversions count
- **Fallback**: Free engines used when limits exceeded

### Optimization Tips
- Use ElevenLabs for important/final content
- Use gTTS for testing and drafts
- Monitor character usage in ElevenLabs dashboard
- Consider voice caching for repeated content

## 🎵 Quality Comparison

### ElevenLabs
- ✅ **Extremely natural** sounding
- ✅ **Emotional expression** in speech
- ✅ **Consistent pronunciation** across languages
- ✅ **Professional audiobook quality**
- ❌ **Requires API key and internet**
- ❌ **Character limits apply**

### Google TTS (gTTS)
- ✅ **Good quality** for free
- ✅ **No character limits**
- ✅ **Wide language support**
- ❌ **Robotic compared to ElevenLabs**
- ❌ **Requires internet**

### pyttsx3 (Local)
- ✅ **Works offline**
- ✅ **No limits or costs**
- ✅ **Instant processing**
- ❌ **Lowest quality** of the three
- ❌ **Limited voice options**

## 🚨 Troubleshooting

### Common Issues

#### "API key not found"
```
❌ ELEVENLABS_API_KEY not found in environment
💡 Set it with: set ELEVENLABS_API_KEY=your_api_key
```
**Solution**: Set the environment variable with your API key

#### "ElevenLabs not available"
```
❌ ElevenLabs package not available
💡 Install with: pip install elevenlabs
```
**Solution**: Install the required package

#### "Character limit exceeded"
- **For free accounts**: 10,000 chars/month limit
- **Solution**: System automatically falls back to gTTS
- **Alternative**: Upgrade ElevenLabs plan

#### "Voice not found"
- **Error**: Specified voice doesn't exist
- **Solution**: Check voice names in test_elevenlabs.py
- **Fallback**: System uses default voice

### Debug Commands
```bash
# Test ElevenLabs availability
python test_elevenlabs.py

# Test voice listing
python -c "from elevenlabs import voices; print(voices())"

# Test simple conversion
/ab Test:[inline,eng,elevenlabs]
```

## 🎉 Examples in Practice

### Short Stories
```
/ab Once upon a time in a land far away:[inline,eng,elevenlabs,young]
```

### Technical Documentation  
```
/ab manual.pdf:[pdf,eng,elevenlabs,male]
```

### Language Learning
```
/ab Dzisiaj jest piękny dzień:[inline,pl,elevenlabs,female]
```

### News Articles
```
/ab article.txt:[text,eng,elevenlabs,british]
```

## 🔮 Future Enhancements

### Planned Features
- **Voice Cloning**: Custom voice support
- **Emotion Control**: Happy, sad, excited speech
- **Speed Control**: Variable playback rates
- **SSML Support**: Advanced speech markup
- **Batch Processing**: Multiple files at once

### Integration Possibilities
- **Voice Selection UI**: Interactive voice picker
- **Quality Presets**: Preset configurations for different use cases
- **Usage Analytics**: Track character consumption
- **Voice Previews**: Sample different voices before conversion

The ElevenLabs integration transforms the audiobook experience from basic text-to-speech to professional-grade audio content! 🎭✨
