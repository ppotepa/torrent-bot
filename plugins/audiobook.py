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

# Import Piper Voice Cloning engine
try:
    from piper_voice_cloning_engine import get_piper_voice_cloning_tts, is_piper_voice_cloning_available
    logger.info("Piper Voice Cloning engine imported successfully")
except ImportError as e:
    logger.warning(f"Piper Voice Cloning not available: {e}")
    def get_piper_voice_cloning_tts():
        return None
    def is_piper_voice_cloning_available():
        return False

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
    
    # Priority 1: Piper Voice Cloning for Polish
    if is_piper_voice_cloning_available():
        engines['piper_voice_cloning'] = {
            'name': 'Piper Voice Cloning',
            'quality': 'Premium (Voice Cloned)',
            'available': True,
            'priority': 0,  # Highest priority
            'languages': ['polish']
        }
    
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
        # Auto mode: Prioritize Piper Voice Cloning for Polish
        if language == 'polish' and is_piper_voice_cloning_available():
            logger.info("Using Piper Voice Cloning for Polish (highest quality with voice cloning)")
            engine_instance = get_piper_voice_cloning_tts()
            success = engine_instance.convert_text_to_speech(text, output_path, language, voice_type)
            if success:
                return True, "Piper Voice Cloning conversion successful"
            else:
                logger.warning("Piper Voice Cloning failed, falling back to other engines")
        
        # Fallback to OpenVoice for other languages or if Piper failed
        if is_openvoice_available():
            logger.info("Trying OpenVoice for premium quality")
            engine_instance = get_openvoice_tts()
            success = engine_instance.convert_text_to_speech(text, output_path, language, voice_type)
            if success:
                return True, "OpenVoice conversion successful"
        
        # Fallback to other engines in priority order
        logger.warning("Premium engines not available, trying fallback engines")
        
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
    
    elif engine == 'piper_voice_cloning':
        if is_piper_voice_cloning_available():
            engine_instance = get_piper_voice_cloning_tts()
            success = engine_instance.convert_text_to_speech(text, output_path, language, voice_type)
            if success:
                return True, "Piper Voice Cloning conversion successful"
            else:
                return False, "Piper Voice Cloning conversion failed"
        else:
            return False, "Piper Voice Cloning requested but not available"
    
    elif engine == 'openvoice':
        if is_openvoice_available():
            engine_instance = get_openvoice_tts()
            success = engine_instance.convert_text_to_speech(text, output_path, language, voice_type)
            if success:
                return True, "OpenVoice conversion successful"
            else:
                # OpenVoice available but failed - try fallback engines
                logger.warning("OpenVoice conversion failed, falling back to other engines")
                
                # Try gTTS first
                gtts_success, gtts_error = _try_gtts_conversion(text, output_path, language)
                if gtts_success:
                    return True, f"OpenVoice failed, but gTTS succeeded: {gtts_error}"
                
                # Try pyttsx3 as last resort
                pyttsx3_success, pyttsx3_error = _try_pyttsx3_conversion(text, output_path, voice_type)
                if pyttsx3_success:
                    return True, f"OpenVoice failed, but pyttsx3 succeeded: {pyttsx3_error}"
                
                # All engines failed
                return False, f"OpenVoice conversion failed (implementation incomplete). Fallbacks also failed: gTTS: {gtts_error}, pyttsx3: {pyttsx3_error}"
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
    """Handle audiobook commands with comprehensive error tracking and voice profiles"""
    user_id = message.from_user.id
    chat_id = message.chat.id
    command_text = message.text.strip()
    
    logger.info(f"🎭 AUDIOBOOK REQUEST: User {user_id} | Chat {chat_id} | Command: {command_text}")
    
    try:
        # Import enhanced parser and profile synthesizer
        try:
            import sys
            sys.path.append(os.path.join(os.path.dirname(__file__), 'audiobook'))
            from enhanced_command_parser import parse_audiobook_command
            from profile_synthesizer import get_tts_synthesizer, list_available_profiles
            PROFILE_SYSTEM_AVAILABLE = True
        except ImportError as e:
            logger.warning(f"Profile system not available: {e}, using legacy parsing")
            PROFILE_SYSTEM_AVAILABLE = False
        
        if PROFILE_SYSTEM_AVAILABLE:
            # === NOWY SYSTEM PROFILI ===
            text, profile_id, flags = parse_audiobook_command(command_text)
            
            logger.info(f"🎭 PROFILE PARSING: text='{text[:50]}...', profile='{profile_id}', flags={flags}")
            
            # Handle help command
            if not text.strip():
                available_profiles = list_available_profiles()
                help_text = "🎭 **AUDIOBOOK TTS z profilami głosowymi**\n\n"
                help_text += "📋 **Składnia:**\n"
                help_text += "• `/ab Twój tekst:profil` - Synteza z profilem\n"
                help_text += "• `/ab Twój tekst` - Auto-wybór profilu\n\n"
                help_text += "🎤 **Dostępne profile:**\n"
                
                for profile_key, profile_name in available_profiles.items():
                    help_text += f"• `{profile_key}` - {profile_name}\n"
                
                help_text += "\n💡 **Przykłady:**\n"
                help_text += "• `/ab Cześć jak się masz:pawel` - Twój głos\n"
                help_text += "• `/ab Hello world:natural` - Naturalny angielski\n"
                help_text += "• `/ab Szybka informacja:fast` - Szybka synteza\n"
                help_text += "• `/ab Witaj świecie` - Auto (polski → pawel)\n"
                
                bot.send_message(chat_id, help_text, parse_mode='Markdown')
                return
            
            # Generate filename
            clean_text = text[:30].replace(' ', '_')
            filename = f"{clean_text}_{profile_id}.mp3"
            output_path = os.path.join(AUDIOBOOK_DIR, filename)
            
            logger.info(f"📁 OUTPUT PATH: {output_path}")
            
            # Show processing message
            tts_synthesizer = get_tts_synthesizer()
            profile_info = tts_synthesizer.get_profile_info(profile_id)
            
            status_msg = bot.send_message(
                chat_id, 
                f"🎭 **Synteza z profilem:** `{profile_id}`\n"
                f"📝 **Tekst:** {len(text)} znaków\n"
                f"⚙️ **Profil:** {profile_info.split('📝')[0]}..."
            )
            
            # Synthesize with profile
            logger.info(f"🎵 STARTING PROFILE-BASED TTS CONVERSION...")
            success, result_message = tts_synthesizer.synthesize_with_profile(text, profile_id, output_path)
            logger.info(f"🎵 PROFILE TTS RESULT: success={success}, message='{result_message}'")
            
        else:
            # === LEGACY SYSTEM ===
            flags, remaining_text = parse_universal_flags(command_text)
            final_flags = apply_default_flags(flags, 'ab')
            
            logger.info(f"📊 LEGACY PARSING: {flags} → Final: {final_flags}")
            logger.info(f"📝 REMAINING TEXT: '{remaining_text}' ({len(remaining_text)} chars)")
            
            # Handle help command
            if not remaining_text.strip():
                show_audiobook_help(bot, chat_id)
                return
            
            # Extract parameters
            language = get_language_code(final_flags.get('language', 'polish'))
            voice_type = final_flags.get('voice_type', 'male')
            engine = final_flags.get('engine', 'auto')
            
            logger.info(f"🎛️ LEGACY TTS PARAMS: lang={language}, voice={voice_type}, engine={engine}")
            
            # Generate filename
            clean_text = remaining_text[:30].replace(' ', '_')
            filename = f"{clean_text}_{language}_{voice_type}.mp3"
            output_path = os.path.join(AUDIOBOOK_DIR, filename)
            
            # Show processing message
            if engine == 'auto':
                if language == 'polish' and is_piper_voice_cloning_available():
                    msg = f"🎭 Converting with Piper Voice Cloning (YOUR VOICE!)\n📝 {len(remaining_text)} chars → {language} voice cloned"
                elif is_openvoice_available():
                    msg = f"🎭 Converting with OpenVoice Premium (best quality)\n📝 {len(remaining_text)} chars → {language} {voice_type} voice"
                else:
                    msg = f"⚠️ Premium engines not available, using fallback\n📝 {len(remaining_text)} chars → {language} {voice_type} voice"
            else:
                msg = f"🎵 Converting with {engine}\n📝 {len(remaining_text)} chars → {language} {voice_type} voice"
            
            status_msg = bot.send_message(chat_id, msg)
            
            # Convert using legacy system
            logger.info(f"🎵 STARTING LEGACY TTS CONVERSION...")
            success, result_message = convert_text_to_speech(remaining_text, language, output_path, voice_type, engine)
            logger.info(f"🎵 LEGACY TTS RESULT: success={success}, error='{result_message}'")
            text = remaining_text  # For file handling below
        
        # === COMMON FILE HANDLING ===
        # Check if we have a valid audio file
        file_exists = os.path.exists(output_path)
        file_size = os.path.getsize(output_path) if file_exists else 0
        is_valid_audio = file_exists and file_size > 100
        
        logger.info(f"📊 FILE VERIFICATION: exists={file_exists}, size={file_size} bytes, valid={is_valid_audio}")
        
        if is_valid_audio:
        if is_valid_audio:
            try:
                with open(output_path, 'rb') as audio_file:
                    logger.info(f"� SENDING VOICE MESSAGE...")
                    
                    # Enhanced caption with profile info
                    if PROFILE_SYSTEM_AVAILABLE:
                        caption = f"� {filename} • {file_size} bytes\n🎭 Profil: {profile_id}\n� {result_message}"
                    else:
                        caption = f"🎧 {filename} • {file_size} bytes"
                    
                    bot.send_voice(
                        chat_id,
                        audio_file,
                        caption=caption
                    )
                    logger.info(f"✅ VOICE MESSAGE SENT SUCCESSFULLY")
                
                bot.delete_message(chat_id, status_msg.message_id)
                logger.info(f"🗑️ STATUS MESSAGE DELETED")
                
                # Show success message
                if PROFILE_SYSTEM_AVAILABLE:
                    logger.info(f"🎉 PROFILE AUDIOBOOK SUCCESS: {filename} - {result_message}")
                else:
                    if success:
                        logger.info(f"🎉 AUDIOBOOK SUCCESS: {filename} ({result_message})")
                    else:
                        logger.info(f"🎉 AUDIOBOOK SUCCESS (fallback): {filename} - File created despite engine reporting failure")
                        
            except Exception as send_error:
                logger.error(f"Error sending voice message: {send_error}")
                bot.edit_message_text(
                    f"❌ Error sending audio file: {str(send_error)}",
                    chat_id,
                    status_msg.message_id
                )
        else:
            # Handle failure
            if PROFILE_SYSTEM_AVAILABLE:
                error_text = f"❌ **Błąd syntezy z profilem** `{profile_id}`\n📝 **Szczegóły:** {result_message}"
            else:
                error_text = f"❌ **TTS Conversion Failed**\n📝 **Details:** {result_message}"
                
            try:
                bot.edit_message_text(error_text, chat_id, status_msg.message_id, parse_mode='Markdown')
            except:
                bot.send_message(chat_id, error_text, parse_mode='Markdown')
            
            logger.error(f"💥 AUDIOBOOK FAILED: {result_message}")
            
    except Exception as e:
        logger.error(f"Critical audiobook error: {e}", exc_info=True)
        try:
            error_msg = (
                f"💥 **Critical Error in Audiobook Command**\n\n"
                f"📝 **Error:** {str(e)}\n"
                f"💡 **Try:** `/ab your text` or `/ab text:profile`\n"
                f"📋 **For help:** `/ab` without text"
            )
            bot.send_message(chat_id, error_msg, parse_mode='Markdown')
        except:
            # Final fallback
            bot.send_message(chat_id, f"💥 Critical audiobook error: {str(e)}")

