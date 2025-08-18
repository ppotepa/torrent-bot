import os
import glob
import time
import socket
import yt_dlp
from universal_flags import parse_universal_flags, validate_command_flags, convert_flags_to_legacy

BASE_DIR = "downloads"

def check_internet_connection(timeout=10):
    """Quick check if internet connection is available"""
    try:
        # Try to connect to Google's DNS server
        socket.create_connection(("8.8.8.8", 53), timeout=timeout)
        return True
    except OSError:
        return False

def safe_bot_reply(bot, message, text, retries=3, delay=2):
    """Send a bot reply with retry logic for network issues"""
    for attempt in range(retries):
        try:
            bot.reply_to(message, text, parse_mode="Markdown")
            return True
        except Exception as e:
            if "Network is unreachable" in str(e) or "Max retries exceeded" in str(e):
                if attempt < retries - 1:
                    print(f"⚠️ Network issue, retrying in {delay}s (attempt {attempt + 1}/{retries})")
                    time.sleep(delay)
                    continue
                else:
                    print(f"❌ Failed to send message after {retries} attempts: {e}")
                    return False
            else:
                # For non-network errors, don't retry
                print(f"❌ Bot reply error: {e}")
                return False
    return False

def download(bot, message, url, folder):
    """Download function called by /dl command - handles flags properly"""
    try:
        # Parse flags from the message
        query, flags_list, parse_errors = parse_universal_flags(message.text, "dl")
        valid_flags, validation_errors = validate_command_flags(flags_list, "dl")
        legacy_flags = convert_flags_to_legacy(valid_flags, "dl")
        
        # Determine mode based on audio flag
        mode = "audio" if legacy_flags.get("audio", False) else "video"
        
        # Show any flag errors (but continue processing)
        all_errors = parse_errors + validation_errors
        if all_errors:
            error_msg = "⚠️ Flag parsing errors:\n" + "\n".join(f"• {err}" for err in all_errors)
            safe_bot_reply(bot, message, error_msg)
        
        # Call the main run function
        run(bot, message, folder, url, mode)
        
    except Exception as e:
        error_msg = f"❌ YouTube download error: {e}"
        print(error_msg)  # Log to console
        safe_bot_reply(bot, message, error_msg)  # Try to send to user

