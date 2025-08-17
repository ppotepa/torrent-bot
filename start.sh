#!/bin/bash
# Startup script for torrent-bot with zerotier network

echo "🚀 Starting Torrent Bot with zerotier network..."

# Ensure zerotier network exists
echo "🌐 Checking zerotier network..."
if ! docker network ls | grep -q zerotier; then
    echo "📡 Creating zerotier network..."
    docker network create zerotier
    echo "✅ Zerotier network created"
else
    echo "✅ Zerotier network already exists"
fi

# Stop any existing containers
echo "⏹️ Stopping existing containers..."
docker-compose down

# Remove any banned IPs from previous runs
echo "🧹 Cleaning up any IP bans..."
D_DRIVE_CONFIG_PATH="D:\\qbittorrent-config\\qBittorrent\\banned_IPs.dat"
if [ -f "$D_DRIVE_CONFIG_PATH" ]; then
    rm -f "$D_DRIVE_CONFIG_PATH"
    echo "✅ Removed banned IPs file from D drive"
fi

# Ensure directories exist on D drive
echo "📁 Creating necessary directories on D drive..."
mkdir -p "D:\\downloads"
mkdir -p "D:\\qbittorrent-config"

# Start all services
echo "▶️ Starting all services..."
docker-compose up -d

# Wait for services to start
echo "⏳ Waiting for services to initialize..."
sleep 15

# Check service status
echo "🔍 Checking service status..."

# Get qBittorrent container IP for testing
QBIT_IP=$(docker inspect qbittorrent --format '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' 2>/dev/null || echo "container not found")

# Check qBittorrent
if [ "$QBIT_IP" != "container not found" ] && curl -s -f http://$QBIT_IP:8080 > /dev/null; then
    echo "✅ qBittorrent is running at http://$QBIT_IP:8080 (zerotier network)"
elif curl -s -f http://localhost:8080 > /dev/null; then
    echo "✅ qBittorrent is running at http://localhost:8080 (host network)"
else
    echo "❌ qBittorrent is not responding"
fi

# Check FlareSolverr
FLARE_IP=$(docker inspect flaresolverr --format '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' 2>/dev/null || echo "container not found")
if [ "$FLARE_IP" != "container not found" ] && curl -s -f http://$FLARE_IP:8191 > /dev/null; then
    echo "✅ FlareSolverr is running at http://$FLARE_IP:8191 (zerotier network)"
elif curl -s -f http://localhost:8191 > /dev/null; then
    echo "✅ FlareSolverr is running at http://localhost:8191 (host network)"
else
    echo "❌ FlareSolverr is not responding"
fi

# Show container status
echo ""
echo "📊 Container Status:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "� Network Information:"
echo "   Zerotier network: $(docker network ls | grep zerotier || echo 'Not found')"
echo "   qBittorrent IP: $QBIT_IP"
echo "   FlareSolverr IP: $FLARE_IP"

echo ""
echo "�🎉 Startup complete!"
echo "💡 If you still have issues:"
echo "   1. Check container logs: docker logs telegram-bot"
echo "   2. Check qBittorrent logs: docker logs qbittorrent"
echo "   3. Verify zerotier network connectivity"
echo "   4. Access qBittorrent WebUI: http://localhost:8080 or http://$QBIT_IP:8080 (admin/adminadmin)"
