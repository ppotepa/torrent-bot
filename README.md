# Torrent Bot - Automated Media Server Library

> **⚠️ Legal Disclaimer**: This repository is intended for educational and fair use purposes only. Piracy is illegal and we do not condone or support any illegal downloading of copyrighted material. Users are responsible for ensuring they comply with their local laws and only download content they have the legal right to access.

## 🎯 Purpose

This Telegram bot is designed to create an **automated media server library** by interfacing with torrent indexers and download clients. It provides a seamless way to search, download, and organize media content for personal media servers.

### 🎵 Perfect for Personal Media Libraries

This bot works exceptionally well with media server applications like **Symphonium** and other music/media players that can organize and stream your personal media collection. Create your own comprehensive media library with automated downloads and organization.

## ✨ Features

### 🔍 Advanced Search Capabilities
- **Smart Search**: `/t <query>` - Quick search across configured indexers
- **Rich Mode**: `/t <query> rich` - Comprehensive search across ALL available indexers (20+)
- **All Mode**: `/t <query> all` - Extended search with maximum coverage
- **Music Mode**: `/t <query> music` - Specialized search for music content
- **Real-time Progress**: Live updates during searches with busy indicators

### 📊 Visual Indicators
- 🔥 Hot torrent (100+ seeders)
- ⭐ Good torrent (10+ seeders)  
- ✅ Available (1+ seeders)
- ⚠️ No seeders
- 🧲 Magnet link available
- 📁 Torrent file available

### 🚀 Download Management
- **Smart Fallback System**: Multiple download methods ensure high success rates
- **Auto-monitoring**: Automatic notifications when downloads complete
- **Download Tracking**: `/d` - View active downloads with progress
- **Batch Management**: `/d clear` - Remove all completed torrents
- **System Information**: `/si` - Comprehensive system diagnostics

### 🛠️ Advanced Features
- **Docker Diagnostics**: `/dockerfix` - Troubleshoot container networking issues
- **Seeder Sorting**: Intelligent sorting by seed count for better downloads
- **Fallback Chain**: Multiple retry methods for failed downloads
- **Progress Tracking**: Real-time download progress and status updates

## 🐳 Docker Setup

### Prerequisites

This bot requires the following services to be running in **separate containers**:

1. **ZeroTier** - Must be running in another container for network connectivity
2. **Jackett** - Must be running in another container for torrent indexing
3. **qBittorrent** - Included in this compose file as the download client
4. **FlareSolverr** - Included for Cloudflare bypass

### Docker Compose Configuration

**⚠️ Security Note**: Never commit real credentials to version control. Use environment variables or .env files.

```yaml
version: "3.8"

services:
  telegram-bot:
    build: .
    container_name: telegram-bot
    restart: unless-stopped
    environment:
      # Telegram Bot Configuration
      TELEGRAM_BOT_TOKEN: "${TELEGRAM_BOT_TOKEN}"

      # Jackett Configuration (running in separate container)
      JACKETT_URL: "http://jackett:9117"
      JACKETT_API_KEY: "${JACKETT_API_KEY}"
      
      # 🔥 Popular indexers (must be configured in Jackett)
      JACKETT_INDEXERS: "yts,nyaa,eztv,1337x,torrentgalaxy,thepiratebay,torlock,limetorrents,glodls,bitsearch,torrentfunk,magnetdl,yourbittorrent,zooqle,torrentdownloads,linuxtracker,anidex,animetosho,idope,ettv"

      # Performance Tuning
      JACKETT_CONNECT_TIMEOUT: "3"
      JACKETT_READ_TIMEOUT: "12"
      JACKETT_MAX_WORKERS: "8"
      JACKETT_RESULT_LIMIT: "5"

      # qBittorrent Configuration
      QBIT_HOST: "qbittorrent"
      QBIT_PORT: "8080"
      QBIT_USER: "${QBIT_USER:-admin}"
      QBIT_PASS: "${QBIT_PASS:-adminadmin}"

      # Enhanced Features
      ENABLE_AGGRESSIVE_FALLBACK: "true"
      MAX_FALLBACK_ATTEMPTS: "3"
      RICH_MODE_LIMIT: "15"
      RICH_MODE_TIMEOUT: "20"
    volumes:
      - "${DOWNLOAD_PATH:-./downloads}:/app/downloads"
    depends_on:
      - qbittorrent
      - flaresolverr
    networks:
      - zerotier

  qbittorrent:
    image: lscr.io/linuxserver/qbittorrent:latest
    container_name: qbittorrent
    restart: unless-stopped
    environment:
      - PUID=1000
      - PGID=1000
      - TZ=Europe/Warsaw
      - WEBUI_PORT=8080
      - QBT_WEBUI_USERNAME=${QBIT_USER:-admin}
      - QBT_WEBUI_PASSWORD=${QBIT_PASS:-adminadmin}
    ports:
      - "8080:8080"
      - "6881:6881"
      - "6881:6881/udp"
    volumes:
      - "${DOWNLOAD_PATH:-./downloads}:/downloads"
      - "${QBIT_CONFIG_PATH:-./qbittorrent-config}:/config"
    networks:
      - zerotier

  flaresolverr:
    image: ghcr.io/flaresolverr/flaresolverr:latest
    container_name: flaresolverr
    restart: unless-stopped
    environment:
      - LOG_LEVEL=info
      - TZ=Europe/Warsaw
    ports:
      - "8191:8191"
    networks:
      - zerotier

networks:
  zerotier:
    external: true
```

### Required External Containers

