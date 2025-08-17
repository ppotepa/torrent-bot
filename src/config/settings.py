"""Application configuration following Single Responsibility Principle."""

import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from pathlib import Path


@dataclass
class QBittorrentConfig:
    """qBittorrent client configuration."""
    host: str = "qbittorrent"
    port: int = 8080
    username: str = "admin"
    password: str = "adminpass"
    use_https: bool = False
    
    @property
    def base_url(self) -> str:
        """Get the base URL for qBittorrent."""
        protocol = "https" if self.use_https else "http"
        return f"{protocol}://{self.host}:{self.port}"


@dataclass
class JackettConfig:
    """Jackett search provider configuration."""
    host: str = "jackett"
    port: int = 9117
    api_key: str = ""
    use_https: bool = False
    
    @property
    def base_url(self) -> str:
        """Get the base URL for Jackett."""
        protocol = "https" if self.use_https else "http"
        return f"{protocol}://{self.host}:{self.port}"


@dataclass
class TelegramConfig:
    """Telegram bot configuration."""
    bot_token: str = ""
    allowed_users: List[int] = field(default_factory=list)
    admin_chat_id: Optional[int] = None
    notification_chat_id: Optional[int] = None


@dataclass
class DownloadConfig:
    """Download configuration."""
    default_path: str = "D:\\downloads"
    completed_path: str = "D:\\downloads\\completed"
    temp_path: str = "D:\\downloads\\temp"
    categories: Dict[str, str] = field(default_factory=lambda: {
        "movies": "D:\\downloads\\movies",
        "tv": "D:\\downloads\\tv",
        "music": "D:\\downloads\\music",
        "games": "D:\\downloads\\games",
        "software": "D:\\downloads\\software",
        "books": "D:\\downloads\\books",
        "anime": "D:\\downloads\\anime"
    })
    
    def get_category_path(self, category: str) -> str:
        """Get download path for specific category."""
        return self.categories.get(category.lower(), self.default_path)


@dataclass
class SearchConfig:
    """Search configuration."""
    default_limit: int = 50
    min_seeders: int = 1
    timeout_seconds: int = 30
    fallback_providers: List[str] = field(default_factory=lambda: ["jackett"])


@dataclass
class AppConfig:
    """Main application configuration."""
    qbittorrent: QBittorrentConfig = field(default_factory=QBittorrentConfig)
    jackett: JackettConfig = field(default_factory=JackettConfig)
    telegram: TelegramConfig = field(default_factory=TelegramConfig)
    download: DownloadConfig = field(default_factory=DownloadConfig)
    search: SearchConfig = field(default_factory=SearchConfig)
    debug: bool = False
    log_level: str = "INFO"
    
    @classmethod
    def from_env(cls) -> "AppConfig":
        """Create configuration from environment variables."""
        config = cls()
        
        # qBittorrent config
        config.qbittorrent.host = os.getenv("QBIT_HOST", "qbittorrent")
        config.qbittorrent.port = int(os.getenv("QBIT_PORT", "8080"))
        config.qbittorrent.username = os.getenv("QBIT_USERNAME", "admin")
        config.qbittorrent.password = os.getenv("QBIT_PASSWORD", "adminpass")
        config.qbittorrent.use_https = os.getenv("QBIT_HTTPS", "false").lower() == "true"
        
        # Jackett config
        config.jackett.host = os.getenv("JACKETT_HOST", "jackett")
        config.jackett.port = int(os.getenv("JACKETT_PORT", "9117"))
        config.jackett.api_key = os.getenv("JACKETT_API_KEY", "")
        config.jackett.use_https = os.getenv("JACKETT_HTTPS", "false").lower() == "true"
        
        # Telegram config
        config.telegram.bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
        allowed_users_str = os.getenv("TELEGRAM_ALLOWED_USERS", "")
        if allowed_users_str:
            config.telegram.allowed_users = [int(uid.strip()) for uid in allowed_users_str.split(",")]
        
        admin_chat_id = os.getenv("TELEGRAM_ADMIN_CHAT_ID")
        if admin_chat_id:
            config.telegram.admin_chat_id = int(admin_chat_id)
            
        notification_chat_id = os.getenv("TELEGRAM_NOTIFICATION_CHAT_ID")
        if notification_chat_id:
            config.telegram.notification_chat_id = int(notification_chat_id)
        
        # Download config
        config.download.default_path = os.getenv("DOWNLOAD_PATH", "D:\\downloads")
        config.download.completed_path = os.getenv("COMPLETED_PATH", "D:\\downloads\\completed")
        config.download.temp_path = os.getenv("TEMP_PATH", "D:\\downloads\\temp")
        
        # Search config
        config.search.default_limit = int(os.getenv("SEARCH_LIMIT", "50"))
        config.search.min_seeders = int(os.getenv("MIN_SEEDERS", "1"))
        config.search.timeout_seconds = int(os.getenv("SEARCH_TIMEOUT", "30"))
        
        # App config
        config.debug = os.getenv("DEBUG", "false").lower() == "true"
        config.log_level = os.getenv("LOG_LEVEL", "INFO")
        
        return config
    
    def validate(self) -> List[str]:
        """Validate configuration and return list of errors."""
        errors = []
        
        if not self.telegram.bot_token:
            errors.append("Telegram bot token is required")
        
        if not self.jackett.api_key:
            errors.append("Jackett API key is required")
        
        if not self.telegram.allowed_users:
            errors.append("At least one allowed Telegram user is required")
        
        # Validate paths exist or can be created
        paths_to_check = [
            self.download.default_path,
            self.download.completed_path,
            self.download.temp_path
        ]
        paths_to_check.extend(self.download.categories.values())
        
        for path in paths_to_check:
            try:
                Path(path).mkdir(parents=True, exist_ok=True)
            except Exception as e:
                errors.append(f"Cannot create/access path {path}: {e}")
        
        return errors
