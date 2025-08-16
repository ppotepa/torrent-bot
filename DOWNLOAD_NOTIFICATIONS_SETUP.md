# Download Completion Notifications Setup

The bot now automatically monitors qBittorrent for completed downloads and sends you Telegram notifications! 🎉

## 🚀 **Quick Setup**

### 1. **Get Your Telegram User ID**
To receive notifications, the bot needs your Telegram user ID.

**Method 1: Use a bot to get your ID**
1. Start a chat with [@userinfobot](https://t.me/userinfobot)
2. Send any message
3. Copy your user ID (numbers only)

**Method 2: Check from your bot**
1. Send any message to your bot
2. Check the bot logs for your user ID

### 2. **Set Environment Variable**
Add your user ID to your `docker-compose.yaml`:

```yaml
telegram-bot:
  environment:
    # ... existing variables ...
    ADMIN_USER_ID: "YOUR_USER_ID_HERE"    # Replace with your actual ID
```

### 3. **Restart Your Bot**
```bash
docker-compose down
docker-compose up -d
```

## 📱 **What You'll Get**

When a download completes, you'll receive a message like:

```
✅ Download Completed!

📁 Ubuntu 22.04.3 Desktop amd64.iso
💾 Size: 4.7 GB  
⏰ Completed: 14:35:22
🏷️ Category: Linux
📂 Location: /downloads/Linux/

🎉 Ready to enjoy!
```

## 🔧 **Bot Commands**

### **Monitor Status**
```bash
/monitor                    # Check monitor status
```

### **Manual Control**
```bash
/monitor_check             # Force check for completions
/monitor_start             # Start the monitor
/monitor_stop              # Stop the monitor
```

## ⚙️ **Configuration Options**

Add these to your `docker-compose.yaml` environment variables:

```yaml
telegram-bot:
  environment:
    # Required
    ADMIN_USER_ID: "123456789"                    # Your Telegram user ID
    
    # Optional
    DOWNLOAD_MONITOR_INTERVAL: "30"              # Check every 30 seconds (default)
    QBIT_HOST: "qbittorrent"                     # qBittorrent container name
    QBIT_PORT: "8080"                            # qBittorrent port
    QBIT_USER: "admin"                           # qBittorrent username
    QBIT_PASS: "adminadmin"                      # qBittorrent password
```

## 🔍 **How It Works**

### **Background Monitoring**
- Runs in a separate thread (doesn't slow down the bot)
- Checks qBittorrent every 30 seconds (configurable)
- Tracks download states and progress
- Detects when downloads transition to "completed"

### **Smart Detection**
- Only notifies for newly completed downloads
- Remembers previous notifications (won't spam)
- Handles bot restarts gracefully
- Persists state to avoid duplicate notifications

### **Completion Detection**
Considers a download "completed" when:
- Progress reaches 100%
- State is one of: `completedUP`, `completedDL`, `uploading`, `queuedUP`, `stalledUP`
- Has not been previously notified

## 🛠️ **Troubleshooting**

### **Not Receiving Notifications?**

1. **Check your user ID is correct**:
   ```bash
   /monitor         # Check if monitor is running
   ```

2. **Verify bot can connect to qBittorrent**:
   ```bash
   /qdiag          # Run qBittorrent diagnostics
   ```

3. **Check monitor status**:
   ```bash
   /monitor        # Should show "Running: ✅ Yes"
   ```

4. **Test with a quick download**:
   - Add a small torrent to qBittorrent
   - Wait for it to complete
   - Use `/monitor_check` to force a check

### **Monitor Not Running?**

```bash
/monitor_start              # Start the monitor
/monitor                    # Check status
```

### **Getting Admin User ID**

If you don't know your Telegram user ID:

1. Send any message to your bot
2. Check bot logs:
   ```bash
   docker logs telegram-bot | grep "user_id"
   ```

3. Or use [@userinfobot](https://t.me/userinfobot)

## 📊 **Monitor Status Information**

The `/monitor` command shows:
- ✅ Monitor running status
- ⏱️ Check interval (seconds)
- 📊 Number of torrents being tracked
- 📨 Number of completion notifications sent
- 📋 Current downloads (last 5 with progress)

## 🎯 **Example Complete Setup**

Your `docker-compose.yaml` should include:

```yaml
version: "3.8"

services:
  telegram-bot:
    build: .
    container_name: telegram-bot
    restart: unless-stopped
    environment:
      TELEGRAM_BOT_TOKEN: "your_bot_token_here"
      ADMIN_USER_ID: "123456789"                    # Your user ID for notifications
      
      # qBittorrent connection
      QBIT_HOST: "qbittorrent"
      QBIT_PORT: "8080"
      QBIT_USER: "admin"
      QBIT_PASS: "adminadmin"
      
      # Optional: Monitor settings
      DOWNLOAD_MONITOR_INTERVAL: "30"              # Check every 30 seconds
      
      # ... other existing variables ...
    volumes:
      - "D:/Music:/app/downloads"
    depends_on:
      - qbittorrent
    networks:
      - zerotier

  qbittorrent:
    # ... your qbittorrent config ...
```

## 🎉 **Features**

### **Rich Notifications**
- 📁 Download name
- 💾 File size (formatted nicely)
- ⏰ Completion time
- 🏷️ Category (if set)
- 📂 Save location
- 🎉 Celebration message

### **Persistence**
- Survives bot restarts
- Remembers completed downloads
- State saved to `download_monitor_state.json`

### **Performance**
- Lightweight background monitoring
- Configurable check intervals
- Efficient state tracking
- Minimal resource usage

## 🚀 **Getting Started**

1. Add `ADMIN_USER_ID` to your docker-compose.yaml
2. Restart your bot
3. Send `/monitor` to verify it's working
4. Download something and wait for your notification! 🎉

Your bot will now keep you informed about every completed download! 📱✨
