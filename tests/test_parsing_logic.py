#!/usr/bin/env python3
"""
Test script to verify our parsing logic with simulated Flow CLI output.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.cli.flow_manager import FlowProjectManager

def test_parsing_with_simulated_output():
    """Test parsing logic with various simulated Flow CLI outputs."""
    
    print("🔍 Testing Flow CLI Output Parsing Logic")
    print("=" * 50)
    
    # Create a FlowProjectManager instance
    manager = FlowProjectManager()
    
    # Test cases based on Flow CLI documentation
    test_cases = [
        {
            "name": "Successful deployment (from docs)",
            "stdout": """
Deploying 2 contracts for accounts: my-testnet-account

NonFungibleToken -> 0x8910590293346ec4
KittyItems -> 0x8910590293346ec4

✨ All contracts deployed successfully

Transaction ID: 0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef
""",
            "stderr": "",
            "returncode": 0
        },
        {
            "name": "Single contract deployment",
            "stdout": """
Deploying 1 contracts for accounts: emulator-account

HelloWorld -> 0xf8d6e0586b0a20c7

✨ All contracts deployed successfully

Transaction ID: 0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890
""",
            "stderr": "",
            "returncode": 0
        },
        {
            "name": "Deployment with account info",
            "stdout": """
Deploying 1 contracts for accounts: my-account

Using account: 0x1234567890abcdef
Contract deployed at: 0x1234567890abcdef
Organization -> 0x1234567890abcdef

✨ All contracts deployed successfully

Transaction ID: 0x9876543210fedcba9876543210fedcba9876543210fedcba9876543210fedcba
""",
            "stderr": "",
            "returncode": 0
        },
        {
            "name": "Deployment with verbose output",
            "stdout": """
Deploying 1 contracts for accounts: testnet-account

Account address: 0xea0b8be271e5a26b
Deploying to account: 0xea0b8be271e5a26b
Organization -> 0xea0b8be271e5a26b

✨ All contracts deployed successfully

Transaction ID: 0x5555aaaa5555aaaa5555aaaa5555aaaa5555aaaa5555aaaa5555aaaa5555aaaa
""",
            "stderr": "",
            "returncode": 0
        },
        {
            "name": "Failed deployment",
            "stdout": """
Deploying 1 contracts for accounts: emulator-account

❌ Failed to deploy contract HelloWorld: failed to deploy contract HelloWorld: [Error Code: 1009] error caused by: 1 error occurred:
        * transaction verification failed: [Error Code: 1006] invalid proposal key
""",
            "stderr": "❌ Command Error: failed deploying all contracts",
            "returncode": 1
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}️⃣ Testing: {test_case['name']}")
        print("-" * 40)
        
        # Test the parsing
        result = manager._parse_deployment_output(test_case['stdout'])
        
        print(f"📋 Input stdout:")
        print(repr(test_case['stdout']))
        print(f"\n📋 Parsed result:")
        for key, value in result.items():
            print(f"  {key}: {value}")
        
        # Check what we extracted
        if result.get('transaction_hash'):
            print(f"✅ Transaction hash extracted: {result['transaction_hash']}")
        else:
            print("❌ No transaction hash extracted")
            
        if result.get('account_address'):
            print(f"✅ Account address extracted: {result['account_address']}")
        else:
            print("❌ No account address extracted")
            
        if result.get('contract_address'):
            print(f"✅ Contract address extracted: {result['contract_address']}")
        else:
            print("❌ No contract address extracted")

def test_regex_patterns():
    """Test individual regex patterns."""
    print(f"\n🔍 Testing Individual Regex Patterns")
    print("=" * 50)
    
    import re
    
    test_text = """
Deploying 1 contracts for accounts: my-testnet-account

Using account: 0x1234567890abcdef
Account address: 0xea0b8be271e5a26b
Deploying to account: 0x9999888877776666
Contract deployed at: 0xaaabbbcccdddeeef
Organization -> 0x1111222233334444

✨ All contracts deployed successfully

Transaction ID: 0x5555aaaa5555aaaa5555aaaa5555aaaa5555aaaa5555aaaa5555aaaa5555aaaa
tx_id: 0x6666bbbb6666bbbb6666bbbb6666bbbb6666bbbb6666bbbb6666bbbb6666bbbb
"""
    
    patterns = [
        (r"Transaction ID:\s*0x([0-9a-fA-F]+)", "Transaction ID"),
        (r"tx_id:\s*0x([0-9a-fA-F]+)", "tx_id"),
        (r"transaction_id:\s*0x([0-9a-fA-F]+)", "transaction_id"),
        (r"Transaction:\s*0x([0-9a-fA-F]+)", "Transaction"),
        (r"0x([0-9a-fA-F]{64})", "64-char hex"),
        (r"0x([0-9a-fA-F]{16})", "16-char hex"),
        (r"Contract deployed at:\s*(0x[0-9a-fA-F]+)", "Contract deployed at"),
        (r"Account:\s*(0x[0-9a-fA-F]+)", "Account"),
        (r"Deploying to account:\s*(0x[0-9a-fA-F]+)", "Deploying to account"),
        (r"Using account:\s*(0x[0-9a-fA-F]+)", "Using account"),
        (r"Account address:\s*(0x[0-9a-fA-F]+)", "Account address"),
        (r"(\w+)\s*->\s*(0x[0-9a-fA-F]+)", "Contract -> Address"),
    ]
    
    for pattern, name in patterns:
        matches = re.findall(pattern, test_text, re.IGNORECASE)
        if matches:
            print(f"✅ {name}: {matches}")
        else:
            print(f"❌ {name}: No matches")

if __name__ == "__main__":
    print("🚀 Starting Flow CLI parsing test...")
    test_parsing_with_simulated_output()
    test_regex_patterns()
    print("\n🎉 Test completed!")