#!/usr/bin/env python3
"""
Test the new numbered list format for torrent results.
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from plugins.torrent.result_formatter import format_torrent_results, create_summary_message

def test_numbered_list_format():
    """Test the numbered list formatting."""
    
    print("🧪 Testing Numbered List Format")
    print("=" * 50)
    
    # Test cases with various media types
    test_results = [
        {
            'Title': 'Avengers Endgame 2019 2160p UHD BluRay x265 HDR10 Atmos-TERMINAL',
            'Size': 15000000000,  # 15GB
            'Seeders': 250,
            'Peers': 45
        },
        {
            'Title': 'The Beatles - Abbey Road (50th Anniversary Edition) [2019] [FLAC 24bit 96kHz]',
            'Size': 2500000000,  # 2.5GB
            'Seeders': 120,
            'Peers': 30
        },
        {
            'Title': 'Game.of.Thrones.S08E06.The.Iron.Throne.1080p.AMZN.WEB-DL.DDP5.1.H.264-GoT',
            'Size': 3200000000,  # 3.2GB
            'Seeders': 85,
            'Peers': 25
        },
        {
            'Title': 'Adobe Photoshop 2024 v25.0.0.37 (x64) Multilingual Pre-Activated [FileCR]',
            'Size': 4500000000,  # 4.5GB
            'Seeders': 45,
            'Peers': 12
        },
        {
            'Title': 'Cyberpunk 2077 Ultimate Edition v2.01 + All DLCs (FitGirl Repack, Selective Download)',
            'Size': 65000000000,  # 65GB
            'Seeders': 180,
            'Peers': 35
        }
    ]
    
    # Format results with media information
    formatted_results = format_torrent_results(test_results)
    
    # Create summary message
    summary = create_summary_message(formatted_results, "test search", "🔍 Test Search Results")
    
    print("📋 **Formatted Message:**")
    print("-" * 30)
    print(summary)
    print()
    print(f"📏 **Message Length:** {len(summary)} characters")
    print()
    print("💡 **Benefits of Numbered List:**")
    print("• ✅ No character limits - full titles visible")
    print("• ✅ Rich metadata displayed clearly")
    print("• ✅ Quality indicators and type-specific info")
    print("• ✅ Easy selection by typing number")
    print("• ✅ Better mobile experience")
    print("• ✅ No button truncation issues")

if __name__ == "__main__":
    test_numbered_list_format()
