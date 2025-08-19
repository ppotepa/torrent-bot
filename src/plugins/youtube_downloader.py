"""
YouTube Downloader Plugin - Downloads videos and audio from YouTube
"""

import os
import re
import time
from typing import Optional
from urllib.parse import urlparse, parse_qs

from core import PluginBase, plugin_info, command, message_handler, CommandScope, PermissionLevel


@plugin_info(
    name="YouTube Downloader",
    version="1.0.0", 
    author="TorrentBot",
    description="Downloads videos and audio from YouTube using yt-dlp",
    dependencies=["yt-dlp"],
    enabled=True
)
class YouTubeDownloaderPlugin(PluginBase):
    """Plugin for downloading YouTube videos and audio"""
    
    def __init__(self, bot, logger=None):
        super().__init__(bot, logger)
        self.downloads_dir = "downloads/youtube"
        os.makedirs(self.downloads_dir, exist_ok=True)
    
    def get_plugin_description(self) -> str:
        return "Downloads videos and audio from YouTube URLs with format selection"
    
    @command(
        name="youtube",
        aliases=["yt", "ytdl"],
        description="Download video or audio from YouTube",
        usage="/youtube <url> [audio|video] [quality]",
        examples=[
            "/youtube https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "/youtube https://youtu.be/dQw4w9WgXcQ audio",
            "/youtube https://www.youtube.com/watch?v=dQw4w9WgXcQ video 720p"
        ],
        flags=["audio", "video", "720p", "1080p", "best", "worst"],
        category="Media"
    )
    def youtube_download_command(self, message):
        """Handle YouTube download command"""
        try:
            args = message.text.split()[1:]
            if not args:
                self.bot.reply_to(message, 
                    "❌ Please provide a YouTube URL\n"
                    "Usage: `/youtube <url> [audio|video] [quality]`\n\n"
                    "Examples:\n"
                    "• `/youtube https://youtu.be/dQw4w9WgXcQ`\n"
                    "• `/youtube https://youtu.be/dQw4w9WgXcQ audio`\n"
                    "• `/youtube https://youtu.be/dQw4w9WgXcQ video 720p`",
                    parse_mode="Markdown"
                )
                return
            
            url = args[0]
            
            # Validate YouTube URL
            if not self._is_youtube_url(url):
                self.bot.reply_to(message, "❌ Invalid YouTube URL")
                return
            
            # Parse options
            format_type = "video"  # default
            quality = "best"      # default
            
            for arg in args[1:]:
                arg_lower = arg.lower()
                if arg_lower in ["audio", "video"]:
                    format_type = arg_lower
                elif arg_lower in ["720p", "1080p", "best", "worst"]:
                    quality = arg_lower
            
            # Start download
            self._download_youtube(message, url, format_type, quality)
            
        except Exception as e:
            self.logger.error(f"YouTube download command failed: {e}")
            self.bot.reply_to(message, f"❌ Error: {e}")
    
    @message_handler(
        regexp=r'(?:https?://)?(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)[\w-]+',
        description="Auto-download YouTube links"
    )
    def auto_youtube_handler(self, message):
        """Automatically handle YouTube URLs posted in chat"""
        try:
            url = message.text.strip()
            
            if self._is_youtube_url(url):
                self.logger.info(f"Auto-detected YouTube URL: {url}")
                
                # Send confirmation message
                self.bot.reply_to(message, 
                    f"🎥 Detected YouTube URL! Starting download...\n"
                    f"📹 Format: Video (default)\n"
                    f"🔗 URL: {url[:50]}..."
                )
                
                # Download with default settings
                self._download_youtube(message, url, "video", "best")
        
        except Exception as e:
            self.logger.error(f"Auto YouTube handler failed: {e}")
    
    def _is_youtube_url(self, url: str) -> bool:
        """Check if URL is a valid YouTube URL"""
        youtube_patterns = [
            r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=[\w-]+',
            r'(?:https?://)?youtu\.be/[\w-]+',
            r'(?:https?://)?(?:www\.)?youtube\.com/embed/[\w-]+',
            r'(?:https?://)?(?:www\.)?youtube\.com/v/[\w-]+',
        ]
        
        for pattern in youtube_patterns:
            if re.match(pattern, url, re.IGNORECASE):
                return True
        
        return False
    
    def _extract_video_id(self, url: str) -> Optional[str]:
        """Extract video ID from YouTube URL"""
        patterns = [
            r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/|youtube\.com/v/)([\w-]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def _download_youtube(self, message, url: str, format_type: str, quality: str):
        """Download YouTube video/audio"""
        try:
            # Show progress message
            status_msg = self.bot.send_message(
                message.chat.id,
                f"⏳ **Starting YouTube Download**\n\n"
                f"🔗 **URL:** {url[:50]}...\n"
                f"📹 **Format:** {format_type.title()}\n"
                f"🎯 **Quality:** {quality}\n"
                f"📁 **Status:** Initializing...",
                parse_mode="Markdown"
            )
            
            # Import yt-dlp
            try:
                import yt_dlp
            except ImportError:
                self.bot.edit_message_text(
                    "❌ **Error:** yt-dlp not installed\n"
                    "Please install: `pip install yt-dlp`",
                    message.chat.id,
                    status_msg.message_id,
                    parse_mode="Markdown"
                )
                return
            
            # Configure yt-dlp options
            video_id = self._extract_video_id(url)
            filename_template = f"{video_id}_%(title)s.%(ext)s" if video_id else "%(title)s.%(ext)s"
            
            ydl_opts = {
                'outtmpl': os.path.join(self.downloads_dir, filename_template),
                'noplaylist': True,
            }
            
            # Set format based on type and quality
            if format_type == "audio":
                ydl_opts['format'] = 'bestaudio/best'
                ydl_opts['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }]
            else:  # video
                if quality == "720p":
                    ydl_opts['format'] = 'best[height<=720]'
                elif quality == "1080p":
                    ydl_opts['format'] = 'best[height<=1080]'
                elif quality == "worst":
                    ydl_opts['format'] = 'worst'
                else:  # best
                    ydl_opts['format'] = 'best'
            
            # Update status
            self.bot.edit_message_text(
                f"⏳ **YouTube Download in Progress**\n\n"
                f"🔗 **URL:** {url[:50]}...\n"
                f"📹 **Format:** {format_type.title()}\n"
                f"🎯 **Quality:** {quality}\n"
                f"📁 **Status:** Downloading...",
                message.chat.id,
                status_msg.message_id,
                parse_mode="Markdown"
            )
            
            # Download with yt-dlp
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Get video info first
                info = ydl.extract_info(url, download=False)
                title = info.get('title', 'Unknown')
                duration = info.get('duration', 0)
                uploader = info.get('uploader', 'Unknown')
                
                # Update status with video info
                duration_str = f"{duration//60}:{duration%60:02d}" if duration else "Unknown"
                
                self.bot.edit_message_text(
                    f"📥 **Downloading: {title[:30]}...**\n\n"
                    f"👤 **Uploader:** {uploader}\n"
                    f"⏱️ **Duration:** {duration_str}\n"
                    f"📹 **Format:** {format_type.title()}\n"
                    f"🎯 **Quality:** {quality}\n"
                    f"📁 **Status:** Processing...",
                    message.chat.id,
                    status_msg.message_id,
                    parse_mode="Markdown"
                )
                
                # Actually download
                ydl.download([url])
            
            # Find downloaded file
            downloaded_files = []
            for file in os.listdir(self.downloads_dir):
                if video_id and video_id in file:
                    downloaded_files.append(file)
                elif not video_id and file.endswith(('.mp4', '.mp3', '.webm', '.mkv')):
                    # Fallback: find recent files
                    file_path = os.path.join(self.downloads_dir, file)
                    if os.path.getctime(file_path) > (time.time() - 300):  # 5 minutes
                        downloaded_files.append(file)
            
            if downloaded_files:
                downloaded_file = downloaded_files[0]  # Take first match
                file_path = os.path.join(self.downloads_dir, downloaded_file)
                file_size = os.path.getsize(file_path)
                file_size_mb = file_size / (1024 * 1024)
                
                # Success message
                success_msg = (
                    f"✅ **Download Complete!**\n\n"
                    f"📁 **File:** {downloaded_file}\n"
                    f"📊 **Size:** {file_size_mb:.1f} MB\n"
                    f"📹 **Format:** {format_type.title()}\n"
                    f"🎯 **Quality:** {quality}"
                )
                
                # Send file if small enough for Telegram (50MB limit)
                if file_size < 50 * 1024 * 1024:  # 50MB
                    try:
                        with open(file_path, 'rb') as f:
                            if format_type == "audio":
                                self.bot.send_audio(
                                    message.chat.id,
                                    f,
                                    caption=f"🎵 {title}",
                                    title=title,
                                    performer=uploader
                                )
                            else:
                                self.bot.send_video(
                                    message.chat.id,
                                    f,
                                    caption=f"🎥 {title}"
                                )
                        
                        self.bot.edit_message_text(
                            success_msg,
                            message.chat.id,
                            status_msg.message_id,
                            parse_mode="Markdown"
                        )
                        
                    except Exception as send_error:
                        self.logger.error(f"Error sending file: {send_error}")
                        self.bot.edit_message_text(
                            f"{success_msg}\n\n❌ File too large to send via Telegram",
                            message.chat.id,
                            status_msg.message_id,
                            parse_mode="Markdown"
                        )
                else:
                    self.bot.edit_message_text(
                        f"{success_msg}\n\n📁 File saved locally (too large for Telegram)",
                        message.chat.id,
                        status_msg.message_id,
                        parse_mode="Markdown"
                    )
                
            else:
                self.bot.edit_message_text(
                    "❌ **Download failed** - Could not find downloaded file",
                    message.chat.id,
                    status_msg.message_id,
                    parse_mode="Markdown"
                )
        
        except Exception as e:
            self.logger.error(f"YouTube download failed: {e}")
            try:
                self.bot.edit_message_text(
                    f"❌ **Download failed**\n\n"
                    f"🔍 **Error:** {str(e)[:100]}...\n"
                    f"💡 Try a different URL or format",
                    message.chat.id,
                    status_msg.message_id,
                    parse_mode="Markdown"
                )
            except:
                self.bot.reply_to(message, f"❌ Download failed: {e}")
    
    @command(
        name="ytinfo",
        aliases=["youtube_info"],
        description="Get information about a YouTube video without downloading",
        usage="/ytinfo <url>",
        examples=["/ytinfo https://www.youtube.com/watch?v=dQw4w9WgXcQ"],
        category="Media"
    )
    def youtube_info_command(self, message):
        """Get YouTube video information"""
        try:
            args = message.text.split()[1:]
            if not args:
                self.bot.reply_to(message, "❌ Please provide a YouTube URL")
                return
            
            url = args[0]
            
            if not self._is_youtube_url(url):
                self.bot.reply_to(message, "❌ Invalid YouTube URL")
                return
            
            # Import yt-dlp
            try:
                import yt_dlp
            except ImportError:
                self.bot.reply_to(message, "❌ yt-dlp not installed")
                return
            
            # Extract info
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(url, download=False)
                
                title = info.get('title', 'Unknown')
                uploader = info.get('uploader', 'Unknown')
                duration = info.get('duration', 0)
                view_count = info.get('view_count', 0)
                upload_date = info.get('upload_date', '')
                description = info.get('description', '')[:200]
                
                duration_str = f"{duration//60}:{duration%60:02d}" if duration else "Unknown"
                views_str = f"{view_count:,}" if view_count else "Unknown"
                
                # Format upload date
                if upload_date and len(upload_date) == 8:
                    upload_date_formatted = f"{upload_date[:4]}-{upload_date[4:6]}-{upload_date[6:]}"
                else:
                    upload_date_formatted = "Unknown"
                
                info_text = (
                    f"🎥 **YouTube Video Info**\n\n"
                    f"**Title:** {title}\n"
                    f"**Uploader:** {uploader}\n"
                    f"**Duration:** {duration_str}\n"
                    f"**Views:** {views_str}\n"
                    f"**Upload Date:** {upload_date_formatted}\n\n"
                    f"**Description:** {description}..."
                )
                
                self.bot.send_message(message.chat.id, info_text, parse_mode="Markdown")
        
        except Exception as e:
            self.logger.error(f"YouTube info command failed: {e}")
            self.bot.reply_to(message, f"❌ Error getting video info: {e}")
