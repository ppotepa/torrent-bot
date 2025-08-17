# PowerShell startup script for torrent-bot with zerotier network

Write-Host "🚀 Starting Torrent Bot with zerotier network..." -ForegroundColor Cyan

# Ensure zerotier network exists
Write-Host "🌐 Checking zerotier network..." -ForegroundColor Cyan
$networkExists = docker network ls | Select-String "zerotier"
if (-not $networkExists) {
    Write-Host "📡 Creating zerotier network..." -ForegroundColor Yellow
    docker network create zerotier
    Write-Host "✅ Zerotier network created" -ForegroundColor Green
} else {
    Write-Host "✅ Zerotier network already exists" -ForegroundColor Green
}

# Stop any existing containers
Write-Host "⏹️ Stopping existing containers..." -ForegroundColor Yellow
docker-compose down

# Remove any banned IPs from previous runs
Write-Host "🧹 Cleaning up any IP bans..." -ForegroundColor Green
$bannedIpsPath = "D:\qbittorrent-config\qBittorrent\banned_IPs.dat"
if (Test-Path $bannedIpsPath) {
    Remove-Item $bannedIpsPath -Force
    Write-Host "✅ Removed banned IPs file from D drive" -ForegroundColor Green
}

# Ensure directories exist on D drive
Write-Host "📁 Creating necessary directories on D drive..." -ForegroundColor Cyan
$downloadsPath = "D:\downloads"
$configPath = "D:\qbittorrent-config"
if (-not (Test-Path $downloadsPath)) { New-Item -ItemType Directory -Path $downloadsPath -Force }
if (-not (Test-Path $configPath)) { New-Item -ItemType Directory -Path $configPath -Force }

# Start all services
Write-Host "▶️ Starting all services..." -ForegroundColor Green
docker-compose up -d

# Wait for services to start
Write-Host "⏳ Waiting for services to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

# Check service status
Write-Host "🔍 Checking service status..." -ForegroundColor Cyan

# Get container IPs
try {
    $qbitIP = docker inspect qbittorrent --format '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' 2>$null
    if (-not $qbitIP) { $qbitIP = "container not found" }
} catch {
    $qbitIP = "container not found"
}

# Check qBittorrent
$qbitWorking = $false
if ($qbitIP -ne "container not found") {
    try {
        Invoke-WebRequest -Uri "http://$qbitIP:8080" -TimeoutSec 5 -ErrorAction Stop | Out-Null
        Write-Host "✅ qBittorrent is running at http://$qbitIP:8080 (zerotier network)" -ForegroundColor Green
        $qbitWorking = $true
    } catch { }
}

if (-not $qbitWorking) {
    try {
        Invoke-WebRequest -Uri "http://localhost:8080" -TimeoutSec 5 -ErrorAction Stop | Out-Null
        Write-Host "✅ qBittorrent is running at http://localhost:8080 (host network)" -ForegroundColor Green
    } catch {
        Write-Host "❌ qBittorrent is not responding" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "📊 Container Status:" -ForegroundColor Cyan
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

Write-Host ""
Write-Host "🌐 Network Information:" -ForegroundColor Cyan
$zerotierNetwork = docker network ls | Select-String "zerotier"
if ($zerotierNetwork) {
    Write-Host "   Zerotier network: Found" -ForegroundColor Green
} else {
    Write-Host "   Zerotier network: Not found" -ForegroundColor Red
}
Write-Host "   qBittorrent IP: $qbitIP" -ForegroundColor White

Write-Host ""
Write-Host "🎉 Startup complete!" -ForegroundColor Green
Write-Host "💡 If you still have issues:" -ForegroundColor Yellow
Write-Host "   1. Check container logs: docker logs telegram-bot" -ForegroundColor White
Write-Host "   2. Check qBittorrent logs: docker logs qbittorrent" -ForegroundColor White
Write-Host "   3. Verify zerotier network connectivity" -ForegroundColor White
Write-Host "   4. Access qBittorrent WebUI: http://localhost:8080 or http://$qbitIP:8080 (admin/adminadmin)" -ForegroundColor White
