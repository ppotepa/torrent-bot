"""
Torrent plugin compatibility layer.
Maintains backward compatibility while using the refactored structure.
"""

# Re-export the main functions for backward compatibility
from .torrent.telegram_handlers import start_search, handle_selection
from .torrent.search_service import SearchService

# Initialize global search service for diagnostics
_search_service = SearchService()

def test_indexer_performance(query="ubuntu", limit=3):
    """Test indexer performance - legacy function for compatibility."""
    return _search_service.test_performance(query)

# Export all the functions that bot.py expects
__all__ = ['start_search', 'handle_selection', 'test_indexer_performance']
