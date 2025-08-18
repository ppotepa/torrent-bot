# 🎵 Audiobook Plugin - Complete Documentation

## Overview
The Audiobook Plugin is a comprehensive text-to-speech system that converts various text formats into MP3 audiobooks. It supports three conversion methods: file uploads, inline text processing, and automatic format detection.

## 🚀 Features

### ✅ Multi-Format Support
- **Text Files (.txt)** - Direct text file processing
- **PDF Documents (.pdf)** - Extract text from PDF files
- **EPUB Books (.epub)** - Extract text from EPUB e-books
- **Inline Text** - Convert text directly from messages

### ✅ Language Support
- **English** (`eng`, `english`) - Default language
- **Polish** (`polish`, `pl`) - Full Polish TTS support

### ✅ TTS Engines
- **Primary**: Google Text-to-Speech (gTTS) - Cloud-based, high quality
- **Fallback**: pyttsx3 - Local TTS engine for offline use

## 📝 Command Syntax

The audiobook plugin follows the same flag-based syntax as the torrent plugin:

```
/ab [content]:[flags]
```

### Flag Types
- **Format Flags**: `text`, `pdf`, `epub`, `inline`
- **Language Flags**: `eng`, `english`, `polish`, `pl`

### Flag Rules
- Format flags are mutually exclusive (only one allowed)
- Language flags are mutually exclusive (only one allowed)
- Default format is auto-detected from file extension
- Default language is English (`eng`)

## 🎯 Usage Examples

### 1. File Upload with Flags
```
/ab document.txt:[text,eng]      # Upload text file in English
/ab book.pdf:[pdf,polish]        # Upload PDF in Polish
/ab novel.epub:[epub,pl]         # Upload EPUB in Polish (short code)
/ab file.txt:[text]              # Upload with default English
```

### 2. Inline Text Conversion
```
/ab Hello world this is a test:[inline,eng]    # English inline text
/ab To jest test:[inline,polish]               # Polish inline text
/ab Your story here:[inline]                   # Default English inline
```

### 3. Auto-Detection (File Upload without Format Flag)
```
/ab book.pdf:[eng]               # Auto-detect PDF format
/ab story.epub:[polish]          # Auto-detect EPUB format  
/ab notes.txt:[pl]               # Auto-detect text format
```

## ⚙️ Technical Implementation

### Core Functions

#### `handle_audiobook_command(message, bot)`
- Main command handler
- Parses flags and routes to appropriate conversion method
- Handles error cases and user feedback

#### `extract_text_from_file(file_path, file_type)`
- Multi-format text extraction
- Supports TXT, PDF, EPUB with error handling
- Returns extracted text or None on failure

#### `convert_text_to_speech(text, language, output_path)`
- Dual-engine TTS conversion
- Primary: gTTS (cloud-based)
- Fallback: pyttsx3 (local)
- Returns success status

#### `convert_inline_text(text, language, bot, chat_id)`
- Direct text-to-audiobook conversion
- Length validation (10-10,000 characters)
- Automatic filename generation
- Immediate MP3 delivery

### State Management
- JSON-based state tracking in `notification_state/`
- Tracks conversion progress and status
- Handles multi-step workflows

### Error Handling
- Comprehensive input validation
- Graceful fallback mechanisms
- User-friendly error messages
- Detailed logging for debugging

## 📊 Validation Rules

### Text Length (Inline Mode)
- **Minimum**: 10 characters
- **Maximum**: 10,000 characters
- Prevents very short/long conversions

### File Size Limits
- **PDF**: Reasonable size for text extraction
- **EPUB**: Standard e-book file limits
- **TXT**: Large text files supported

### Language Validation
- Supported languages only
- Default fallback to English
- Clear error messages for unsupported languages

## 🔧 Dependencies

### Required Python Packages
```
PyPDF2       # PDF text extraction
ebooklib     # EPUB processing
beautifulsoup4  # HTML parsing for EPUB
gTTS         # Google Text-to-Speech
pyttsx3      # Local TTS engine
```

### System Requirements
- Internet connection (for gTTS)
- Audio output capabilities
- File system write permissions

## 🚨 Error Scenarios

### Common Errors and Solutions

#### 1. Flag Conflicts
```
❌ /ab test:[text,pdf]        # Multiple format flags
❌ /ab test:[eng,polish]      # Multiple language flags
✅ /ab test:[text,eng]        # Correct usage
```

#### 2. Text Length Issues
```
❌ /ab Hi:[inline]            # Too short (< 10 chars)
❌ /ab [very long text]:[inline]  # Too long (> 10K chars)
✅ /ab Hello world:[inline]   # Perfect length
```

#### 3. File Processing Errors
- **Corrupted PDF**: Fallback to manual text input
- **Protected EPUB**: Error message with alternatives
- **Empty files**: Clear feedback to user

## 🎵 Output Format

### Generated Files
- **Format**: MP3 audio files
- **Quality**: High-quality TTS conversion
- **Naming**: Descriptive filenames based on content
- **Metadata**: Basic audio file information

### Example Filenames
```
Hello_world_test_eng.mp3      # Inline English text
Document_title_polish.mp3     # PDF in Polish
Book_chapter_pl.mp3           # EPUB in Polish (short)
```

## 🔄 Workflow Examples

### Complete File Upload Workflow
1. User uploads file with command: `/ab book.pdf:[pdf,eng]`
2. Bot validates file and flags
3. Bot extracts text from PDF
4. Bot converts text to speech using English TTS
5. Bot generates MP3 file
6. Bot sends audiobook to user

### Complete Inline Text Workflow  
1. User sends: `/ab Your story here:[inline,polish]`
2. Bot parses text and validates length
3. Bot converts to speech using Polish TTS
4. Bot generates MP3 with descriptive filename
5. Bot sends audiobook immediately

## 🧪 Testing

### Test Files Available
- `test_audiobook_flags.py` - Flag parsing validation
- `test_audiobook_inline.py` - Inline text functionality
- `test_complete_audiobook_system.py` - Full integration testing
- `test_complete_audiobook.py` - End-to-end workflow testing

### Test Coverage
- ✅ Flag parsing and validation
- ✅ Multi-format text extraction
- ✅ TTS engine functionality
- ✅ Error handling scenarios
- ✅ File upload workflows
- ✅ Inline text conversion

## 🎉 Production Status

### Ready Features
- ✅ Multi-format file processing
- ✅ Inline text conversion
- ✅ Flag-based command syntax
- ✅ Dual TTS engine support
- ✅ Comprehensive error handling
- ✅ State management system

### Integration Status
- ✅ Universal flag system integration
- ✅ Bot command routing
- ✅ Help system documentation
- ✅ Dependency management

## 🚀 Quick Start

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Test the System**:
   ```bash
   python test_complete_audiobook_system.py
   ```

3. **Use in Production**:
   ```
   /ab Hello world:[inline,eng]     # Quick test
   /ab filename.pdf:[pdf,polish]    # File conversion
   ```

The audiobook plugin is now production-ready with comprehensive functionality, error handling, and testing coverage! 🎵✨
