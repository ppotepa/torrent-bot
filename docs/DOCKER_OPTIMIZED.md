# 🐳 Optimized Docker Setup

## Overview

This Docker setup is optimized to **minimize rebuild times** and **maximize cache efficiency**. It uses a multi-stage build that separates:

1. **System dependencies** (rarely change) - cached for weeks
2. **Python dependencies** (change when requirements.txt changes) - cached until requirements change
3. **Application code** (changes frequently) - only this layer rebuilds during development

## 🚀 Quick Start

### **Development Mode (Recommended)**
```bash
# Build for development (faster rebuilds)
docker-build.bat --dev

# Run with hot-reload
docker-compose -f docker-compose.yaml -f docker-compose.dev.yaml up
```

### **Production Mode**
```bash
# Build complete image
docker-build.bat

# Run production stack
docker-compose up -d
```

## 📁 File Structure

```
├── Dockerfile              # Multi-stage optimized Dockerfile
├── docker-compose.yaml     # Main compose file
├── docker-compose.dev.yaml # Development overrides
├── docker-build.bat        # Optimized build script (Windows)
├── docker-build.sh         # Optimized build script (Linux/Mac)
└── .dockerignore           # Optimized build context
```

## 🏗️ Multi-Stage Build Explained

### **Stage 1: base-system**
- Installs system packages (ffmpeg, curl, git, espeak)
- **Cached until:** System dependencies change (rarely)
- **Build time:** ~2-3 minutes first time, then cached

### **Stage 2: python-deps**
- Installs Python packages from requirements.txt
- **Cached until:** requirements.txt changes
- **Build time:** ~1-2 minutes first time, then cached

### **Stage 3: app**
- Copies application code
- **Cached until:** Source code changes
- **Build time:** ~10-30 seconds

## ⚡ Build Performance

| Scenario | Build Time | Cache Used |
|----------|------------|------------|
| **First build** | ~5-8 minutes | None |
| **Code change only** | ~10-30 seconds | Stages 1+2 |
| **Requirements change** | ~1-3 minutes | Stage 1 only |
| **System deps change** | ~5-8 minutes | None |

## 🛠️ Build Commands

### **Windows**
```batch
REM Development build (fastest for code changes)
docker-build.bat --dev

REM Production build
docker-build.bat

REM Force complete rebuild (when cache is corrupted)
docker-build.bat --force

REM Build without any cache
docker-build.bat --no-cache
```

### **Linux/Mac**
```bash
# Development build (fastest for code changes)
./docker-build.sh --dev

# Production build
./docker-build.sh

# Force complete rebuild
./docker-build.sh --force

# Build without any cache
./docker-build.sh --no-cache
```

## 🔧 Docker Compose Modes

### **Development Mode**
```bash
# Uses docker-compose.dev.yaml overrides
docker-compose -f docker-compose.yaml -f docker-compose.dev.yaml up

# Features:
# ✅ Source code mounted as volume (hot-reload)
# ✅ Faster startup (no health checks)
# ✅ Debug environment variables
# ✅ Auto-restart disabled for manual control
```

### **Production Mode**
```bash
# Uses main docker-compose.yaml only
docker-compose up -d

# Features:
# ✅ Complete image build
# ✅ Health checks enabled
# ✅ Auto-restart on failure
# ✅ Optimized for stability
```

## 📦 Services Included

### **telegram-bot**
- Main bot application
- **Ports:** None (connects to Telegram API)
- **Volumes:** Downloads, audiobooks, logs
- **Dependencies:** qbittorrent

### **qbittorrent**
- Torrent client with web UI
- **Ports:** 8080 (Web UI), 6881 (Torrents)
- **Volumes:** Downloads, config
- **Health check:** HTTP check on port 8080

### **jackett** (Optional)
- Torrent indexer proxy
- **Ports:** 9117 (Web UI)
- **Volumes:** Config, downloads
- **Enable with:** `--profile jackett`