def handle_audiobook_file(message, bot):
    """Handle file uploads for audiobook conversion"""
    bot.send_message(message.chat.id, "📁 File processing not yet implemented. Use inline text: `/ab Your text here`")

def show_audiobook_help(bot, chat_id):
    """Show legacy audiobook help"""
    help_text = """
🎧 **AUDIOBOOK TTS COMMANDS**

🎯 **Quick Commands:**
• `/ab Your text here` - Auto conversion (Voice Cloning for Polish!)
• `/ab [openvoice] Text` - Force OpenVoice engine  
• `/ab [english] Text` - Force English
• `/ab text:[piper_voice_cloning]` - Force voice cloning

🎛️ **Available Flags:**
• Language: `[polish]`, `[english]` 
• Voice: `[male]`, `[female]`
• Engine: `[openvoice]`, `[gtts]`, `[piper_voice_cloning]`

📊 **Examples:**
• `/ab Witaj świecie` → Polish Voice Cloning
• `/ab [english,female] Hello world` → English Female
• `/ab [openvoice,male] Test message` → OpenVoice Male

⚙️ **Available Engines:**"""
    
    engines = get_available_engines()
    for engine_id, engine_info in engines.items():
        available = "✅" if engine_info['available'] else "❌"
        help_text += f"\n{available} {engine_info['name']} - {engine_info['quality']}"
    
    bot.send_message(chat_id, help_text, parse_mode='Markdown')