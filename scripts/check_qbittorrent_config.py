#!/usr/bin/env python3
"""
Check qBittorrent connection configuration.
"""

import os
import sys

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from plugins.torrent.config import config

def check_qbittorrent_config():
    """Check qBittorrent configuration."""
    
    print("🔧 qBittorrent Configuration Check")
    print("=" * 40)
    
    print("📋 Current Configuration:")
    print(f"   Host: {config.QBIT_HOST}")
    print(f"   Port: {config.QBIT_PORT}")
    print(f"   Username: {config.QBIT_USER}")
    print(f"   Password: {'*' * len(config.QBIT_PASS) if config.QBIT_PASS else 'Not set'}")
    print()
    
    print("🌐 Environment Variables:")
    qbit_vars = [
        "QBIT_HOST", "QBIT_PORT", "QBIT_USER", "QBIT_PASS"
    ]
    
    for var in qbit_vars:
        value = os.getenv(var, "Not set")
        if "PASS" in var and value != "Not set":
            value = '*' * len(value)
        print(f"   {var}: {value}")
    
    print()
    print("💡 For notifications to work, you need:")
    print("   1. qBittorrent running and accessible")
    print("   2. Correct QBIT_HOST (IP address or hostname)")
    print("   3. Correct QBIT_PORT (usually 8080)")
    print("   4. Valid QBIT_USER and QBIT_PASS")
    print()
    print("🔍 Suggested fixes:")
    if config.QBIT_HOST == "qbittorrent":
        print("   • Set QBIT_HOST to actual IP address (e.g., 192.168.1.100)")
        print("   • Or set QBIT_HOST to localhost if qBittorrent is local")
    
    print("   • Test connection with qBittorrent web UI first")
    print("   • Make sure qBittorrent WebUI is enabled")
    print("   • Set QBIT_USER and QBIT_PASS environment variables")

if __name__ == "__main__":
    check_qbittorrent_config()
