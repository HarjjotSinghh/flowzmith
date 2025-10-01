#!/usr/bin/env python3
"""
Test script for Flowzmith CLI

This script runs basic functionality tests for the CLI tool.
"""

import sys
import subprocess
import json
from pathlib import Path
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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
        ("python cli.py crawl-docs --help", "Firecrawl crawl-docs command help"),
        ("python cli.py firecrawl-search --help", "Firecrawl search command help"),
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

def test_firecrawl_integration():
    """Test Firecrawl integration functionality."""
    print("\n🔥 Testing Firecrawl Integration")
    print("-" * 30)

    # Test Firecrawl CLI integration import
    try:
        from src.cli.firecrawl_integration import FirecrawlCLIIntegration
        from src.cli.api_client import APIClient
        print("✅ FirecrawlCLIIntegration import successful")
        
        # Test initialization with required api_client
        api_client = APIClient("http://localhost:8000")
        firecrawl_cli = FirecrawlCLIIntegration(api_client)
        print("✅ FirecrawlCLIIntegration initialization successful")
        
        # Test that required methods exist
        required_methods = [
            'search_documentation_for_contract',
            'crawl_custom_documentation',
            'interactive_documentation_search'
        ]
        
        for method in required_methods:
            if hasattr(firecrawl_cli, method):
                print(f"✅ Method {method} exists")
            else:
                print(f"❌ Method {method} missing")
                return False
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing Firecrawl integration: {e}")
        return False

def test_contract_creator_firecrawl():
    """Test ContractCreator Firecrawl integration."""
    print("\n📝 Testing ContractCreator Firecrawl Integration")
    print("-" * 30)

    try:
        from src.cli.contract_creator import ContractCreator
        from src.cli.api_client import APIClient
        
        # Test that ContractCreator can be initialized with Firecrawl
        api_client = APIClient("http://localhost:8000")
        creator = ContractCreator(api_client)
        
        # Test that firecrawl_integration attribute exists
        if hasattr(creator, 'firecrawl_integration'):
            print("✅ ContractCreator has firecrawl_integration attribute")
        else:
            print("❌ ContractCreator missing firecrawl_integration attribute")
            return False
        
        # Test that _get_firecrawl_search_input method exists
        if hasattr(creator, '_get_firecrawl_search_input'):
            print("✅ ContractCreator has _get_firecrawl_search_input method")
        else:
            print("❌ ContractCreator missing _get_firecrawl_search_input method")
            return False
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing ContractCreator Firecrawl integration: {e}")
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

    # Test Firecrawl integration
    firecrawl_ok = test_firecrawl_integration()

    # Test ContractCreator Firecrawl integration
    contract_firecrawl_ok = test_contract_creator_firecrawl()

    print("\n" + "=" * 60)
    print("📋 Test Summary")
    print("-" * 30)
    print(f"Dependencies: {'✅' if deps_ok else '❌'}")
    print(f"Server: {'✅' if server_ok else '❌'}")
    print(f"CLI Commands: {'✅' if cli_ok else '❌'}")
    print(f"Firecrawl Integration: {'✅' if firecrawl_ok else '❌'}")
    print(f"ContractCreator Firecrawl: {'✅' if contract_firecrawl_ok else '❌'}")

    if deps_ok and cli_ok and firecrawl_ok and contract_firecrawl_ok:
        print("\n🎉 CLI tool is ready to use!")
        if server_ok:
            print("✅ Full functionality available including Firecrawl integration")
        else:
            print("⚠️  Server needs to be started for full functionality")
        return 0
    else:
        print("\n❌ Issues found. Please fix the problems above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())