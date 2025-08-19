#!/usr/bin/env python3
"""
Simple test script to verify the reflection-based plugin system works
"""

import sys
import os
from pathlib import Path
from unittest.mock import Mock

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

def test_core_imports():
    """Test that core modules can be imported"""
    print("🧪 Testing core module imports...")
    
    try:
        from core import PluginBase, PluginRegistry, command, plugin_info
        print("✅ Core modules imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Core import failed: {e}")
        return False

def test_plugin_discovery():
    """Test plugin discovery mechanism"""
    print("🧪 Testing plugin discovery...")
    
    try:
        from core import PluginRegistry
        
        # Create mock bot
        bot_mock = Mock()
        
        # Create registry
        registry = PluginRegistry(
            bot=bot_mock,
            plugins_directory="plugins"
        )
        
        # Discover plugins
        registry.discover_plugins()
        
        # Check if plugins were found
        plugins = registry.get_plugin_info()
        print(f"✅ Found {len(plugins)} plugins:")
        
        for name, info in plugins.items():
            print(f"   • {name} v{info['version']}")
        
        return len(plugins) > 0
        
    except Exception as e:
        print(f"❌ Plugin discovery failed: {e}")
        return False

def test_command_registration():
    """Test command registration"""
    print("🧪 Testing command registration...")
    
    try:
        from core import PluginRegistry
        
        # Create mock bot
        bot_mock = Mock()
        
        # Create registry
        registry = PluginRegistry(
            bot=bot_mock,
            plugins_directory="plugins"
        )
        
        # Discover plugins
        registry.discover_plugins()
        
        # Check commands
        commands = registry.commands
        print(f"✅ Found {len(commands)} commands:")
        
        # Show some commands
        for cmd_name, cmd_data in list(commands.items())[:5]:
            if cmd_name == cmd_data['name']:  # Skip aliases
                print(f"   • /{cmd_name} - {cmd_data['description']}")
        
        return len(commands) > 0
        
    except Exception as e:
        print(f"❌ Command registration failed: {e}")
        return False

def test_plugin_metadata():
    """Test plugin metadata extraction"""
    print("🧪 Testing plugin metadata...")
    
    try:
        from plugins.system_info import SystemInfoPlugin
        from core import get_plugin_metadata
        
        # Test metadata extraction
        metadata = get_plugin_metadata(SystemInfoPlugin)
        
        print("✅ Plugin metadata extracted:")
        print(f"   • Name: {metadata['name']}")
        print(f"   • Version: {metadata['version']}")
        print(f"   • Description: {metadata['description']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Metadata extraction failed: {e}")
        return False

def test_command_attributes():
    """Test command attribute extraction"""
    print("🧪 Testing command attributes...")
    
    try:
        from plugins.system_info import SystemInfoPlugin
        from core import get_command_metadata
        
        # Create mock bot and plugin instance
        bot_mock = Mock()
        plugin = SystemInfoPlugin(bot_mock)
        
        # Test command discovery
        commands = plugin.commands
        
        print(f"✅ Found {len(commands)} commands in SystemInfoPlugin:")
        for cmd_name, cmd_data in commands.items():
            if cmd_name == cmd_data['name']:  # Skip aliases
                print(f"   • /{cmd_name} - {cmd_data['description']}")
        
        return len(commands) > 0
        
    except Exception as e:
        print(f"❌ Command attributes test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing Reflection-Based Plugin System")
    print("=" * 50)
    
    tests = [
        test_core_imports,
        test_plugin_discovery,
        test_command_registration,
        test_plugin_metadata,
        test_command_attributes
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            failed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! The plugin system is working correctly.")
        return True
    else:
        print("💥 Some tests failed. Check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

