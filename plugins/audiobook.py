import os
import tempfile
import shutil
from pathlib import Path
from typing import Optional, Dict, Any
from universal_flags import parse_universal_flags, validate_command_flags

# Base directory for audiobook storage
AUDIOBOOK_DIR = "audiobooks"

# Supported formats and languages
SUPPORTED_FORMATS = ['text', 'pdf', 'epub']
SUPPORTED_LANGUAGES = {
    'eng': 'en',
    'english': 'en', 
    'polish': 'pl',
    'pl': 'pl'
}

def process_audiobook(bot, message, file_format: str, language: str = 'eng'):
    """
    Main function to process audiobook conversion
    
    Args:
        bot: Telegram bot instance
        message: Telegram message object
        file_format: Format type (text, pdf, epub)
        language: Language code for TTS
    """
    try:
        # Ensure audiobook directory exists
        os.makedirs(AUDIOBOOK_DIR, exist_ok=True)
        
        # Validate format
        if file_format not in SUPPORTED_FORMATS:
            bot.reply_to(
                message, 
                f"❌ Unsupported format: {file_format}\n"
                f"📚 Supported formats: {', '.join(SUPPORTED_FORMATS)}"
            )
            return
            
        # Validate language
        lang_code = SUPPORTED_LANGUAGES.get(language.lower(), 'en')
        
        bot.reply_to(
            message,
            f"📚 Audiobook Conversion Started!\n"
            f"📄 Format: {file_format.upper()}\n"
            f"🗣️ Language: {language} ({lang_code})\n"
            f"⏳ Please send the file to convert..."
        )
        
        # Set up conversion state for this user
        setup_conversion_state(message.from_user.id, file_format, lang_code)
        
    except Exception as e:
        bot.reply_to(message, f"❌ Audiobook error: {e}")

def setup_conversion_state(user_id: int, file_format: str, language: str):
    """
    Set up conversion state for tracking user's audiobook request
    """
    # This will be used to track pending conversions
    # For now, we'll implement basic state tracking
    state_file = os.path.join(AUDIOBOOK_DIR, f"pending_{user_id}.json")
    
    import json
    state = {
        'user_id': user_id,
        'format': file_format,
        'language': language,
        'status': 'waiting_for_file',
        'timestamp': str(os.time.time() if hasattr(os, 'time') else 0)
    }
    
    try:
        with open(state_file, 'w') as f:
            json.dump(state, f)
    except Exception:
        pass  # State tracking is optional

def extract_text_from_file(file_path: str, file_format: str) -> str:
    """
    Extract text content from different file formats
    
    Args:
        file_path: Path to the file
        file_format: Format type (text, pdf, epub)
    
    Returns:
        Extracted text content
    """
    try:
        if file_format == 'text':
            return extract_text_from_txt(file_path)
        elif file_format == 'pdf':
            return extract_text_from_pdf(file_path)
        elif file_format == 'epub':
            return extract_text_from_epub(file_path)
        else:
            raise ValueError(f"Unsupported format: {file_format}")
            
    except Exception as e:
        raise Exception(f"Text extraction failed: {e}")

def extract_text_from_txt(file_path: str) -> str:
    """Extract text from plain text files"""
    try:
        # Try different encodings
        encodings = ['utf-8', 'utf-16', 'latin-1', 'cp1252']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue
                
        raise Exception("Could not decode text file with any supported encoding")
        
    except Exception as e:
        raise Exception(f"Text file reading failed: {e}")

