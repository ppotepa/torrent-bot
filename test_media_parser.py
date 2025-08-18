#!/usr/bin/env python3
"""
Test script for media parser functionality.
"""

from plugins.torrent.media_parser import media_parser
from plugins.torrent.result_formatter import format_torrent_results, create_summary_message

def test_media_parser():
    """Test the media parser with sample data."""
    
    # Test with sample torrent data
    test_results = [
        {'Title': 'The Matrix 1999 1080p BluRay x264-GROUP', 'Size': 8589934592, 'Seeders': 150},
        {'Title': 'Radiohead - OK Computer [FLAC] (1997)', 'Size': 419430400, 'Seeders': 85},
        {'Title': 'Ubuntu 22.04.3 Desktop amd64.iso', 'Size': 3865470976, 'Seeders': 200},
        {'Title': 'Game.of.Thrones.S08E06.720p.WEB.H264-MEMENTO', 'Size': 2147483648, 'Seeders': 45},
        {'Title': 'Adobe Photoshop 2024 v25.0.0.37 (x64) Multilingual', 'Size': 4294967296, 'Seeders': 30}
    ]

    print("🧪 Testing Media Parser")
    print("=" * 50)
    
    # Format results
    formatted = format_torrent_results(test_results)
    print(f"✅ Successfully formatted {len(formatted)} results")
    print()
    
    # Test media type detection
    print("📋 Media Type Detection Results:")
    print("-" * 30)
    
    for i, result in enumerate(formatted):
        media_info = result['media_info']
        quality_emoji = "🔥" if media_info.quality_score >= 80 else "⭐" if media_info.quality_score >= 60 else "✅"
        
        print(f"{i+1}. {media_info.title}")
        print(f"   Type: {media_info.media_type.value} {quality_emoji}")
        print(f"   Quality Score: {media_info.quality_score}")
        print(f"   Button: {result['button_text']}")
        print()
    
    # Test summary message
    print("📊 Summary Message:")
    print("-" * 20)
    summary = create_summary_message(formatted, "test query", "🔍 Test Results")
    print(summary)

if __name__ == "__main__":
    test_media_parser()
