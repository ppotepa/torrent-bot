"""Jackett search provider implementation."""

import aiohttp
import asyncio
import logging
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin, urlencode
from datetime import datetime

from ..interfaces.search_provider import ISearchProvider, SearchQuery, SearchResult, SearchCategory
from ..config.settings import JackettConfig


class JackettSearchProvider(ISearchProvider):
    """Jackett torrent search provider implementation."""
    
    def __init__(self, config: JackettConfig):
        self._config = config
        self._session: Optional[aiohttp.ClientSession] = None
        self._logger = logging.getLogger(__name__)
        
        # Category mapping from our enum to Jackett categories
        self._category_mapping = {
            SearchCategory.MOVIES: "2000",
            SearchCategory.TV_SHOWS: "5000", 
            SearchCategory.MUSIC: "3000",
            SearchCategory.GAMES: "1000",
            SearchCategory.SOFTWARE: "4000",
            SearchCategory.BOOKS: "7000",
            SearchCategory.ANIME: "5070",
            SearchCategory.ALL: ""
        }
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session."""
        if not self._session:
            connector = aiohttp.TCPConnector(
                limit=10,
                limit_per_host=5,
                ttl_dns_cache=300,
                use_dns_cache=True,
            )
            timeout = aiohttp.ClientTimeout(total=30, connect=10)
            self._session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout
            )
        return self._session
    
    async def search(self, query: SearchQuery) -> List[SearchResult]:
        """Search for torrents using Jackett API."""
        try:
            session = await self._get_session()
            
            # Build search parameters
            params = {
                "apikey": self._config.api_key,
                "q": query.query,
                "Tracker[]": "all",  # Search all trackers
                "limit": query.limit
            }
            
            # Add category if specified
            if query.category != SearchCategory.ALL:
                category_id = self._category_mapping.get(query.category)
                if category_id:
                    params["cat"] = category_id
            
            # Make request to Jackett
            url = urljoin(self._config.base_url, "/api/v2.0/indexers/all/results")
            
            self._logger.info(f"Searching Jackett with query: {query.query}")
            
            async with session.get(url, params=params) as response:
                response.raise_for_status()
                data = await response.json()
            
            # Parse results
            results = []
            if "Results" in data:
                for item in data["Results"]:
                    try:
                        result = self._parse_search_result(item)
                        if result and result.seeders >= query.min_seeders:
                            results.append(result)
                    except Exception as e:
                        self._logger.warning(f"Error parsing search result: {e}")
                        continue
            
            self._logger.info(f"Found {len(results)} results for query: {query.query}")
            return results
            
        except Exception as e:
            self._logger.error(f"Error searching Jackett: {e}")
            return []
    
    def _parse_search_result(self, item: Dict[str, Any]) -> Optional[SearchResult]:
        """Parse a single search result from Jackett response."""
        try:
            # Extract magnet link from download URL or Link field
            magnet_link = ""
            if "MagnetUri" in item and item["MagnetUri"]:
                magnet_link = item["MagnetUri"]
            elif "Link" in item and item["Link"] and item["Link"].startswith("magnet:"):
                magnet_link = item["Link"]
            
            if not magnet_link:
                return None
            
            # Parse published date
            published_date = ""
            if "PublishDate" in item:
                try:
                    date_obj = datetime.fromisoformat(item["PublishDate"].replace("Z", "+00:00"))
                    published_date = date_obj.strftime("%Y-%m-%d %H:%M")
                except:
                    published_date = item["PublishDate"]
            
            # Determine category name from category ID
            category_name = self._get_category_name(item.get("CategoryDesc", ""))
            
            return SearchResult(
                title=item.get("Title", "Unknown"),
                size=item.get("Size", 0),
                seeders=item.get("Seeders", 0),
                leechers=item.get("Peers", 0),
                category=category_name,
                magnet_link=magnet_link,
                indexer=item.get("Tracker", "Unknown"),
                published_date=published_date,
                download_url=item.get("Link"),
                info_hash=self._extract_info_hash(magnet_link)
            )
            
        except Exception as e:
            self._logger.error(f"Error parsing search result: {e}")
            return None
    
    def _get_category_name(self, category_desc: str) -> str:
        """Convert category description to simplified category name."""
        category_desc = category_desc.lower()
        
        if "movie" in category_desc or "film" in category_desc:
            return "movies"
        elif "tv" in category_desc or "television" in category_desc or "series" in category_desc:
            return "tv"
        elif "music" in category_desc or "audio" in category_desc:
            return "music"
        elif "game" in category_desc:
            return "games"
        elif "software" in category_desc or "app" in category_desc:
            return "software"
        elif "book" in category_desc or "ebook" in category_desc:
            return "books"
        elif "anime" in category_desc:
            return "anime"
        else:
            return "other"
    
    def _extract_info_hash(self, magnet_link: str) -> Optional[str]:
        """Extract info hash from magnet link."""
        try:
            if not magnet_link.startswith("magnet:"):
                return None
            
            # Look for xt parameter
            parts = magnet_link.split("&")
            for part in parts:
                if part.startswith("xt=urn:btih:"):
                    return part.split(":")[-1]
            
            return None
            
        except Exception:
            return None
    
    async def get_categories(self) -> List[str]:
        """Get available categories."""
        return [
            "movies", "tv", "music", "games", 
            "software", "books", "anime", "all"
        ]
    
    async def is_available(self) -> bool:
        """Check if Jackett is available."""
        try:
            session = await self._get_session()
            
            # Test endpoint
            url = urljoin(self._config.base_url, "/api/v2.0/server/config")
            params = {"apikey": self._config.api_key}
            
            async with session.get(url, params=params) as response:
                return response.status == 200
                
        except Exception as e:
            self._logger.error(f"Jackett availability check failed: {e}")
            return False
    
    def get_provider_name(self) -> str:
        """Get the provider name."""
        return "Jackett"
    
    async def close(self) -> None:
        """Close the HTTP session."""
        if self._session:
            await self._session.close()
            self._session = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
