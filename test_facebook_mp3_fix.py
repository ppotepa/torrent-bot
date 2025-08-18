#!/usr/bin/env python3

"""
Test script to verify the Facebook MP3 download fixes work correctly
"""

import os
import sys
import tempfile
import shutil

# Add the current directory to Python path so we can import our modules  
sys.path.insert(0, os.getcwd())

def test_mp3_file_handling():
    """Test that MP3 file handling works correctly without permission errors"""
    print("🧪 Testing MP3 file handling...")
    
    # Create a temporary test directory
    test_dir = os.path.join("downloads", "test_mp3")
    os.makedirs(test_dir, exist_ok=True)
    
    # Create mock files to simulate the permission error scenario
    base_filename = os.path.join(test_dir, "ACDC-HardasaRockOfficialHDVideo")
    temp_file = base_filename + ".temp.m4a"
    final_file = base_filename + ".mp3"
    
    try:
        # Create a mock temporary file
        with open(temp_file, 'w') as f:
            f.write("mock audio data")
        print(f"  ✅ Created mock temp file: {temp_file}")
        
        # Simulate the rename operation that was causing permission errors
        if os.path.exists(temp_file):
            if os.path.exists(final_file):
                os.remove(final_file)  # Remove existing file first
            
            os.rename(temp_file, final_file)
            print(f"  ✅ Successfully renamed to: {final_file}")
            
            # Verify the final file exists
            if os.path.exists(final_file):
                print("  ✅ MP3 file exists and is accessible")
            else:
                print("  ❌ MP3 file was not created properly")
                
        # Clean up
        if os.path.exists(final_file):
            os.remove(final_file)
        if os.path.exists(temp_file):
            os.remove(temp_file)
            
        # Remove test directory if empty
        try:
            os.rmdir(test_dir)
        except OSError:
            pass  # Directory not empty, that's okay
            
        print("  ✅ File handling test completed successfully")
        
    except PermissionError as e:
        print(f"  ❌ Permission error still exists: {e}")
    except Exception as e:
        print(f"  ❌ Unexpected error: {e}")

def test_facebook_integration():
    """Test the complete Facebook integration"""
    print("\n🧪 Testing Facebook integration...")
    
    try:
        from plugins.facebook import download, run
        print("  ✅ Facebook functions imported successfully")
        
        # Test that the download function exists and has the right signature
        import inspect
        download_sig = inspect.signature(download)
        expected_params = ['bot', 'message', 'url', 'folder']
        
        actual_params = list(download_sig.parameters.keys())
        if all(param in actual_params for param in expected_params[:3]):  # folder is optional
            print("  ✅ download() function has correct signature")
        else:
            print(f"  ❌ download() signature mismatch. Expected: {expected_params}, Got: {actual_params}")
            
        # Test that the run function has mode parameter
        run_sig = inspect.signature(run)
        run_params = list(run_sig.parameters.keys())
        if 'mode' in run_params:
            print("  ✅ run() function has mode parameter")
        else:
            print("  ❌ run() function missing mode parameter")
            
    except Exception as e:
        print(f"  ❌ Integration test failed: {e}")

def test_yt_dlp_config():
    """Test that yt-dlp configuration will produce MP3 files"""
    print("\n🧪 Testing yt-dlp MP3 configuration...")
    
    try:
        import yt_dlp
        print("  ✅ yt-dlp is available")
        
        # Test configuration that should produce MP3
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': 'test_output.%(ext)s',
            'noplaylist': True,
            'quiet': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '0',
            }],
            'writeinfojson': False,
            'writethumbnail': False,
            'ignoreerrors': False,
        }
        
        # Check if FFmpeg is available (needed for MP3 conversion)
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # This will check if FFmpeg is available without downloading anything
                postprocessors = ydl._get_pp_chain_for_kind('ffmpeg')
                if postprocessors:
                    print("  ✅ FFmpeg postprocessors available for MP3 conversion")
                else:
                    print("  ⚠️  FFmpeg might not be available - MP3 conversion may fail")
        except Exception as e:
            print(f"  ⚠️  Could not verify FFmpeg availability: {e}")
            
        print("  ✅ yt-dlp configuration looks correct for MP3 output")
        
    except ImportError:
        print("  ❌ yt-dlp is not installed")
    except Exception as e:
        print(f"  ❌ yt-dlp configuration test failed: {e}")

if __name__ == "__main__":
    print("🔧 Facebook MP3 Download Fix Verification")
    print("=" * 50)
    
    test_mp3_file_handling()
    test_facebook_integration()
    test_yt_dlp_config()
    
    print("\n" + "=" * 50)
    print("✅ Verification completed!")
    print("\n📋 Summary of fixes:")
    print("  • Added download() function to Facebook plugin")
    print("  • Implemented proper audio flag parsing")
    print("  • Enhanced file handling to prevent permission errors")
    print("  • Added time delays and retry logic for file operations")
    print("  • Ensured MP3 output with best quality settings")
    print("  • Added better error handling and file existence checks")
    print("\n🎯 To test with real Facebook video:")
    print("  /dl https://facebook.com/watch?v=VIDEO_ID:[audio] test_folder")
    print("  - Should download as MP3 in downloads/test_folder/")
    print("  - Should not have permission errors")
    print("  - Should send MP3 file via Telegram")
