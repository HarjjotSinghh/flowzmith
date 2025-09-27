#!/usr/bin/env python3
"""
Test script for Flowzmith CLI

This script runs basic functionality tests for the CLI tool.
"""

import sys
import subprocess
import json
from pathlib import Path

def run_command(cmd, description):
    """Run a command and return the result."""
    print(f"\n🧪 Testing: {description}")
    print(f"🔧 Command: {cmd}")

    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            print("✅ Success")
            return result.stdout
        else:
            print("❌ Failed")
            print(f"Error: {result.stderr}")
            return None
    except subprocess.TimeoutExpired:
        print("❌ Timeout")
        return None
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None

def test_cli_commands():
    """Test basic CLI commands."""
    print("🚀 Testing Flowzmith CLI")
    print("=" * 50)

    tests = [
        ("python cli.py --help", "CLI help command"),
        ("python cli.py version", "CLI version command"),
        ("python cli.py status", "CLI status command"),
    ]

    passed = 0
    total = len(tests)

    for cmd, desc in tests:
        output = run_command(cmd, desc)
        if output:
            passed += 1
        print("-" * 50)

    print(f"\n📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed!")
        return True
    else:
        print("❌ Some tests failed")
        return False

def test_server_connection():
    """Test if server is running and accessible."""
    print("\n🌐 Testing Server Connection")
    print("-" * 30)

    import requests

    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "healthy":
                print("✅ Server is healthy and running")
                return True
            else:
                print("❌ Server is unhealthy")
                return False
        else:
            print(f"❌ Server returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server")
        print("💡 Please start the server with: python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload")
        return False
    except Exception as e:
        print(f"❌ Error checking server: {e}")
        return False

def test_dependencies():
    """Test if all required dependencies are installed."""
    print("\n📦 Testing Dependencies")
    print("-" * 30)

    required_packages = [
        "typer",
        "rich",
        "aiohttp",
        "websockets",
        "sqlalchemy",
        "fastapi",
        "uvicorn"
    ]

    missing = []

    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} (missing)")
            missing.append(package)

    if missing:
        print(f"\n❌ Missing packages: {', '.join(missing)}")
        print("💡 Install with: pip install -r requirements.txt")
        return False
    else:
        print("\n✅ All dependencies are installed")
        return True

def main():
    """Run all tests."""
    print("🧪 Flowzmith CLI Test Suite")
    print("=" * 60)

    # Test dependencies
    deps_ok = test_dependencies()

    # Test server connection
    server_ok = test_server_connection()

    # Test CLI commands
    cli_ok = test_cli_commands()

    print("\n" + "=" * 60)
    print("📋 Test Summary")
    print("-" * 30)
    print(f"Dependencies: {'✅' if deps_ok else '❌'}")
    print(f"Server: {'✅' if server_ok else '❌'}")
    print(f"CLI Commands: {'✅' if cli_ok else '❌'}")

    if deps_ok and cli_ok:
        print("\n🎉 CLI tool is ready to use!")
        if server_ok:
            print("✅ Full functionality available")
        else:
            print("⚠️  Server needs to be started for full functionality")
        return 0
    else:
        print("\n❌ Issues found. Please fix the problems above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())