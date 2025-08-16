# System Information Plugin Documentation

## Overview

The **sysinfo** plugin provides comprehensive system information for the bot's host machine via the `/si` command. It displays hardware, software, network, and bot-specific details in a user-friendly format.

## Usage

### Basic Command
```bash
/si
```

### Alternative Commands
```bash
/sysinfo
/system_info
```

## Features

### 🔧 **System Details**
- Operating system and version
- System architecture (x64, ARM, etc.)
- Hostname and processor information
- Python version
- System boot time (if psutil available)

### ⚙️ **Hardware Information** *(requires psutil)*
- CPU core count (logical and physical)
- Real-time CPU usage percentage
- Memory usage (total, used, available)
- Memory usage percentage

### 🌐 **Network Information**
- System hostname
- Local IP address
- Network interface count (if psutil available)

### 💾 **Storage Information** *(requires psutil)*
- All mounted drives/partitions
- File system types
- Storage usage per drive (used/total/free)
- Storage usage percentages

### ⚡ **Process Information** *(requires psutil)*
- Total number of running processes
- User account running the bot

### 🤖 **Bot Information**
- Bot directory location
- Current working directory
- Python executable path
- Running user account

## Sample Output

### Full Output (with psutil)
```
🖥️ System Information
==============================

🔧 System Details:
• Platform: Windows 11
• Architecture: AMD64
• Hostname: BOT-SERVER
• Processor: Intel Core i7-9700K
• Python: 3.11.5
• Boot Time: 2024-01-15 08:30:22

⚙️ Hardware:
• CPU Cores: 8 logical, 8 physical
• CPU Usage: 15.3%
• Memory: 8.2 GB / 16.0 GB (51.2% used)
• Available: 7.8 GB

🌐 Network:
• Hostname: BOT-SERVER
• Local IP: 192.168.1.100
• Interfaces: 3

💾 Storage:
• C:\ (NTFS)
  📁 C:\
  📊 245.6 GB / 500.0 GB (49.1% used)
  💿 254.4 GB free

• D:\ (NTFS)
  📁 D:\
  📊 1.2 TB / 2.0 TB (60.0% used)
  💿 800.0 GB free

⚡ Processes:
• Total Processes: 187
• Running as: botuser

🤖 Bot Information:
• Bot Directory: /opt/torrent-bot
• Working Directory: /opt/torrent-bot
• Python Executable: /usr/bin/python3.11
• Running as: botuser

📊 System information gathered successfully
```

### Limited Output (without psutil)
```
🖥️ System Information
==============================
⚠️ Limited info - psutil not available

🔧 System Details:
• Platform: Windows 11
• Architecture: AMD64
• Hostname: BOT-SERVER
• Processor: Intel Core i7-9700K
• Python: 3.11.5

🌐 Network:
• Hostname: BOT-SERVER
• Local IP: 192.168.1.100

🤖 Bot Information:
• Working Directory: /opt/torrent-bot
• Python Executable: /usr/bin/python3.11
• Running as: botuser

📊 Basic system information (install psutil for full details)
```

## Dependencies

### Required (Core Python)
- `os` - Operating system interface
- `platform` - Platform identification
- `socket` - Network interface
- `datetime` - Time formatting
- `pathlib` - Path handling

### Optional (Enhanced Features)
- `psutil` - System and process utilities

**Installation**:
```bash
pip install psutil
```

## Technical Implementation

### Architecture
The plugin follows a clean, modular design:

```python
# Core functions
get_system_info()        # Gathers all system data
get_basic_system_info()  # Fallback without psutil
format_system_info()     # Formats for display
format_bytes()           # Human-readable file sizes
handle_sysinfo_command() # Telegram command handler
```

### Error Handling
- **Graceful degradation**: Works without psutil (limited features)
- **Permission handling**: Skips inaccessible storage devices
- **Network errors**: Shows error message if network info fails
- **Message limits**: Truncates output to fit Telegram limits (4000 chars)

### Performance
- **Fast execution**: Most operations complete in < 1 second
- **Memory efficient**: Minimal memory footprint
- **Non-blocking**: Uses async status messages

## Configuration

### Environment Variables
No environment variables required. The plugin works out-of-the-box.

### Bot Integration
The plugin is automatically available when imported in `bot.py`:

```python
from plugins import sysinfo

@bot.message_handler(commands=["si", "sysinfo", "system_info"])
def cmd_sysinfo(message):
    sysinfo.handle_sysinfo_command(bot, message)
```

## Use Cases

### **System Monitoring**
- Check system resource usage
- Monitor memory and CPU utilization
- Verify available storage space

### **Troubleshooting**
- Identify system configuration issues
- Check Python version and environment
- Verify network connectivity

### **Deployment Verification**
- Confirm bot is running on correct machine
- Check working directory and permissions
- Verify system requirements

### **Performance Analysis**
- Monitor resource usage trends
- Identify bottlenecks
- Plan capacity upgrades

## Security Considerations

### **Information Exposure**
- System info is only shown to bot users
- No sensitive data (passwords, keys) exposed
- Network info limited to basic details

### **Permissions**
- Only reads system information
- No system modification capabilities
- Respects OS permission boundaries

## Troubleshooting

### **"Limited info - psutil not available"**
**Solution**: Install psutil for full functionality
```bash
pip install psutil
```

### **"Permission denied" for storage**
**Cause**: Some drives require elevated permissions
**Solution**: Normal behavior, inaccessible drives are skipped

### **"Network error"**
**Cause**: Network configuration issues
**Solution**: Check system networking, info will show error details

### **Message truncated**
**Cause**: Very detailed system info exceeds Telegram limits
**Solution**: Normal behavior, most important info is preserved

## Extension Points

### **Custom Metrics**
Add custom system metrics by extending `get_system_info()`:

```python
# Add custom monitoring
info['custom'] = {
    'docker_status': check_docker(),
    'service_status': check_services(),
    'uptime': get_uptime()
}
```

### **Platform-Specific Info**
Add OS-specific details:

```python
if platform.system() == "Linux":
    info['linux'] = get_linux_specific_info()
elif platform.system() == "Windows":
    info['windows'] = get_windows_specific_info()
```

### **Integration with Other Plugins**
Combine with other bot features:

```python
# Include bot-specific stats
info['bot_stats'] = {
    'active_downloads': get_download_count(),
    'cache_size': get_cache_size(),
    'uptime': get_bot_uptime()
}
```

## Performance Metrics

Typical execution times:
- **Basic info**: 50-100ms
- **Full info with psutil**: 200-500ms
- **Storage enumeration**: 100-300ms
- **Network discovery**: 50-150ms

Memory usage:
- **Plugin memory**: < 1MB
- **Temporary data**: < 500KB
- **No persistent storage**: 0 bytes

## Best Practices

### **Regular Monitoring**
- Use `/si` to check system health
- Monitor resource usage trends
- Plan capacity before limits reached

### **Troubleshooting Workflow**
1. Run `/si` to get baseline info
2. Check resource usage (CPU/memory)
3. Verify storage availability
4. Confirm network connectivity

### **Performance Optimization**
- Install psutil for full features
- Run on systems with adequate resources
- Monitor storage space regularly

The sysinfo plugin provides essential system visibility for bot administrators and helps ensure optimal performance and troubleshooting capabilities.
