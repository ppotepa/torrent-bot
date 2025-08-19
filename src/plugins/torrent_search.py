"""
Torrent Search Plugin - Search and download torrents via qBittorrent
"""

import os
import re
import json
from typing import List, Dict, Any, Optional

from core import PluginBase, plugin_info, command, callback_query, startup_task, CommandScope, PermissionLevel


@plugin_info(
    name="Torrent Search",
    version="1.0.0",
    author="TorrentBot",
    description="Search and download torrents using qBittorrent and Jackett",
    dependencies=["requests"],
    enabled=True
)
class TorrentSearchPlugin(PluginBase):
    """Plugin for torrent search and download functionality"""
    
    def __init__(self, bot, logger=None):
        super().__init__(bot, logger)
        self.search_cache = {}  # Cache search results per user
        self.qbittorrent_available = False
        self.jackett_available = False
    
    def get_plugin_description(self) -> str:
        return "Search torrents via Jackett and download through qBittorrent with rich result formatting"
    
    @startup_task(priority=2)
    def initialize_torrent_services(self):
        """Initialize torrent services and check availability"""
        self.logger.info("Initializing torrent services...")
        
        # Check qBittorrent availability
        try:
            import requests
            qbit_url = os.getenv("QBITTORRENT_URL", "http://localhost:8080")
            response = requests.get(f"{qbit_url}/api/v2/app/version", timeout=5)
            if response.status_code == 200:
                self.qbittorrent_available = True
                self.logger.info("✅ qBittorrent available")
            else:
                self.logger.warning("❌ qBittorrent not responding")
        except Exception as e:
            self.logger.warning(f"qBittorrent check failed: {e}")
        
        # Check Jackett availability  
        try:
            jackett_url = os.getenv("JACKETT_URL", "http://localhost:9117")
            jackett_key = os.getenv("JACKETT_API_KEY", "")
            if jackett_key:
                response = requests.get(f"{jackett_url}/api/v2.0/indexers", 
                                      params={"apikey": jackett_key}, timeout=5)
                if response.status_code == 200:
                    self.jackett_available = True
                    self.logger.info("✅ Jackett available")
                else:
                    self.logger.warning("❌ Jackett not responding")
            else:
                self.logger.warning("❌ Jackett API key not configured")
        except Exception as e:
            self.logger.warning(f"Jackett check failed: {e}")
        
        if not self.qbittorrent_available or not self.jackett_available:
            self.logger.warning("Some torrent services are unavailable - functionality will be limited")
    
    @command(
        name="torrent",
        aliases=["t", "search"],
        description="Search for torrents",
        usage="/torrent <query> [flags]",
        examples=[
            "/torrent ubuntu",
            "/torrent movie 2023 [rich]",
            "/torrent music album [all]"
        ],
        flags=["rich", "all", "music", "notify", "silent"],
        category="Torrents"
    )
    def torrent_search_command(self, message):
        """Handle torrent search command"""
        try:
            args = message.text.split()[1:]
            if not args:
                self._show_torrent_help(message)
                return
            
            # Parse query and flags
            query_parts = []
            flags = []
            
            for arg in args:
                if arg.startswith('[') and arg.endswith(']'):
                    # Flag format: [rich]
                    flags.append(arg[1:-1].lower())
                elif '[' in arg and ']' in arg:
                    # Flag format: word[rich]
                    parts = arg.split('[')
                    query_parts.append(parts[0])
                    flag_part = parts[1].rstrip(']')
                    flags.extend(f.strip().lower() for f in flag_part.split(','))
                else:
                    query_parts.append(arg)
            
            query = ' '.join(query_parts).strip()
            
            if not query:
                self._show_torrent_help(message)
                return
            
            # Check service availability
            if not self.jackett_available:
                self.bot.reply_to(message, "❌ Torrent search unavailable - Jackett not configured")
                return
            
            # Process flags
            rich_mode = 'rich' in flags
            all_mode = 'all' in flags  
            music_mode = 'music' in flags
            notify = 'notify' in flags
            
            # Start search
            self._start_torrent_search(message, query, rich_mode, all_mode, music_mode, notify)
            
        except Exception as e:
            self.logger.error(f"Torrent search command failed: {e}")
            self.bot.reply_to(message, f"❌ Search error: {e}")
    
    @command(
        name="downloads",
        aliases=["d", "dl_status"],
        description="Show active downloads",
        usage="/downloads [filter]",
        examples=[
            "/downloads",
            "/downloads active",
            "/downloads completed"
        ],
        flags=["active", "completed", "paused", "seeding"],
        category="Torrents"
    )
    def downloads_command(self, message):
        """Show download status"""
        try:
            if not self.qbittorrent_available:
                self.bot.reply_to(message, "❌ Downloads unavailable - qBittorrent not configured")
                return
            
            args = message.text.split()[1:]
            filter_type = args[0].lower() if args else "all"
            
            downloads_info = self._get_downloads_info(filter_type)
            
            if downloads_info:
                self.bot.send_message(message.chat.id, downloads_info, parse_mode="Markdown")
            else:
                self.bot.reply_to(message, f"📁 No downloads found (filter: {filter_type})")
                
        except Exception as e:
            self.logger.error(f"Downloads command failed: {e}")
            self.bot.reply_to(message, f"❌ Error getting downloads: {e}")
    
    @command(
        name="tdiag",
        aliases=["torrent_diag"],
        description="Run torrent system diagnostics",
        usage="/tdiag",
        category="Torrents",
        permission=PermissionLevel.ADMIN
    )
    def torrent_diagnostics_command(self, message):
        """Run torrent diagnostics"""
        try:
            self.bot.send_message(message.chat.id, "🔍 Running torrent diagnostics...")
            
            diag_info = self._run_diagnostics()
            
            # Split long messages
            if len(diag_info) > 4000:
                parts = [diag_info[i:i+3900] for i in range(0, len(diag_info), 3900)]
                for i, part in enumerate(parts):
                    if i == 0:
                        self.bot.send_message(message.chat.id, part, parse_mode="Markdown")
                    else:
                        self.bot.send_message(message.chat.id, f"🔍 Diagnostics (part {i+1}):\n{part}", parse_mode="Markdown")
            else:
                self.bot.send_message(message.chat.id, diag_info, parse_mode="Markdown")
                
        except Exception as e:
            self.logger.error(f"Torrent diagnostics failed: {e}")
            self.bot.reply_to(message, f"❌ Diagnostics failed: {e}")
    
    @callback_query(
        pattern="torrent_",
        description="Handle torrent selection callbacks"
    )
    def torrent_callback_handler(self, call):
        """Handle torrent selection from inline buttons"""
        try:
            data = call.data
            user_id = call.from_user.id
            
            if data.startswith("torrent_select_"):
                # Extract selection index
                index = int(data.split("_")[-1])
                
                # Get cached search results
                if user_id not in self.search_cache:
                    self.bot.answer_callback_query(call.id, "❌ Search results expired")
                    return
                
                results = self.search_cache[user_id]["results"]
                if index >= len(results):
                    self.bot.answer_callback_query(call.id, "❌ Invalid selection")
                    return
                
                selected_result = results[index]
                
                # Start download
                self._download_torrent(call.message, selected_result, user_id)
                self.bot.answer_callback_query(call.id, "⏳ Starting download...")
                
            elif data == "torrent_cancel":
                # Cancel search
                if user_id in self.search_cache:
                    del self.search_cache[user_id]
                
                self.bot.edit_message_text(
                    "❌ Search cancelled",
                    call.message.chat.id,
                    call.message.message_id
                )
                self.bot.answer_callback_query(call.id, "Search cancelled")
                
        except Exception as e:
            self.logger.error(f"Torrent callback failed: {e}")
            self.bot.answer_callback_query(call.id, f"❌ Error: {e}")
    
    def _start_torrent_search(self, message, query: str, rich_mode: bool = False, 
                            all_mode: bool = False, music_mode: bool = False, notify: bool = False):
        """Start torrent search"""
        try:
            # Show search status
            status_msg = self.bot.send_message(
                message.chat.id,
                f"🔍 **Searching torrents...**\n\n"
                f"📝 **Query:** {query}\n"
                f"🎯 **Mode:** {'Rich' if rich_mode else 'All' if all_mode else 'Music' if music_mode else 'Normal'}\n"
                f"📡 **Status:** Contacting indexers...",
                parse_mode="Markdown"
            )
            
            # Perform search
            results = self._search_torrents(query, all_mode, music_mode)
            
            if not results:
                self.bot.edit_message_text(
                    f"❌ **No results found**\n\n"
                    f"📝 **Query:** {query}\n"
                    f"💡 Try different keywords or use `[all]` flag",
                    message.chat.id,
                    status_msg.message_id,
                    parse_mode="Markdown"
                )
                return
            
            # Cache results
            user_id = message.from_user.id
            self.search_cache[user_id] = {
                "results": results,
                "query": query,
                "timestamp": message.date
            }
            
            # Format and send results
            if rich_mode:
                self._send_rich_results(message, status_msg, results, query)
            else:
                self._send_simple_results(message, status_msg, results, query)
            
        except Exception as e:
            self.logger.error(f"Torrent search failed: {e}")
            try:
                self.bot.edit_message_text(
                    f"❌ **Search failed**\n\n"
                    f"🔍 **Error:** {str(e)[:100]}...\n"
                    f"💡 Try again or check diagnostics with `/tdiag`",
                    message.chat.id,
                    status_msg.message_id,
                    parse_mode="Markdown"
                )
            except:
                self.bot.reply_to(message, f"❌ Search failed: {e}")
    
    def _search_torrents(self, query: str, all_mode: bool = False, music_mode: bool = False) -> List[Dict[str, Any]]:
        """Search torrents via Jackett"""
        try:
            import requests
            
            jackett_url = os.getenv("JACKETT_URL", "http://localhost:9117")
            jackett_key = os.getenv("JACKETT_API_KEY", "")
            
            # Build search parameters
            params = {
                "apikey": jackett_key,
                "Query": query,
                "Category[]": "2000" if music_mode else "5000"  # Music vs Movies/TV
            }
            
            if all_mode:
                # Search all indexers
                search_url = f"{jackett_url}/api/v2.0/indexers/all/results"
            else:
                # Search configured indexers only
                search_url = f"{jackett_url}/api/v2.0/indexers/configured/results"
            
            response = requests.get(search_url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            results = data.get("Results", [])
            
            # Sort by seeders (descending)
            results.sort(key=lambda x: x.get("Seeders", 0), reverse=True)
            
            # Limit results
            return results[:20]
            
        except Exception as e:
            self.logger.error(f"Jackett search failed: {e}")
            raise
    
    def _send_simple_results(self, message, status_msg, results: List[Dict[str, Any]], query: str):
        """Send simple text results"""
        try:
            results_text = f"🔍 **Search Results for:** `{query}`\n"
            results_text += f"📊 **Found:** {len(results)} torrents\n\n"
            
            for i, result in enumerate(results[:10], 1):
                title = result.get("Title", "Unknown")[:50]
                size = result.get("Size", 0)
                seeders = result.get("Seeders", 0)
                leechers = result.get("Leechers", 0)
                
                # Format size
                size_mb = size / (1024 * 1024) if size > 0 else 0
                if size_mb > 1024:
                    size_str = f"{size_mb/1024:.1f} GB"
                else:
                    size_str = f"{size_mb:.0f} MB"
                
                # Quality indicators
                if seeders > 50:
                    quality = "🔥"
                elif seeders > 10:
                    quality = "⭐"
                elif seeders > 0:
                    quality = "✅"
                else:
                    quality = "⚠️"
                
                results_text += f"{quality} **{i}.** {title}...\n"
                results_text += f"   📦 {size_str} | 🌱 {seeders} | 📥 {leechers}\n\n"
            
            results_text += "💡 **To download:** Reply with number (1-10)"
            
            # Update status message
            self.bot.edit_message_text(
                results_text,
                message.chat.id,
                status_msg.message_id,
                parse_mode="Markdown"
            )
            
        except Exception as e:
            self.logger.error(f"Error sending simple results: {e}")
            raise
    
    def _send_rich_results(self, message, status_msg, results: List[Dict[str, Any]], query: str):
        """Send rich results with inline buttons"""
        try:
            from telebot import types
            
            results_text = f"🔍 **Rich Search Results**\n\n"
            results_text += f"📝 **Query:** `{query}`\n"
            results_text += f"📊 **Found:** {len(results)} torrents\n\n"
            
            # Create inline keyboard
            markup = types.InlineKeyboardMarkup(row_width=2)
            
            for i, result in enumerate(results[:5], 0):  # Show top 5
                title = result.get("Title", "Unknown")[:30]
                size = result.get("Size", 0)
                seeders = result.get("Seeders", 0)
                
                # Format button text
                size_mb = size / (1024 * 1024) if size > 0 else 0
                if size_mb > 1024:
                    size_str = f"{size_mb/1024:.1f}GB"
                else:
                    size_str = f"{size_mb:.0f}MB"
                
                button_text = f"🔥 {title}... ({size_str}, {seeders}🌱)"
                callback_data = f"torrent_select_{i}"
                
                markup.add(types.InlineKeyboardButton(button_text, callback_data=callback_data))
            
            # Add cancel button
            markup.add(types.InlineKeyboardButton("❌ Cancel", callback_data="torrent_cancel"))
            
            # Update message with buttons
            self.bot.edit_message_text(
                results_text,
                message.chat.id,
                status_msg.message_id,
                parse_mode="Markdown",
                reply_markup=markup
            )
            
        except Exception as e:
            self.logger.error(f"Error sending rich results: {e}")
            # Fallback to simple results
            self._send_simple_results(message, status_msg, results, query)
    
    def _download_torrent(self, message, torrent_result: Dict[str, Any], user_id: int):
        """Download selected torrent"""
        try:
            if not self.qbittorrent_available:
                self.bot.reply_to(message, "❌ Download unavailable - qBittorrent not configured")
                return
            
            import requests
            
            # Get torrent details
            title = torrent_result.get("Title", "Unknown")
            magnet_link = torrent_result.get("MagnetUri", "")
            torrent_link = torrent_result.get("Link", "")
            
            if not magnet_link and not torrent_link:
                self.bot.reply_to(message, "❌ No download link available")
                return
            
            # Try magnet link first, then torrent file
            download_url = magnet_link if magnet_link else torrent_link
            
            # Add to qBittorrent
            qbit_url = os.getenv("QBITTORRENT_URL", "http://localhost:8080")
            qbit_user = os.getenv("QBITTORRENT_USER", "admin")
            qbit_pass = os.getenv("QBITTORRENT_PASS", "adminadmin")
            
            # Login to qBittorrent
            session = requests.Session()
            login_data = {"username": qbit_user, "password": qbit_pass}
            session.post(f"{qbit_url}/api/v2/auth/login", data=login_data)
            
            # Add torrent
            add_data = {"urls": download_url}
            response = session.post(f"{qbit_url}/api/v2/torrents/add", data=add_data)
            
            if response.status_code == 200:
                success_msg = (
                    f"✅ **Download Started**\n\n"
                    f"📁 **Name:** {title[:50]}...\n"
                    f"🔗 **Type:** {'Magnet' if magnet_link else 'Torrent file'}\n"
                    f"👤 **User:** {user_id}\n"
                    f"📊 **Status:** Added to queue"
                )
                
                self.bot.send_message(message.chat.id, success_msg, parse_mode="Markdown")
                
                # Clean up search cache
                if user_id in self.search_cache:
                    del self.search_cache[user_id]
                
            else:
                self.bot.reply_to(message, f"❌ Failed to add torrent (status: {response.status_code})")
            
        except Exception as e:
            self.logger.error(f"Torrent download failed: {e}")
            self.bot.reply_to(message, f"❌ Download failed: {e}")
    
    def _get_downloads_info(self, filter_type: str = "all") -> Optional[str]:
        """Get current downloads information"""
        try:
            import requests
            
            qbit_url = os.getenv("QBITTORRENT_URL", "http://localhost:8080")
            qbit_user = os.getenv("QBITTORRENT_USER", "admin")
            qbit_pass = os.getenv("QBITTORRENT_PASS", "adminadmin")
            
            # Login
            session = requests.Session()
            login_data = {"username": qbit_user, "password": qbit_pass}
            session.post(f"{qbit_url}/api/v2/auth/login", data=login_data)
            
            # Get torrents
            params = {}
            if filter_type != "all":
                params["filter"] = filter_type
            
            response = session.get(f"{qbit_url}/api/v2/torrents/info", params=params)
            torrents = response.json()
            
            if not torrents:
                return None
            
            info_text = f"📁 **Downloads ({filter_type.title()}): {len(torrents)}**\n\n"
            
            for torrent in torrents[:10]:  # Show max 10
                name = torrent.get("name", "Unknown")[:40]
                progress = torrent.get("progress", 0) * 100
                state = torrent.get("state", "unknown")
                size = torrent.get("size", 0)
                
                # Format size
                size_gb = size / (1024**3) if size > 0 else 0
                
                # State emoji
                state_emoji = {
                    "downloading": "⬇️",
                    "uploading": "⬆️", 
                    "seeding": "🌱",
                    "completed": "✅",
                    "paused": "⏸️",
                    "error": "❌"
                }.get(state, "❓")
                
                info_text += f"{state_emoji} **{name}...**\n"
                info_text += f"   📊 {progress:.1f}% | 📦 {size_gb:.1f} GB | 🔄 {state}\n\n"
            
            return info_text
            
        except Exception as e:
            self.logger.error(f"Error getting downloads info: {e}")
            return f"❌ Error getting downloads: {e}"
    
    def _run_diagnostics(self) -> str:
        """Run torrent system diagnostics"""
        try:
            diag_text = "🔍 **Torrent System Diagnostics**\n\n"
            
            # Check qBittorrent
            diag_text += "**qBittorrent:**\n"
            if self.qbittorrent_available:
                diag_text += "✅ Available\n"
                qbit_url = os.getenv("QBITTORRENT_URL", "http://localhost:8080")
                diag_text += f"🔗 URL: {qbit_url}\n"
            else:
                diag_text += "❌ Not available\n"
                diag_text += "💡 Check QBITTORRENT_URL environment variable\n"
            
            # Check Jackett
            diag_text += "\n**Jackett:**\n"
            if self.jackett_available:
                diag_text += "✅ Available\n"
                jackett_url = os.getenv("JACKETT_URL", "http://localhost:9117")
                diag_text += f"🔗 URL: {jackett_url}\n"
            else:
                diag_text += "❌ Not available\n"
                diag_text += "💡 Check JACKETT_URL and JACKETT_API_KEY\n"
            
            # Environment variables
            diag_text += "\n**Environment Variables:**\n"
            env_vars = [
                "QBITTORRENT_URL", "QBITTORRENT_USER", "QBITTORRENT_PASS",
                "JACKETT_URL", "JACKETT_API_KEY"
            ]
            
            for var in env_vars:
                value = os.getenv(var, "")
                status = "✅" if value else "❌"
                masked_value = "***" if value and "PASS" in var or "KEY" in var else value
                diag_text += f"{status} {var}: {masked_value or 'Not set'}\n"
            
            # Search cache
            diag_text += f"\n**Search Cache:**\n"
            diag_text += f"📊 Active searches: {len(self.search_cache)}\n"
            
            return diag_text
            
        except Exception as e:
            return f"❌ Diagnostics error: {e}"
    
    def _show_torrent_help(self, message):
        """Show torrent help message"""
        help_text = """🔍 **Torrent Search Commands**

🎯 **Basic Search:**
• `/torrent <query>` - Search torrents
• `/torrent ubuntu` - Simple search
• `/torrent movie 2023 [rich]` - Rich results with buttons

🎛️ **Search Flags:**
• `[rich]` - Rich results with inline buttons
• `[all]` - Search ALL indexers (slower)
• `[music]` - Music-focused search
• `[notify]` - Get notification when download completes

📊 **Other Commands:**
• `/downloads` - Show active downloads
• `/downloads active` - Show only active downloads
• `/tdiag` - Run system diagnostics (admin only)

📝 **Examples:**
• `/torrent linux distro`
• `/torrent "movie title" [rich,notify]`
• `/torrent album artist [music,all]`

💡 **Tips:**
• Use quotes for exact phrases
• Numbers 1-10 select results after search
• Rich mode shows top 5 with buttons"""
        
        self.bot.send_message(message.chat.id, help_text, parse_mode="Markdown")

