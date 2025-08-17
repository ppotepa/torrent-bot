"""Torrent service implementing business logic following Single Responsibility Principle."""

import asyncio
import logging
from typing import List, Optional, Dict, Any
from dataclasses import dataclass

from ..interfaces.torrent_client import ITorrentClient, TorrentInfo, AddTorrentResult
from ..interfaces.search_provider import ISearchProvider, SearchQuery, SearchResult
from ..interfaces.telegram_bot import INotificationService
from ..config.settings import AppConfig


@dataclass
class DownloadRequest:
    """Data class for download requests."""
    magnet_link: str
    category: str = ""
    chat_id: Optional[int] = None
    custom_path: Optional[str] = None


class TorrentService:
    """Service for managing torrent operations."""
    
    def __init__(
        self,
        torrent_client: ITorrentClient,
        search_provider: ISearchProvider,
        notification_service: INotificationService,
        config: AppConfig
    ):
        self._torrent_client = torrent_client
        self._search_provider = search_provider
        self._notification_service = notification_service
        self._config = config
        self._logger = logging.getLogger(__name__)
    
    async def search_torrents(self, query: str, category: str = "all", limit: int = None) -> List[SearchResult]:
        """Search for torrents using the configured search provider."""
        try:
            search_query = SearchQuery(
                query=query,
                category=category,
                limit=limit or self._config.search.default_limit
            )
            
            if not await self._search_provider.is_available():
                self._logger.error(f"Search provider {self._search_provider.get_provider_name()} is not available")
                return []
            
            results = await self._search_provider.search(search_query)
            
            # Filter by minimum seeders
            filtered_results = [
                result for result in results 
                if result.seeders >= self._config.search.min_seeders
            ]
            
            self._logger.info(f"Found {len(filtered_results)} torrents for query: {query}")
            return filtered_results
            
        except Exception as e:
            self._logger.error(f"Error searching torrents: {e}")
            return []
    
    async def download_torrent(self, request: DownloadRequest) -> AddTorrentResult:
        """Download a torrent using the configured torrent client."""
        try:
            # Ensure client is connected
            if not await self._torrent_client.connect():
                return AddTorrentResult(success=False, message="Failed to connect to torrent client")
            
            # Determine save path
            save_path = request.custom_path or self._config.download.get_category_path(request.category)
            
            # Add torrent
            result = await self._torrent_client.add_torrent(
                magnet_link=request.magnet_link,
                category=request.category,
                save_path=save_path
            )
            
            # Send notification if successful
            if result.success and request.chat_id:
                await self._notification_service.notify_download_started(
                    torrent_name=f"Torrent in {request.category or 'default'} category",
                    chat_id=request.chat_id
                )
            
            self._logger.info(f"Download request result: {result.message}")
            return result
            
        except Exception as e:
            error_msg = f"Error downloading torrent: {e}"
            self._logger.error(error_msg)
            
            if request.chat_id:
                await self._notification_service.notify_download_failed(
                    torrent_name="Unknown",
                    error=str(e),
                    chat_id=request.chat_id
                )
            
            return AddTorrentResult(success=False, message=error_msg)
    
    async def get_active_downloads(self) -> List[TorrentInfo]:
        """Get list of active downloads."""
        try:
            if not await self._torrent_client.connect():
                self._logger.error("Failed to connect to torrent client")
                return []
            
            torrents = await self._torrent_client.get_torrents()
            active_torrents = [t for t in torrents if t.status.lower() in ['downloading', 'queued', 'paused']]
            
            return active_torrents
            
        except Exception as e:
            self._logger.error(f"Error getting active downloads: {e}")
            return []
    
    async def get_torrent_status(self, torrent_hash: str) -> Optional[TorrentInfo]:
        """Get status of a specific torrent."""
        try:
            if not await self._torrent_client.connect():
                return None
            
            return await self._torrent_client.get_torrent_info(torrent_hash)
            
        except Exception as e:
            self._logger.error(f"Error getting torrent status: {e}")
            return None
    
    async def pause_torrent(self, torrent_hash: str, chat_id: Optional[int] = None) -> bool:
        """Pause a torrent."""
        try:
            if not await self._torrent_client.connect():
                return False
            
            success = await self._torrent_client.pause_torrent(torrent_hash)
            
            if success:
                self._logger.info(f"Paused torrent: {torrent_hash}")
            
            return success
            
        except Exception as e:
            self._logger.error(f"Error pausing torrent: {e}")
            return False
    
    async def resume_torrent(self, torrent_hash: str, chat_id: Optional[int] = None) -> bool:
        """Resume a torrent."""
        try:
            if not await self._torrent_client.connect():
                return False
            
            success = await self._torrent_client.resume_torrent(torrent_hash)
            
            if success:
                self._logger.info(f"Resumed torrent: {torrent_hash}")
            
            return success
            
        except Exception as e:
            self._logger.error(f"Error resuming torrent: {e}")
            return False
    
    async def delete_torrent(self, torrent_hash: str, delete_files: bool = False, chat_id: Optional[int] = None) -> bool:
        """Delete a torrent."""
        try:
            if not await self._torrent_client.connect():
                return False
            
            success = await self._torrent_client.delete_torrent(torrent_hash, delete_files)
            
            if success:
                self._logger.info(f"Deleted torrent: {torrent_hash} (files: {delete_files})")
            
            return success
            
        except Exception as e:
            self._logger.error(f"Error deleting torrent: {e}")
            return False
    
    async def monitor_downloads(self) -> None:
        """Monitor downloads and send notifications when completed."""
        previous_torrents: Dict[str, str] = {}
        
        while True:
            try:
                current_torrents = await self.get_active_downloads()
                current_dict = {t.hash: t.status for t in current_torrents}
                
                # Check for completed torrents
                for torrent in current_torrents:
                    if torrent.hash in previous_torrents:
                        prev_status = previous_torrents[torrent.hash]
                        if prev_status != "completed" and torrent.status == "completed":
                            # Torrent just completed
                            if self._config.telegram.notification_chat_id:
                                await self._notification_service.notify_download_completed(
                                    torrent_name=torrent.name,
                                    chat_id=self._config.telegram.notification_chat_id
                                )
                
                previous_torrents = current_dict
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                self._logger.error(f"Error in download monitor: {e}")
                await asyncio.sleep(60)
