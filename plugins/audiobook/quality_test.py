#!/usr/bin/env python3
"""
🎭 Comprehensive TTS Quality Test
Porównanie jakości różnych konfiguracji TTS
"""

import os
import sys
import logging
import time

# Setup paths
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_piper_configurations():
    """Test różnych konfiguracji Piper TTS"""
    print("🎭 Comprehensive TTS Quality Test")
    print("=" * 50)
    
    test_sentences = [
        "Witaj świecie! To jest test systemu syntezy mowy.",
        "Czy ten głos brzmi naturalnie i przyjemnie?",
        "Testujemy różne parametry jakości dźwięku."
    ]
    
    # Test 1: Original Piper TTS
    print("\n1️⃣ Testing Original Piper TTS...")
    try:
        from piper_tts import get_piper_tts
        
        original_piper = get_piper_tts()
        if original_piper.is_available():
            for i, text in enumerate(test_sentences):
                output_path = f"test_original_{i+1}.wav"
                start_time = time.time()
                success = original_piper.synthesize_text(text, output_path)
                duration = time.time() - start_time
                
                if success and os.path.exists(output_path):
                    file_size = os.path.getsize(output_path)
                    print(f"   ✅ Sentence {i+1}: {file_size} bytes, {duration:.2f}s")
                else:
                    print(f"   ❌ Sentence {i+1}: Failed")
        else:
            print("   ❌ Original Piper not available")
    except Exception as e:
        print(f"   💥 Original Piper failed: {e}")
    
    # Test 2: Enhanced Piper TTS (Natural preset)
    print("\n2️⃣ Testing Enhanced Piper TTS (Natural)...")
    try:
        from enhanced_piper_tts import get_piper_tts as get_enhanced_piper
        
        enhanced_piper = get_enhanced_piper()
        if enhanced_piper.is_available():
            for i, text in enumerate(test_sentences):
                output_path = f"test_enhanced_natural_{i+1}.wav"
                start_time = time.time()
                success = enhanced_piper.synthesize_text(text, output_path, quality_preset="natural")
                duration = time.time() - start_time
                
                if success and os.path.exists(output_path):
                    file_size = os.path.getsize(output_path)
                    print(f"   ✅ Sentence {i+1}: {file_size} bytes, {duration:.2f}s")
                else:
                    print(f"   ❌ Sentence {i+1}: Failed")
        else:
            print("   ❌ Enhanced Piper not available")
    except Exception as e:
        print(f"   💥 Enhanced Piper failed: {e}")
    
    # Test 3: Enhanced Piper TTS (Expressive preset)
    print("\n3️⃣ Testing Enhanced Piper TTS (Expressive)...")
    try:
        enhanced_piper = get_enhanced_piper()
        if enhanced_piper.is_available():
            for i, text in enumerate(test_sentences):
                output_path = f"test_enhanced_expressive_{i+1}.wav"
                start_time = time.time()
                success = enhanced_piper.synthesize_text(text, output_path, quality_preset="expressive")
                duration = time.time() - start_time
                
                if success and os.path.exists(output_path):
                    file_size = os.path.getsize(output_path)
                    print(f"   ✅ Sentence {i+1}: {file_size} bytes, {duration:.2f}s")
                else:
                    print(f"   ❌ Sentence {i+1}: Failed")
    except Exception as e:
        print(f"   💥 Enhanced Expressive failed: {e}")
    
    # Test 4: Voice Cloning with Enhanced Piper
    print("\n4️⃣ Testing Voice Cloning (Enhanced + Processing)...")
    try:
        from polish_voice_converter import PolishVoiceConverter
        
        voice_converter = PolishVoiceConverter()
        if voice_converter.is_available():
            for i, text in enumerate(test_sentences):
                output_path = f"test_voice_cloning_{i+1}.wav"
                start_time = time.time()
                success = voice_converter.synthesize_with_voice_cloning(text, output_path)
                duration = time.time() - start_time
                
                if success and os.path.exists(output_path):
                    file_size = os.path.getsize(output_path)
                    print(f"   ✅ Sentence {i+1}: {file_size} bytes, {duration:.2f}s")
                else:
                    print(f"   ❌ Sentence {i+1}: Failed")
        else:
            print("   ❌ Voice Cloning not available")
    except Exception as e:
        print(f"   💥 Voice Cloning failed: {e}")

def analyze_audio_quality():
    """Analizuje jakość wygenerowanych plików audio"""
    print("\n📊 Audio Quality Analysis")
    print("=" * 30)
    
    import glob
    
    test_files = {
        "Original Piper": glob.glob("test_original_*.wav"),
        "Enhanced Natural": glob.glob("test_enhanced_natural_*.wav"),
        "Enhanced Expressive": glob.glob("test_enhanced_expressive_*.wav"),
        "Voice Cloning": glob.glob("test_voice_cloning_*.wav")
    }
    
    for category, files in test_files.items():
        if files:
            total_size = sum(os.path.getsize(f) for f in files)
            avg_size = total_size / len(files)
            print(f"📁 {category}:")
            print(f"   Files: {len(files)}")
            print(f"   Average size: {avg_size:.0f} bytes")
            print(f"   Total size: {total_size} bytes")
            
            # Próba analizy audio właściwości
            try:
                import torchaudio
                
                for file in files[:1]:  # Analizuj tylko pierwszy plik z kategorii
                    try:
                        audio, sr = torchaudio.load(file)
                        duration = audio.shape[1] / sr
                        max_amp = audio.max().item()
                        rms = audio.pow(2).mean().sqrt().item()
                        
                        print(f"   📊 {os.path.basename(file)}:")
                        print(f"      Duration: {duration:.2f}s")
                        print(f"      Sample rate: {sr} Hz")
                        print(f"      Max amplitude: {max_amp:.4f}")
                        print(f"      RMS level: {rms:.4f}")
                        print(f"      Dynamic range: {max_amp/rms:.2f}x")
                        
                    except Exception as e:
                        print(f"      ❌ Analysis failed: {e}")
                        
            except ImportError:
                print("   ℹ️ TorchAudio not available for detailed analysis")
        else:
            print(f"❌ {category}: No files found")

def cleanup_test_files():
    """Opcjonalne czyszczenie plików testowych"""
    import glob
    
    test_files = glob.glob("test_*.wav")
    if test_files:
        response = input(f"\n🗑️ Remove {len(test_files)} test files? (y/N): ")
        if response.lower() == 'y':
            for file in test_files:
                try:
                    os.remove(file)
                    print(f"   Removed {file}")
                except Exception as e:
                    print(f"   Failed to remove {file}: {e}")
        else:
            print("   Test files kept for manual review")

if __name__ == "__main__":
    try:
        test_piper_configurations()
        analyze_audio_quality()
        
        print("\n🎯 Quality Test Complete!")
        print("\nRecommendations:")
        print("📋 1. Compare audio files manually to hear differences")
        print("📋 2. Enhanced Piper should sound less robotic")
        print("📋 3. Voice Cloning should have more natural characteristics")
        print("📋 4. Check file sizes - larger may indicate better quality")
        
        cleanup_test_files()
        
    except KeyboardInterrupt:
        print("\n⏹️ Test interrupted by user")
    except Exception as e:
        print(f"\n💥 Test failed: {e}")
        import traceback
        traceback.print_exc()
