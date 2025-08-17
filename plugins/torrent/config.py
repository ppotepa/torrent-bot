"""
Configuration management for the torrent plugin.
Handles all environment variables and default settings.
"""

import os

class TorrentConfig:
    """Configuration settings for torrent operations."""
    
    # qBittorrent settings (using Docker service names for zerotier network)
    QBIT_HOST = os.getenv("QBIT_HOST", "qbittorrent")
    QBIT_PORT = int(os.getenv("QBIT_PORT", "8080"))
    QBIT_USER = os.getenv("QBIT_USER", "admin")
    QBIT_PASS = os.getenv("QBIT_PASS", "adminadmin")
    QBIT_SAVE_ROOT = os.getenv("QBIT_SAVE_ROOT", "/downloads")
    
    # Bot download directory
    BOT_DOWNLOADS_DIR = os.getenv("BOT_DOWNLOADS_DIR", "/app/downloads")
    
    # Jackett settings (using Docker service names for zerotier network)
    JACKETT_URL = os.getenv("JACKETT_URL", "http://jackett:9117").rstrip("/")
    JACKETT_API_KEY = os.getenv("JACKETT_API_KEY", "")
    
    # Default indexers (popular and reliable ones)
    POPULAR_INDEXERS_DEFAULT = "yts,1337x,thepiratebay,eztv,limetorrents,torrentgalaxy,torlock,torrentdownloads,linuxtracker,idope"
    JACKETT_INDEXERS = os.getenv("JACKETT_INDEXERS", POPULAR_INDEXERS_DEFAULT).replace(" ", "")
    
    # Timeout and concurrency settings
    CONNECT_TIMEOUT = int(os.getenv("JACKETT_CONNECT_TIMEOUT", "3"))
    READ_TIMEOUT = int(os.getenv("JACKETT_READ_TIMEOUT", "12"))
    MAX_WORKERS = int(os.getenv("JACKETT_MAX_WORKERS", "4"))
    RESULT_LIMIT = int(os.getenv("JACKETT_RESULT_LIMIT", "5"))
    
    # Fallback settings
    ENABLE_AGGRESSIVE_FALLBACK = os.getenv("ENABLE_AGGRESSIVE_FALLBACK", "true").lower() == "true"
    MAX_FALLBACK_ATTEMPTS = int(os.getenv("MAX_FALLBACK_ATTEMPTS", "3"))
    
    # Rich mode settings
    RICH_MODE_LIMIT = int(os.getenv("RICH_MODE_LIMIT", "15"))
    RICH_MODE_TIMEOUT = int(os.getenv("RICH_MODE_TIMEOUT", "20"))
    
    # All mode settings (searches ALL indexers on Jackett)
    ALL_MODE_LIMIT = int(os.getenv("ALL_MODE_LIMIT", "25"))  # More results for comprehensive search
    ALL_MODE_TIMEOUT = int(os.getenv("ALL_MODE_TIMEOUT", "30"))  # Longer timeout for exhaustive search
    
    # Music mode settings (searches music-specific indexers)
    MUSIC_MODE_LIMIT = int(os.getenv("MUSIC_MODE_LIMIT", "12"))  # Music-focused results
    MUSIC_MODE_TIMEOUT = int(os.getenv("MUSIC_MODE_TIMEOUT", "15"))  # Medium timeout for music search
    
    # Download monitor settings
    AUTO_START_MONITOR = os.getenv("AUTO_START_MONITOR", "true").lower() == "true"  # Auto-start monitor on downloads
    
    # All available indexers for ALL mode (comprehensive list)
    ALL_INDEXERS = [
        # 🎬 Movies & TV
        "1337x",
        "thepiratebay", "piratebay",  # Alternative names
        "yts",
        "eztv",
        "torlock",
        "torrentgalaxyclone", "torrentgalaxy",
        "torrentdownloads",
        "torrentproject2", "torrentproject",
        "torrent9",
        "oxtorrent",
        "oxtorrent-vip",
        "limetorrents",
        "torrentkitty",
        "torrenttip",
        "divxtotal",
        "cinecalidad",
        "dontorrent",
        "elitetorrent-wf",
        "extratorrents",
        "isohunt2",
        
        # 📺 TV / Series Specialists
        "showrss",
        "skidrowrepack",
        "torrentdosfilmes",
        "torrentoyunindir",
        "torrentsir",
        "torrentsome",
        "zetorrents",
        "internetarchive",
        
        # 🎵 Music & Audio
        "rutracker",
        "rutor",
        "noname-club",
        "torrentcore",
        "mixtapetorrent",
        "nipponsei",
        "tokyotoshokan",
        "vsttorrentz",
        "vsthouse",
        "vstorrent",
        "linuxtracker",
        "torrentqq",
        
        # 💻 Software, Games, E-Books
        "gamestorrents",
        "mactorrentsdownload",
        "pc-torrent",
        "crackingpatching",
        "byrutor",
        "torrentssg",
        "ebookbay",
        "epublibre",
        "frozenlayer",
        "bt-etree",
        "megapeer",
        "plugintorrent",
        "wolfmax4k",
        "idope", "idopeclone",
        "kickasstorrents", "kickasstorrents.to", "kickasstorrents.ws",
        "yourbittorrent",
        
        # Legacy/fallback indexers
        "rarbg", "rarbgapi",
        "nyaa",
        "glodls", "magnetdl", "btdiggg", 
        "zooqle", "torrentfunk",
        "skytorrents", "solidtorrents",
        
        # Private trackers (if configured)
        "iptorrents", "torrentleech", "passthepopcorn", "broadcastthenet",
        "redacted", "orpheus", "gazellegames", "jpopsuki"
    ]
    
    # Popular music indexers for music mode
    MUSIC_INDEXERS = [
        # 🎵 Top Music Specialists
        "rutracker",           # Largest music tracker
        "rutor",               # Russian content including music
        "noname-club",         # Music releases
        "torrentcore",         # Scene music releases
        "redacted",            # Private music specialist
        "orpheus",             # Private music specialist
        
        # 🎧 Music-focused Public Trackers
        "1337x",               # Has good music section
        "thepiratebay",        # Large music collection
        "torrentgalaxy",       # Good music selection
        "limetorrents",        # Music section
        "kickasstorrents",     # Music category
        "idope",               # Music search
        
        # 🎶 Specialized Audio Content
        "mixtapetorrent",      # Hip-hop/rap speciality
        "nipponsei",           # Anime & J-music
        "tokyotoshokan",       # J-music specialist
        "vsttorrentz",         # Audio plugins/software
        "vsthouse",            # Audio software
        "vstorrent",           # Music production tools
        "torrentqq",           # Music heavy content
        
        # 🎼 General trackers with good music
        "nyaa",                # Anime music
        "linuxtracker",        # Sometimes has music software
        "glodls",              # General with music
        "solidtorrents",       # Clean music section
        "zooqle"               # Verified music torrents
    ]
    
    # Common indexer name mappings (Jackett internal name -> common name)
    INDEXER_ALIASES = {
        # Alternative names for existing indexers
        "rarbgapi": "rarbg",
        "torrentgalaxyclone": "torrentgalaxy", 
        "idopeclone": "idope",
        "thepiratebay": "tpb",
        "piratebay": "thepiratebay",
        "kickasstorrents": "kat",
        "kickasstorrents.to": "kat",
        "kickasstorrents.ws": "kat",
        
        # Movie/TV specialized indexers
        "torrentproject2": "torrentproject",
        "oxtorrent-vip": "oxtorrent",
        "elitetorrent-wf": "elitetorrent",
        "extratorrents": "extratorrent",
        
        # Music/Audio indexers
        "noname-club": "nonameclub",
        "torrentcore": "torrent[core]",
        "tokyotoshokan": "tokyotosho",
        "vsttorrentz": "vst-torrents",
        "bt-etree": "bt.etree",
        
        # Software/Games indexers
        "mactorrentsdownload": "mactorrents",
        "pc-torrent": "pctorrent",
        "torrentssg": "torrents.sg",
        
        # General variations
        "internetarchive": "archive.org",
        "wolfmax4k": "wolfmax",
        "yourbittorrent": "ybt"
    }

# Global configuration instance
config = TorrentConfig()
