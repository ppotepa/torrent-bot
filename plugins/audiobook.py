#!/usr/bin/env python3
"""
Audiobook Plugin - Text-to-speech conversion with OpenVoice priority
"""

import os
import logging
from typing import Dict, Any, Optional

# Enhanced logging
try:
    from enhanced_logging import get_logger
    logger = get_logger("audiobook_plugin")
except ImportError:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("audiobook_plugin")

# Import universal flags
try:
    from universal_flags import parse_universal_flags, apply_default_flags
except ImportError:
    logger.warning("Universal flags not available, using fallback parsing")
    
    def parse_universal_flags(text):
        """Fallback flag parsing for audiobook commands"""
        import re
        flags = {}
        remaining_text = text.strip()
        
        # Remove command prefix
        if remaining_text.startswith('/'):
            parts = remaining_text.split(' ', 1)
            remaining_text = parts[1] if len(parts) > 1 else ""
        
        # Parse bracket flags: [openvoice,male,polish]
        bracket_pattern = r'\[([^\]]+)\]'
        matches = re.findall(bracket_pattern, remaining_text)
        
        if matches:
            for match in matches:
                flag_values = [v.strip().lower() for v in match.split(',')]
                
                for value in flag_values:
                    # Language detection
                    if value in ['eng', 'english', 'en']:
                        flags['language'] = 'english'
                    elif value in ['pl', 'polish', 'polski']:
                        flags['language'] = 'polish'
                    # Voice type detection
                    elif value in ['male', 'female', 'british', 'young']:
                        flags['voice_type'] = value
                    # Engine detection
                    elif value in ['openvoice', 'auto', 'gtts', 'enhanced_sapi', 'pyttsx3']:
                        flags['engine'] = value
                    # File type detection
                    elif value in ['txt', 'pdf', 'epub', 'inline']:
                        flags['file_type'] = value
            
            # Remove brackets from text
            remaining_text = re.sub(bracket_pattern, '', remaining_text).strip()
        
        return flags, remaining_text
    
    def apply_default_flags(flags, command):
        """Apply default flags for audiobook commands"""
        defaults = {
            'file_type': 'inline',
            'language': 'english',
            'voice_type': 'female',
            'engine': 'auto'  # Auto prioritizes OpenVoice
        }
        defaults.update(flags)
        return defaults

# Import OpenVoice engine
from openvoice_engine import get_openvoice_tts, is_openvoice_available

# Check other TTS engines
try:
    import win32com.client
    SAPI_AVAILABLE = True
except ImportError:
    SAPI_AVAILABLE = False

try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False

# Audiobook directory
AUDIOBOOK_DIR = "audiobooks"
if not os.path.exists(AUDIOBOOK_DIR):
    os.makedirs(AUDIOBOOK_DIR)

def get_available_engines() -> Dict[str, Dict[str, Any]]:
    """Get available TTS engines with OpenVoice priority"""
    engines = {}
    
    if is_openvoice_available():
        engines['openvoice'] = {
            'name': 'OpenVoice Premium',
            'quality': 'Premium',
            'available': True,
            'priority': 1
        }
    
    if SAPI_AVAILABLE:
        engines['enhanced_sapi'] = {
            'name': 'Enhanced Windows SAPI',
            'quality': 'High',
            'available': True,
            'priority': 2
        }
    
    if GTTS_AVAILABLE:
        engines['gtts'] = {
            'name': 'Google TTS',
            'quality': 'Good',
            'available': True,
            'priority': 3
        }
    
    if PYTTSX3_AVAILABLE:
        engines['pyttsx3'] = {
            'name': 'Local TTS',
            'quality': 'Basic',
            'available': True,
            'priority': 4
        }
    
    return engines

def detect_language(text: str) -> str:
    """Simple language detection"""
    polish_chars = set('ąćęłńóśźżĄĆĘŁŃÓŚŹŻ')
    if any(char in polish_chars for char in text):
        return 'polish'
    return 'english'

def get_language_code(lang_input: str) -> str:
    """Normalize language input"""
    lang_lower = lang_input.lower().strip()
    if lang_lower in ['pl', 'pol', 'polish', 'polski']:
        return 'polish'
    return 'english'

