#!/usr/bin/env python3

"""
Test script for the audiobook plugin functionality
"""

import os
import sys

# Add the current directory to Python path so we can import our modules  
sys.path.insert(0, os.getcwd())

def test_audiobook_import():
    """Test that the audiobook plugin can be imported"""
    print("🧪 Testing audiobook plugin import...")
    
    try:
        from plugins import audiobook
        print("  ✅ Audiobook plugin imported successfully")
        
        # Check for required functions
        functions_to_check = [
            'handle_command',
            'handle_audiobook_command', 
            'process_audiobook',
            'extract_text_from_file',
            'convert_text_to_speech',
            'show_audiobook_usage'
        ]
        
        for func_name in functions_to_check:
            if hasattr(audiobook, func_name):
                print(f"  ✅ {func_name}() function found")
            else:
                print(f"  ❌ {func_name}() function missing")
                
    except ImportError as e:
        print(f"  ❌ Failed to import audiobook plugin: {e}")

def test_command_parsing():
    """Test command parsing functionality"""
    print("\n🧪 Testing command parsing...")
    
    test_commands = [
        "/ab text:eng",
        "/ab pdf:polish", 
        "/ab epub",
        "/ab text",
        "/ab help",
        "/ab status"
    ]
    
    try:
        from plugins.audiobook import SUPPORTED_FORMATS, SUPPORTED_LANGUAGES
        
        print(f"  📋 Supported formats: {SUPPORTED_FORMATS}")
        print(f"  📋 Supported languages: {list(SUPPORTED_LANGUAGES.keys())}")
        
        for cmd in test_commands:
            print(f"  🔍 Testing command: {cmd}")
            
            # Basic parsing test
            parts = cmd.split()
            if len(parts) >= 2:
                format_lang = parts[1]
                if ':' in format_lang:
                    file_format, language = format_lang.split(':', 1)
                    print(f"    → Format: {file_format}, Language: {language}")
                else:
                    file_format = format_lang
                    language = 'eng'  # default
                    print(f"    → Format: {file_format}, Language: {language} (default)")
                    
                # Validate format
                if file_format in SUPPORTED_FORMATS:
                    print(f"    ✅ Format '{file_format}' is supported")
                else:
                    print(f"    ❌ Format '{file_format}' is not supported")
                    
                # Validate language
                if language in SUPPORTED_LANGUAGES:
                    print(f"    ✅ Language '{language}' is supported")
                else:
                    print(f"    ❌ Language '{language}' is not supported")
            else:
                print(f"    → Special command or help")
        
    except Exception as e:
        print(f"  ❌ Command parsing test failed: {e}")

def test_text_extraction():
    """Test text extraction functionality"""
    print("\n🧪 Testing text extraction...")
    
    # Create a test text file
    test_file = "test_audiobook.txt"
    test_content = "This is a test content for audiobook conversion. Hello world!"
    
    try:
        # Create test file
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_content)
        print(f"  ✅ Created test file: {test_file}")
        
        # Test extraction
        from plugins.audiobook import extract_text_from_txt
        
        extracted = extract_text_from_txt(test_file)
        if extracted == test_content:
            print("  ✅ Text extraction successful")
            print(f"    Content: {extracted[:50]}...")
        else:
            print(f"  ❌ Text extraction mismatch")
            print(f"    Expected: {test_content}")
            print(f"    Got: {extracted}")
            
        # Clean up
        os.remove(test_file)
        print("  ✅ Test file cleaned up")
        
    except Exception as e:
        print(f"  ❌ Text extraction test failed: {e}")
        # Clean up on error
        if os.path.exists(test_file):
            os.remove(test_file)

def test_directory_creation():
    """Test audiobook directory creation"""
    print("\n🧪 Testing directory creation...")
    
    try:
        from plugins.audiobook import AUDIOBOOK_DIR
        
        # The plugin should create this directory
        if os.path.exists(AUDIOBOOK_DIR):
            print(f"  ✅ Audiobook directory exists: {AUDIOBOOK_DIR}")
        else:
            # Try to create it
            os.makedirs(AUDIOBOOK_DIR, exist_ok=True)
            print(f"  ✅ Created audiobook directory: {AUDIOBOOK_DIR}")
            
        # Check if we can write to it
        test_file = os.path.join(AUDIOBOOK_DIR, "test_write.tmp")
        with open(test_file, 'w') as f:
            f.write("test")
        os.remove(test_file)
        print("  ✅ Directory is writable")
        
    except Exception as e:
        print(f"  ❌ Directory test failed: {e}")

def test_dependencies():
    """Test for required dependencies"""
    print("\n🧪 Testing dependencies...")
    
    dependencies = [
        ('PyPDF2', 'PDF text extraction'),
        ('pdfplumber', 'Alternative PDF extraction'),
        ('ebooklib', 'EPUB text extraction'), 
        ('pyttsx3', 'Text-to-speech conversion'),
        ('gtts', 'Google Text-to-speech'),
        ('pathlib', 'Path handling')
    ]
    
    for dep, purpose in dependencies:
        try:
            __import__(dep)
            print(f"  ✅ {dep} is available ({purpose})")
        except ImportError:
            print(f"  ⚠️  {dep} not installed ({purpose})")
            
    print("\n  📝 Note: Missing dependencies will use placeholder implementations")

if __name__ == "__main__":
    print("📚 Audiobook Plugin Test Suite")
    print("=" * 50)
    
    test_audiobook_import()
    test_command_parsing()
    test_text_extraction()
    test_directory_creation()
    test_dependencies()
    
    print("\n" + "=" * 50)
    print("✅ Audiobook plugin test completed!")
    print("\n🎯 Next steps:")
    print("  1. Install dependencies for full functionality:")
    print("     pip install PyPDF2 ebooklib pyttsx3 gTTS")
    print("  2. Test with real commands:")
    print("     /ab text:eng")
    print("     /ab help")
    print("     /ab status")
    print("  3. Upload files to convert to audiobooks!")
    print("\n📁 Audiobooks will be saved to: audiobooks/")
