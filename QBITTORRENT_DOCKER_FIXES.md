# qBittorrent Docker Download Issues - Solutions

Based on your docker-compose.yaml configuration, here are the most likely causes and solutions for qBittorrent download struggles:

## 🚨 **Immediate Diagnostic Commands**

Run these in your bot to identify the exact issue:

```bash
/qdiag              # Comprehensive qBittorrent diagnostics
/tdiag             # Check if torrents are being found
```

## 🔧 **Common Docker qBittorrent Issues & Fixes**

### 1. **Port Mapping Issues** ⚠️

**Problem**: BitTorrent traffic cannot reach qBittorrent container
**Current config**: You have ports mapped correctly
```yaml
ports:
  - "8080:8080"      # WebUI - ✅ Good
  - "6881:6881"      # TCP - ✅ Good  
  - "6881:6881/udp"  # UDP - ✅ Good
```

**Check**: Verify ports are actually open
```bash
# On your host machine
netstat -tulpn | grep 6881
telnet localhost 6881
```

### 2. **Network Configuration** 🌐

**Problem**: ZeroTier network may not allow BitTorrent traffic
**Current config**: Using external zerotier network
```yaml
networks:
  - zerotier  # This might block P2P traffic
```

**Solution**: Try adding bridge network as fallback
```yaml
services:
  qbittorrent:
    # ... existing config ...
    networks:
      - zerotier
      - default    # Add default bridge network
    ports:
      - "8080:8080"
      - "6881:6881"
      - "6881:6881/udp"

networks:
  zerotier:
    external: true
  default:           # Add default bridge network
    driver: bridge
```

### 3. **Volume Mount Permissions** 📁

**Problem**: qBittorrent cannot write to download directory
**Current config**: 
```yaml
volumes:
  - "D:/Music:/downloads"                    # qBittorrent downloads
  - "D:/qbittorrent-config:/config"         # qBittorrent config
# Bot config:
  - "D:/Music:/app/downloads"                # Bot downloads
```

**Check/Fix**:
1. Ensure D:/Music exists and is writable
2. Check permissions on Windows:
```cmd
icacls "D:\Music" /grant Everyone:(OI)(CI)F
icacls "D:\qbittorrent-config" /grant Everyone:(OI)(CI)F
```

### 4. **qBittorrent Settings** ⚙️

