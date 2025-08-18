def convert_inline_text_fixed(bot, message, text_content: str, language: str, voice_type: str = 'default', engine: str = 'auto'):
    """
    Convert inline text directly to audiobook without file upload - FIXED VERSION
    
    Args:
        bot: Telegram bot instance
        message: Telegram message object
        text_content: Text content to convert
        language: Language code for TTS
        voice_type: Voice type (default, male, female, british, young)
        engine: TTS engine preference (auto, enhanced_sapi, elevenlabs, gtts, pyttsx3)
    """
    try:
        # Validate text content
        if not text_content.strip():
            bot.reply_to(message, "❌ No text content provided for conversion.")
            return
            
        if len(text_content) < 10:
            bot.reply_to(message, "❌ Text is too short (minimum 10 characters).")
            return
            
        if len(text_content) > 10000:  # Limit for inline text
            bot.reply_to(
                message, 
                f"❌ Text is too long ({len(text_content)} characters). "
                f"Maximum for inline text: 10,000 characters.\n"
                f"Please use file upload for longer texts."
            )
            return
        
        # Show text preview with engine and voice info
        engine_display = engine if engine != 'auto' else 'Enhanced SAPI (auto)'
        voice_display = voice_type if voice_type != 'default' else 'Default'
        
        preview = text_content[:150] + "..." if len(text_content) > 150 else text_content
        
        # Send status without Markdown to avoid parsing issues
        status_msg = (
            f"🎧 Processing Inline Text\n\n"
            f"📊 Length: {len(text_content)} characters\n"
            f"🗣️ Language: {language}\n"
            f"🎭 Voice: {voice_display}\n"
            f"🔧 Engine: {engine_display}\n"
            f"📝 Preview: {preview}\n\n"
            f"⏳ Converting to speech..."
        )
        
        bot.reply_to(message, status_msg)
        
        # Create output filename based on first few words and settings
        words = text_content.split()[:5]  # First 5 words
        title = "_".join(words).replace(" ", "_")
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()[:25]
        
        if not safe_title:
            safe_title = "inline_text"
            
        # Include engine and voice in filename for clarity
        filename_parts = [safe_title, language]
        if engine != 'auto':
            filename_parts.append(engine)
        if voice_type != 'default':
            filename_parts.append(voice_type)
            
        output_filename = f"{'_'.join(filename_parts)}.mp3"
        output_path = os.path.join(AUDIOBOOK_DIR, output_filename)
        
        # Convert to speech with specified parameters
        try:
            success = convert_text_to_speech(text_content, language, output_path, voice_type, engine)
            
            if success and os.path.exists(output_path):
                # Send the audiobook file
                file_size = os.path.getsize(output_path)
                file_size_mb = file_size / (1024 * 1024)
                
                result_msg = (
                    f"✅ Inline Text Audiobook Created!\n\n"
                    f"📁 File: {output_filename}\n"
                    f"💾 Size: {file_size_mb:.1f} MB\n"
                    f"🗣️ Language: {language}\n"
                    f"🎭 Voice: {voice_display}\n"
                    f"🔧 Engine: {engine_display}\n"
                    f"📤 Sending audio..."
                )
                
                bot.reply_to(message, result_msg)
                
                # Send as audio file
                with open(output_path, 'rb') as audio_file:
                    bot.send_audio(
                        message.chat.id,
                        audio_file,
                        caption=f"🎧 Inline Text Audiobook",
                        title=safe_title,
                        performer="Enhanced TTS Bot"
                    )
                    
                bot.reply_to(message, f"🎉 Inline text conversion completed!\n📚 Saved to: audiobooks/{output_filename}")
                
            else:
                bot.reply_to(message, "❌ TTS conversion failed. Please try again.")
                
        except Exception as e:
            bot.reply_to(message, f"❌ TTS conversion error: {e}")
            
    except Exception as e:
        bot.reply_to(message, f"❌ Inline text conversion error: {e}")
