#!/usr/bin/env python3
"""
TTS Engine Manager
Manages all TTS engines and handles fallback logic
"""

import os
import logging
from typing import List, Tuple, Optional
from .engines import AVAILABLE_ENGINES, BaseTTSEngine

logger = logging.getLogger(__name__)

class TTSEngineManager:
    """Manages all TTS engines with automatic fallback"""
    
    def __init__(self):
        self.engines: List[BaseTTSEngine] = []
        self.initialize_engines()
    
    def initialize_engines(self):
        """Initialize all available engines"""
        logger.info("🔧 Initializing TTS engines...")
        
        for engine_class in AVAILABLE_ENGINES:
            try:
                engine = engine_class()
                self.engines.append(engine)
                availability = "✅ Available" if engine.is_available() else "❌ Not available"
                logger.info(f"   {engine.name} (Priority {engine.priority}) - {availability}")
            except Exception as e:
                logger.warning(f"   Failed to initialize {engine_class.__name__}: {e}")
        
        # Sort by priority (0 = highest)
        self.engines.sort(key=lambda x: x.priority)
        logger.info(f"✅ Initialized {len(self.engines)} TTS engines")
    
    def get_available_engines(self) -> List[BaseTTSEngine]:
        """Get list of available engines"""
        return [engine for engine in self.engines if engine.is_available()]
    
    def convert_text(self, text: str, output_path: str, language: str = 'english', 
                    voice_type: str = 'female', preferred_engine: Optional[str] = None) -> Tuple[bool, str]:
        """
        Convert text to speech using best available engine
        
        Args:
            text: Text to convert
            output_path: Output file path
            language: Language ('english' or 'polish')
            voice_type: Voice type ('male' or 'female')
            preferred_engine: Preferred engine name (optional)
            
        Returns:
            (success, message)
        """
        
        if not text.strip():
            return False, "Empty text provided"
        
        # Get available engines
        available_engines = self.get_available_engines()
        
        if not available_engines:
            return False, "No TTS engines available"
        
        # If preferred engine specified, try it first
        if preferred_engine:
            for engine in available_engines:
                if preferred_engine.lower() in engine.name.lower():
                    logger.info(f"🎯 Trying preferred engine: {engine.name}")
                    success, message = engine.convert(text, output_path, language, voice_type)
                    if success:
                        return True, f"{engine.name}: {message}"
                    logger.warning(f"Preferred engine failed: {message}")
                    break
        
        # Try engines in priority order
        for engine in available_engines:
            if not engine.supports_language(language):
                logger.debug(f"⏭️ Skipping {engine.name} - doesn't support {language}")
                continue
            
            logger.info(f"🔄 Trying engine: {engine.name} (Priority {engine.priority})")
            
            try:
                success, message = engine.convert(text, output_path, language, voice_type)
                
                if success:
                    logger.info(f"✅ Success with {engine.name}: {message}")
                    return True, f"{engine.name}: {message}"
                else:
                    logger.warning(f"❌ Failed with {engine.name}: {message}")
                    
            except Exception as e:
                logger.error(f"💥 Exception in {engine.name}: {str(e)}")
                continue
        
        return False, "All TTS engines failed"
    
    def get_engine_status(self) -> dict:
        """Get status of all engines"""
        status = {
            'total_engines': len(self.engines),
            'available_engines': len(self.get_available_engines()),
            'engines': []
        }
        
        for engine in self.engines:
            engine_info = {
                'name': engine.name,
                'priority': engine.priority,
                'quality': engine.quality,
                'available': engine.is_available(),
                'languages': engine.supported_languages
            }
            status['engines'].append(engine_info)
        
        return status