def convert_text_to_speech(text: str, language: str, output_path: str, voice_type: str = "female", engine: str = "auto") -> tuple[bool, str]:
    """Convert text to speech with proper engine fallback. Returns (success, error_message)"""
    logger.info(f"TTS conversion: {len(text)} chars, {language}, {voice_type}, engine={engine}")
    
    if engine == 'auto':
        # Auto mode prioritizes OpenVoice
        if is_openvoice_available():
            logger.info("Prioritizing OpenVoice for premium quality")
            engine_instance = get_openvoice_tts()
            success = engine_instance.convert_text_to_speech(text, output_path, language, voice_type)
            if success:
                return True, "OpenVoice conversion successful"
        
        # Fallback to other engines in priority order
        logger.warning("OpenVoice not available, trying fallback engines")
        
        # Try gTTS first (most reliable for basic TTS)
        gtts_success, gtts_error = _try_gtts_conversion(text, output_path, language)
        if gtts_success:
            return True, "gTTS conversion successful"
        
        # Try pyttsx3 as last resort
        pyttsx3_success, pyttsx3_error = _try_pyttsx3_conversion(text, output_path, voice_type)
        if pyttsx3_success:
            return True, "pyttsx3 conversion successful"
        
        # If all engines fail, return detailed error
        error_msg = f"All TTS engines failed. gTTS: {gtts_error}, pyttsx3: {pyttsx3_error}"
        logger.error(error_msg)
        return False, error_msg
    
    elif engine == 'openvoice':
        if is_openvoice_available():
            engine_instance = get_openvoice_tts()
            success = engine_instance.convert_text_to_speech(text, output_path, language, voice_type)
            if success:
                return True, "OpenVoice conversion successful"
            else:
                return False, "OpenVoice conversion failed (implementation incomplete)"
        else:
            # OpenVoice requested but not available - inform user and fallback
            logger.warning("OpenVoice requested but not available, falling back to auto mode")
            return convert_text_to_speech(text, language, output_path, voice_type, engine="auto")
    
    elif engine == 'gtts':
        return _try_gtts_conversion(text, output_path, language)
        
    elif engine == 'pyttsx3':
        return _try_pyttsx3_conversion(text, output_path, voice_type)
    
    # Unknown engine
    error_msg = f"Unknown TTS engine: {engine}"
    logger.error(error_msg)
    return False, error_msg

def _try_gtts_conversion(text: str, output_path: str, language: str) -> tuple[bool, str]:
    """Try converting using gTTS. Returns (success, error_message)"""
    if not GTTS_AVAILABLE:
        return False, "gTTS not available (import failed)"
    
    try:
        logger.info("Attempting gTTS conversion")
        # Map language codes for gTTS
        gtts_lang = 'pl' if language == 'polish' else 'en'
        
        logger.info(f"gTTS: Creating TTS object with lang='{gtts_lang}', text='{text[:50]}...'")
        tts = gTTS(text=text, lang=gtts_lang, slow=False)
        
        logger.info(f"gTTS: Saving to '{output_path}'")
        tts.save(output_path)
        
        # Verify file was created and has content
        if os.path.exists(output_path):
            size = os.path.getsize(output_path)
            logger.info(f"gTTS: File created with size {size} bytes")
            
            if size > 100:
                logger.info(f"gTTS conversion successful: {size} bytes")
                return True, f"gTTS success ({size} bytes)"
            else:
                error_msg = f"gTTS created too small file ({size} bytes)"
                logger.warning(error_msg)
                return False, error_msg
        else:
            error_msg = "gTTS did not create output file"
            logger.warning(error_msg)
            return False, error_msg
            
    except Exception as e:
        error_type = type(e).__name__
        error_details = str(e)
        
        # Specific error handling for common issues
        if "URLError" in error_type or "HTTPError" in error_type:
            error_msg = f"gTTS network error: {error_details} (check internet connection)"
        elif "timeout" in error_details.lower():
            error_msg = f"gTTS timeout error: {error_details} (slow internet)"
        elif "permission" in error_details.lower():
            error_msg = f"gTTS permission error: {error_details} (check file write access)"
        else:
            error_msg = f"gTTS conversion failed ({error_type}): {error_details}"
        
        logger.error(error_msg)
        return False, error_msg

