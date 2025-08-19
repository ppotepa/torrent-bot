"""
Facebook Downloader Plugin - Downloads videos from Facebook
"""

import os
import re
import time
from typing import Optional

from core import PluginBase, plugin_info, command, message_handler, CommandScope, PermissionLevel


@plugin_info(
    name="Facebook Downloader",
    version="1.0.0",
    author="TorrentBot",
    description="Downloads videos from Facebook using yt-dlp",
    dependencies=["yt-dlp"],
    enabled=True
)
class FacebookDownloaderPlugin(PluginBase):
    """Plugin for downloading Facebook videos"""
    
    def __init__(self, bot, logger=None):
        super().__init__(bot, logger)
        self.downloads_dir = "downloads/facebook"
        os.makedirs(self.downloads_dir, exist_ok=True)
    
    def get_plugin_description(self) -> str:
        return "Downloads videos from Facebook URLs with quality selection"
    
    @command(
        name="facebook",
        aliases=["fb", "fbdl"],
        description="Download video from Facebook",
        usage="/facebook <url> [quality]",
        examples=[
            "/facebook https://www.facebook.com/watch/?v=123456789",
            "/facebook https://fb.watch/abc123 720p"
        ],
        flags=["720p", "1080p", "best", "worst"],
        category="Media"
    )
    def facebook_download_command(self, message):
        """Handle Facebook download command"""
        try:
            args = message.text.split()[1:]
            if not args:
                self.bot.reply_to(message,
                    "❌ Please provide a Facebook URL\n"
                    "Usage: `/facebook <url> [quality]`\n\n"
                    "Examples:\n"
                    "• `/facebook https://www.facebook.com/watch/?v=123`\n"
                    "• `/facebook https://fb.watch/abc123 720p`",
                    parse_mode="Markdown"
                )
                return
            
            url = args[0]
            
            # Validate Facebook URL
            if not self._is_facebook_url(url):
                self.bot.reply_to(message, "❌ Invalid Facebook URL")
                return
            
            # Parse quality option
            quality = "best"  # default
            if len(args) > 1:
                quality_arg = args[1].lower()
                if quality_arg in ["720p", "1080p", "best", "worst"]:
                    quality = quality_arg
            
            # Start download
            self._download_facebook(message, url, quality)
            
        except Exception as e:
            self.logger.error(f"Facebook download command failed: {e}")
            self.bot.reply_to(message, f"❌ Error: {e}")
    
    @message_handler(
        regexp=r'(?:https?://)?(?:www\.)?(?:facebook\.com/watch/\?v=|fb\.watch/)[\w-]+',
        description="Auto-download Facebook links"
    )
    def auto_facebook_handler(self, message):
        """Automatically handle Facebook URLs posted in chat"""
        try:
            url = message.text.strip()
            
            if self._is_facebook_url(url):
                self.logger.info(f"Auto-detected Facebook URL: {url}")
                
                # Send confirmation message
                self.bot.reply_to(message,
                    f"📘 Detected Facebook URL! Starting download...\n"
                    f"📹 Format: Video (best quality)\n"
                    f"🔗 URL: {url[:50]}..."
                )
                
                # Download with default settings
                self._download_facebook(message, url, "best")
        
        except Exception as e:
            self.logger.error(f"Auto Facebook handler failed: {e}")
    
    def _is_facebook_url(self, url: str) -> bool:
        """Check if URL is a valid Facebook URL"""
        facebook_patterns = [
            r'(?:https?://)?(?:www\.)?facebook\.com/watch/\?v=[\w-]+',
            r'(?:https?://)?fb\.watch/[\w-]+',
            r'(?:https?://)?(?:www\.)?facebook\.com/.*?/videos/[\w-]+',
            r'(?:https?://)?(?:www\.)?facebook\.com/video\.php\?v=[\w-]+',
        ]
        
        for pattern in facebook_patterns:
            if re.match(pattern, url, re.IGNORECASE):
                return True
        
        return False
    
    def _download_facebook(self, message, url: str, quality: str):
        """Download Facebook video"""
        try:
            # Show progress message
            status_msg = self.bot.send_message(
                message.chat.id,
                f"⏳ **Starting Facebook Download**\n\n"
                f"🔗 **URL:** {url[:50]}...\n"
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
            filename_template = "fb_%(title)s.%(ext)s"
            
            ydl_opts = {
                'outtmpl': os.path.join(self.downloads_dir, filename_template),
                'noplaylist': True,
            }
            
            # Set format based on quality
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
                f"⏳ **Facebook Download in Progress**\n\n"
                f"🔗 **URL:** {url[:50]}...\n"
                f"🎯 **Quality:** {quality}\n"
                f"📁 **Status:** Downloading...",
                message.chat.id,
                status_msg.message_id,
                parse_mode="Markdown"
            )
            
            # Download with yt-dlp
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Get video info first
                try:
                    info = ydl.extract_info(url, download=False)
                    title = info.get('title', 'Facebook Video')
                    duration = info.get('duration', 0)
                    uploader = info.get('uploader', 'Facebook')
                    
                    # Update status with video info
                    duration_str = f"{duration//60}:{duration%60:02d}" if duration else "Unknown"
                    
                    self.bot.edit_message_text(
                        f"📥 **Downloading: {title[:30]}...**\n\n"
                        f"👤 **Page:** {uploader}\n"
                        f"⏱️ **Duration:** {duration_str}\n"
                        f"🎯 **Quality:** {quality}\n"
                        f"📁 **Status:** Processing...",
                        message.chat.id,
                        status_msg.message_id,
                        parse_mode="Markdown"
                    )
                except Exception as info_error:
                    self.logger.warning(f"Could not extract video info: {info_error}")
                    title = "Facebook Video"
                    uploader = "Facebook"
                
                # Actually download
                ydl.download([url])
            
            # Find downloaded file
            downloaded_files = []
            for file in os.listdir(self.downloads_dir):
                if file.startswith('fb_') and file.endswith(('.mp4', '.webm', '.mkv')):
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
                    f"🎯 **Quality:** {quality}"
                )
                
                # Send file if small enough for Telegram (50MB limit)
                if file_size < 50 * 1024 * 1024:  # 50MB
                    try:
                        with open(file_path, 'rb') as f:
                            self.bot.send_video(
                                message.chat.id,
                                f,
                                caption=f"📘 {title}"
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
                            f"{success_msg}\n\n❌ Error sending file: {send_error}",
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
            self.logger.error(f"Facebook download failed: {e}")
            try:
                self.bot.edit_message_text(
                    f"❌ **Download failed**\n\n"
                    f"🔍 **Error:** {str(e)[:100]}...\n"
                    f"💡 Try a different URL or check the link",
                    message.chat.id,
                    status_msg.message_id,
                    parse_mode="Markdown"
                )
            except:
                self.bot.reply_to(message, f"❌ Download failed: {e}")
    
    @command(
        name="fbinfo",
        aliases=["facebook_info"],
        description="Get information about a Facebook video without downloading",
        usage="/fbinfo <url>",
        examples=["/fbinfo https://www.facebook.com/watch/?v=123456789"],
        category="Media"
    )
    def facebook_info_command(self, message):
        """Get Facebook video information"""
        try:
            args = message.text.split()[1:]
            if not args:
                self.bot.reply_to(message, "❌ Please provide a Facebook URL")
                return
            
            url = args[0]
            
            if not self._is_facebook_url(url):
                self.bot.reply_to(message, "❌ Invalid Facebook URL")
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
                uploader = info.get('uploader', 'Facebook')
                duration = info.get('duration', 0)
                view_count = info.get('view_count', 0)
                upload_date = info.get('upload_date', '')
                description = info.get('description', '')[:200] if info.get('description') else 'No description'
                
                duration_str = f"{duration//60}:{duration%60:02d}" if duration else "Unknown"
                views_str = f"{view_count:,}" if view_count else "Unknown"
                
                # Format upload date
                if upload_date and len(upload_date) == 8:
                    upload_date_formatted = f"{upload_date[:4]}-{upload_date[4:6]}-{upload_date[6:]}"
                else:
                    upload_date_formatted = "Unknown"
                
                info_text = (
                    f"📘 **Facebook Video Info**\n\n"
                    f"**Title:** {title}\n"
                    f"**Page:** {uploader}\n"
                    f"**Duration:** {duration_str}\n"
                    f"**Views:** {views_str}\n"
                    f"**Upload Date:** {upload_date_formatted}\n\n"
                    f"**Description:** {description}..."
                )
                
                self.bot.send_message(message.chat.id, info_text, parse_mode="Markdown")
        
        except Exception as e:
            self.logger.error(f"Facebook info command failed: {e}")
            self.bot.reply_to(message, f"❌ Error getting video info: {e}")
    
    def download(self, bot, message, url: str, folder: Optional[str] = None):
        """Legacy method for compatibility with old system"""
        self.logger.info(f"Legacy download method called for: {url}")
        self._download_facebook(message, url, "best")