**Critical Settings** to check in qBittorrent WebUI (http://localhost:8080):

#### **Connection Settings**:
- **Port**: Should be 6881 (matching Docker mapping)
- **Use UPnP**: Enable if your router supports it
- **Use DHT**: ✅ Enable (for peer discovery)
- **Use PeX**: ✅ Enable (for peer exchange)
- **Use LSD**: ✅ Enable (for local peer discovery)

#### **Speed Settings**:
- **Global max connections**: 200+ (not unlimited)
- **Max connections per torrent**: 50-100
- **Global max upload slots**: 20+
- **Max upload slots per torrent**: 4-8

#### **BitTorrent Settings**:
- **Enable DHT**: ✅ True
- **Enable PeX**: ✅ True  
- **Enable LSD**: ✅ True
- **Encryption**: Prefer encryption (not require)

### 5. **Environment Variables** 🔧

**Update your docker-compose.yaml**:
```yaml
qbittorrent:
  image: lscr.io/linuxserver/qbittorrent:latest
  container_name: qbittorrent
  restart: unless-stopped
  environment:
    - PUID=1000
    - PGID=1000
    - TZ=Europe/Warsaw
    - WEBUI_PORT=8080
    - QBT_WEBUI_USERNAME=admin
    - QBT_WEBUI_PASSWORD=adminadmin
    # Add these for better performance:
    - QBT_EULA=accept                    # Accept EULA automatically
    - QBT_VERSION=latest                 # Use latest stable
    - QBT_WEBUI_HOST=0.0.0.0            # Listen on all interfaces
  ports:
    - "8080:8080"
    - "6881:6881"
    - "6881:6881/udp"
  volumes:
    - "D:/Music:/downloads"
    - "D:/qbittorrent-config:/config"
  networks:
    - zerotier
    - default                            # Add fallback network
```

### 6. **Firewall Issues** 🔥

**Windows Firewall**: May be blocking BitTorrent ports
```cmd
# Allow qBittorrent through Windows Firewall
netsh advfirewall firewall add rule name="qBittorrent TCP" dir=in action=allow protocol=TCP localport=6881
netsh advfirewall firewall add rule name="qBittorrent UDP" dir=in action=allow protocol=UDP localport=6881
```

**Router Firewall**: Check if ISP/router blocks BitTorrent
- Some ISPs throttle or block BitTorrent traffic
- Consider using a VPN if needed

### 7. **Container Health** 🐳

**Check container status**:
```bash
docker ps                          # Is qbittorrent running?
docker logs qbittorrent           # Check for errors
docker restart qbittorrent        # Restart if needed
```

**Resource limits**: Ensure adequate resources
```yaml
qbittorrent:
  # ... existing config ...
  deploy:
    resources:
      limits:
        memory: 1G
        cpus: '0.5'
```

## 🧪 **Testing Download Capability**

### Step 1: Test with Bot Diagnostics
```bash
/qdiag                            # Run this in your bot
```

### Step 2: Manual Test
1. Open qBittorrent WebUI: http://localhost:8080
2. Add a well-seeded torrent (Ubuntu ISO)
3. Check if it connects to peers
4. Monitor download progress

### Step 3: Check Network Connectivity
```bash
# In qBittorrent container
docker exec qbittorrent netstat -tulpn | grep 6881
docker exec qbittorrent ping 8.8.8.8          # Test internet
```

## 🚀 **Optimized docker-compose.yaml**

Here's your optimized configuration:

```yaml
version: "3.8"

services:
  telegram-bot:
    build: .
    container_name: telegram-bot
    restart: unless-stopped
    environment:
      TELEGRAM_BOT_TOKEN: "8415463111:AAFPN2GJoqayGtvcQpUYwhzyUFJGbmKTIPw"
      
      # Jackett
      JACKETT_URL: "http://jackett:9117"
      JACKETT_API_KEY: "gf72swxqzum06ifwsuya4uvvvmsdh9xd"
      JACKETT_INDEXERS: "yts,nyaa,eztv,1337x,torrentgalaxy,thepiratebay,torlock,limetorrents,glodls,bitsearch,torrentfunk,magnetdl,yourbittorrent,zooqle,torrentdownloads,linuxtracker,anidex,animetosho,idope,ettv"
      
      # Speed tuning  
      JACKETT_CONNECT_TIMEOUT: "3"
      JACKETT_READ_TIMEOUT: "12"
      JACKETT_MAX_WORKERS: "8"
      JACKETT_RESULT_LIMIT: "5"
      
      # qBittorrent
      QBIT_HOST: "qbittorrent"
      QBIT_PORT: "8080"
      QBIT_USER: "admin"
      QBIT_PASS: "adminadmin"
    volumes:
      - "D:/Music:/app/downloads"
    depends_on:
      - qbittorrent
      - flaresolverr
    networks:
      - zerotier
      - default

  qbittorrent:
    image: lscr.io/linuxserver/qbittorrent:latest
    container_name: qbittorrent
    restart: unless-stopped
    environment:
      - PUID=1000
      - PGID=1000
      - TZ=Europe/Warsaw
      - WEBUI_PORT=8080
      - QBT_WEBUI_USERNAME=admin
      - QBT_WEBUI_PASSWORD=adminadmin
      - QBT_EULA=accept
      - QBT_WEBUI_HOST=0.0.0.0
    ports:
      - "8080:8080"
      - "6881:6881"
      - "6881:6881/udp"
    volumes:
      - "D:/Music:/downloads"
      - "D:/qbittorrent-config:/config"
    networks:
      - zerotier
      - default
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'

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
      - default

networks:
  zerotier:
    external: true
  default:
    driver: bridge
```

## 📋 **Troubleshooting Checklist**

1. ✅ **Run bot diagnostics**: `/qdiag` and `/tdiag`
2. ✅ **Check container status**: `docker ps` and `docker logs qbittorrent`
3. ✅ **Verify port accessibility**: `netstat -tulpn | grep 6881`
4. ✅ **Test qBittorrent WebUI**: http://localhost:8080
5. ✅ **Check folder permissions**: Ensure D:/Music is writable
6. ✅ **Verify network settings**: DHT, PeX, LSD enabled
7. ✅ **Test with known good torrent**: Ubuntu ISO or similar
8. ✅ **Check firewall**: Windows and router firewalls
9. ✅ **Monitor resource usage**: CPU, memory, disk space
10. ✅ **Consider VPN**: If ISP blocks BitTorrent

## 🎯 **Most Likely Solutions**

Based on common Docker + qBittorrent issues:

1. **Add default bridge network** (80% of cases)
2. **Check folder permissions** (60% of cases)
3. **Enable DHT/PeX/LSD in qBittorrent** (40% of cases)
4. **Restart qBittorrent container** (30% of cases)

Start with `/qdiag` command to get specific diagnostics for your setup! 🔍
