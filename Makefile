# Makefile for Telegram Bot Docker Operations
.PHONY: help build build-dev build-force up up-dev down logs clean test

# Default target
help:
	@echo "🤖 Telegram Bot Docker Commands"
	@echo "================================"
	@echo ""
	@echo "Build Commands:"
	@echo "  build       - Build production image with cache"
	@echo "  build-dev   - Build development image (faster rebuilds)"
	@echo "  build-force - Force complete rebuild (ignore cache)"
	@echo ""
	@echo "Run Commands:"
	@echo "  up          - Start production stack"
	@echo "  up-dev      - Start development stack (hot-reload)"
	@echo "  down        - Stop all services"
	@echo ""
	@echo "Utility Commands:"
	@echo "  logs        - Show logs from all services"
	@echo "  logs-bot    - Show logs from bot only"
	@echo "  test        - Run system tests"
	@echo "  clean       - Clean unused Docker resources"
	@echo ""
	@echo "Examples:"
	@echo "  make build-dev && make up-dev    # Development workflow"
	@echo "  make build && make up             # Production deployment"

# Build commands
build:
	@echo "🏗️ Building production image..."
	docker-build.bat

build-dev:
	@echo "🚀 Building development image..."
	docker-build.bat --dev

build-force:
	@echo "⚠️ Force rebuilding all layers..."
	docker-build.bat --force

# Run commands
up:
	@echo "🚀 Starting production stack..."
	docker-compose up -d

up-dev:
	@echo "🛠️ Starting development stack..."
	docker-compose -f docker-compose.yaml -f docker-compose.dev.yaml up

down:
	@echo "🛑 Stopping all services..."
	docker-compose down

# Utility commands
logs:
	@echo "📋 Showing logs from all services..."
	docker-compose logs -f

logs-bot:
	@echo "📋 Showing bot logs..."
	docker-compose logs -f telegram-bot

test:
	@echo "🧪 Running system tests..."
	cd src && python test_system.py

clean:
	@echo "🧹 Cleaning unused Docker resources..."
	docker image prune -f
	docker container prune -f
	docker volume prune -f

# Development workflow shortcuts
dev: build-dev up-dev

prod: build up

# Restart services
restart:
	docker-compose restart

restart-bot:
	docker-compose restart telegram-bot

# Show status
status:
	docker-compose ps
	@echo ""
	@echo "📊 Resource usage:"
	docker stats --no-stream

