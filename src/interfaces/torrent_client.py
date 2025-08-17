"""Torrent client interface following the Interface Segregation Principle."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class TorrentInfo:
    """Data class representing torrent information."""
    name: str
    hash: str
    size: int
    progress: float
    status: str
    download_speed: int
    upload_speed: int
    eta: int
    priority: int
    category: str


@dataclass
class AddTorrentResult:
    """Result of adding a torrent."""
    success: bool
    message: str
    torrent_hash: Optional[str] = None


class ITorrentClient(ABC):
    """Interface for torrent client operations."""
    
    @abstractmethod
    async def connect(self) -> bool:
        """Connect to the torrent client."""
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect from the torrent client."""
        pass
    
    @abstractmethod
    async def add_torrent(self, magnet_link: str, category: str = "", save_path: str = "") -> AddTorrentResult:
        """Add a torrent via magnet link."""
        pass
    
    @abstractmethod
    async def get_torrents(self) -> List[TorrentInfo]:
        """Get list of all torrents."""
        pass
    
    @abstractmethod
    async def get_torrent_info(self, torrent_hash: str) -> Optional[TorrentInfo]:
        """Get information about specific torrent."""
        pass
    
    @abstractmethod
    async def pause_torrent(self, torrent_hash: str) -> bool:
        """Pause a torrent."""
        pass
    
    @abstractmethod
    async def resume_torrent(self, torrent_hash: str) -> bool:
        """Resume a torrent."""
        pass
    
    @abstractmethod
    async def delete_torrent(self, torrent_hash: str, delete_files: bool = False) -> bool:
        """Delete a torrent."""
        pass
    
    @abstractmethod
    async def set_category(self, torrent_hash: str, category: str) -> bool:
        """Set torrent category."""
        pass