def run(bot, message, folder, url, mode="video"):
    try:
        # Quick connectivity check
        if not check_internet_connection():
            safe_bot_reply(bot, message, "❌ No internet connection available. Please check your network and try again.")
            return
        
        target_dir = os.path.join(BASE_DIR, folder) if folder else BASE_DIR
        os.makedirs(target_dir, exist_ok=True)

        # Use safe reply for initial message
        initial_msg = (
            f"🎬 YouTube detected!\n"
            f"📂 Folder: {folder or 'root'}\n"
            f"🔗 {url}\n"
            f"🎛 Mode: {mode}\n"
            f"⏳ Starting download..."
        )
        safe_bot_reply(bot, message, initial_msg)

        if mode == "audio":
            # Audio-only: Download best quality audio track only
            ydl_opts = {
                'format': 'bestaudio[ext=m4a]/bestaudio[ext=webm]/bestaudio/best',
                'outtmpl': f'{target_dir}/%(title).200s.%(ext)s',  # Limit filename length
                'noplaylist': True,
                'quiet': True,
                'restrictfilenames': True,  # Use only ASCII characters
            }
            
            # Try to add MP3 conversion if FFmpeg is available
            try:
                import subprocess
                subprocess.run(['ffmpeg', '-version'], capture_output=True, timeout=5)
                # FFmpeg is available, add conversion
                ydl_opts.update({
                    'extractaudio': True,
                    'audioformat': 'mp3',
                    'audioquality': '0',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '0',
                    }],
                    'prefer_ffmpeg': True,
                })
            except (FileNotFoundError, subprocess.TimeoutExpired):
                # FFmpeg not available, download best audio format as-is
                safe_bot_reply(bot, message, "⚠️ FFmpeg not found - downloading best audio format (may not be MP3)")
                
        else:  # video (default - includes audio)
            # Video: Download best quality video+audio (video always has audio)
            ydl_opts = {
                'format': 'bestvideo[height<=2160]+bestaudio[ext=m4a]/bestvideo[height<=2160]+bestaudio/best[height<=2160]/best',
                'outtmpl': f'{target_dir}/%(title).200s.%(ext)s',  # Limit filename length
                'noplaylist': True,
                'quiet': True,
                'merge_output_format': 'mp4',
                'writesubtitles': False,
                'writeautomaticsub': False,
                'restrictfilenames': True,  # Use only ASCII characters
            }
            
            # Add FFmpeg preference if available
            try:
                import subprocess
                subprocess.run(['ffmpeg', '-version'], capture_output=True, timeout=5)
                ydl_opts['prefer_ffmpeg'] = True
            except (FileNotFoundError, subprocess.TimeoutExpired):
                pass  # Will use default merger

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                original_filename = ydl.prepare_filename(info)
                title = info.get('title', 'Unknown')

            # Find the actual downloaded file
            actual_filename = original_filename
            
            # For audio mode, check for MP3 conversion
            if mode == "audio":
                mp3_filename = os.path.splitext(original_filename)[0] + ".mp3"
                if os.path.exists(mp3_filename):
                    actual_filename = mp3_filename
                elif not original_filename.endswith(".mp3"):
                    # Look for any .mp3 file with similar name in the directory
                    import glob
                    base_name = os.path.splitext(os.path.basename(original_filename))[0]
                    search_pattern = os.path.join(target_dir, f"*{base_name}*.mp3")
                    mp3_files = glob.glob(search_pattern)
                    if mp3_files:
                        actual_filename = mp3_files[0]  # Use the first match

            # Verify file exists and is readable
            if os.path.exists(actual_filename) and os.path.isfile(actual_filename):
                try:
                    file_size = os.path.getsize(actual_filename)
                    size_mb = file_size / (1024 * 1024)
                    
                    # Get actual file extension
                    file_ext = os.path.splitext(actual_filename)[1].upper()
                    
                    # Clear messaging about what was downloaded
                    if mode == "audio":
                        format_desc = f"Audio track only ({file_ext.lstrip('.')})"
                    else:
                        format_desc = f"Full video with audio ({file_ext.lstrip('.')})"
                    
                    safe_bot_reply(
                        bot, message,
                        f"✅ **Download Complete!**\n"
                        f"📁 **{title}**\n"
                        f"💾 Size: {size_mb:.1f} MB\n"
                        f"📂 Saved to: {folder or 'root'}\n"
                        f"🎛 Format: {format_desc}\n"
                        f"📄 File: {os.path.basename(actual_filename)}"
                    )
                    
                    # Send the file if it's small enough (under 50MB for Telegram)
                    if file_size < 50 * 1024 * 1024:  # 50MB limit
                        try:
                            # Test file readability before sending
                            with open(actual_filename, "rb") as test_file:
                                test_file.read(1024)  # Try to read first 1KB
                            
                            with open(actual_filename, "rb") as f:
                                if mode == "audio":
                                    bot.send_audio(message.chat.id, f, caption=f"🎵 {title}")
                                else:
                                    bot.send_video(message.chat.id, f, caption=f"🎬 {title}")
                        except PermissionError:
                            safe_bot_reply(bot, message, f"⚠️ File downloaded but permission denied when trying to send: {actual_filename}")
                        except Exception as send_error:
                            safe_bot_reply(bot, message, f"⚠️ File downloaded but couldn't send: {send_error}")
                    else:
                        safe_bot_reply(bot, message, f"📁 File too large for Telegram ({size_mb:.1f} MB). Check your downloads folder.")
                        
                except OSError as file_error:
                    safe_bot_reply(bot, message, f"❌ File downloaded but cannot access: {file_error}")
            else:
                safe_bot_reply(bot, message, f"❌ Download completed but file not found: {actual_filename}")
                
        except yt_dlp.DownloadError as e:
            safe_bot_reply(bot, message, f"❌ YouTube download failed: {str(e)}")
        except Exception as e:
            safe_bot_reply(bot, message, f"❌ Download error: {str(e)}")

    except Exception as e:
        safe_bot_reply(bot, message, f"❌ YouTube error: {e}")
