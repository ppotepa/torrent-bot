# 🐳 Docker Deployment Guide

This guide covers deploying the torrent-bot using Docker and Docker Compose.

## 📋 Quick Start

1. **Clone the repository**:
   ```bash
   git clone https://github.com/ppotepa/torrent-bot.git
   cd torrent-bot
   ```

2. **Set up environment variables**:
   ```bash
   cp .env.example .env
   nano .env  # Edit with your actual values
   ```

3. **Start the services**:
   ```bash
   docker-compose up -d
   ```

## ⚙️ Configuration

### Required Environment Variables

Edit `.env` file with your configuration:

```bash
# Telegram Bot Configuration (REQUIRED)
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here  # Get from @BotFather
ADMIN_USER_ID=your_admin_user_id_here            # Your Telegram user ID

# qBittorrent Configuration (REQUIRED)
QBIT_USER=admin                                   # qBittorrent username
QBIT_PASS=your_secure_password_here              # qBittorrent password
```

### Optional Configuration

```bash
# Jackett Configuration (for torrent search - optional)
JACKETT_URL=http://jackett:9117
JACKETT_API_KEY=your_jackett_api_key_here

# Advanced Jackett Settings
JACKETT_INDEXERS=yts,nyaa,eztv,1337x,torrentgalaxy,thepiratebay
JACKETT_CONNECT_TIMEOUT=3
JACKETT_READ_TIMEOUT=12
JACKETT_MAX_WORKERS=8
JACKETT_RESULT_LIMIT=5

# Path Configuration
DOWNLOAD_PATH=./downloads                         # Host download path
QBIT_CONFIG_PATH=./qbittorrent-config            # qBittorrent config path
```

## 🏗️ Architecture

The Docker setup includes:

- **telegram-bot**: Main bot application with TTS capabilities
- **qbittorrent**: Download client for torrents
- **Docker volumes**: Persistent storage for downloads and config
- **Internal network**: Secure communication between services

## 🎙️ TTS Features

The bot includes advanced Text-to-Speech capabilities:

- **Voice Cloning**: Uses your voice samples for personalized TTS
- **Multiple Profiles**: 6 pre-configured voice profiles
- **Multi-language**: Polish and English support
- **Multiple Engines**: Enhanced Piper TTS, Voice Cloning, gTTS

### TTS Commands

```bash
/ab Hello world:pawel          # Voice cloning with your voice
/ab Natural speech:natural     # Enhanced Piper TTS
/ab Quick message:fast         # Fast synthesis
/ab Automatic detection        # Auto language/profile selection
```

## 🚀 Deployment

### Development

```bash
# Start in development mode with logs
docker-compose up

# Rebuild after code changes
docker-compose up --build
```

### Production

```bash
# Start in background
docker-compose up -d

# View logs
docker-compose logs -f telegram-bot

# Update and restart
git pull
docker-compose down
docker-compose up -d --build
```

## 📁 File Structure

```
torrent-bot/
├── docker-compose.yaml      # Main deployment configuration
├── dockerfile_final         # Production Dockerfile
├── .env.example            # Environment variables template
├── .env                    # Your actual configuration (create this)
├── downloads/              # Download directory (created automatically)
├── qbittorrent-config/     # qBittorrent configuration (created automatically)
└── plugins/audiobook/      # TTS system files
```

## 🔧 Troubleshooting

### Common Issues

1. **Bot not starting**:
   - Check `TELEGRAM_BOT_TOKEN` is correct
   - Verify `.env` file exists and has proper values

2. **qBittorrent connection failed**:
   - Check `QBIT_USER` and `QBIT_PASS` in `.env`
   - Ensure qBittorrent container is running: `docker-compose ps`

3. **Downloads not working**:
   - Verify download path permissions
   - Check qBittorrent web UI at `http://localhost:8080`

4. **TTS not working**:
   - Ensure voice samples exist in `plugins/audiobook/voice_samples/`
   - Check logs: `docker-compose logs telegram-bot`

### Useful Commands

```bash
# Check service status
docker-compose ps

# View live logs
docker-compose logs -f

# Restart specific service
docker-compose restart telegram-bot

# Access qBittorrent web interface
# Open: http://localhost:8080

# Stop all services
docker-compose down

# Remove all data (⚠️ DESTRUCTIVE)
docker-compose down -v
```

## 🔒 Security Notes

- Never commit `.env` file to version control
- Use strong passwords for qBittorrent
- Keep your Telegram bot token secure
- Regularly update the Docker images

## 📊 Monitoring

### Health Checks

The bot includes built-in health monitoring:

```bash
# Check bot status
docker-compose exec telegram-bot python -c "print('Bot is running')"

# Check qBittorrent status
curl http://localhost:8080

# View resource usage
docker stats
```

### Log Monitoring

```bash
# Real-time logs
docker-compose logs -f telegram-bot

# Last 100 lines
docker-compose logs --tail=100 telegram-bot

# Error logs only
docker-compose logs telegram-bot | grep ERROR
```

---

**Ready to deploy your personal media bot with advanced TTS capabilities!** 🎙️🚀
