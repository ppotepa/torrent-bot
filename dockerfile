FROM python:3.11-slim

WORKDIR /app

# Install ffmpeg, curl, git, and TTS dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    git \
    espeak \
    espeak-data \
    && rm -rf /var/lib/apt/lists/*

# Install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 🔥 Update yt-dlp to latest version
RUN yt-dlp -U || true

# Copy bot + plugins
COPY . .

CMD ["python", "bot.py"]
