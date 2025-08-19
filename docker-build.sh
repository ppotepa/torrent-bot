#!/bin/bash

# Docker Build Script with Optimized Caching
# This script builds the Docker image with maximum cache efficiency

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
IMAGE_NAME="telegram-bot"
DOCKERFILE="Dockerfile"
BUILD_ARGS=""

# Parse command line arguments
FORCE_REBUILD=false
DEV_MODE=false
NO_CACHE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --force|-f)
            FORCE_REBUILD=true
            shift
            ;;
        --dev|-d)
            DEV_MODE=true
            shift
            ;;
        --no-cache|-n)
            NO_CACHE=true
            shift
            ;;
        --help|-h)
            echo "Docker Build Script for Telegram Bot"
            echo ""
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --force, -f     Force complete rebuild (ignore cache)"
            echo "  --dev, -d       Development mode (mount source code)"
            echo "  --no-cache, -n  Build without using cache"
            echo "  --help, -h      Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0              # Normal build with cache"
            echo "  $0 --dev        # Development build"
            echo "  $0 --force      # Force complete rebuild"
            exit 0
            ;;
        *)
            echo "Unknown option $1"
            exit 1
            ;;
    esac
done

echo -e "${BLUE}🐳 Docker Build Script for Telegram Bot${NC}"
echo "=============================================="

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running. Please start Docker first.${NC}"
    exit 1
fi

# Enable BuildKit for better caching
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1

echo -e "${BLUE}📋 Build Configuration:${NC}"
echo "  Image name: $IMAGE_NAME"
echo "  Dockerfile: $DOCKERFILE"
echo "  Force rebuild: $FORCE_REBUILD"
echo "  Development mode: $DEV_MODE"
echo "  No cache: $NO_CACHE"
echo ""

# Build cache arguments
CACHE_ARGS=""
if [ "$NO_CACHE" = false ]; then
    # Try to pull existing images for cache
    echo -e "${YELLOW}📦 Pulling existing images for cache...${NC}"
    docker pull $IMAGE_NAME:base-system 2>/dev/null || echo "  No base-system cache found"
    docker pull $IMAGE_NAME:python-deps 2>/dev/null || echo "  No python-deps cache found"
    docker pull $IMAGE_NAME:latest 2>/dev/null || echo "  No latest cache found"
    
    CACHE_ARGS="--cache-from $IMAGE_NAME:base-system --cache-from $IMAGE_NAME:python-deps --cache-from $IMAGE_NAME:latest"
fi

# Build arguments
BUILD_ARGS="--build-arg BUILDKIT_INLINE_CACHE=1"

if [ "$FORCE_REBUILD" = true ]; then
    BUILD_ARGS="$BUILD_ARGS --no-cache"
    echo -e "${YELLOW}⚠️  Force rebuild enabled - ignoring all cache${NC}"
fi

# Build the image
echo -e "${BLUE}🔨 Building Docker image...${NC}"

if [ "$DEV_MODE" = true ]; then
    echo -e "${YELLOW}🚀 Development mode - building up to python-deps stage${NC}"
    docker build \
        --target python-deps \
        --tag $IMAGE_NAME:python-deps \
        --tag $IMAGE_NAME:dev \
        $CACHE_ARGS \
        $BUILD_ARGS \
        -f $DOCKERFILE \
        .
    
    # Tag intermediate stages for caching
    docker build \
        --target base-system \
        --tag $IMAGE_NAME:base-system \
        $CACHE_ARGS \
        $BUILD_ARGS \
        -f $DOCKERFILE \
        .
else
    echo -e "${GREEN}🏗️  Production mode - building complete image${NC}"
    docker build \
        --tag $IMAGE_NAME:latest \
        $CACHE_ARGS \
        $BUILD_ARGS \
        -f $DOCKERFILE \
        .
    
    # Tag intermediate stages for future caching
    docker build \
        --target base-system \
        --tag $IMAGE_NAME:base-system \
        $CACHE_ARGS \
        $BUILD_ARGS \
        -f $DOCKERFILE \
        .
    
    docker build \
        --target python-deps \
        --tag $IMAGE_NAME:python-deps \
        $CACHE_ARGS \
        $BUILD_ARGS \
        -f $DOCKERFILE \
        .
fi

echo ""
echo -e "${GREEN}✅ Build completed successfully!${NC}"

# Show image information
echo -e "${BLUE}📊 Image Information:${NC}"
docker images | grep $IMAGE_NAME | head -5

echo ""
echo -e "${BLUE}🚀 Next Steps:${NC}"
if [ "$DEV_MODE" = true ]; then
    echo "  Development build ready!"
    echo "  Run: docker-compose -f docker-compose.yaml -f docker-compose.dev.yaml up"
else
    echo "  Production build ready!"
    echo "  Run: docker-compose up"
fi

echo ""
echo -e "${YELLOW}💡 Tips:${NC}"
echo "  • Use --dev for faster rebuilds during development"
echo "  • Use --force only when you need to rebuild everything"
echo "  • The multi-stage build caches system deps and Python deps separately"
echo "  • Source code changes only rebuild the final app layer"