def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from PDF files"""
    try:
        import PyPDF2
        
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            for page_num, page in enumerate(pdf_reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text.strip():
                        text += f"\n--- Page {page_num + 1} ---\n"
                        text += page_text + "\n"
                except Exception as e:
                    print(f"Warning: Could not extract text from page {page_num + 1}: {e}")
                    continue
                    
        if not text.strip():
            raise Exception("No text could be extracted from the PDF")
            
        return text.strip()
        
    except ImportError:
        raise Exception("PyPDF2 not installed. Please install with: pip install PyPDF2")
    except Exception as e:
        raise Exception(f"PDF text extraction failed: {e}")

def extract_text_from_epub(file_path: str) -> str:
    """Extract text from EPUB files"""
    try:
        import ebooklib
        from ebooklib import epub
        from bs4 import BeautifulSoup
        
        book = epub.read_epub(file_path)
        text = ""
        
        # Extract text from all chapters
        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                try:
                    # Parse HTML content
                    soup = BeautifulSoup(item.get_content(), 'html.parser')
                    
                    # Remove script and style elements
                    for script in soup(["script", "style"]):
                        script.decompose()
                    
                    # Get text content
                    chapter_text = soup.get_text()
                    
                    # Clean up whitespace
                    lines = (line.strip() for line in chapter_text.splitlines())
                    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                    chapter_text = '\n'.join(chunk for chunk in chunks if chunk)
                    
                    if chapter_text.strip():
                        text += f"\n--- Chapter ---\n"
                        text += chapter_text + "\n"
                        
                except Exception as e:
                    print(f"Warning: Could not extract text from a chapter: {e}")
                    continue
                    
        if not text.strip():
            raise Exception("No text could be extracted from the EPUB")
            
        return text.strip()
        
    except ImportError:
        raise Exception("ebooklib not installed. Please install with: pip install ebooklib beautifulsoup4")
    except Exception as e:
        raise Exception(f"EPUB text extraction failed: {e}")

def convert_text_to_speech(text: str, language: str, output_path: str) -> bool:
    """
    Convert text to speech and save as MP3
    
    Args:
        text: Text content to convert
        language: Language code for TTS
        output_path: Path where to save the MP3 file
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Check text length
        if len(text.strip()) == 0:
            raise Exception("No text content to convert")
            
        if len(text) > 100000:  # Limit to ~100KB of text
            print(f"Warning: Text is very long ({len(text)} characters). This may take a while...")
            
        # Try gTTS first (Google Text-to-Speech) - works better for longer texts
        try:
            from gtts import gTTS
            import io
            
            # Create TTS object
            tts = gTTS(text=text, lang=language, slow=False)
            
            # Save to a temporary file first
            temp_path = output_path + ".temp"
            tts.save(temp_path)
            
            # Move to final location
            import shutil
            shutil.move(temp_path, output_path)
            
            print(f"✅ TTS conversion completed using gTTS")
            return True
            
        except ImportError:
            print("gTTS not available, trying pyttsx3...")
        except Exception as e:
            print(f"gTTS failed: {e}, trying pyttsx3...")
            
        # Fallback to pyttsx3 (offline TTS)
        try:
            import pyttsx3
            
            engine = pyttsx3.init()
            
            # Set properties
            voices = engine.getProperty('voices')
            
            # Try to find a voice for the language
            selected_voice = None
            for voice in voices:
                if language == 'pl' and ('polish' in voice.name.lower() or 'pl' in voice.id.lower()):
                    selected_voice = voice.id
                    break
                elif language == 'en' and ('english' in voice.name.lower() or 'en' in voice.id.lower()):
                    selected_voice = voice.id
                    break
                    
            if selected_voice:
                engine.setProperty('voice', selected_voice)
                
            # Set speech rate (words per minute)
            engine.setProperty('rate', 150)  # Slightly slower for audiobooks
            
            # Convert text to speech and save
            engine.save_to_file(text, output_path)
            engine.runAndWait()
            
            print(f"✅ TTS conversion completed using pyttsx3")
            return True
            
        except ImportError:
            raise Exception("Neither gTTS nor pyttsx3 is available. Please install with: pip install gTTS pyttsx3")
        except Exception as e:
            raise Exception(f"pyttsx3 TTS failed: {e}")
            
    except Exception as e:
        print(f"TTS conversion failed: {e}")
        return False

def handle_audiobook_command(bot, message):
    """
    Handle /ab command with format and language parsing
    
    Expected formats:
    /ab text:eng
    /ab pdf:polish
    /ab epub:en
    /ab text (defaults to english)
    """
    try:
        # Parse the command
        command_text = message.text.strip()
        parts = command_text.split()
        
        if len(parts) < 2:
            show_audiobook_usage(bot, message)
            return
            
        # Parse format and language
        format_lang = parts[1]
        
        if ':' in format_lang:
            file_format, language = format_lang.split(':', 1)
        else:
            file_format = format_lang
            language = 'eng'  # Default language
            
        # Clean up the inputs
        file_format = file_format.lower().strip()
        language = language.lower().strip()
        
        # Start the conversion process
        process_audiobook(bot, message, file_format, language)
        
    except Exception as e:
        bot.reply_to(message, f"❌ Command parsing error: {e}")
        show_audiobook_usage(bot, message)

