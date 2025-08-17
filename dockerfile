FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Update yt-dlp to latest version
RUN yt-dlp -U || true

# Copy application code with SOLID architecture
COPY . .

# Create downloads directory
RUN mkdir -p /app/downloads

# Use modern bot with SOLID architecture
CMD ["python", "modern_bot.py"]
