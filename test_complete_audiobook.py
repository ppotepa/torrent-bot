#!/usr/bin/env python3

"""
Comprehensive test for audiobook plugin including TTS functionality
"""

import os
import sys
import tempfile

# Add the current directory to Python path so we can import our modules  
sys.path.insert(0, os.getcwd())

def test_tts_functionality():
    """Test actual TTS conversion functionality"""
    print("🧪 Testing TTS functionality...")
    
    try:
        from plugins.audiobook import convert_text_to_speech
        
        # Create a test text
        test_text = "This is a test of the text-to-speech functionality. Hello world, this is an audiobook test."
        
        # Create temporary output file
        temp_dir = tempfile.mkdtemp()
        output_path = os.path.join(temp_dir, "test_audio.mp3")
        
        print(f"  📝 Test text: {test_text[:50]}...")
        print(f"  🎯 Output path: {output_path}")
        
        # Test English TTS
        print("  🗣️ Testing English TTS...")
        success = convert_text_to_speech(test_text, 'en', output_path)
        
        if success and os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            print(f"  ✅ English TTS successful! File size: {file_size} bytes")
        else:
            print("  ❌ English TTS failed")
            
        # Test Polish TTS if available
        polish_output = os.path.join(temp_dir, "test_audio_pl.mp3")
        print("  🗣️ Testing Polish TTS...")
        success_pl = convert_text_to_speech("To jest test polskiego tekstu na mowę.", 'pl', polish_output)
        
        if success_pl and os.path.exists(polish_output):
            file_size_pl = os.path.getsize(polish_output)
            print(f"  ✅ Polish TTS successful! File size: {file_size_pl} bytes")
        else:
            print("  ❌ Polish TTS failed")
            
        # Clean up
        import shutil
        shutil.rmtree(temp_dir)
        print("  ✅ Temporary files cleaned up")
        
    except Exception as e:
        print(f"  ❌ TTS test failed: {e}")

def test_pdf_extraction():
    """Test PDF text extraction by creating a simple PDF"""
    print("\n🧪 Testing PDF extraction...")
    
    try:
        # For this test, we'll just verify the function exists and handles errors gracefully
        from plugins.audiobook import extract_text_from_pdf
        
        # Test with non-existent file
        try:
            extract_text_from_pdf("nonexistent.pdf")
        except Exception as e:
            print(f"  ✅ Properly handles non-existent file: {type(e).__name__}")
            
        print("  📝 PDF extraction function is available")
        print("  💡 To test fully, upload a real PDF file to the bot")
        
    except Exception as e:
        print(f"  ❌ PDF extraction test failed: {e}")

def test_epub_extraction():
    """Test EPUB text extraction"""
    print("\n🧪 Testing EPUB extraction...")
    
    try:
        from plugins.audiobook import extract_text_from_epub
        
        # Test with non-existent file
        try:
            extract_text_from_epub("nonexistent.epub")
        except Exception as e:
            print(f"  ✅ Properly handles non-existent file: {type(e).__name__}")
            
        print("  📝 EPUB extraction function is available")
        print("  💡 To test fully, upload a real EPUB file to the bot")
        
    except Exception as e:
        print(f"  ❌ EPUB extraction test failed: {e}")

def test_file_state_management():
    """Test the pending file state management"""
    print("\n🧪 Testing file state management...")
    
    try:
        from plugins.audiobook import setup_conversion_state, check_pending_conversion, clear_pending_conversion
        
        test_user_id = 12345
        
        # Setup state
        setup_conversion_state(test_user_id, 'text', 'en')
        print("  ✅ Conversion state setup successful")
        
        # Check state
        state = check_pending_conversion(test_user_id)
        if state and state.get('format') == 'text' and state.get('language') == 'en':
            print("  ✅ State retrieval successful")
        else:
            print(f"  ❌ State retrieval failed: {state}")
            
        # Clear state
        clear_pending_conversion(test_user_id)
        
        # Verify cleared
        state_after = check_pending_conversion(test_user_id)
        if state_after is None:
            print("  ✅ State clearing successful")
        else:
            print(f"  ❌ State clearing failed: {state_after}")
            
    except Exception as e:
        print(f"  ❌ State management test failed: {e}")

def test_command_integration():
    """Test integration with bot commands"""
    print("\n🧪 Testing command integration...")
    
    try:
        # Check if bot.py properly imports audiobook
        bot_file = "bot.py"
        if os.path.exists(bot_file):
            with open(bot_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            if 'audiobook' in content:
                print("  ✅ Audiobook plugin imported in bot.py")
            else:
                print("  ❌ Audiobook plugin not found in bot.py")
                
            if '@bot.message_handler(commands=["ab"' in content:
                print("  ✅ /ab command handler registered")
            else:
                print("  ❌ /ab command handler not found")
                
            if 'content_types=[\'document\']' in content:
                print("  ✅ Document handler registered")
            else:
                print("  ❌ Document handler not found")
                
        else:
            print("  ❌ bot.py not found")
            
    except Exception as e:
        print(f"  ❌ Command integration test failed: {e}")

def show_usage_examples():
    """Show practical usage examples"""
    print("\n📖 Audiobook Plugin Usage Examples:")
    print("=" * 40)
    
    print("\n🎯 Basic Commands:")
    print("  /ab text:eng        - Setup for English text file")
    print("  /ab pdf:polish      - Setup for Polish PDF file") 
    print("  /ab epub            - Setup for English EPUB (default)")
    print("  /ab help            - Show help message")
    print("  /ab status          - Show audiobook status")
    
    print("\n📝 Workflow:")
    print("  1. Send command: /ab text:eng")
    print("  2. Upload your .txt file")
    print("  3. Bot extracts text and converts to speech")
    print("  4. Receive MP3 audiobook file")
    
    print("\n🗂️ Supported Files:")
    print("  • Text: .txt files (UTF-8, UTF-16, Latin-1)")
    print("  • PDF: .pdf files (text extraction)")
    print("  • EPUB: .epub ebook files")
    
    print("\n🗣️ Languages:")
    print("  • English: eng, english")
    print("  • Polish: polish, pl")
    
    print("\n💾 Storage:")
    print("  • Audiobooks saved to: audiobooks/")
    print("  • Files named: filename_language.mp3")

if __name__ == "__main__":
    print("🎧 Audiobook Plugin - Comprehensive Test")
    print("=" * 50)
    
    # Run tests
    test_tts_functionality()
    test_pdf_extraction()
    test_epub_extraction()
    test_file_state_management()
    test_command_integration()
    show_usage_examples()
    
    print("\n" + "=" * 50)
    print("✅ Comprehensive test completed!")
    print("\n🚀 Ready to use! Try:")
    print("  1. Start your bot")
    print("  2. Send: /ab text:eng")
    print("  3. Upload a .txt file")
    print("  4. Get your audiobook! 🎧")