def show_audiobook_usage(bot, message):
    """Show usage instructions for the audiobook command"""
    usage_text = (
        "📚 **Audiobook Converter Usage**\n\n"
        "**Command Format:**\n"
        "`/ab <format>:<language>`\n\n"
        "**Supported Formats:**\n"
        "• `text` - Plain text files (.txt)\n"
        "• `pdf` - PDF documents (.pdf)\n"
        "• `epub` - EPUB ebooks (.epub)\n\n"
        "**Supported Languages:**\n"
        "• `eng` or `english` - English\n"
        "• `polish` or `pl` - Polish\n\n"
        "**Examples:**\n"
        "• `/ab text:eng` - Convert text file to English audiobook\n"
        "• `/ab pdf:polish` - Convert PDF to Polish audiobook\n"
        "• `/ab epub` - Convert EPUB to English audiobook (default)\n\n"
        "**Steps:**\n"
        "1. Send the command with your preferred format and language\n"
        "2. Upload the file you want to convert\n"
        "3. Wait for processing and MP3 generation\n"
        "4. Download your audiobook! 🎧"
    )
    
    bot.reply_to(message, usage_text, parse_mode="Markdown")

def get_audiobook_status(bot, message):
    """Get status of audiobook conversions"""
    try:
        # List all audiobooks in the directory
        if not os.path.exists(AUDIOBOOK_DIR):
            bot.reply_to(message, "📚 No audiobooks found. Create your first one with /ab!")
            return
            
        audiobooks = []
        for file in os.listdir(AUDIOBOOK_DIR):
            if file.endswith('.mp3'):
                file_path = os.path.join(AUDIOBOOK_DIR, file)
                size = os.path.getsize(file_path)
                size_mb = size / (1024 * 1024)
                audiobooks.append(f"🎧 {file} ({size_mb:.1f} MB)")
                
        if audiobooks:
            status_text = "📚 **Your Audiobooks:**\n\n" + "\n".join(audiobooks[:10])
            if len(audiobooks) > 10:
                status_text += f"\n\n... and {len(audiobooks) - 10} more"
        else:
            status_text = "📚 No audiobooks found. Create your first one with /ab!"
            
        bot.reply_to(message, status_text, parse_mode="Markdown")
        
    except Exception as e:
        bot.reply_to(message, f"❌ Status check error: {e}")