## 🎯 Optimization Features

### **BuildKit Caching**
- Uses Docker BuildKit for advanced caching
- Inline cache metadata stored in images
- Pull existing images for cache reuse

### **Smart .dockerignore**
- Excludes unnecessary files from build context
- Reduces build context size by ~80%
- Faster context transfer to Docker daemon

### **Volume Mounting**
```yaml
# Development: Source code mounted for hot-reload
volumes:
  - "./src:/app/src"
  - "./bot.py:/app/bot.py"

# Production: Only data directories mounted
volumes:
  - "./downloads:/app/downloads"
  - "./audiobooks:/app/audiobooks"
```

### **Health Checks**
- Services have proper health checks
- Dependencies wait for health before starting
- Automatic restart on health check failure

## 🚀 Development Workflow

### **1. Initial Setup**
```bash
# Build development image
docker-build.bat --dev

# Start services
docker-compose -f docker-compose.yaml -f docker-compose.dev.yaml up
```

### **2. Code Changes**
- Edit files in `src/` directory
- Changes are immediately reflected (volume mounted)
- No rebuild needed for code changes

### **3. Requirements Changes**
```bash
# Rebuild when requirements.txt changes
docker-build.bat --dev

# Restart services
docker-compose -f docker-compose.yaml -f docker-compose.dev.yaml up --force-recreate
```

### **4. System Dependencies Changes**
```bash
# Full rebuild when Dockerfile changes
docker-build.bat --force

# Restart services
docker-compose -f docker-compose.yaml -f docker-compose.dev.yaml up --force-recreate
```

## 📊 Monitoring and Logs

### **View Logs**
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f telegram-bot

# Last 100 lines
docker-compose logs --tail=100 telegram-bot
```

### **Service Status**
```bash
# Check running containers
docker-compose ps

# Check health status
docker-compose ps --format table
```

### **Resource Usage**
```bash
# Container resource usage
docker stats

# Container details
docker inspect telegram-bot
```

## 🔧 Troubleshooting

### **Build Issues**
```bash
# Clear all cache and rebuild
docker-build.bat --force --no-cache

# Remove old images
docker image prune -f

# Remove all unused data
docker system prune -f
```

### **Runtime Issues**
```bash
# Restart services
docker-compose restart

# Recreate containers
docker-compose up --force-recreate

# Check service logs
docker-compose logs telegram-bot
```

### **Performance Issues**
```bash
# Check resource usage
docker stats

# Optimize Docker Desktop settings:
# - Increase memory allocation (4GB+)
# - Enable WSL 2 backend (Windows)
# - Disable unused features
```

## 🎯 Best Practices

### **Development**
1. Always use `--dev` flag for development builds
2. Use development compose file for hot-reload
3. Keep requirements.txt changes separate from code changes
4. Use `docker-compose logs -f` to monitor issues

### **Production**
1. Use production build without `--dev` flag
2. Run services in detached mode (`-d`)
3. Set up proper environment variables
4. Monitor health checks and logs
5. Set up log rotation for long-running containers

### **Cache Optimization**
1. Don't use `--no-cache` unless absolutely necessary
2. Pull existing images before building for better cache
3. Keep Dockerfile instructions in optimal order
4. Use `.dockerignore` to minimize build context

## 🔄 Migration from Old Setup

If you're migrating from the old Docker setup:

1. **Backup your data:**
   ```bash
   # Backup downloads and config
   cp -r downloads downloads-backup
   cp -r qbittorrent-config qbittorrent-config-backup
   ```

2. **Stop old containers:**
   ```bash
   docker-compose down
   ```

3. **Build new optimized image:**
   ```bash
   docker-build.bat --dev
   ```

4. **Start with new setup:**
   ```bash
   docker-compose -f docker-compose.yaml -f docker-compose.dev.yaml up
   ```

The new setup is **fully backward compatible** with your existing data and configuration files.

