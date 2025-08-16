#!/usr/bin/env python3
"""
Test script to verify seeder extraction and sorting functionality.
Run this script to test the robust seeder counting and sorting logic.
"""

import sys
import os

# Add the plugins directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'plugins'))

try:
    from torrent import get_seeders_count, sort_results_by_seeders
    
    # Test data with various seeder formats that different indexers might return
    test_results = [
        {"Title": "Movie A", "Seeders": 150, "Tracker": "test1"},
        {"Title": "Movie B", "Seeders": "25", "Tracker": "test2"},  # String number
        {"Title": "Movie C", "seeders": 5, "Tracker": "test3"},     # Lowercase field
        {"Title": "Movie D", "Seeds": 75, "Tracker": "test4"},     # Different field name
        {"Title": "Movie E", "Seeders": "0", "Tracker": "test5"},  # String zero
        {"Title": "Movie F", "Tracker": "test6"},                  # No seeder field
        {"Title": "Movie G", "Seeders": "12 seeders", "Tracker": "test7"},  # String with text
        {"Title": "Movie H", "Seeders": -1, "Tracker": "test8"},   # Negative (should become 0)
    ]
    
    print("🧪 Testing seeder extraction:")
    for result in test_results:
        seeders = get_seeders_count(result)
        title = result.get("Title")
        original = result.get("Seeders") or result.get("seeders") or result.get("Seeds") or "None"
        print(f"  {title}: '{original}' → {seeders}")
    
    print("\n🔢 Testing sorting:")
    sorted_results = sort_results_by_seeders(test_results)
    
    print("\n✅ Sorting test completed!")
    print("Expected order: Movie A (150) → Movie G (75) → Movie B (25) → Movie C (5) → Movie E/F/H (0)")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running this from the torrent-bot directory")
except Exception as e:
    print(f"❌ Test error: {e}")
