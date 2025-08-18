#!/usr/bin/env python3
"""
Enhanced Logging System - Comprehensive logging for the torrent bot
Supports structured logging for audiobook and TTS operations
"""

import os
import sys
import logging
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

# Configure logging directory
LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

class EnhancedLogger:
    """Enhanced logger with structured logging capabilities"""
    
    def __init__(self, name: str, level: str = "INFO"):
        self.name = name
        self.logger = logging.getLogger(name)
        
        # Set level
        log_level = getattr(logging, level.upper(), logging.INFO)
        self.logger.setLevel(log_level)
        
        # Avoid duplicate handlers
        if not self.logger.handlers:
            self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup file and console handlers"""
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # File handler
        log_file = os.path.join(LOG_DIR, f"{self.name}.log")
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
    
    def info(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log info message with optional structured data"""
        if extra:
            message = f"{message} | {json.dumps(extra)}"
        self.logger.info(message)
    
    def debug(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log debug message with optional structured data"""
        if extra:
            message = f"{message} | {json.dumps(extra)}"
        self.logger.debug(message)
    
    def warning(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log warning message with optional structured data"""
        if extra:
            message = f"{message} | {json.dumps(extra)}"
        self.logger.warning(message)
    
    def error(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log error message with optional structured data"""
        if extra:
            message = f"{message} | {json.dumps(extra)}"
        self.logger.error(message)
    
    def critical(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log critical message with optional structured data"""
        if extra:
            message = f"{message} | {json.dumps(extra)}"
        self.logger.critical(message)
    
    def log_tts_operation(self, operation: str, details: Dict[str, Any]):
        """Log TTS-specific operations"""
        self.info(f"TTS_{operation.upper()}", {
            'timestamp': time.time(),
            'operation': operation,
            **details
        })
    
    def log_audiobook_conversion(self, 
                               text_length: int,
                               language: str,
                               voice_type: str,
                               engine: str,
                               output_file: str,
                               success: bool,
                               duration: float = None,
                               file_size: int = None):
        """Log audiobook conversion operations"""
        details = {
            'text_length': text_length,
            'language': language,
            'voice_type': voice_type,
            'engine': engine,
            'output_file': output_file,
            'success': success,
            'timestamp': time.time()
        }
        
        if duration is not None:
            details['duration_seconds'] = duration
        
        if file_size is not None:
            details['file_size_bytes'] = file_size
        
        if success:
            self.info("AUDIOBOOK_CONVERSION_SUCCESS", details)
        else:
            self.error("AUDIOBOOK_CONVERSION_FAILED", details)
    
    def log_engine_selection(self, requested: str, selected: str, available_engines: list):
        """Log TTS engine selection process"""
        self.info("TTS_ENGINE_SELECTION", {
            'requested_engine': requested,
            'selected_engine': selected,
            'available_engines': available_engines,
            'timestamp': time.time()
        })
    
    def log_file_processing(self, 
                          file_path: str,
                          file_type: str,
                          file_size: int,
                          processing_time: float,
                          success: bool,
                          extracted_chars: int = None):
        """Log file processing operations"""
        details = {
            'file_path': file_path,
            'file_type': file_type,
            'file_size_bytes': file_size,
            'processing_time_seconds': processing_time,
            'success': success,
            'timestamp': time.time()
        }
        
        if extracted_chars is not None:
            details['extracted_characters'] = extracted_chars
        
        if success:
            self.info("FILE_PROCESSING_SUCCESS", details)
        else:
            self.error("FILE_PROCESSING_FAILED", details)
    
    def log_user_command(self, user_id: int, command: str, flags: Dict[str, Any]):
        """Log user command execution"""
        self.info("USER_COMMAND", {
            'user_id': user_id,
            'command': command,
            'flags': flags,
            'timestamp': time.time()
        })
    
    def log_system_info(self, component: str, message: str, details: Optional[Dict[str, Any]] = None):
        """Log system information"""
        log_details = {
            'component': component,
            'timestamp': time.time()
        }
        
        if details:
            log_details.update(details)
        
        self.info(f"SYSTEM_{component.upper()}: {message}", log_details)
    
    def log_performance_metric(self, metric_name: str, value: float, unit: str = "seconds"):
        """Log performance metrics"""
        self.info(f"PERFORMANCE_{metric_name.upper()}", {
            'metric': metric_name,
            'value': value,
            'unit': unit,
            'timestamp': time.time()
        })

# Global logger instances
_loggers: Dict[str, EnhancedLogger] = {}

def get_logger(name: str) -> EnhancedLogger:
    """Get or create an enhanced logger instance"""
    if name not in _loggers:
        _loggers[name] = EnhancedLogger(name)
    return _loggers[name]

def configure_logging(level: str = "INFO"):
    """Configure global logging settings"""
    log_level = getattr(logging, level.upper(), logging.INFO)
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

def get_log_stats() -> Dict[str, Any]:
    """Get logging statistics"""
    stats = {
        'log_directory': LOG_DIR,
        'active_loggers': list(_loggers.keys()),
        'log_files': []
    }
    
    # Get log file information
    if os.path.exists(LOG_DIR):
        for filename in os.listdir(LOG_DIR):
            if filename.endswith('.log'):
                file_path = os.path.join(LOG_DIR, filename)
                file_stat = os.stat(file_path)
                stats['log_files'].append({
                    'name': filename,
                    'size_bytes': file_stat.st_size,
                    'modified': datetime.fromtimestamp(file_stat.st_mtime).isoformat()
                })
    
    return stats

def cleanup_old_logs(days: int = 30):
    """Clean up log files older than specified days"""
    if not os.path.exists(LOG_DIR):
        return
    
    cutoff_time = time.time() - (days * 24 * 60 * 60)
    cleaned_files = []
    
    for filename in os.listdir(LOG_DIR):
        if filename.endswith('.log'):
            file_path = os.path.join(LOG_DIR, filename)
            if os.path.getmtime(file_path) < cutoff_time:
                try:
                    os.remove(file_path)
                    cleaned_files.append(filename)
                except Exception as e:
                    print(f"Failed to remove {filename}: {e}")
    
    if cleaned_files:
        print(f"Cleaned up {len(cleaned_files)} old log files")
    
    return cleaned_files

def test_logging():
    """Test the enhanced logging system"""
    print("📝 Enhanced Logging System Test")
    print("=" * 40)
    
    # Test basic logging
    logger = get_logger("test_logger")
    
    logger.info("Test info message")
    logger.debug("Test debug message") 
    logger.warning("Test warning message")
    logger.error("Test error message")
    
    # Test structured logging
    logger.info("Structured log test", {
        'user_id': 12345,
        'action': 'test_action',
        'data': {'key': 'value'}
    })
    
    # Test TTS-specific logging
    logger.log_tts_operation("conversion", {
        'engine': 'openvoice',
        'language': 'english',
        'voice_type': 'female',
        'text_length': 100
    })
    
    # Test audiobook logging
    logger.log_audiobook_conversion(
        text_length=1500,
        language='english',
        voice_type='female', 
        engine='openvoice',
        output_file='test.mp3',
        success=True,
        duration=45.5,
        file_size=2048000
    )
    
    # Test engine selection logging
    logger.log_engine_selection(
        requested='auto',
        selected='openvoice',
        available_engines=['openvoice', 'enhanced_sapi', 'gtts']
    )
    
    # Show log stats
    stats = get_log_stats()
    print(f"\nLog Statistics:")
    print(f"  Directory: {stats['log_directory']}")
    print(f"  Active loggers: {len(stats['active_loggers'])}")
    print(f"  Log files: {len(stats['log_files'])}")
    
    for log_file in stats['log_files']:
        print(f"    {log_file['name']}: {log_file['size_bytes']} bytes")
    
    print(f"\n✅ Logging test complete!")

if __name__ == "__main__":
    test_logging()
