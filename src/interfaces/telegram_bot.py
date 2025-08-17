"""Telegram bot interface following the Interface Segregation Principle."""

from abc import ABC, abstractmethod
from typing import Any, Callable, Optional, Dict, List
from dataclasses import dataclass


@dataclass
class BotMessage:
    """Data class representing a bot message."""
    chat_id: int
    text: str
    reply_to_message_id: Optional[int] = None
    parse_mode: Optional[str] = None
    reply_markup: Optional[Any] = None


@dataclass
class BotUpdate:
    """Data class representing a bot update."""
    update_id: int
    message: Optional[Any] = None
    callback_query: Optional[Any] = None


class ITelegramBot(ABC):
    """Interface for Telegram bot operations."""
    
    @abstractmethod
    async def send_message(self, message: BotMessage) -> bool:
        """Send a message."""
        pass
    
    @abstractmethod
    async def edit_message(self, chat_id: int, message_id: int, text: str, reply_markup: Any = None) -> bool:
        """Edit an existing message."""
        pass
    
    @abstractmethod
    async def delete_message(self, chat_id: int, message_id: int) -> bool:
        """Delete a message."""
        pass
    
    @abstractmethod
    def add_handler(self, handler: Callable, filter_type: str = "message") -> None:
        """Add a message handler."""
        pass
    
    @abstractmethod
    async def start_polling(self) -> None:
        """Start bot polling."""
        pass
    
    @abstractmethod
    async def stop_polling(self) -> None:
        """Stop bot polling."""
        pass


class INotificationService(ABC):
    """Interface for notification services."""
    
    @abstractmethod
    async def notify_download_started(self, torrent_name: str, chat_id: int) -> None:
        """Notify when download starts."""
        pass
    
    @abstractmethod
    async def notify_download_completed(self, torrent_name: str, chat_id: int) -> None:
        """Notify when download completes."""
        pass
    
    @abstractmethod
    async def notify_download_failed(self, torrent_name: str, error: str, chat_id: int) -> None:
        """Notify when download fails."""
        pass
    
    @abstractmethod
    async def notify_search_results(self, results: List[Any], chat_id: int) -> None:
        """Notify with search results."""
        pass