def _try_pyttsx3_conversion(text: str, output_path: str, voice_type: str) -> tuple[bool, str]:
    """Try converting using pyttsx3. Returns (success, error_message)"""
    if not PYTTSX3_AVAILABLE:
        return False, "pyttsx3 not available (import failed)"
    
    try:
        logger.info("Attempting pyttsx3 conversion")
        engine = pyttsx3.init()
        
        # Configure voice
        voices = engine.getProperty('voices')
        if voices:
            # Try to select appropriate voice
            for voice in voices:
                if voice_type.lower() in voice.name.lower():
                    engine.setProperty('voice', voice.id)
                    break
        
        # Set reasonable speaking rate
        engine.setProperty('rate', 150)
        
        # Save to file
        engine.save_to_file(text, output_path)
        engine.runAndWait()
        
        # Verify file was created and has content
        if os.path.exists(output_path) and os.path.getsize(output_path) > 100:
            size = os.path.getsize(output_path)
            logger.info(f"pyttsx3 conversion successful: {size} bytes")
            return True, f"pyttsx3 success ({size} bytes)"
        else:
            error_msg = "pyttsx3 created empty or too small file"
            logger.warning(error_msg)
            return False, error_msg
            
    except Exception as e:
        error_msg = f"pyttsx3 conversion failed: {str(e)}"
        logger.error(error_msg)
        return False, error_msg

def handle_audiobook_command(message, bot):
    """Handle audiobook commands with comprehensive error tracking"""
    user_id = message.from_user.id
    chat_id = message.chat.id
    command_text = message.text.strip()
    
    logger.info(f"🎭 AUDIOBOOK REQUEST: User {user_id} | Chat {chat_id} | Command: {command_text}")
    
    try:
        # Parse flags
        flags, remaining_text = parse_universal_flags(command_text)
        final_flags = apply_default_flags(flags, 'ab')
        
        logger.info(f"📊 PARSED FLAGS: {flags} → Final: {final_flags}")
        logger.info(f"📝 REMAINING TEXT: '{remaining_text}' ({len(remaining_text)} chars)")
        
        # Extract parameters
        language = get_language_code(final_flags.get('language', 'english'))
        voice_type = final_flags.get('voice_type', 'female')
        engine = final_flags.get('engine', 'auto')  # Auto prioritizes OpenVoice
        
        logger.info(f"🎛️ TTS PARAMS: lang={language}, voice={voice_type}, engine={engine}")
        
        # Handle inline text conversion
        if remaining_text:
            # Auto-detect language if not specified
            if 'language' not in flags:
                detected_lang = detect_language(remaining_text)
                if detected_lang != language:
                    language = detected_lang
                    logger.info(f"🌍 Auto-detected language: {language}")
            
            # Show processing message
            engines = get_available_engines()
            if engine == 'auto' and is_openvoice_available():
                msg = f"🎭 Converting with OpenVoice Premium (best quality)\n📝 {len(remaining_text)} chars → {language} {voice_type} voice"
            elif engine == 'openvoice':
                if is_openvoice_available():
                    msg = f"🎭 Converting with OpenVoice Premium\n📝 {len(remaining_text)} chars → {language} {voice_type} voice"
                else:
                    msg = f"⚠️ OpenVoice not available, using fallback\n📝 {len(remaining_text)} chars → {language} {voice_type} voice"
            else:
                msg = f"🎵 Converting with {engine}\n📝 {len(remaining_text)} chars → {language} {voice_type} voice"
            
            logger.info(f"📱 SENDING STATUS MESSAGE: {msg}")
            status_msg = bot.send_message(chat_id, msg)
            logger.info(f"✅ STATUS MESSAGE SENT: ID={status_msg.message_id}")
            
            # Generate filename
            clean_text = remaining_text[:30].replace(' ', '_')
            filename = f"{clean_text}_{language}_{voice_type}.mp3"
            output_path = os.path.join(AUDIOBOOK_DIR, filename)
            
            logger.info(f"📁 OUTPUT PATH: {output_path}")
            
            # Convert
            logger.info(f"🎵 STARTING TTS CONVERSION...")
            success, error_message = convert_text_to_speech(remaining_text, language, output_path, voice_type, engine)
            logger.info(f"🎵 TTS CONVERSION RESULT: success={success}, error='{error_message}'")
            
            if success and os.path.exists(output_path):
                try:
                    file_size = os.path.getsize(output_path)
                    logger.info(f"📊 FILE VERIFICATION: exists=True, size={file_size} bytes")
                    
                    with open(output_path, 'rb') as audio_file:
                        logger.info(f"🎧 SENDING VOICE MESSAGE...")
                        bot.send_voice(
                            chat_id,
                            audio_file,
                            caption=f"🎧 {filename} • {file_size} bytes"
                        )
                        logger.info(f"✅ VOICE MESSAGE SENT SUCCESSFULLY")
                    
                    bot.delete_message(chat_id, status_msg.message_id)
                    logger.info(f"🗑️ STATUS MESSAGE DELETED")
                    logger.info(f"🎉 AUDIOBOOK SUCCESS: {filename} ({error_message})")
                    
                except Exception as e:
                    detailed_error = f"❌ Error sending audiobook: {str(e)}\n🔧 File: {filename}\n📊 Size: {os.path.getsize(output_path) if os.path.exists(output_path) else 0} bytes"
                    logger.error(f"❌ SEND ERROR: {e}")
                    bot.edit_message_text(detailed_error, chat_id, status_msg.message_id)
            else:
                # Detailed error reporting
                file_exists = os.path.exists(output_path)
                file_size = os.path.getsize(output_path) if file_exists else 0
                
                logger.error(f"❌ CONVERSION FAILED: file_exists={file_exists}, file_size={file_size}, error='{error_message}'")
                
                detailed_error = f"""❌ **Conversion Failed**
🔧 **Engine**: {engine}
📝 **Text**: {len(remaining_text)} chars  
🌍 **Language**: {language}
🎤 **Voice**: {voice_type}
📁 **File exists**: {file_exists}
📊 **File size**: {file_size} bytes
⚠️ **Error**: {error_message}

🛠️ **Debug Info**:
• OpenVoice available: {is_openvoice_available()}
• gTTS available: {GTTS_AVAILABLE}
• pyttsx3 available: {PYTTSX3_AVAILABLE}

🔍 **File path**: `{output_path}`"""
                
                bot.edit_message_text(detailed_error, chat_id, status_msg.message_id, parse_mode='Markdown')
            return
            
    except Exception as e:
        logger.error(f"❌ AUDIOBOOK HANDLER EXCEPTION: {e}")
        import traceback
        logger.error(f"📋 TRACEBACK: {traceback.format_exc()}")
        try:
            bot.send_message(chat_id, f"❌ **Critical Error in Audiobook Handler**\n\n🔧 **Error**: {str(e)}\n\n🔍 Check logs for details", parse_mode='Markdown')
        except:
            pass  # Fallback if even error message fails
        return
    
    # Show help
    show_audiobook_help(bot, chat_id)
    
    # Show help
    show_audiobook_help(bot, chat_id)

