# 🔧 Docker Torrent Stalling - Complete Fix Guide

## 🔍 Why Torrents Stall in Docker

**Root Cause:** Docker containers run in isolated networks. Torrents need:
- **Incoming connections** from peers (not just outgoing)
- **Proper port forwarding** for the listening port  
- **No NAT traversal issues**

Your host machine downloads fine because it has direct network access. Docker needs special configuration.

---

## 🚀 SOLUTION 1: Fix Docker Compose (RECOMMENDED)

### **Current Problem Check**
```bash
# Check your current setup
docker ps | grep qbit
docker port qbittorrent  # See what ports are mapped
```

### **Fixed docker-compose.yaml**
```yaml
version: '3'
services:
  qbittorrent:
    image: lscr.io/linuxserver/qbittorrent:latest
    container_name: qbittorrent
    environment:
      - PUID=1000
      - PGID=1000
      - TZ=Etc/UTC
      - WEBUI_PORT=8080
    volumes:
      - /path/to/qbittorrent/config:/config
      - /path/to/downloads:/downloads
    ports:
      - "8080:8080"           # WebUI
      - "6881:6881"           # BitTorrent TCP
      - "6881:6881/udp"       # BitTorrent UDP
      # Optional: Range for multiple connections
      - "6881-6890:6881-6890"
      - "6881-6890:6881-6890/udp"
    restart: unless-stopped
```

### **Apply the Fix**
```bash
# Stop containers
docker-compose down

# Edit your docker-compose.yaml with the ports above
nano docker-compose.yaml

# Restart with new config
docker-compose up -d
```

---

## 🚀 SOLUTION 2: qBittorrent Configuration

### **Access WebUI**
1. Go to `http://your-server:8080`
2. Login (check logs for credentials: `docker logs qbittorrent`)

### **Fix Connection Settings**
**Tools → Options → Connection:**
```
Listening Port: 6881
☐ Use UPnP/NAT-PMP port forwarding: DISABLED
☐ Use different port on each startup: DISABLED
☐ Enable embedded tracker: ENABLED

Connection Limits:
- Global maximum connections: 200
- Maximum connections per torrent: 100
- Global maximum uploads: 20
- Maximum uploads per torrent: 4
```

**Tools → Options → BitTorrent:**
```
☑️ Enable DHT: ENABLED
☑️ Enable PeX: ENABLED  
☑️ Enable LSD: ENABLED
```

---

## 🚀 SOLUTION 3: Host Network Mode (Alternative)

### **If Bridge Mode Doesn't Work**
```yaml
qbittorrent:
  image: lscr.io/linuxserver/qbittorrent:latest
  network_mode: "host"  # Use host networking directly
  environment:
    - WEBUI_PORT=8080
  volumes:
    - /path/to/config:/config
    - /path/to/downloads:/downloads
  # No ports section needed with host mode
```

**Pros:** No port mapping issues, direct host network access  
**Cons:** Less isolation, qBittorrent uses host network directly

---

## 🚀 SOLUTION 4: Immediate Troubleshooting

### **Quick Fixes to Try Now**
```bash
# 1. Restart qBittorrent container
docker restart qbittorrent

# 2. Check container logs
docker logs qbittorrent | tail -50

# 3. Test port accessibility
curl -I http://localhost:8080  # Should return 200 OK

# 4. Check if containers can communicate
docker exec torrent-bot ping qbittorrent
```

### **Force Reannounce Stalled Torrents**
1. Open qBittorrent WebUI
2. Select stalled torrents
3. Right-click → "Force reannounce"
4. Wait 30 seconds to see if they start

---

## 🚀 SOLUTION 5: Use New Bot Command

### **Diagnostic Command**
Use the new bot command to analyze your setup:
```
/dockerfix
```

This will:
- ✅ Check current torrent states
- ✅ Identify stalled torrents
- ✅ Provide specific Docker fixes
- ✅ Give immediate troubleshooting steps

---

## 🔍 Verification Steps

### **Test Download**
1. Download a popular torrent (Ubuntu ISO)
2. Should start downloading within 30 seconds
3. Check peers/seeds are connecting

### **Check Port Status**
```bash
# Verify ports are mapped
docker port qbittorrent

# Should show:
# 6881/tcp -> 0.0.0.0:6881
# 6881/udp -> 0.0.0.0:6881
# 8080/tcp -> 0.0.0.0:8080
```

### **Monitor Progress**
```bash
# Watch logs for connection info
docker logs -f qbittorrent | grep -i "DHT\|peer\|announce"
```

---

## 🎯 Expected Results

**After fixing:**
- ✅ Torrents start downloading immediately
- ✅ Multiple peers connect quickly  
- ✅ Download speeds match your connection
- ✅ No more "stalled" status

**If still having issues:**
- Check host firewall (port 6881)
- Verify ISP doesn't block BitTorrent
- Try different trackers/indexers
- Consider VPN if ISP throttles P2P

---

## 💡 Pro Tips

1. **Use popular torrents first** - they have more peers
2. **Enable DHT/PeX/LSD** - helps find peers without trackers
3. **Increase connection limits** - Docker can handle more connections
4. **Monitor with bot** - Use `/qdiag` and `/dockerfix` regularly
5. **Test with Ubuntu ISO** - always works if network is correct

The key is proper port mapping - Docker containers can't accept incoming connections without it!
