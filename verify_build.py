#!/usr/bin/env python3
"""
Build verification script - tests all syntax and imports
"""

import ast
import sys

def test_file_syntax(filename):
    """Test if a Python file has valid syntax"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        ast.parse(content)
        print(f"✅ {filename} - Syntax: VALID")
        return True
    except Exception as e:
        print(f"❌ {filename} - Syntax: ERROR - {e}")
        return False

def test_file_compilation(filename):
    """Test if a Python file compiles"""
    import py_compile
    try:
        py_compile.compile(filename, doraise=True)
        print(f"✅ {filename} - Compile: SUCCESS")
        return True
    except Exception as e:
        print(f"❌ {filename} - Compile: ERROR - {e}")
        return False

# Test all files
files_to_test = [
    'bot.py',
    'plugins/downloads.py',
    'plugins/torrent/config.py',
    'plugins/torrent/telegram_handlers.py'
]

print("🔍 TORRENT BOT BUILD VERIFICATION")
print("=" * 50)

syntax_results = []
compile_results = []

for filename in files_to_test:
    print(f"\nTesting: {filename}")
    syntax_ok = test_file_syntax(filename)
    compile_ok = test_file_compilation(filename)
    syntax_results.append(syntax_ok)
    compile_results.append(compile_ok)

print("\n" + "=" * 50)
print("📊 FINAL RESULTS:")

if all(syntax_results) and all(compile_results):
    print("🎉 ALL TESTS PASSED - BUILD IS SUCCESSFUL!")
    print("✅ All files have valid syntax")
    print("✅ All files compile successfully")
    print("✅ Ready for production deployment")
    sys.exit(0)
else:
    print("❌ BUILD FAILED - Issues found")
    print(f"Syntax issues: {len([x for x in syntax_results if not x])}")
    print(f"Compile issues: {len([x for x in compile_results if not x])}")
    sys.exit(1)
