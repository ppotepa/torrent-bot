"""
System Information Plugin - Shows system stats and diagnostics
"""

import psutil
import platform
import os
import shutil
from datetime import datetime
from typing import Optional

from core import PluginBase, plugin_info, command, CommandScope, PermissionLevel


@plugin_info(
    name="System Info",
    version="1.0.0",
    author="TorrentBot",
    description="Provides system information and diagnostics",
    dependencies=["psutil"],
    enabled=True
)
class SystemInfoPlugin(PluginBase):
    """Plugin for system information and diagnostics"""
    
    def get_plugin_description(self) -> str:
        return "Shows system information including CPU, memory, disk usage, and network stats"
    
    @command(
        name="sysinfo",
        aliases=["si", "system"],
        description="Show system information",
        usage="/sysinfo [brief|detailed|cpu|memory|disk|network]",
        examples=[
            "/sysinfo",
            "/sysinfo brief",
            "/sysinfo detailed",
            "/sysinfo cpu"
        ],
        flags=["brief", "detailed", "cpu", "memory", "disk", "network"],
        category="System",
        permission=PermissionLevel.ADMIN
    )
    def system_info_command(self, message):
        """Handle system info command"""
        try:
            # Parse command arguments
            args = message.text.split()[1:] if len(message.text.split()) > 1 else []
            mode = args[0].lower() if args else "normal"
            
            if mode == "brief":
                info = self._get_brief_info()
            elif mode == "detailed":
                info = self._get_detailed_info()
            elif mode == "cpu":
                info = self._get_cpu_info()
            elif mode == "memory":
                info = self._get_memory_info()
            elif mode == "disk":
                info = self._get_disk_info()
            elif mode == "network":
                info = self._get_network_info()
            else:
                info = self._get_normal_info()
            
            # Split message if too long
            if len(info) > 4000:
                parts = [info[i:i+3900] for i in range(0, len(info), 3900)]
                for i, part in enumerate(parts):
                    if i == 0:
                        self.bot.send_message(message.chat.id, part, parse_mode="Markdown")
                    else:
                        self.bot.send_message(message.chat.id, f"📊 System Info (part {i+1}):\n{part}", parse_mode="Markdown")
            else:
                self.bot.send_message(message.chat.id, info, parse_mode="Markdown")
                
        except Exception as e:
            self.logger.error(f"System info command failed: {e}")
            self.bot.reply_to(message, f"❌ Error getting system info: {e}")
    
    @command(
        name="uptime",
        description="Show system uptime",
        usage="/uptime",
        category="System",
        permission=PermissionLevel.ADMIN
    )
    def uptime_command(self, message):
        """Show system uptime"""
        try:
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            current_time = datetime.now()
            uptime_delta = current_time - boot_time
            
            days = uptime_delta.days
            hours, remainder = divmod(uptime_delta.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            
            uptime_text = f"🕐 **System Uptime**\n\n"
            uptime_text += f"**Boot time:** {boot_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            uptime_text += f"**Uptime:** {days} days, {hours} hours, {minutes} minutes, {seconds} seconds"
            
            self.bot.send_message(message.chat.id, uptime_text, parse_mode="Markdown")
            
        except Exception as e:
            self.logger.error(f"Uptime command failed: {e}")
            self.bot.reply_to(message, f"❌ Error getting uptime: {e}")
    
    def _get_brief_info(self) -> str:
        """Get brief system information"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            
            info = f"📊 **Brief System Info**\n\n"
            info += f"💻 **CPU:** {cpu_percent:.1f}%\n"
            info += f"🧠 **Memory:** {memory_percent:.1f}%\n"
            info += f"💾 **Disk:** {disk_percent:.1f}%\n"
            info += f"🖥️ **OS:** {platform.system()} {platform.release()}"
            
            return info
            
        except Exception as e:
            return f"❌ Error getting brief info: {e}"
    
    def _get_normal_info(self) -> str:
        """Get normal system information"""
        try:
            # System info
            system_info = f"🖥️ **System:** {platform.system()} {platform.release()} ({platform.machine()})\n"
            system_info += f"🐍 **Python:** {platform.python_version()}\n"
            
            # CPU info
            cpu_count = psutil.cpu_count()
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_info = f"💻 **CPU:** {cpu_count} cores, {cpu_percent:.1f}% usage\n"
            
            # Memory info
            memory = psutil.virtual_memory()
            memory_gb = memory.total / (1024**3)
            memory_used_gb = memory.used / (1024**3)
            memory_info = f"🧠 **Memory:** {memory_used_gb:.1f}GB / {memory_gb:.1f}GB ({memory.percent:.1f}%)\n"
            
            # Disk info
            disk = psutil.disk_usage('/')
            disk_total_gb = disk.total / (1024**3)
            disk_used_gb = disk.used / (1024**3)
            disk_free_gb = disk.free / (1024**3)
            disk_percent = (disk.used / disk.total) * 100
            disk_info = f"💾 **Disk:** {disk_used_gb:.1f}GB / {disk_total_gb:.1f}GB ({disk_percent:.1f}% used, {disk_free_gb:.1f}GB free)\n"
            
            info = f"📊 **System Information**\n\n{system_info}{cpu_info}{memory_info}{disk_info}"
            
            return info
            
        except Exception as e:
            return f"❌ Error getting system info: {e}"
    
    def _get_detailed_info(self) -> str:
        """Get detailed system information"""
        try:
            info = self._get_normal_info()
            
            # Add more detailed information
            
            # Network interfaces
            try:
                network_info = "\n🌐 **Network Interfaces:**\n"
                for interface, addrs in psutil.net_if_addrs().items():
                    if interface != 'lo':  # Skip loopback
                        for addr in addrs:
                            if addr.family == 2:  # IPv4
                                network_info += f"• {interface}: {addr.address}\n"
                info += network_info
            except:
                pass
            
            # Load averages (Unix only)
            try:
                if hasattr(os, 'getloadavg'):
                    load1, load5, load15 = os.getloadavg()
                    info += f"\n📈 **Load Average:** {load1:.2f}, {load5:.2f}, {load15:.2f}\n"
            except:
                pass
            
            # Process count
            try:
                process_count = len(psutil.pids())
                info += f"⚙️ **Processes:** {process_count}\n"
            except:
                pass
            
            return info
            
        except Exception as e:
            return f"❌ Error getting detailed info: {e}"
    
    def _get_cpu_info(self) -> str:
        """Get CPU information"""
        try:
            cpu_count_logical = psutil.cpu_count()
            cpu_count_physical = psutil.cpu_count(logical=False)
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_freq = psutil.cpu_freq()
            
            info = f"💻 **CPU Information**\n\n"
            info += f"**Physical cores:** {cpu_count_physical}\n"
            info += f"**Logical cores:** {cpu_count_logical}\n"
            info += f"**Usage:** {cpu_percent:.1f}%\n"
            
            if cpu_freq:
                info += f"**Frequency:** {cpu_freq.current:.2f} MHz (max: {cpu_freq.max:.2f} MHz)\n"
            
            # Per-core usage
            cpu_per_core = psutil.cpu_percent(percpu=True)
            info += f"\n**Per-core usage:**\n"
            for i, usage in enumerate(cpu_per_core):
                info += f"Core {i}: {usage:.1f}%\n"
            
            return info
            
        except Exception as e:
            return f"❌ Error getting CPU info: {e}"
    
    def _get_memory_info(self) -> str:
        """Get memory information"""
        try:
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            info = f"🧠 **Memory Information**\n\n"
            info += f"**Total:** {memory.total / (1024**3):.1f} GB\n"
            info += f"**Available:** {memory.available / (1024**3):.1f} GB\n"
            info += f"**Used:** {memory.used / (1024**3):.1f} GB ({memory.percent:.1f}%)\n"
            info += f"**Free:** {memory.free / (1024**3):.1f} GB\n"
            
            if swap.total > 0:
                info += f"\n**Swap Total:** {swap.total / (1024**3):.1f} GB\n"
                info += f"**Swap Used:** {swap.used / (1024**3):.1f} GB ({swap.percent:.1f}%)\n"
                info += f"**Swap Free:** {swap.free / (1024**3):.1f} GB\n"
            
            return info
            
        except Exception as e:
            return f"❌ Error getting memory info: {e}"
    
    def _get_disk_info(self) -> str:
        """Get disk information"""
        try:
            info = f"💾 **Disk Information**\n\n"
            
            # Get all disk partitions
            partitions = psutil.disk_partitions()
            
            for partition in partitions:
                try:
                    partition_usage = psutil.disk_usage(partition.mountpoint)
                    
                    info += f"**{partition.device}** ({partition.fstype})\n"
                    info += f"  Mount: {partition.mountpoint}\n"
                    info += f"  Total: {partition_usage.total / (1024**3):.1f} GB\n"
                    info += f"  Used: {partition_usage.used / (1024**3):.1f} GB\n"
                    info += f"  Free: {partition_usage.free / (1024**3):.1f} GB\n"
                    info += f"  Usage: {(partition_usage.used / partition_usage.total) * 100:.1f}%\n\n"
                    
                except PermissionError:
                    info += f"**{partition.device}** - Permission denied\n\n"
            
            return info
            
        except Exception as e:
            return f"❌ Error getting disk info: {e}"
    
    def _get_network_info(self) -> str:
        """Get network information"""
        try:
            info = f"🌐 **Network Information**\n\n"
            
            # Network I/O statistics
            net_io = psutil.net_io_counters()
            info += f"**Total bytes sent:** {net_io.bytes_sent / (1024**2):.1f} MB\n"
            info += f"**Total bytes received:** {net_io.bytes_recv / (1024**2):.1f} MB\n"
            info += f"**Packets sent:** {net_io.packets_sent:,}\n"
            info += f"**Packets received:** {net_io.packets_recv:,}\n\n"
            
            # Network interfaces
            info += "**Interfaces:**\n"
            for interface, addrs in psutil.net_if_addrs().items():
                info += f"**{interface}:**\n"
                for addr in addrs:
                    if addr.family == 2:  # IPv4
                        info += f"  IPv4: {addr.address}\n"
                    elif addr.family == 10:  # IPv6
                        info += f"  IPv6: {addr.address}\n"
                info += "\n"
            
            return info
            
        except Exception as e:
            return f"❌ Error getting network info: {e}"

