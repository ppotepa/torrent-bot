#!/usr/bin/env python3
"""
Test button formatting with long titles that commonly cause truncation issues.
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from plugins.torrent.media_parser import media_parser

def test_button_formatting():
    """Test button formatting with challenging long titles."""
    
    print("🧪 Testing Button Formatting with Long Titles")
    print("=" * 60)
    
    # Test cases with commonly problematic long titles
    test_cases = [
        {
            'title': 'Avengers Endgame 2019 2160p UHD BluRay x265 HDR10 Atmos-TERMINAL',
            'size': 15000000000,  # 15GB
            'seeders': 250
        },
        {
            'title': 'The Beatles - Abbey Road (50th Anniversary Edition) [2019] [FLAC 24bit 96kHz]',
            'size': 2500000000,  # 2.5GB
            'seeders': 120
        },
        {
            'title': 'Game.of.Thrones.S08E06.The.Iron.Throne.1080p.AMZN.WEB-DL.DDP5.1.H.264-GoT',
            'size': 3200000000,  # 3.2GB
            'seeders': 85
        },
        {
            'title': 'Adobe Photoshop 2024 v25.0.0.37 (x64) Multilingual Pre-Activated [FileCR]',
            'size': 4500000000,  # 4.5GB
            'seeders': 45
        },
        {
            'title': 'Cyberpunk 2077 Ultimate Edition v2.01 + All DLCs (FitGirl Repack, Selective Download)',
            'size': 65000000000,  # 65GB
            'seeders': 180
        },
        {
            'title': 'Stephen King - The Stand Complete & Uncut Edition (Audiobook) [MP3 320kbps]',
            'size': 1800000000,  # 1.8GB
            'seeders': 35
        }
    ]
    
    print("📋 Button Formatting Results:")
    print("-" * 40)
    
    for i, test_case in enumerate(test_cases, 1):
        media_info = media_parser.parse(
            test_case['title'],
            test_case['size'],
            test_case['seeders'],
            0
        )
        
        button_text = media_parser.format_button_text(media_info)
        
        print(f"{i}. Original: {test_case['title']}")
        print(f"   Type: {media_info.media_type.value} | Quality: {media_info.quality_score}")
        print(f"   Button:")
        for line in button_text.split('\n'):
            print(f"     {line}")
        print(f"   Length: {len(button_text)} chars")
        print()
    
    print("💡 **Button Display Tips:**")
    print("• Two-line format shows more info in limited space")
    print("• First line: Quality emoji + shortened clean title")
    print("• Second line: Type-specific metadata + size + seeders")
    print("• Telegram limits: ~64 chars per button (total)")
    print("• Longer text gets truncated by Telegram client")

if __name__ == "__main__":
    test_button_formatting()
