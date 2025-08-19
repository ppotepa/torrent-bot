@echo off
REM Docker Build Script with Optimized Caching for Windows
REM This script builds the Docker image with maximum cache efficiency

setlocal enabledelayedexpansion

REM Configuration
set IMAGE_NAME=telegram-bot
set DOCKERFILE=Dockerfile
set BUILD_ARGS=
set FORCE_REBUILD=false
set DEV_MODE=false
set NO_CACHE=false

REM Parse command line arguments
:parse_args
if "%~1"=="" goto end_parse
if /i "%~1"=="--force" set FORCE_REBUILD=true
if /i "%~1"=="-f" set FORCE_REBUILD=true
if /i "%~1"=="--dev" set DEV_MODE=true
if /i "%~1"=="-d" set DEV_MODE=true
if /i "%~1"=="--no-cache" set NO_CACHE=true
if /i "%~1"=="-n" set NO_CACHE=true
if /i "%~1"=="--help" goto show_help
if /i "%~1"=="-h" goto show_help
shift
goto parse_args

:show_help
echo Docker Build Script for Telegram Bot
echo.
echo Usage: %~nx0 [OPTIONS]
echo.
echo Options:
echo   --force, -f     Force complete rebuild (ignore cache)
echo   --dev, -d       Development mode (mount source code)
echo   --no-cache, -n  Build without using cache
echo   --help, -h      Show this help message
echo.
echo Examples:
echo   %~nx0              # Normal build with cache
echo   %~nx0 --dev        # Development build
echo   %~nx0 --force      # Force complete rebuild
exit /b 0

:end_parse

echo.
echo 🐳 Docker Build Script for Telegram Bot
echo ==============================================

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not running. Please start Docker first.
    exit /b 1
)

REM Enable BuildKit for better caching
set DOCKER_BUILDKIT=1
set COMPOSE_DOCKER_CLI_BUILD=1

echo.
echo 📋 Build Configuration:
echo   Image name: %IMAGE_NAME%
echo   Dockerfile: %DOCKERFILE%
echo   Force rebuild: %FORCE_REBUILD%
echo   Development mode: %DEV_MODE%
echo   No cache: %NO_CACHE%
echo.

REM Build cache arguments
set CACHE_ARGS=
if /i "%NO_CACHE%"=="false" (
    echo 📦 Pulling existing images for cache...
    docker pull %IMAGE_NAME%:base-system 2>nul || echo   No base-system cache found
    docker pull %IMAGE_NAME%:python-deps 2>nul || echo   No python-deps cache found
    docker pull %IMAGE_NAME%:latest 2>nul || echo   No latest cache found
    
    set CACHE_ARGS=--cache-from %IMAGE_NAME%:base-system --cache-from %IMAGE_NAME%:python-deps --cache-from %IMAGE_NAME%:latest
)

REM Build arguments
set BUILD_ARGS=--build-arg BUILDKIT_INLINE_CACHE=1

if /i "%FORCE_REBUILD%"=="true" (
    set BUILD_ARGS=%BUILD_ARGS% --no-cache
    echo ⚠️  Force rebuild enabled - ignoring all cache
)

REM Build the image
echo.
echo 🔨 Building Docker image...

if /i "%DEV_MODE%"=="true" (
    echo 🚀 Development mode - building up to python-deps stage
    docker build --target python-deps --tag %IMAGE_NAME%:python-deps --tag %IMAGE_NAME%:dev %CACHE_ARGS% %BUILD_ARGS% -f %DOCKERFILE% .
    
    REM Tag intermediate stages for caching
    docker build --target base-system --tag %IMAGE_NAME%:base-system %CACHE_ARGS% %BUILD_ARGS% -f %DOCKERFILE% .
) else (
    echo 🏗️  Production mode - building complete image
    docker build --tag %IMAGE_NAME%:latest %CACHE_ARGS% %BUILD_ARGS% -f %DOCKERFILE% .
    
    REM Tag intermediate stages for future caching
    docker build --target base-system --tag %IMAGE_NAME%:base-system %CACHE_ARGS% %BUILD_ARGS% -f %DOCKERFILE% .
    docker build --target python-deps --tag %IMAGE_NAME%:python-deps %CACHE_ARGS% %BUILD_ARGS% -f %DOCKERFILE% .
)

echo.
echo ✅ Build completed successfully!

REM Show image information
echo.
echo 📊 Image Information:
docker images | findstr %IMAGE_NAME%

echo.
echo 🚀 Next Steps:
if /i "%DEV_MODE%"=="true" (
    echo   Development build ready!
    echo   Run: docker-compose -f docker-compose.yaml -f docker-compose.dev.yaml up
) else (
    echo   Production build ready!
    echo   Run: docker-compose up
)

echo.
echo 💡 Tips:
echo   • Use --dev for faster rebuilds during development
echo   • Use --force only when you need to rebuild everything
echo   • The multi-stage build caches system deps and Python deps separately
echo   • Source code changes only rebuild the final app layer

endlocal

