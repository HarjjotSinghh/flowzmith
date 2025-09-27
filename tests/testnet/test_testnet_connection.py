#!/usr/bin/env python3
"""
Simple test to validate Flow Testnet connection and credentials.
This test does not deploy any contracts, just validates the setup.
"""

import sys
import os
import asyncio
import subprocess
from pathlib import Path

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

def check_flow_cli():
    """Check if Flow CLI is installed and working."""
    try:
        result = subprocess.run(
            ["flow", "version"],
            capture_output=True,
            text=True,
            check=True
        )
        print(f"✅ Flow CLI installed: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError:
        print("❌ Flow CLI not found or not working")
        print("Please install Flow CLI:")
        print("  sh -ci \"$(curl -fsSL https://storage.googleapis.com/flow-cli/install.sh)\"")
        return False
    except FileNotFoundError:
        print("❌ Flow CLI not found in PATH")
        return False

def check_testnet_credentials():
    """Check if required testnet credentials are available."""
    flow_account_address = os.getenv("FLOW_ACCOUNT_ADDRESS")
    flow_private_key = os.getenv("FLOW_PRIVATE_KEY")
    
    print("\n🔍 Checking testnet credentials...")
    
    if not flow_account_address:
        print("❌ FLOW_ACCOUNT_ADDRESS environment variable not set")
        return False, None, None
    
    if not flow_private_key:
        print("❌ FLOW_PRIVATE_KEY environment variable not set")
        return False, None, None
    
    # Basic format validation
    if not flow_account_address.startswith('0x') or len(flow_account_address) != 18:
        print(f"❌ Invalid account address format: {flow_account_address}")
        print("Expected format: 0x1234567890abcdef (18 characters)")
        return False, None, None
    
    if len(flow_private_key) != 64:
        print(f"❌ Invalid private key length: {len(flow_private_key)} (expected 64)")
        return False, None, None
    
    print(f"✅ Account Address: {flow_account_address}")
    print(f"✅ Private Key: {'*' * 56}{flow_private_key[-8:]}")
    
    return True, flow_account_address, flow_private_key

def test_testnet_connection(account_address):
    """Test connection to Flow Testnet."""
    print(f"\n🌐 Testing connection to Flow Testnet...")
    
    try:
        # Try to get account information
        result = subprocess.run(
            ["flow", "accounts", "get", account_address, "--network", "testnet"],
            capture_output=True,
            text=True,
            check=True
        )
        
        print("✅ Successfully connected to Flow Testnet")
        
        # Parse account information
        output = result.stdout
        if "Balance:" in output:
            # Extract balance
            for line in output.split('\n'):
                if "Balance:" in line:
                    balance = line.split("Balance:")[1].strip()
                    print(f"💰 Account Balance: {balance}")
                    
                    # Check if balance is sufficient
                    try:
                        balance_float = float(balance.split()[0])
                        if balance_float < 1.0:
                            print("⚠️  Low balance detected. Consider getting more FLOW from the faucet:")
                            print("   https://faucet.flow.com/")
                        else:
                            print("✅ Sufficient balance for testing")
                    except (ValueError, IndexError):
                        print("⚠️  Could not parse balance amount")
                    break
        
        return True
        
    except subprocess.CalledProcessError as e:
        print("❌ Failed to connect to Flow Testnet")
        print(f"Error: {e.stderr}")
        return False

def test_flow_cli_testnet_config():
    """Test Flow CLI testnet configuration."""
    print(f"\n⚙️  Testing Flow CLI testnet configuration...")
    
    try:
        # Test basic testnet connectivity
        result = subprocess.run(
            ["flow", "blocks", "get", "latest", "--network", "testnet"],
            capture_output=True,
            text=True,
            check=True
        )
        
        print("✅ Flow CLI can connect to testnet")
        
        # Parse block information
        if "Height:" in result.stdout:
            for line in result.stdout.split('\n'):
                if "Height:" in line:
                    height = line.split("Height:")[1].strip()
                    print(f"📦 Latest Block Height: {height}")
                    break
        
        return True
        
    except subprocess.CalledProcessError as e:
        print("❌ Flow CLI cannot connect to testnet")
        print(f"Error: {e.stderr}")
        return False

async def main():
    """Main test function."""
    print("🔍 Flow Testnet Connection Test")
    print("=" * 40)
    
    # Test 1: Flow CLI installation
    if not check_flow_cli():
        return False
    
    # Test 2: Credentials
    creds_valid, account_address, private_key = check_testnet_credentials()
    if not creds_valid:
        print("\n❌ Please set up your testnet credentials:")
        print("  export FLOW_ACCOUNT_ADDRESS=0x1234567890abcdef")
        print("  export FLOW_PRIVATE_KEY=your_private_key_here")
        print("\nOr run the setup script:")
        print("  ./tests/testnet/setup_testnet_env.sh")
        return False
    
    # Test 3: Flow CLI testnet configuration
    if not test_flow_cli_testnet_config():
        return False
    
    # Test 4: Account connection
    if not test_testnet_connection(account_address):
        return False
    
    print("\n🎉 All testnet connection tests passed!")
    print("✅ You're ready to run testnet deployment tests")
    print("\nNext steps:")
    print("  python tests/testnet/test_complete_workflow_testnet.py")
    
    return True

if __name__ == "__main__":
    print("🚀 Starting testnet connection test...")
    success = asyncio.run(main())
    
    if not success:
        print("\n❌ TESTNET CONNECTION TEST FAILED!")
        print("Please fix the issues above before running deployment tests.")
        sys.exit(1)
    else:
        print("\n✅ TESTNET CONNECTION TEST SUCCESSFUL!")
        sys.exit(0)