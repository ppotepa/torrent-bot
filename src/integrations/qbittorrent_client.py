"""qBittorrent client implementation."""

import aiohttp
import asyncio
import logging
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin

from ..interfaces.torrent_client import ITorrentClient, TorrentInfo, AddTorrentResult
from ..config.settings import QBittorrentConfig


class QBittorrentClient(ITorrentClient):
    """qBittorrent Web API client implementation."""
    
    def __init__(self, config: QBittorrentConfig):
        self._config = config
        self._session: Optional[aiohttp.ClientSession] = None
        self._authenticated = False
        self._logger = logging.getLogger(__name__)
    
    async def connect(self) -> bool:
        """Connect and authenticate to qBittorrent."""
        try:
            if not self._session:
                # Create session with custom connector settings
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
            
            if self._authenticated:
                # Test if still authenticated
                try:
                    await self._make_request("GET", "/api/v2/app/version")
                    return True
                except:
                    self._authenticated = False
            
            # Authenticate
            login_data = {
                "username": self._config.username,
                "password": self._config.password
            }
            
            response = await self._make_request("POST", "/api/v2/auth/login", data=login_data)
            
            if response == "Ok.":
                self._authenticated = True
                self._logger.info("Successfully connected to qBittorrent")
                return True
            else:
                self._logger.error(f"Authentication failed: {response}")
                return False
                
        except Exception as e:
            self._logger.error(f"Failed to connect to qBittorrent: {e}")
            return False
    
    async def disconnect(self) -> None:
        """Disconnect from qBittorrent."""
        try:
            if self._session and self._authenticated:
                await self._make_request("POST", "/api/v2/auth/logout")
            
            if self._session:
                await self._session.close()
                self._session = None
            
            self._authenticated = False
            self._logger.info("Disconnected from qBittorrent")
            
        except Exception as e:
            self._logger.error(f"Error during disconnect: {e}")
    
    async def add_torrent(self, magnet_link: str, category: str = "", save_path: str = "") -> AddTorrentResult:
        """Add a torrent via magnet link."""
        try:
            data = {
                "urls": magnet_link,
                "autoTMM": "false" if save_path else "true"
            }
            
            if category:
                data["category"] = category
            
            if save_path:
                data["savepath"] = save_path
            
            response = await self._make_request("POST", "/api/v2/torrents/add", data=data)
            
            if response == "Ok.":
                return AddTorrentResult(
                    success=True,
                    message="Torrent added successfully"
                )
            else:
                return AddTorrentResult(
                    success=False,
                    message=f"Failed to add torrent: {response}"
                )
                
        except Exception as e:
            return AddTorrentResult(
                success=False,
                message=f"Error adding torrent: {e}"
            )
    
    async def get_torrents(self) -> List[TorrentInfo]:
        """Get list of all torrents."""
        try:
            response = await self._make_request("GET", "/api/v2/torrents/info")
            
            if not isinstance(response, list):
                self._logger.error(f"Unexpected response format: {type(response)}")
                return []
            
            torrents = []
            for torrent_data in response:
                torrent = TorrentInfo(
                    name=torrent_data.get("name", "Unknown"),
                    hash=torrent_data.get("hash", ""),
                    size=torrent_data.get("size", 0),
                    progress=torrent_data.get("progress", 0.0) * 100,  # Convert to percentage
                    status=torrent_data.get("state", "unknown"),
                    download_speed=torrent_data.get("dlspeed", 0),
                    upload_speed=torrent_data.get("upspeed", 0),
                    eta=torrent_data.get("eta", 0),
                    priority=torrent_data.get("priority", 0),
                    category=torrent_data.get("category", "")
                )
                torrents.append(torrent)
            
            return torrents
            
        except Exception as e:
            self._logger.error(f"Error getting torrents: {e}")
            return []
    
    async def get_torrent_info(self, torrent_hash: str) -> Optional[TorrentInfo]:
        """Get information about specific torrent."""
        try:
            params = {"hashes": torrent_hash}
            response = await self._make_request("GET", "/api/v2/torrents/info", params=params)
            
            if not isinstance(response, list) or not response:
                return None
            
            torrent_data = response[0]
            return TorrentInfo(
                name=torrent_data.get("name", "Unknown"),
                hash=torrent_data.get("hash", ""),
                size=torrent_data.get("size", 0),
                progress=torrent_data.get("progress", 0.0) * 100,
                status=torrent_data.get("state", "unknown"),
                download_speed=torrent_data.get("dlspeed", 0),
                upload_speed=torrent_data.get("upspeed", 0),
                eta=torrent_data.get("eta", 0),
                priority=torrent_data.get("priority", 0),
                category=torrent_data.get("category", "")
            )
            
        except Exception as e:
            self._logger.error(f"Error getting torrent info: {e}")
            return None
    
    async def pause_torrent(self, torrent_hash: str) -> bool:
        """Pause a torrent."""
        try:
            data = {"hashes": torrent_hash}
            response = await self._make_request("POST", "/api/v2/torrents/pause", data=data)
            return response == "Ok."
            
        except Exception as e:
            self._logger.error(f"Error pausing torrent: {e}")
            return False
    
    async def resume_torrent(self, torrent_hash: str) -> bool:
        """Resume a torrent."""
        try:
            data = {"hashes": torrent_hash}
            response = await self._make_request("POST", "/api/v2/torrents/resume", data=data)
            return response == "Ok."
            
        except Exception as e:
            self._logger.error(f"Error resuming torrent: {e}")
            return False
    
    async def delete_torrent(self, torrent_hash: str, delete_files: bool = False) -> bool:
        """Delete a torrent."""
        try:
            data = {
                "hashes": torrent_hash,
                "deleteFiles": "true" if delete_files else "false"
            }
            response = await self._make_request("POST", "/api/v2/torrents/delete", data=data)
            return response == "Ok."
            
        except Exception as e:
            self._logger.error(f"Error deleting torrent: {e}")
            return False
    
    async def set_category(self, torrent_hash: str, category: str) -> bool:
        """Set torrent category."""
        try:
            data = {
                "hashes": torrent_hash,
                "category": category
            }
            response = await self._make_request("POST", "/api/v2/torrents/setCategory", data=data)
            return response == "Ok."
            
        except Exception as e:
            self._logger.error(f"Error setting category: {e}")
            return False
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Any:
        """Make HTTP request to qBittorrent API."""
        if not self._session:
            raise Exception("Session not initialized")
        
        url = urljoin(self._config.base_url, endpoint)
        
        async with self._session.request(
            method=method,
            url=url,
            data=data,
            params=params
        ) as response:
            response.raise_for_status()
            
            content_type = response.headers.get("content-type", "")
            
            if "application/json" in content_type:
                return await response.json()
            else:
                return await response.text()
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()
