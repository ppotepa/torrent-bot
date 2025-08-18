# FFmpeg Installation Guide for MP3 Support

## Why FFmpeg is needed
FFmpeg is required to convert audio from Facebook videos to MP3 format. Without it, the bot will download audio in the original format (usually M4A or WebM).

## Installation Options

### Option 1: Chocolatey (Recommended for Windows)
```powershell
# Install Chocolatey first (if not already installed)
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Install FFmpeg
choco install ffmpeg
```

### Option 2: Direct Download
1. Go to https://ffmpeg.org/download.html
2. Download the Windows build
3. Extract to a folder (e.g., `C:\ffmpeg`)
4. Add `C:\ffmpeg\bin` to your PATH environment variable

### Option 3: Winget (Windows Package Manager)
```powershell
winget install ffmpeg
```

## Verification
After installation, restart your terminal and run:
```powershell
ffmpeg -version
```

You should see FFmpeg version information.

## Benefits
Once FFmpeg is installed:
- ✅ Facebook audio downloads will be converted to MP3 format
- ✅ Better compatibility with audio players
- ✅ Smaller file sizes in most cases
- ✅ Consistent audio format across all downloads

## Current Behavior (Without FFmpeg)
- ✅ Audio downloads still work
- ⚠️ Files are saved in original format (M4A, WebM, etc.)
- ⚠️ Some devices/players may not support these formats
- ✅ No permission errors (this has been fixed)

## Test After Installation
After installing FFmpeg, test with:
```
/dl https://facebook.com/watch?v=VIDEO_ID:[audio]
```

The bot should now download and convert to MP3 format automatically.