def handle_audiobook_file(message, bot):
    """Handle file uploads for audiobook conversion"""
    bot.send_message(message.chat.id, "📁 File processing not yet implemented. Use inline text: `/ab Your text here`")

def show_audiobook_help(bot, chat_id: int):
    """Show audiobook help"""
    engines = get_available_engines()
    engine_list = []
    
    for engine_id, engine_info in engines.items():
        priority = engine_info.get('priority', 99)
        name = engine_info.get('name', engine_id)
        quality = engine_info.get('quality', 'Unknown')
        available = "✅" if engine_info.get('available', False) else "❌"
        engine_list.append(f"  {priority}. {available} {name} ({quality})")
    
    engine_text = "\n".join(engine_list) if engine_list else "  No engines available"
    
    help_text = f"""🎭 **Audiobook Converter with OpenVoice Premium**

**Available Engines:**
{engine_text}

**Usage:**
• `/ab Your text here` - Auto OpenVoice conversion
• `/ab Hello world:[eng,female]` - English female voice  
• `/ab Witaj świecie:[pl,male]` - Polish male voice
• `/ab text:[english,british,openvoice]` - Force OpenVoice British

**Features:**
🎭 OpenVoice Premium (default for auto mode)
🌍 Auto language detection
🎤 Multiple voice types
⚡ Instant conversion

**Examples:**
• `/ab Hello world` → OpenVoice English female (auto)
• `/ab Witaj` → Auto-detects Polish, OpenVoice male
• `/ab Test:[british]` → OpenVoice British accent"""
    
    bot.send_message(chat_id, help_text, parse_mode='Markdown')