#!/usr/bin/env python3
"""
Test updated YouTube download logic
"""

def test_youtube_logic():
    """Test the clarified YouTube download behavior"""
    print("🎬 Testing Updated YouTube Download Logic")
    print("=" * 50)
    
    try:
        from universal_flags import parse_universal_flags, validate_command_flags, convert_flags_to_legacy
        
        test_cases = [
            {
                'command': '/dl https://youtube.com/watch?v=123',
                'expected_mode': 'video',
                'description': 'Default: Full video with audio (MP4)'
            },
            {
                'command': '/dl https://youtube.com/watch?v=123:[audio]',
                'expected_mode': 'audio',
                'description': 'Audio flag: Audio track only (MP3)'
            },
            {
                'command': '/dl https://youtube.com/watch?v=123:[notify]',
                'expected_mode': 'video',
                'description': 'Other flags: Full video with audio (MP4)'
            },
            {
                'command': '/dl https://youtube.com/watch?v=123:[audio,notify]',
                'expected_mode': 'audio',
                'description': 'Audio + other flags: Audio track only (MP3)'
            }
        ]
        
        for i, case in enumerate(test_cases, 1):
            print(f"🧪 Test {i}: {case['description']}")
            print(f"   Command: {case['command']}")
            
            # Parse flags
            query, flags_list, parse_errors = parse_universal_flags(case['command'], "dl")
            valid_flags, validation_errors = validate_command_flags(flags_list, "dl")
            legacy_flags = convert_flags_to_legacy(valid_flags, "dl")
            
            # Determine mode (same logic as plugin)
            actual_mode = "audio" if legacy_flags.get("audio", False) else "video"
            
            print(f"   Flags: {valid_flags}")
            print(f"   Expected mode: {case['expected_mode']}")
            print(f"   Actual mode: {actual_mode}")
            
            if actual_mode == case['expected_mode']:
                print("   ✅ PASS")
            else:
                print("   ❌ FAIL")
                return False
            
            print()
        
        print("🎯 All Tests PASSED!")
        print()
        print("📋 Logic Summary:")
        print("   • Default behavior: Download full video with audio (MP4)")
        print("   • [audio] flag: Download audio track only (MP3)")
        print("   • Video always includes audio when downloaded")
        print("   • Audio flag extracts only the audio track")
        print()
        print("💡 Usage Examples:")
        print("   • Full video: /dl https://youtube.com/watch?v=123")
        print("   • Audio only: /dl https://youtube.com/watch?v=123:[audio]")
        print("   • Audio + notification: /dl https://youtube.com/watch?v=123:[audio,notify]")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_youtube_logic()
    
    if success:
        print()
        print("🚀 YouTube download logic is correctly implemented!")
    else:
        print()
        print("❌ YouTube download logic needs fixes")
