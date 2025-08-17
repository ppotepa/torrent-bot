"""
Search service that coordinates between Jackett and provides unified search interface.
"""

from .jackett_client import JackettClient
from .utils import get_seeders_count


# Cache: user_id → {results, folder}
search_cache = {}


class SearchService:
    """Coordinates torrent searches across different sources."""
    
    def __init__(self):
        self.jackett_client = JackettClient()
    
    def search(self, query: str, rich_mode: bool = False, all_mode: bool = False, music_mode: bool = False, bot=None, message=None):
        """
        Perform torrent search with appropriate strategy.
        Returns (results, errors, search_type_description)
        """
        if all_mode:
            results, errors = self.jackett_client.search_all(query, bot, message)
            search_type = "all"
        elif music_mode:
            results, errors = self.jackett_client.search_music(query, bot, message)
            search_type = "music"
        elif rich_mode:
            results, errors = self.jackett_client.search_rich(query, bot, message)
            search_type = "rich"
        else:
            # Normal mode: fast search with fallback to extended if needed
            results, errors = self.jackett_client.search_fast(query)
            
            # If we didn't get good results, try extended search
            if len(results) < 3 or all(get_seeders_count(r) == 0 for r in results[:3]):
                if bot and message:
                    from .busy_indicator import BusyIndicator
                    BusyIndicator.update(bot, message, found_results=len(results))
                results, errors = self.jackett_client.search_extended(query)
            
            search_type = "normal"
        
        return results, errors, search_type
    
    def test_performance(self, query="ubuntu"):
        """Test indexer performance for diagnostics."""
        return self.jackett_client.test_indexer_performance(query)
    
    def cache_results(self, user_id: int, results: list, folder: str, rich_mode: bool = False, all_mode: bool = False, music_mode: bool = False, notify: bool = False):
        """Cache search results for user selection."""
        search_cache[user_id] = {
            "results": results, 
            "folder": folder, 
            "rich_mode": rich_mode,
            "all_mode": all_mode,
            "music_mode": music_mode,
            "notify": notify
        }
    
    def get_cached_results(self, user_id: int):
        """Get cached search results for user."""
        return search_cache.pop(user_id, None)