def handle_file_upload(bot, message, file_format: str, language: str):
    """
    Handle file upload and convert to audiobook
    
    Args:
        bot: Telegram bot instance
        message: Telegram message with file
        file_format: Expected format (text, pdf, epub)
        language: Language for TTS
    """
    try:
        # Get file info
        if message.document:
            file_info = bot.get_file(message.document.file_id)
            file_name = message.document.file_name or f"audiobook.{file_format}"
        else:
            bot.reply_to(message, "❌ No file found in the message.")
            return
            
        # Validate file extension
        allowed_extensions = {
            'text': ['.txt', '.text'],
            'pdf': ['.pdf'],
            'epub': ['.epub']
        }
        
        file_ext = os.path.splitext(file_name)[1].lower()
        if file_ext not in allowed_extensions.get(file_format, []):
            bot.reply_to(
                message,
                f"❌ Invalid file type for {file_format} format.\n"
                f"Expected: {', '.join(allowed_extensions.get(file_format, []))}\n"
                f"Got: {file_ext}"
            )
            return
            
        # Download the file
        bot.reply_to(message, f"📥 Downloading {file_name}...")
        
        downloaded_file = bot.download_file(file_info.file_path)
        
        # Create temporary file
        temp_dir = tempfile.mkdtemp()
        temp_file_path = os.path.join(temp_dir, file_name)
        
        with open(temp_file_path, 'wb') as temp_file:
            temp_file.write(downloaded_file)
            
        # Extract text
        bot.reply_to(message, f"📄 Extracting text from {file_format.upper()} file...")
        
        try:
            text_content = extract_text_from_file(temp_file_path, file_format)
            
            if len(text_content) < 10:
                bot.reply_to(message, "❌ File contains very little text. Please check your file.")
                return
                
            # Show text preview
            preview = text_content[:200] + "..." if len(text_content) > 200 else text_content
            bot.reply_to(
                message,
                f"📖 Text extracted successfully!\n"
                f"📊 Length: {len(text_content)} characters\n"
                f"📝 Preview: {preview}"
            )
            
        except Exception as e:
            bot.reply_to(message, f"❌ Text extraction failed: {e}")
            shutil.rmtree(temp_dir)
            return
            
        # Convert to speech
        bot.reply_to(message, f"🗣️ Converting to speech ({language})...")
        
        # Create output filename
        base_name = os.path.splitext(file_name)[0]
        safe_name = "".join(c for c in base_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        output_filename = f"{safe_name}_{language}.mp3"
        output_path = os.path.join(AUDIOBOOK_DIR, output_filename)
        
        try:
            success = convert_text_to_speech(text_content, language, output_path)
            
            if success and os.path.exists(output_path):
                # Send the audiobook file
                file_size = os.path.getsize(output_path)
                file_size_mb = file_size / (1024 * 1024)
                
                bot.reply_to(
                    message,
                    f"✅ Audiobook created successfully!\n"
                    f"📁 File: {output_filename}\n"
                    f"💾 Size: {file_size_mb:.1f} MB\n"
                    f"🗣️ Language: {language}\n"
                    f"📤 Sending file..."
                )
                
                # Send as audio file
                with open(output_path, 'rb') as audio_file:
                    bot.send_audio(
                        message.chat.id,
                        audio_file,
                        caption=f"🎧 Audiobook: {safe_name}",
                        title=safe_name,
                        performer="Text-to-Speech Bot"
                    )
                    
                bot.reply_to(message, f"🎉 Audiobook conversion completed!\n📚 Saved to: audiobooks/{output_filename}")
                
            else:
                bot.reply_to(message, "❌ TTS conversion failed. Please try again.")
                
        except Exception as e:
            bot.reply_to(message, f"❌ TTS conversion error: {e}")
            
        # Clean up temporary files
        shutil.rmtree(temp_dir)
        
    except Exception as e:
        bot.reply_to(message, f"❌ File processing error: {e}")

def check_pending_conversion(user_id: int) -> Optional[Dict[str, Any]]:
    """
    Check if user has a pending conversion request
    
    Returns:
        Dictionary with conversion state or None
    """
    state_file = os.path.join(AUDIOBOOK_DIR, f"pending_{user_id}.json")
    
    if not os.path.exists(state_file):
        return None
        
    try:
        import json
        with open(state_file, 'r') as f:
            state = json.load(f)
        return state
    except Exception:
        return None

def clear_pending_conversion(user_id: int):
    """Clear pending conversion state for user"""
    state_file = os.path.join(AUDIOBOOK_DIR, f"pending_{user_id}.json")
    
    if os.path.exists(state_file):
        try:
            os.remove(state_file)
        except Exception:
            pass

# File handler that should be registered in bot.py
def handle_document(bot, message):
    """
    Handle document uploads for audiobook conversion
    This should be called from bot.py when a document is received
    """
    try:
        user_id = message.from_user.id
        pending_state = check_pending_conversion(user_id)
        
        if pending_state:
            file_format = pending_state.get('format', 'text')
            language = pending_state.get('language', 'en')
            
            # Clear the pending state
            clear_pending_conversion(user_id)
            
            # Process the file
            handle_file_upload(bot, message, file_format, language)
        else:
            # No pending conversion - show usage
            bot.reply_to(
                message,
                "📚 To convert this file to an audiobook:\n\n"
                "1. First use: `/ab <format>:<language>`\n"
                "2. Then upload your file\n\n"
                "Example:\n"
                "• `/ab text:eng` then upload .txt file\n"
                "• `/ab pdf:polish` then upload .pdf file"
            )
            
    except Exception as e:
        bot.reply_to(message, f"❌ Document handling error: {e}")

# Main command handler function that will be called from bot.py
def handle_command(bot, message):
    """Main entry point for audiobook commands"""
    command_text = message.text.strip().lower()
    
    if command_text.startswith('/ab'):
        if command_text == '/ab' or command_text == '/ab help':
            show_audiobook_usage(bot, message)
        elif command_text == '/ab status':
            get_audiobook_status(bot, message)
        else:
            handle_audiobook_command(bot, message)
    else:
        show_audiobook_usage(bot, message)
