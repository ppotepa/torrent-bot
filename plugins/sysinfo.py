"""
System Information plugin for the bot.
Provides comprehensive system information via /si command.
"""

import os
import platform
import socket
import datetime
from pathlib import Path

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("Warning: psutil not available. System info will be limited.")


def get_basic_system_info():
    """Get basic system info without psutil."""
    info = {
        'system': {
            'platform': platform.system(),
            'platform_release': platform.release(),
            'platform_version': platform.version(),
            'architecture': platform.machine(),
            'hostname': platform.node(),
            'processor': platform.processor(),
            'python_version': platform.python_version()
        },
        'bot_info': {
            'working_directory': os.getcwd(),
            'python_executable': os.sys.executable,
            'user': os.getenv('USER', os.getenv('USERNAME', 'unknown'))
        }
    }
    
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        info['network'] = {
            'hostname': hostname,
            'local_ip': local_ip
        }
    except Exception as e:
        info['network'] = {'error': str(e)}
    
    return info


def get_system_info():
    """Gather comprehensive system information."""
    try:
        if not PSUTIL_AVAILABLE:
            return get_basic_system_info()
            
        info = {
            'system': {},
            'hardware': {},
            'network': {},
            'storage': {},
            'processes': {},
            'bot_info': {}
        }
        
        # System Information
        info['system'] = {
            'platform': platform.system(),
            'platform_release': platform.release(),
            'platform_version': platform.version(),
            'architecture': platform.machine(),
            'hostname': platform.node(),
            'processor': platform.processor(),
            'python_version': platform.python_version(),
            'boot_time': datetime.datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Hardware Information
        memory = psutil.virtual_memory()
        info['hardware'] = {
            'cpu_count': psutil.cpu_count(),
            'cpu_count_physical': psutil.cpu_count(logical=False),
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_total': memory.total,
            'memory_available': memory.available,
            'memory_used': memory.used,
            'memory_percent': memory.percent
        }
        
        # Network Information
        try:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            info['network'] = {
                'hostname': hostname,
                'local_ip': local_ip,
                'network_interfaces': len(psutil.net_if_addrs())
            }
        except Exception as e:
            info['network'] = {'error': str(e)}
        
        # Storage Information
        storage_info = []
        for partition in psutil.disk_partitions():
            try:
                partition_usage = psutil.disk_usage(partition.mountpoint)
                storage_info.append({
                    'device': partition.device,
                    'mountpoint': partition.mountpoint,
                    'file_system': partition.fstype,
                    'total': partition_usage.total,
                    'used': partition_usage.used,
                    'free': partition_usage.free,
                    'percent': round((partition_usage.used / partition_usage.total) * 100, 2)
                })
            except PermissionError:
                continue
        info['storage'] = storage_info
        
        # Process Information
        process_count = len(psutil.pids())
        info['processes'] = {
            'total_processes': process_count,
            'running_user': os.getenv('USER', os.getenv('USERNAME', 'unknown'))
        }
        
        # Bot-specific Information
        try:
            bot_dir = Path(__file__).parent.parent.parent
            info['bot_info'] = {
                'bot_directory': str(bot_dir.absolute()),
                'working_directory': os.getcwd(),
                'python_executable': os.sys.executable
            }
        except Exception as e:
            info['bot_info'] = {'error': str(e)}
            
        return info
        
    except Exception as e:
        return {'error': f"Failed to gather system info: {str(e)}"}


def format_bytes(bytes_value):
    """Convert bytes to human readable format."""
    if bytes_value == 0:
        return "0 B"
    
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    size = float(bytes_value)
    unit_index = 0
    
    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024.0
        unit_index += 1
    
    return f"{size:.2f} {units[unit_index]}"


def format_system_info(info):
    """Format system information for display."""
    if 'error' in info:
        return f"❌ Error gathering system info: {info['error']}"
    
    lines = []
    
    # Header
    lines.append("🖥️ <b>System Information</b>")
    lines.append("=" * 30)
    
    # Check if this is basic info (no psutil)
    if not PSUTIL_AVAILABLE:
        lines.append("⚠️ <i>Limited info - psutil not available</i>")
        lines.append("")
    
    # System Details
    sys_info = info.get('system', {})
    lines.append(f"<b>🔧 System Details:</b>")
    lines.append(f"• <b>Platform</b>: {_escape_html(sys_info.get('platform', 'Unknown'))} {_escape_html(sys_info.get('platform_release', ''))}")
    lines.append(f"• <b>Architecture</b>: {_escape_html(sys_info.get('architecture', 'Unknown'))}")
    lines.append(f"• <b>Hostname</b>: {_escape_html(sys_info.get('hostname', 'Unknown'))}")
    lines.append(f"• <b>Processor</b>: {_escape_html(sys_info.get('processor', 'Unknown'))}")
    lines.append(f"• <b>Python</b>: {_escape_html(sys_info.get('python_version', 'Unknown'))}")
    if 'boot_time' in sys_info:
        lines.append(f"• <b>Boot Time</b>: {_escape_html(sys_info.get('boot_time', 'Unknown'))}")
    lines.append("")
    
    # Hardware Information
    hw_info = info.get('hardware', {})
    if hw_info:  # Only show if psutil is available
        lines.append(f"<b>⚙️ Hardware:</b>")
        lines.append(f"• <b>CPU Cores</b>: {hw_info.get('cpu_count', 'Unknown')} logical, {hw_info.get('cpu_count_physical', 'Unknown')} physical")
        lines.append(f"• <b>CPU Usage</b>: {hw_info.get('cpu_percent', 0):.1f}%")
        
        if 'memory_total' in hw_info:
            total_mem = format_bytes(hw_info['memory_total'])
            used_mem = format_bytes(hw_info['memory_used'])
            available_mem = format_bytes(hw_info['memory_available'])
            mem_percent = hw_info.get('memory_percent', 0)
            lines.append(f"• <b>Memory</b>: {used_mem} / {total_mem} ({mem_percent:.1f}% used)")
            lines.append(f"• <b>Available</b>: {available_mem}")
        lines.append("")
    
    # Network Information
    net_info = info.get('network', {})
    if 'error' not in net_info:
        lines.append(f"<b>🌐 Network:</b>")
        lines.append(f"• <b>Hostname</b>: {_escape_html(net_info.get('hostname', 'Unknown'))}")
        lines.append(f"• <b>Local IP</b>: {_escape_html(net_info.get('local_ip', 'Unknown'))}")
        lines.append(f"• <b>Interfaces</b>: {_escape_html(str(net_info.get('network_interfaces', 'Unknown')))}")
        lines.append("")
    
    # Storage Information
    storage_info = info.get('storage', [])
    if storage_info:  # Only show if psutil is available
        lines.append(f"<b>💾 Storage:</b>")
        for storage in storage_info[:5]:  # Limit to first 5 drives
            device = _escape_html(storage.get('device', 'Unknown'))
            mountpoint = _escape_html(storage.get('mountpoint', 'Unknown'))
            file_system = _escape_html(storage.get('file_system', 'Unknown'))
            
            if 'total' in storage:
                total = format_bytes(storage['total'])
                used = format_bytes(storage['used'])
                free = format_bytes(storage['free'])
                percent = storage.get('percent', 0)
                lines.append(f"• <b>{device}</b> ({file_system})")
                lines.append(f"  📁 {mountpoint}")
                lines.append(f"  📊 {used} / {total} ({percent:.1f}% used)")
                lines.append(f"  💿 {free} free")
            else:
                lines.append(f"• <b>{device}</b> ({file_system}) - {mountpoint}")
        lines.append("")
    
    # Process Information
    proc_info = info.get('processes', {})
    if proc_info:  # Only show if psutil is available
        lines.append(f"<b>⚡ Processes:</b>")
        lines.append(f"• <b>Total Processes</b>: {proc_info.get('total_processes', 'Unknown')}")
        lines.append(f"• <b>Running as</b>: {_escape_html(proc_info.get('running_user', 'Unknown'))}")
        lines.append("")
    
    # Bot Information
    bot_info = info.get('bot_info', {})
    if 'error' not in bot_info:
        lines.append(f"<b>🤖 Bot Information:</b>")
        if 'bot_directory' in bot_info:
            lines.append(f"• <b>Bot Directory</b>: <code>{_escape_html(bot_info.get('bot_directory', 'Unknown'))}</code>")
        lines.append(f"• <b>Working Directory</b>: <code>{_escape_html(bot_info.get('working_directory', 'Unknown'))}</code>")
        lines.append(f"• <b>Python Executable</b>: <code>{_escape_html(bot_info.get('python_executable', 'Unknown'))}</code>")
        if 'user' in bot_info:
            lines.append(f"• <b>Running as</b>: {_escape_html(bot_info.get('user', 'Unknown'))}")
    
    # Footer
    lines.append("")
    if PSUTIL_AVAILABLE:
        lines.append("📊 <i>System information gathered successfully</i>")
    else:
        lines.append("📊 <i>Basic system information (install psutil for full details)</i>")
    
    # Join and ensure it fits Telegram's message limit
    result = "\n".join(lines)
    if len(result) > 4000:
        result = result[:3900] + "\n\n... (truncated due to length)"
    
    return result


def _escape_html(text):
    """Escape HTML special characters to prevent parsing errors."""
    if text is None:
        return "Unknown"
    # Convert to string and escape HTML entities
    text = str(text)
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    # Also escape backslashes which can cause issues in paths
    text = text.replace('\\', '/')
    return text


def handle_sysinfo_command(bot, message):
    """Handle the /si command."""
    try:
        bot.send_chat_action(message.chat.id, "typing")
        
        # Send initial message
        status_msg = bot.send_message(message.chat.id, "🔍 Gathering system information...")
        
        # Get system information
        info = get_system_info()
        
        # Format the information
        formatted_info = format_system_info(info)
        
        # Delete status message and send results
        try:
            bot.delete_message(message.chat.id, status_msg.message_id)
        except:
            pass  # Ignore deletion errors
        
        bot.send_message(message.chat.id, formatted_info, parse_mode='HTML')
        
    except Exception as e:
        error_msg = f"❌ Failed to get system information: {str(e)}"
        bot.reply_to(message, error_msg)
        print(f"Sysinfo error: {e}")  # Log for debugging