#### ZeroTier Container
ZeroTier must be running in a separate container to provide network connectivity:
```yaml
# Add this to your separate ZeroTier compose file
zerotier:
  image: zerotier/zerotier:latest
  container_name: zerotier
  privileged: true
  network_mode: host
  volumes:
    - /var/lib/zerotier-one:/var/lib/zerotier-one
  restart: unless-stopped
```

#### Jackett Container
Jackett must be running in a separate container:
```yaml
# Add this to your separate Jackett compose file
jackett:
  image: lscr.io/linuxserver/jackett:latest
  container_name: jackett
  restart: unless-stopped
  environment:
    - PUID=1000
    - PGID=1000
    - TZ=Europe/Warsaw
  ports:
    - "9117:9117"
  volumes:
    - "/path/to/jackett-config:/config"
  networks:
    - zerotier
```

## 🚀 Quick Start

1. **Set up external containers** (ZeroTier and Jackett)
2. **Configure environment variables**:
   ```bash
   # Copy the example environment file
   cp .env.example .env
   
   # Edit .env with your actual values
   nano .env
   ```
3. **Required Environment Variables**:
   - `TELEGRAM_BOT_TOKEN` - Get from @BotFather on Telegram
   - `JACKETT_API_KEY` - Get from Jackett web interface
   - `QBIT_USER` and `QBIT_PASS` - qBittorrent credentials
   - `DOWNLOAD_PATH` - Path where downloads will be stored
4. **Configure Jackett** with your preferred indexers
5. **Start the bot**:
   ```bash
   docker-compose up -d
   ```

### 🔒 Environment Configuration

Create a `.env` file in the project root with your configuration:

```bash
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

# Jackett Configuration  
JACKETT_API_KEY=your_jackett_api_key_here

# qBittorrent Configuration
QBIT_USER=admin
QBIT_PASS=your_secure_password_here

# File Paths
DOWNLOAD_PATH=/path/to/your/downloads
QBIT_CONFIG_PATH=/path/to/qbittorrent/config
```

**⚠️ Important**: Never commit your `.env` file to version control!

## 📱 Usage Commands

### Search Commands
- `/t <query>` - Standard search
- `/t <query> rich` - Comprehensive search across all indexers
- `/t <query> all` - Extended search with maximum coverage  
- `/t <query> music` - Music-optimized search

### Download Management
- `/d` - View active downloads
- `/d clear` - Remove completed torrents
- Download monitoring is automatic with completion notifications

### System Commands
- `/si` - System information and diagnostics
- `/dockerfix` - Docker networking troubleshooting
- `/help` - Show all available commands

## 🔧 Configuration Options

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ENABLE_AGGRESSIVE_FALLBACK` | `true` | Enable searching alternative sources when primary methods fail |
| `MAX_FALLBACK_ATTEMPTS` | `3` | Maximum retry attempts for failed downloads |
| `RICH_MODE_LIMIT` | `15` | Maximum results in rich search mode |
| `RICH_MODE_TIMEOUT` | `20` | Timeout in seconds for rich mode searches |
| `JACKETT_CONNECT_TIMEOUT` | `3` | Connection timeout for Jackett requests |
| `JACKETT_READ_TIMEOUT` | `12` | Read timeout for Jackett requests |
| `JACKETT_MAX_WORKERS` | `8` | Maximum concurrent workers for searches |

### Indexer Configuration

The bot supports 20+ popular indexers. Configure them in Jackett and list them in the `JACKETT_INDEXERS` environment variable:

**Popular Indexers:**
- `yts` - Movies (high quality, small size)
- `nyaa` - Anime and Asian content
- `eztv` - TV shows
- `1337x` - General content
- `torrentgalaxy` - Movies and TV
- `thepiratebay` - General content
- `limetorrents` - General content
- `anidex` - Anime
- `animetosho` - Anime

## 🎵 Media Server Integration

### Symphonium Integration
This bot is perfect for building media libraries that work with **Symphonium** and similar media players:

1. **Download Organization**: Torrents are automatically organized by category
2. **Quality Control**: Seeder-based filtering ensures good quality downloads
3. **Automated Workflow**: Set up automatic downloads for artists, series, or specific content
4. **Real-time Updates**: Get notified when new content is added to your library

### Media Server Workflow
1. Search for content using the bot
2. Downloads automatically start in qBittorrent
3. Completed downloads are organized in your media directory
4. Your media server (Plex, Jellyfin, etc.) picks up new content
5. Enjoy your automated media library!

## 🛠️ Troubleshooting

### Common Issues

**Downloads Stalling in Docker:**
- Use `/dockerfix` command for diagnostics
- Ensure proper port forwarding (6881 TCP/UDP)
- Check ZeroTier network connectivity

**No Search Results:**
- Verify Jackett is running and accessible
- Check indexer configuration in Jackett
- Try rich mode: `/t <query> rich`

**Bot Not Responding:**
- Check Telegram bot token
- Verify container networking
- Review container logs: `docker logs telegram-bot`

### Performance Optimization
- Increase `JACKETT_MAX_WORKERS` for faster searches
- Adjust `RICH_MODE_LIMIT` based on your needs
- Enable `ENABLE_AGGRESSIVE_FALLBACK` for better success rates

## 📝 Legal Notice

This software is provided for educational and fair use purposes only. Users are solely responsible for:

- Ensuring compliance with local copyright laws
- Only downloading content they have legal rights to access
- Understanding that piracy is illegal in most jurisdictions
- Using this tool responsibly and ethically

The developers do not condone or support any illegal downloading of copyrighted material.

## 🤝 Contributing

Contributions are welcome! Please ensure any changes maintain the educational and fair use nature of this project.

## 📄 License

This project is intended for educational and fair use purposes. Please respect copyright laws and use responsibly.

---

**Enjoy building your automated media server library! 🎬🎵📚**
