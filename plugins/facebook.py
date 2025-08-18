import os
import yt_dlp
import time
import subprocess
from universal_flags import parse_universal_flags, validate_command_flags

BASE_DIR = "downloads"

def check_ffmpeg():
    """Check if FFmpeg is available for audio conversion"""
    try:
        subprocess.run(['ffmpeg', '-version'], 
                      capture_output=True, check=True, timeout=5)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return False

def download(bot, message, url, folder=None):
    """
    Main download function called by bot.py - handles flag parsing and mode detection
    """
    try:
        # Parse flags from the command
        full_text = message.text.strip()
        query, flags_list, parse_errors = parse_universal_flags(full_text, 'dl')
        
        # Validate flags for download command
        valid_flags, validation_errors = validate_command_flags(flags_list, 'dl')
        
        # Show any flag parsing errors
        all_errors = parse_errors + validation_errors
        if all_errors:
            error_msg = "⚠️ Flag parsing errors:\n" + "\n".join(f"• {err}" for err in all_errors)
            bot.reply_to(message, error_msg)
        
        # Determine mode from flags
        mode = "audio" if "audio" in valid_flags else "video"
        
        # Call the main run function
        run(bot, message, folder, url, mode)
        
    except Exception as e:
        bot.reply_to(message, f"❌ Facebook error: {e}")

def run(bot, message, folder, url, mode="video"):
    try:
        target_dir = os.path.join(BASE_DIR, folder) if folder else BASE_DIR
        os.makedirs(target_dir, exist_ok=True)

        bot.reply_to(
            message,
            f"📘 Facebook detected!\n📂 Folder: {folder or 'root'}\n🔗 {url}\n🎛 Mode: {mode}"
        )

        if mode == "audio":
            # Check if FFmpeg is available for MP3 conversion
            ffmpeg_available = check_ffmpeg()
            
            if ffmpeg_available:
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': f'{target_dir}/%(title)s.%(ext)s',
                    'noplaylist': True,
                    'quiet': True,
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '0',  # keep best quality
                    }],
                    # Add these options to handle file operations better
                    'writeinfojson': False,
                    'writethumbnail': False,
                    'ignoreerrors': False,
                }
            else:
                # Fallback: download best audio format available (likely M4A or WebM)
                bot.reply_to(
                    message,
                    "⚠️ FFmpeg not found! Downloading best available audio format instead of MP3.\n"
                    "To get MP3 files, please install FFmpeg."
                )
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': f'{target_dir}/%(title)s.%(ext)s',
                    'noplaylist': True,
                    'quiet': True,
                    'writeinfojson': False,
                    'writethumbnail': False,
                    'ignoreerrors': False,
                }
        else:  # video
            ydl_opts = {
                'format': 'bestvideo+bestaudio/best',
                'outtmpl': f'{target_dir}/%(title)s.%(ext)s',
                'noplaylist': True,
                'quiet': True,
                'merge_output_format': 'mp4',
                'writeinfojson': False,
                'writethumbnail': False,
                'ignoreerrors': False,
            }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(url, download=True)
                title = info.get('title', 'Unknown')
                
                # For audio mode, the file should be converted to MP3 (if FFmpeg available)
                if mode == "audio":
                    base_filename = ydl.prepare_filename(info)
                    
                    if ffmpeg_available:
                        # FFmpeg should create an MP3 file
                        mp3_filename = os.path.splitext(base_filename)[0] + '.mp3'
                        
                        # Wait a bit for file operations to complete
                        time.sleep(1)
                        
                        # Check if MP3 file exists
                        if os.path.exists(mp3_filename):
                            final_filename = mp3_filename
                        else:
                            # Fallback: look for any audio file with the title
                            import glob
                            title_safe = title.replace('/', '_').replace('\\', '_')  # Make title safe for file paths
                            audio_pattern = os.path.join(target_dir, f"*{title_safe}*.mp3")
                            matches = glob.glob(audio_pattern)
                            if matches:
                                final_filename = matches[0]
                            else:
                                # Look for other audio formats that might not have been converted
                                audio_extensions = ['*.mp3', '*.m4a', '*.wav', '*.ogg', '*.webm']
                                for ext in audio_extensions:
                                    pattern = os.path.join(target_dir, f"*{title_safe}*{ext}")
                                    matches = glob.glob(pattern)
                                    if matches:
                                        final_filename = matches[0]
                                        break
                                else:
                                    raise FileNotFoundError(f"Could not find downloaded audio file for: {title}")
                    else:
                        # No FFmpeg - use the original file (likely M4A, WebM, etc.)
                        final_filename = base_filename
                        
                        # Wait for download to complete
                        time.sleep(1)
                        
                        if not os.path.exists(final_filename):
                            # Look for any audio file that was downloaded
                            import glob
                            title_safe = title.replace('/', '_').replace('\\', '_')
                            audio_extensions = ['*.m4a', '*.webm', '*.mp3', '*.wav', '*.ogg']
                            for ext in audio_extensions:
                                pattern = os.path.join(target_dir, f"*{title_safe}*{ext}")
                                matches = glob.glob(pattern)
                                if matches:
                                    final_filename = matches[0]
                                    break
                            else:
                                # Try without title matching
                                pattern = os.path.join(target_dir, f"*{ext}")
                                matches = glob.glob(pattern)
                                if matches:
                                    # Get the most recently created file
                                    final_filename = max(matches, key=os.path.getctime)
                                else:
                                    raise FileNotFoundError(f"Could not find downloaded audio file for: {title}")
                else:
                    final_filename = ydl.prepare_filename(info)
                    # For video, ensure we have the right extension
                    if not final_filename.endswith('.mp4'):
                        base = os.path.splitext(final_filename)[0]
                        final_filename = base + '.mp4'

                # Verify file exists before sending
                if not os.path.exists(final_filename):
                    bot.reply_to(message, f"❌ Download failed: file not found at {final_filename}")
                    return

                # Send the file
                try:
                    with open(final_filename, "rb") as f:
                        if mode == "audio":
                            # Determine the actual format for the caption
                            file_ext = os.path.splitext(final_filename)[1].upper().replace('.', '')
                            format_desc = f"{file_ext} audio" if file_ext else "audio"
                            
                            bot.send_audio(
                                message.chat.id, 
                                f, 
                                caption=f"✅ {title}\n📂 Saved to {folder or 'root'} ({format_desc})",
                                title=title
                            )
                        else:
                            bot.send_video(
                                message.chat.id, 
                                f, 
                                caption=f"✅ {title}\n📂 Saved to {folder or 'root'} (MP4 video)"
                            )
                            
                    bot.reply_to(message, f"✅ Facebook download complete!\n📁 File: {os.path.basename(final_filename)}")
                    
                except Exception as send_error:
                    bot.reply_to(message, f"✅ Download complete but could not send file: {send_error}\n📁 Saved: {final_filename}")
                    
            except yt_dlp.DownloadError as dl_error:
                bot.reply_to(message, f"❌ Download error: {dl_error}")
            except Exception as yt_error:
                bot.reply_to(message, f"❌ YouTube-DL error: {yt_error}")

    except Exception as e:
        bot.reply_to(message, f"❌ Facebook error: {e}")
