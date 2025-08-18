#!/usr/bin/env python3

"""
Test TTS dependencies and create a simple audiobook
"""

import os
import sys

# Add the current directory to Python path so we can import our modules  
sys.path.insert(0, os.getcwd())

def test_dependencies():
    """Test if TTS dependencies are available"""
    print("🧪 Testing TTS Dependencies")
    print("=" * 30)
    
    # Test gTTS
    try:
        import gtts
        print("✅ gTTS available")
        gtts_available = True
    except ImportError as e:
        print(f"❌ gTTS not available: {e}")
        gtts_available = False
    
    # Test pyttsx3
    try:
        import pyttsx3
        print("✅ pyttsx3 available")
        pyttsx3_available = True
    except ImportError as e:
        print(f"❌ pyttsx3 not available: {e}")
        pyttsx3_available = False
    
    return gtts_available, pyttsx3_available

def test_simple_conversion():
    """Test a simple TTS conversion"""
    print("\n🎵 Testing Simple TTS Conversion")
    print("=" * 35)
    
    try:
        from plugins.audiobook import convert_text_to_speech, AUDIOBOOK_DIR
        
        # Ensure directory exists
        os.makedirs(AUDIOBOOK_DIR, exist_ok=True)
        
        # Test text
        test_text = "Hello world, this is a test audiobook conversion."
        test_file = os.path.join(AUDIOBOOK_DIR, "test_conversion.mp3")
        
        print(f"📝 Test text: {test_text}")
        print(f"📁 Output file: {test_file}")
        
        # Try conversion
        success = convert_text_to_speech(test_text, "en", test_file)
        
        if success:
            if os.path.exists(test_file):
                file_size = os.path.getsize(test_file)
                print(f"✅ Conversion successful!")
                print(f"📁 File created: {test_file}")
                print(f"💾 File size: {file_size} bytes")
                return True
            else:
                print(f"❌ Conversion reported success but file not found")
                return False
        else:
            print(f"❌ Conversion failed")
            return False
            
    except Exception as e:
        print(f"❌ Conversion error: {e}")
        return False

def test_directory_permissions():
    """Test if we can write to the audiobooks directory"""
    print("\n📁 Testing Directory Permissions")
    print("=" * 32)
    
    try:
        from plugins.audiobook import AUDIOBOOK_DIR
        
        # Test creating directory
        os.makedirs(AUDIOBOOK_DIR, exist_ok=True)
        print(f"✅ Directory created: {AUDIOBOOK_DIR}")
        
        # Test writing a file
        test_file = os.path.join(AUDIOBOOK_DIR, "permission_test.txt")
        with open(test_file, 'w') as f:
            f.write("test")
        print(f"✅ Write permission OK")
        
        # Clean up test file
        os.remove(test_file)
        print(f"✅ Delete permission OK")
        
        return True
        
    except Exception as e:
        print(f"❌ Permission error: {e}")
        return False

def list_audiobook_files():
    """List current files in audiobooks directory"""
    print("\n📂 Current Audiobook Files")
    print("=" * 25)
    
    try:
        from plugins.audiobook import AUDIOBOOK_DIR
        
        if not os.path.exists(AUDIOBOOK_DIR):
            print(f"📁 Directory doesn't exist: {AUDIOBOOK_DIR}")
            return
            
        files = os.listdir(AUDIOBOOK_DIR)
        if not files:
            print("📁 Directory is empty")
        else:
            print(f"📁 Found {len(files)} files:")
            for file in files:
                file_path = os.path.join(AUDIOBOOK_DIR, file)
                if os.path.isfile(file_path):
                    size = os.path.getsize(file_path)
                    print(f"   📄 {file} ({size} bytes)")
                    
    except Exception as e:
        print(f"❌ Error listing files: {e}")

if __name__ == "__main__":
    print("🔍 Audiobook Troubleshooting Tool")
    print("=" * 40)
    
    # Test dependencies
    gtts_ok, pyttsx3_ok = test_dependencies()
    
    # Test permissions
    permissions_ok = test_directory_permissions()
    
    # List current files
    list_audiobook_files()
    
    # Test conversion if dependencies are available
    if gtts_ok or pyttsx3_ok:
        conversion_ok = test_simple_conversion()
        
        # List files after conversion
        print("\n📂 Files After Test Conversion:")
        list_audiobook_files()
        
    else:
        print("\n❌ No TTS engines available - cannot test conversion")
        print("💡 Install dependencies with: pip install gTTS pyttsx3")
    
    print(f"\n{'=' * 40}")
    print("📊 Summary:")
    print(f"   gTTS: {'✅' if gtts_ok else '❌'}")
    print(f"   pyttsx3: {'✅' if pyttsx3_ok else '❌'}")
    print(f"   Permissions: {'✅' if permissions_ok else '❌'}")
    
    if gtts_ok or pyttsx3_ok:
        print(f"   Test Conversion: {'✅' if conversion_ok else '❌'}")
