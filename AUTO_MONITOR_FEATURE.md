# 🔔 Auto-Start Download Monitor Feature

## Overview
The torrent bot now automatically starts the download completion monitor whenever you initiate a torrent download. This ensures you'll never miss completion notifications without having to manually start the monitor.

## How It Works

### Automatic Activation
- **Triggers**: Monitor starts automatically when ANY torrent download succeeds:
  - ✅ Magnet link downloads
  - ✅ .torrent file downloads  
  - ✅ Fallback method downloads
  - ✅ Alternative source downloads

### Smart Behavior
- **No Duplicates**: If monitor is already running, it won't start another instance
- **User Notification**: When auto-started, you'll see: `🔔 Download monitor started automatically - you'll get notified when downloads complete!`
- **Error Handling**: If monitor fails to start, your download still succeeds (monitor failure won't break downloads)

## Configuration

### Enable/Disable Auto-Start
Add to your `docker-compose.yaml` environment variables:

```yaml
environment:
  # Enable automatic monitor start (default: true)
  AUTO_START_MONITOR: "true"
  
  # Disable automatic monitor start  
  # AUTO_START_MONITOR: "false"
```

### Default Behavior
- **Default**: `AUTO_START_MONITOR=true` (enabled by default)
- **Backwards Compatible**: Existing setups work without changes

## User Experience

### Before Auto-Start
1. Search and download torrent: `/t ubuntu`
2. **Manually** start monitor: `/monitor`
3. Wait for completion notification

### With Auto-Start  
1. Search and download torrent: `/t ubuntu`
2. ✅ **Monitor starts automatically**
3. ✅ **Get notification when complete**

## Monitor Commands Still Available

Even with auto-start enabled, you can still use manual monitor commands:

- `/monitor` - Start monitor manually
- `/monitor_check` - Check monitor status  
- `/monitor_stop` - Stop monitor
- `/monitor_start` - Start monitor manually

## Technical Details

### Implementation
- **Location**: Integrated into `plugins/torrent/telegram_handlers.py`
- **Trigger Point**: After successful torrent addition to qBittorrent
- **Notification Target**: Same chat where download was initiated
- **Error Isolation**: Monitor startup errors don't affect downloads

### Requirements
- **Admin User ID**: Still need `ADMIN_USER_ID` configured for notifications to work
- **qBittorrent Access**: Monitor needs working qBittorrent API connection
- **Background Thread**: Uses same monitoring system as manual start

## Troubleshooting

### Monitor Not Starting
1. Check `AUTO_START_MONITOR` is set to `"true"` 
2. Verify `ADMIN_USER_ID` is configured
3. Ensure qBittorrent is accessible
4. Check container logs for error messages

### Multiple Start Messages
- Normal if monitor was manually stopped and new download triggered auto-start
- Monitor won't duplicate if already running

### Disabling Auto-Start
If you prefer manual control:

```yaml
environment:
  AUTO_START_MONITOR: "false"
```

Then restart the bot container.

## Benefits

1. **Zero Manual Work**: No need to remember to start monitor
2. **Never Miss Notifications**: Auto-activation ensures coverage  
3. **Smart Operation**: Won't create duplicate monitors
4. **Configurable**: Can disable if not wanted
5. **Reliable**: Download success isn't affected by monitor issues

---

**🚀 Ready to Use**: This feature is active immediately - your next torrent download will auto-start the monitor!
