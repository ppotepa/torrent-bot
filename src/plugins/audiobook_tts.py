"""
Audiobook TTS Plugin - Text-to-speech conversion with multiple engines
"""

import os
import sys
import logging
from typing import Dict, Any, Optional, Tuple

from core import PluginBase, plugin_info, command, message_handler, startup_task, CommandScope, PermissionLevel


@plugin_info(
    name="Audiobook TTS",
    version="2.0.0",
    author="TorrentBot", 
    description="Convert text to speech using multiple TTS engines with voice cloning support",
    dependencies=["gtts", "pyttsx3"],
    enabled=True
)
class AudiobookTTSPlugin(PluginBase):
    """Plugin for text-to-speech conversion with multiple engine support"""
    
    def __init__(self, bot, logger=None):
        super().__init__(bot, logger)
        self.audiobook_dir = "audiobooks"
        os.makedirs(self.audiobook_dir, exist_ok=True)
        
        # Engine availability
        self.engines_available = {}
        self.profile_system_available = False
        
    def get_plugin_description(self) -> str:
        return "Converts text to high-quality speech using OpenVoice, voice cloning, and fallback engines"
    
    @startup_task(priority=1)
    def initialize_tts_engines(self):
        """Initialize and check availability of TTS engines"""
        self.logger.info("Initializing TTS engines...")
        
        # Check OpenVoice availability (with graceful fallback)
        try:
            # Add the old audiobook plugin path for OpenVoice
            old_audiobook_path = os.path.join(os.path.dirname(__file__), '..', '..', 'plugins', 'audiobook')
            old_engines_path = os.path.join(old_audiobook_path, 'engines')
            
            # Add both paths to sys.path if they exist
            if os.path.exists(old_audiobook_path) and old_audiobook_path not in sys.path:
                sys.path.insert(0, old_audiobook_path)
            if os.path.exists(old_engines_path) and old_engines_path not in sys.path:
                sys.path.insert(0, old_engines_path)
            
            # Try to import OpenVoice components
            from openvoice_engine import get_openvoice_tts, is_openvoice_available
            self.engines_available['openvoice'] = is_openvoice_available()
            if self.engines_available['openvoice']:
                self.logger.info("✅ OpenVoice engine available")
            else:
                self.logger.warning("❌ OpenVoice engine not available")
        except ImportError as e:
            self.logger.warning(f"OpenVoice import failed: {e} - will use gTTS fallback")
            self.engines_available['openvoice'] = False
        except Exception as e:
            self.logger.warning(f"OpenVoice initialization failed: {e} - will use gTTS fallback")
            self.engines_available['openvoice'] = False
        
        # Check Voice Cloning availability
        try:
            from piper_voice_cloning_engine import get_piper_voice_cloning_tts, is_piper_voice_cloning_available
            self.engines_available['voice_cloning'] = is_piper_voice_cloning_available()
            if self.engines_available['voice_cloning']:
                self.logger.info("✅ Voice Cloning engine available")
            else:
                self.logger.warning("❌ Voice Cloning engine not available")
        except ImportError as e:
            self.logger.warning(f"Voice Cloning import failed: {e}")
            self.engines_available['voice_cloning'] = False
        
        # Check gTTS
        try:
            from gtts import gTTS
            self.engines_available['gtts'] = True
            self.logger.info("✅ Google TTS available")
        except ImportError:
            self.engines_available['gtts'] = False
            self.logger.warning("❌ Google TTS not available")
        
        # Check pyttsx3
        try:
            import pyttsx3
            self.engines_available['pyttsx3'] = True
            self.logger.info("✅ pyttsx3 available")
        except ImportError:
            self.engines_available['pyttsx3'] = False
            self.logger.warning("❌ pyttsx3 not available")
        
        # Check profile system
        try:
            sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'plugins', 'audiobook'))
            from enhanced_command_parser import parse_audiobook_command
            from profile_synthesizer import get_tts_synthesizer, list_available_profiles
            self.profile_system_available = True
            self.logger.info("✅ Profile system available")
        except ImportError as e:
            self.logger.warning(f"Profile system not available: {e}")
            self.profile_system_available = False
        
        available_count = sum(1 for available in self.engines_available.values() if available)
        self.logger.info(f"TTS initialization complete: {available_count} engines available")
    
    @command(
        name="audiobook",
        aliases=["ab", "tts", "speak"],
        description="Convert text to speech with multiple engine support",
        usage="/audiobook <text> [options]",
        examples=[
            "/audiobook Hello world",
            "/audiobook Witaj świecie:pawel",
            "/audiobook Hello world:natural",
            "/audiobook Test message:openvoice,male,english"
        ],
        flags=["openvoice", "voice_cloning", "gtts", "pyttsx3", "polish", "english", "male", "female"],
        category="Media"
    )
    def audiobook_command(self, message):
        """Handle audiobook TTS command"""
        try:
            command_text = message.text.strip()
            user_id = message.from_user.id
            chat_id = message.chat.id
            
            self.logger.info(f"🎭 AUDIOBOOK REQUEST: User {user_id} | Chat {chat_id} | Command: {command_text}")
            
            # Parse command
            if self.profile_system_available:
                text, profile_id, flags = self._parse_with_profiles(command_text)
                
                if not text.strip():
                    self._show_profile_help(message)
                    return
                
                # Process with profile system
                self._process_with_profiles(message, text, profile_id, flags)
                
            else:
                # Fallback to legacy parsing
                text, options = self._parse_legacy_command(command_text)
                
                if not text.strip():
                    self._show_legacy_help(message)
                    return
                
                # Process with legacy system
                self._process_legacy(message, text, options)
        
        except Exception as e:
            self.logger.error(f"Audiobook command failed: {e}", exc_info=True)
            self.bot.reply_to(message, f"❌ Error: {e}")
    
    @message_handler(
        content_types=['document'],
        description="Handle document uploads for TTS conversion"
    )
    def document_handler(self, message):
        """Handle document uploads for audiobook conversion"""
        try:
            document = message.document
            
            # Check file type
            if not document.file_name.lower().endswith(('.txt', '.pdf', '.epub')):
                self.bot.reply_to(message, 
                    "❌ Unsupported file type. Supported: .txt, .pdf, .epub\n"
                    "💡 Or use: `/audiobook Your text here`"
                )
                return
            
            self.bot.reply_to(message, 
                "📁 Document processing not yet implemented in new system.\n"
                "💡 Please extract text and use: `/audiobook Your text here`"
            )
            
        except Exception as e:
            self.logger.error(f"Document handler failed: {e}")
            self.bot.reply_to(message, f"❌ Error processing document: {e}")
    
    @command(
        name="tts_engines",
        aliases=["engines"],
        description="Show available TTS engines and their status",
        usage="/tts_engines",
        category="Media"
    )
    def engines_status_command(self, message):
        """Show TTS engines status"""
        try:
            status_text = "🎤 **Available TTS Engines**\n\n"
            
            engines_info = {
                'voice_cloning': {
                    'name': 'Piper Voice Cloning',
                    'quality': 'Premium (Your Voice)',
                    'priority': 0
                },
                'openvoice': {
                    'name': 'OpenVoice Premium',
                    'quality': 'Premium',
                    'priority': 1
                },
                'gtts': {
                    'name': 'Google TTS',
                    'quality': 'Good',
                    'priority': 2
                },
                'pyttsx3': {
                    'name': 'Local TTS',
                    'quality': 'Basic',
                    'priority': 3
                }
            }
            
            for engine_id, info in engines_info.items():
                available = self.engines_available.get(engine_id, False)
                status_icon = "✅" if available else "❌"
                priority_text = f"Priority {info['priority']}" if available else "Unavailable"
                
                status_text += f"{status_icon} **{info['name']}**\n"
                status_text += f"   Quality: {info['quality']}\n"
                status_text += f"   Status: {priority_text}\n\n"
            
            if self.profile_system_available:
                status_text += "🎭 **Profile System:** ✅ Available\n"
                status_text += "   Profiles: `pawel`, `natural`, `fast`\n\n"
            else:
                status_text += "🎭 **Profile System:** ❌ Not Available\n\n"
            
            status_text += "💡 **Usage:**\n"
            status_text += "• `/audiobook Hello world` - Auto engine selection\n"
            status_text += "• `/audiobook Text:profile` - Use specific profile\n"
            status_text += "• `/audiobook Text:engine,voice,language` - Manual options"
            
            self.bot.send_message(message.chat.id, status_text, parse_mode="Markdown")
            
        except Exception as e:
            self.logger.error(f"Engines status command failed: {e}")
            self.bot.reply_to(message, f"❌ Error: {e}")
    
    def _parse_with_profiles(self, command_text: str) -> Tuple[str, str, Dict[str, Any]]:
        """Parse command using profile system"""
        try:
            from enhanced_command_parser import parse_audiobook_command
            return parse_audiobook_command(command_text)
        except Exception as e:
            self.logger.error(f"Profile parsing failed: {e}")
            # Fallback to legacy
            text, options = self._parse_legacy_command(command_text)
            return text, "auto", options
    
    def _parse_legacy_command(self, command_text: str) -> Tuple[str, Dict[str, Any]]:
        """Parse command using legacy system"""
        import re
        
        # Remove command prefix
        text = command_text
        if text.startswith('/'):
            parts = text.split(' ', 1)
            text = parts[1] if len(parts) > 1 else ""
        
        options = {
            'engine': 'auto',
            'language': 'auto',
            'voice_type': 'female'
        }
        
        # Parse flags in brackets: [openvoice,male,polish]
        bracket_pattern = r'\[([^\]]+)\]'
        matches = re.findall(bracket_pattern, text)
        
        if matches:
            for match in matches:
                flags = [f.strip().lower() for f in match.split(',')]
                
                for flag in flags:
                    if flag in ['openvoice', 'voice_cloning', 'gtts', 'pyttsx3']:
                        options['engine'] = flag
                    elif flag in ['polish', 'pl', 'polski']:
                        options['language'] = 'polish'
                    elif flag in ['english', 'en', 'eng']:
                        options['language'] = 'english'
                    elif flag in ['male', 'female']:
                        options['voice_type'] = flag
            
            # Remove brackets from text
            text = re.sub(bracket_pattern, '', text).strip()
        
        return text, options
    
    def _process_with_profiles(self, message, text: str, profile_id: str, flags: Dict[str, Any]):
        """Process TTS using profile system"""
        try:
            from profile_synthesizer import get_tts_synthesizer
            
            # Generate filename
            clean_text = text[:30].replace(' ', '_')
            filename = f"{clean_text}_{profile_id}.mp3"
            output_path = os.path.join(self.audiobook_dir, filename)
            
            # Show processing message
            tts_synthesizer = get_tts_synthesizer()
            profile_info = tts_synthesizer.get_profile_info(profile_id)
            
            status_msg = self.bot.send_message(
                message.chat.id,
                f"🎭 **Synthesizing with Profile:** `{profile_id}`\n"
                f"📝 **Text:** {len(text)} characters\n"
                f"⚙️ **Profile:** {profile_info.split('📝')[0]}...\n"
                f"📁 **Status:** Processing...",
                parse_mode="Markdown"
            )
            
            # Synthesize
            success, result_message = tts_synthesizer.synthesize_with_profile(text, profile_id, output_path)
            
            if success and os.path.exists(output_path) and os.path.getsize(output_path) > 100:
                self._send_audio_file(message, output_path, filename, status_msg, f"Profile: {profile_id}")
            else:
                self._handle_tts_failure(message, status_msg, result_message, profile_system=True)
        
        except Exception as e:
            self.logger.error(f"Profile processing failed: {e}")
            self._handle_tts_failure(message, None, str(e), profile_system=True)
    
    def _process_legacy(self, message, text: str, options: Dict[str, Any]):
        """Process TTS using legacy system"""
        try:
            # Auto-detect language if needed
            if options['language'] == 'auto':
                options['language'] = self._detect_language(text)
            
            # Auto-select engine if needed
            if options['engine'] == 'auto':
                options['engine'] = self._select_best_engine(options['language'])
            
            # Generate filename
            clean_text = text[:30].replace(' ', '_')
            filename = f"{clean_text}_{options['language']}_{options['voice_type']}.mp3"
            output_path = os.path.join(self.audiobook_dir, filename)
            
            # Show processing message
            status_msg = self.bot.send_message(
                message.chat.id,
                f"🎵 **Converting with {options['engine'].title()}**\n"
                f"📝 **Text:** {len(text)} characters\n"
                f"🌍 **Language:** {options['language'].title()}\n"
                f"🎤 **Voice:** {options['voice_type'].title()}\n"
                f"📁 **Status:** Processing...",
                parse_mode="Markdown"
            )
            
            # Convert
            success, result_message = self._convert_text_to_speech(
                text, options['language'], output_path, 
                options['voice_type'], options['engine']
            )
            
            if success and os.path.exists(output_path) and os.path.getsize(output_path) > 100:
                engine_info = f"Engine: {options['engine']}, Language: {options['language']}"
                self._send_audio_file(message, output_path, filename, status_msg, engine_info)
            else:
                self._handle_tts_failure(message, status_msg, result_message, profile_system=False)
        
        except Exception as e:
            self.logger.error(f"Legacy processing failed: {e}")
            self._handle_tts_failure(message, None, str(e), profile_system=False)
    
    def _send_audio_file(self, message, file_path: str, filename: str, status_msg, info: str):
        """Send audio file to user"""
        try:
            file_size = os.path.getsize(file_path)
            file_size_mb = file_size / (1024 * 1024)
            
            with open(file_path, 'rb') as audio_file:
                caption = f"🎧 {filename}\n📊 {file_size_mb:.1f} MB\n🎭 {info}"
                
                self.bot.send_voice(
                    message.chat.id,
                    audio_file,
                    caption=caption
                )
            
            # Clean up status message
            try:
                self.bot.delete_message(message.chat.id, status_msg.message_id)
            except:
                pass
            
            self.logger.info(f"✅ TTS success: {filename}")
            
        except Exception as e:
            self.logger.error(f"Error sending audio file: {e}")
            try:
                self.bot.edit_message_text(
                    f"❌ Error sending audio file: {e}",
                    message.chat.id,
                    status_msg.message_id
                )
            except:
                self.bot.reply_to(message, f"❌ Error sending audio file: {e}")
    
    def _handle_tts_failure(self, message, status_msg, error_message: str, profile_system: bool):
        """Handle TTS conversion failure"""
        try:
            if profile_system:
                error_text = f"❌ **Profile TTS Failed**\n📝 **Error:** {error_message}"
            else:
                error_text = f"❌ **TTS Conversion Failed**\n📝 **Error:** {error_message}"
            
            if status_msg:
                self.bot.edit_message_text(error_text, message.chat.id, status_msg.message_id, parse_mode="Markdown")
            else:
                self.bot.reply_to(message, error_text, parse_mode="Markdown")
            
            self.logger.error(f"TTS failed: {error_message}")
            
        except Exception as e:
            self.logger.error(f"Error handling TTS failure: {e}")
    
    def _detect_language(self, text: str) -> str:
        """Simple language detection"""
        polish_chars = set('ąćęłńóśźżĄĆĘŁŃÓŚŹŻ')
        if any(char in polish_chars for char in text):
            return 'polish'
        return 'english'
    
    def _select_best_engine(self, language: str) -> str:
        """Select best available engine for language"""
        # Priority order with fallback logic
        if language == 'polish' and self.engines_available.get('voice_cloning', False):
            return 'voice_cloning'
        elif self.engines_available.get('openvoice', False):
            # OpenVoice might have import issues, so we'll try it but be ready to fall back
            return 'openvoice'
        elif self.engines_available.get('gtts', False):
            return 'gtts'
        elif self.engines_available.get('pyttsx3', False):
            return 'pyttsx3'
        else:
            # Always fall back to gTTS as it's most reliable
            return 'gtts'
    
    def _convert_text_to_speech(self, text: str, language: str, output_path: str, 
                              voice_type: str, engine: str) -> Tuple[bool, str]:
        """Convert text to speech using specified engine with automatic fallback"""
        try:
            if engine == 'gtts':
                return self._try_gtts(text, output_path, language)
            elif engine == 'pyttsx3':
                return self._try_pyttsx3(text, output_path, voice_type)
            elif engine == 'openvoice':
                # Try OpenVoice first
                success, message = self._try_openvoice(text, output_path, language, voice_type)
                if success:
                    return True, message
                else:
                    # If OpenVoice fails, automatically fall back to gTTS
                    self.logger.warning(f"OpenVoice failed: {message}, falling back to gTTS")
                    fallback_success, fallback_message = self._try_gtts(text, output_path, language)
                    if fallback_success:
                        return True, f"OpenVoice failed, gTTS succeeded: {fallback_message}"
                    else:
                        return False, f"OpenVoice failed: {message}, gTTS also failed: {fallback_message}"
            elif engine == 'voice_cloning':
                return self._try_voice_cloning(text, output_path, language, voice_type)
            else:
                return False, f"Unknown engine: {engine}"
                
        except Exception as e:
            return False, f"Engine error: {e}"
    
    def _try_gtts(self, text: str, output_path: str, language: str) -> Tuple[bool, str]:
        """Try Google TTS conversion"""
        try:
            from gtts import gTTS
            
            lang_code = 'pl' if language == 'polish' else 'en'
            tts = gTTS(text=text, lang=lang_code, slow=False)
            tts.save(output_path)
            
            if os.path.exists(output_path) and os.path.getsize(output_path) > 100:
                return True, "gTTS conversion successful"
            else:
                return False, "gTTS created empty file"
                
        except Exception as e:
            return False, f"gTTS error: {e}"
    
    def _try_pyttsx3(self, text: str, output_path: str, voice_type: str) -> Tuple[bool, str]:
        """Try pyttsx3 conversion"""
        try:
            import pyttsx3
            
            engine = pyttsx3.init()
            
            # Configure voice
            voices = engine.getProperty('voices')
            if voices:
                for voice in voices:
                    if voice_type.lower() in voice.name.lower():
                        engine.setProperty('voice', voice.id)
                        break
            
            engine.setProperty('rate', 150)
            engine.save_to_file(text, output_path)
            engine.runAndWait()
            
            if os.path.exists(output_path) and os.path.getsize(output_path) > 100:
                return True, "pyttsx3 conversion successful"
            else:
                return False, "pyttsx3 created empty file"
                
        except Exception as e:
            return False, f"pyttsx3 error: {e}"
    
    def _try_openvoice(self, text: str, output_path: str, language: str, voice_type: str) -> Tuple[bool, str]:
        """Try OpenVoice conversion"""
        try:
            # Ensure paths are set up
            old_audiobook_path = os.path.join(os.path.dirname(__file__), '..', '..', 'plugins', 'audiobook')
            old_engines_path = os.path.join(old_audiobook_path, 'engines')
            
            if os.path.exists(old_audiobook_path) and old_audiobook_path not in sys.path:
                sys.path.insert(0, old_audiobook_path)
            if os.path.exists(old_engines_path) and old_engines_path not in sys.path:
                sys.path.insert(0, old_engines_path)
            
            # Import OpenVoice with proper error handling
            from openvoice_engine import get_openvoice_tts
            
            engine = get_openvoice_tts()
            if not engine:
                return False, "OpenVoice engine not available"
            
            success = engine.convert_text_to_speech(text, output_path, language, voice_type)
            if success:
                return True, "OpenVoice conversion successful"
            else:
                return False, "OpenVoice conversion failed"
                
        except ImportError as e:
            return False, f"OpenVoice import error: {e}"
        except Exception as e:
            # Handle the relative import error specifically
            error_str = str(e)
            if "attempted relative import with no known parent package" in error_str:
                return False, "OpenVoice module has import issues - using fallback TTS engines"
            return False, f"OpenVoice error: {e}"
    
    def _try_voice_cloning(self, text: str, output_path: str, language: str, voice_type: str) -> Tuple[bool, str]:
        """Try voice cloning conversion"""
        try:
            from piper_voice_cloning_engine import get_piper_voice_cloning_tts
            
            engine = get_piper_voice_cloning_tts()
            if not engine:
                return False, "Voice cloning engine not available"
            
            success = engine.convert_text_to_speech(text, output_path, language, voice_type)
            if success:
                return True, "Voice cloning conversion successful"
            else:
                return False, "Voice cloning conversion failed"
                
        except Exception as e:
            return False, f"Voice cloning error: {e}"
    
    def _show_profile_help(self, message):
        """Show help for profile system"""
        try:
            from profile_synthesizer import list_available_profiles
            
            available_profiles = list_available_profiles()
            help_text = "🎭 **Audiobook TTS with Voice Profiles**\n\n"
            help_text += "📋 **Syntax:**\n"
            help_text += "• `/audiobook Your text:profile` - Use specific profile\n"
            help_text += "• `/audiobook Your text` - Auto-select profile\n\n"
            help_text += "🎤 **Available Profiles:**\n"
            
            for profile_key, profile_name in available_profiles.items():
                help_text += f"• `{profile_key}` - {profile_name}\n"
            
            help_text += "\n💡 **Examples:**\n"
            help_text += "• `/audiobook Hello world:natural`\n"
            help_text += "• `/audiobook Witaj świecie:pawel`\n"
            help_text += "• `/audiobook Quick test:fast`"
            
            self.bot.send_message(message.chat.id, help_text, parse_mode="Markdown")
            
        except Exception as e:
            self.logger.error(f"Error showing profile help: {e}")
            self._show_legacy_help(message)
    
    def _show_legacy_help(self, message):
        """Show help for legacy system"""
        help_text = """🎧 **Audiobook TTS Commands**

🎯 **Quick Commands:**
• `/audiobook Your text here` - Auto conversion with best available engine
• `/audiobook [gtts] Text` - Force Google TTS (most reliable)
• `/audiobook [english] Text` - Force English language
• `/audiobook [polish] Text` - Force Polish language

🎛️ **Available Flags:**
• Language: `[polish]`, `[english]` 
• Voice: `[male]`, `[female]`
• Engine: `[gtts]`, `[pyttsx3]`

📊 **Examples:**
• `/audiobook Hello world` - Auto selection (uses gTTS)
• `/audiobook [english,female] Hello world` - English Female
• `/audiobook [polish,male] Witaj świecie` - Polish Male
• `/audiobook [gtts] Test message` - Force Google TTS

⚙️ **Engine Status:**"""
        
        # Show reliable engines first
        reliable_engines = ['gtts', 'pyttsx3']
        experimental_engines = ['openvoice', 'voice_cloning']
        
        help_text += "\n\n**Reliable Engines:**"
        for engine in reliable_engines:
            if engine in self.engines_available:
                status = "✅" if self.engines_available[engine] else "❌"
                help_text += f"\n{status} {engine.title()}"
        
        help_text += "\n\n**Experimental Engines:**"
        for engine in experimental_engines:
            if engine in self.engines_available:
                status = "✅" if self.engines_available[engine] else "❌"
                note = " (may have import issues)" if engine == 'openvoice' and not self.engines_available[engine] else ""
                help_text += f"\n{status} {engine.title()}{note}"
        
        help_text += "\n\n💡 **Note:** If OpenVoice fails, the system automatically falls back to Google TTS for reliable conversion."
        
        self.bot.send_message(message.chat.id, help_text, parse_mode="Markdown")
