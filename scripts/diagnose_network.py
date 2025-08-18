#!/usr/bin/env python3
"""
Network connectivity diagnostic tool for Telegram bot
"""

import subprocess
import socket
import requests
import time
import os
from urllib.parse import urlparse

def test_basic_connectivity():
    """Test basic internet connectivity"""
    print("🌐 Basic Internet Connectivity")
    print("=" * 50)
    
    # Test 1: DNS Resolution
    try:
        print("🔍 Testing DNS resolution...")
        socket.gethostbyname('google.com')
        print("✅ DNS resolution working")
    except socket.gaierror as e:
        print(f"❌ DNS resolution failed: {e}")
        return False
    
    # Test 2: Basic HTTP connectivity
    try:
        print("🔍 Testing HTTP connectivity...")
        response = requests.get('https://httpbin.org/get', timeout=10)
        if response.status_code == 200:
            print("✅ HTTP connectivity working")
        else:
            print(f"⚠️ HTTP response code: {response.status_code}")
    except Exception as e:
        print(f"❌ HTTP connectivity failed: {e}")
        return False
    
    return True

def test_telegram_api():
    """Test Telegram API connectivity specifically"""
    print("\n📱 Telegram API Connectivity")
    print("=" * 50)
    
    # Get bot token from environment
    token = os.getenv('TELEGRAM_BOT_TOKEN', '').strip()
    if not token:
        print("❌ TELEGRAM_BOT_TOKEN not found in environment")
        return False
    
    # Test Telegram API endpoints
    telegram_urls = [
        f"https://api.telegram.org/bot{token}/getMe",
        f"https://api.telegram.org/bot{token}/getUpdates"
    ]
    
    for i, url in enumerate(telegram_urls, 1):
        print(f"🔍 Test {i}: {url.split('/')[-1]}...")
        try:
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                data = response.json()
                if data.get('ok'):
                    print(f"✅ {url.split('/')[-1]} - Success")
                    if 'result' in data and isinstance(data['result'], dict):
                        if 'username' in data['result']:
                            print(f"   Bot username: @{data['result']['username']}")
                else:
                    print(f"❌ {url.split('/')[-1]} - API returned error: {data}")
                    return False
            else:
                print(f"❌ {url.split('/')[-1]} - HTTP {response.status_code}")
                return False
        except requests.exceptions.ConnectionError as e:
            print(f"❌ {url.split('/')[-1]} - Connection error: {e}")
            return False
        except requests.exceptions.Timeout:
            print(f"❌ {url.split('/')[-1]} - Timeout after 30s")
            return False
        except Exception as e:
            print(f"❌ {url.split('/')[-1]} - Error: {e}")
            return False
    
    return True

def test_docker_network():
    """Test if we're in a Docker environment and check network"""
    print("\n🐳 Docker Network Analysis")
    print("=" * 50)
    
    # Check if we're in Docker
    docker_indicators = [
        os.path.exists('/.dockerenv'),
        os.path.exists('/proc/self/cgroup') and any('docker' in line for line in open('/proc/self/cgroup', 'r').readlines()),
        'container' in os.environ.get('init', '')
    ]
    
    if any(docker_indicators):
        print("🐳 Running inside Docker container")
        
        # Check container network configuration
        try:
            result = subprocess.run(['ip', 'route'], capture_output=True, text=True)
            if result.returncode == 0:
                print("📋 Container routing:")
                for line in result.stdout.strip().split('\n'):
                    print(f"   {line}")
            else:
                print("⚠️ Could not check container routing")
        except FileNotFoundError:
            print("⚠️ ip command not available in container")
        
        # Check DNS configuration
        try:
            with open('/etc/resolv.conf', 'r') as f:
                dns_config = f.read()
            print(f"📋 DNS configuration:")
            for line in dns_config.strip().split('\n'):
                print(f"   {line}")
        except Exception as e:
            print(f"⚠️ Could not read DNS config: {e}")
    else:
        print("💻 Running on host system (not in Docker)")
    
    return True

def test_firewall_ports():
    """Test if specific ports are accessible"""
    print("\n🔥 Port Accessibility Test")
    print("=" * 50)
    
    test_ports = [
        ('api.telegram.org', 443, 'Telegram API HTTPS'),
        ('google.com', 443, 'Google HTTPS'),
        ('httpbin.org', 443, 'Test HTTPS')
    ]
    
    for host, port, description in test_ports:
        print(f"🔍 Testing {description} ({host}:{port})...")
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            result = sock.connect_ex((host, port))
            sock.close()
            
            if result == 0:
                print(f"✅ {description} - Port accessible")
            else:
                print(f"❌ {description} - Port blocked or unreachable")
        except Exception as e:
            print(f"❌ {description} - Error: {e}")

def suggest_fixes():
    """Suggest potential fixes"""
    print("\n💡 Potential Solutions")
    print("=" * 50)
    
    solutions = [
        "🔧 Network Solutions:",
        "   • Check internet connection on host machine",
        "   • Restart Docker daemon: sudo systemctl restart docker",
        "   • Check Docker network: docker network ls",
        "   • Recreate containers with: docker-compose down && docker-compose up",
        "",
        "🔧 Docker-specific Solutions:",
        "   • Add to docker-compose.yml:",
        "     networks:",
        "       - default",
        "   • Check container can reach internet:",
        "     docker exec <container> ping google.com",
        "",
        "🔧 Firewall Solutions:",
        "   • Allow HTTPS traffic (port 443)",
        "   • Check iptables rules",
        "   • Disable firewall temporarily to test",
        "",
        "🔧 DNS Solutions:",
        "   • Add to docker-compose.yml:",
        "     dns:",
        "       - 8.8.8.8",
        "       - 1.1.1.1",
        "",
        "🔧 Environment Solutions:",
        "   • Verify TELEGRAM_BOT_TOKEN is correct",
        "   • Check token has proper permissions",
        "   • Test bot from outside Docker first"
    ]
    
    for solution in solutions:
        print(solution)

def main():
    """Run all diagnostic tests"""
    print("🚀 Telegram Bot Network Diagnostics")
    print("=" * 60)
    print()
    
    # Load environment
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ Environment variables loaded")
    except ImportError:
        print("⚠️ python-dotenv not available, using system env")
    
    # Run tests
    tests_passed = 0
    total_tests = 4
    
    if test_basic_connectivity():
        tests_passed += 1
    
    if test_telegram_api():
        tests_passed += 1
    
    if test_docker_network():
        tests_passed += 1
    
    test_firewall_ports()
    tests_passed += 1  # This test is informational
    
    # Summary
    print(f"\n📊 Test Results: {tests_passed}/{total_tests} components checked")
    
    if tests_passed < total_tests:
        suggest_fixes()
    else:
        print("\n🎉 All network tests passed!")
        print("💡 The connectivity issue may be temporary - try running the bot again")

if __name__ == "__main__":
    main()
