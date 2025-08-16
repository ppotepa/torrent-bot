"""
Torrent plugin package for the bot.
Provides torrent search and download functionality with fallback mechanisms.
"""

from .telegram_handlers import start_search, handle_selection
from .jackett_client import JackettClient

# Create a client instance for testing
def test_indexer_performance(query="ubuntu"):
    """Test indexer performance for diagnostics."""
    client = JackettClient()
    return client.test_indexer_performance(query)

__all__ = ['start_search', 'handle_selection', 'test_indexer_performance']
