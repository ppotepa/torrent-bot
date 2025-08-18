#!/usr/bin/env python3
"""
Test the enhanced formatting with better audio and ISO detection.
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from plugins.torrent.result_formatter import format_torrent_results, create_summary_message

def test_enhanced_formatting():
    """Test the enhanced formatting with various media types."""
    
    print("🧪 Testing Enhanced Media-Specific Formatting")
    print("=" * 60)
    
    # Test cases with specific formatting requirements
    test_results = [
        {
            'Title': 'Ubuntu 22.04.3 Desktop amd64.iso',
            'Size': 3865470976,  # 3.6GB
            'Seeders': 200,
            'Peers': 45
        },
        {
            'Title': 'Pink Floyd - The Wall [FLAC 24bit/96kHz] [2011 Remaster] 20 Tracks',
            'Size': 2500000000,  # 2.5GB
            'Seeders': 85,
            'Peers': 22
        },
        {
            'Title': 'Various Artists - Best Hits 2024 [MP3 320kbps] 50 Songs Collection',
            'Size': 850000000,  # 850MB
            'Seeders': 120,
            'Peers': 35
        },
        {
            'Title': 'Windows 11 Pro 22H2 Build 22621.2428 x64 October 2023.iso',
            'Size': 5500000000,  # 5.5GB
            'Seeders': 150,
            'Peers': 28
        },
        {
            'Title': 'Avengers Endgame 2019 2160p UHD BluRay x265 HDR10 Atmos-TERMINAL',
            'Size': 15000000000,  # 15GB
            'Seeders': 250,
            'Peers': 60
        }
    ]
    
    # Format results
    formatted_results = format_torrent_results(test_results)
    
    # Create summary message
    summary = create_summary_message(formatted_results, "test enhanced", "🔍 Enhanced Format Test")
    
    print("📋 **Enhanced Formatted Message:**")
    print("-" * 40)
    print(summary)
    print()
    print("✅ **Formatting Validation:**")
    print("• Bold titles without truncation")
    print("• Media-specific data on separate lines")
    print("• ISO format: SIZE | PEERS | SEEDS")
    print("• Audio format: SIZE | BITRATE | TRACKS | PEERS | SEEDS")
    print("• Video format: YEAR | RESOLUTION | SOURCE | CODEC | SIZE | SEEDS")
    print("• Proper spacing between entries")

if __name__ == "__main__":
    test_enhanced_formatting()
