"""Search provider interface following the Interface Segregation Principle."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


class SearchCategory(Enum):
    """Supported search categories."""
    MOVIES = "movies"
    TV_SHOWS = "tv"
    MUSIC = "music"
    GAMES = "games"
    SOFTWARE = "software"
    BOOKS = "books"
    ANIME = "anime"
    ALL = "all"


@dataclass
class SearchResult:
    """Data class representing a search result."""
    title: str
    size: int
    seeders: int
    leechers: int
    category: str
    magnet_link: str
    indexer: str
    published_date: str
    download_url: Optional[str] = None
    info_hash: Optional[str] = None


@dataclass
class SearchQuery:
    """Data class representing a search query."""
    query: str
    category: SearchCategory = SearchCategory.ALL
    limit: int = 50
    min_seeders: int = 1


class ISearchProvider(ABC):
    """Interface for torrent search providers."""
    
    @abstractmethod
    async def search(self, query: SearchQuery) -> List[SearchResult]:
        """Search for torrents."""
        pass
    
    @abstractmethod
    async def get_categories(self) -> List[str]:
        """Get available categories."""
        pass
    
    @abstractmethod
    async def is_available(self) -> bool:
        """Check if the search provider is available."""
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """Get the provider name."""
        pass
