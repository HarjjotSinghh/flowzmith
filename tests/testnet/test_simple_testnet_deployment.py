#!/usr/bin/env python3
"""
Simple testnet deployment test for a single contract.
Tests deployment of a basic contract to Flow Testnet with proper configuration.
"""

import sys
import os
import asyncio
import uuid
import json
from pathlib import Path
from datetime import datetime

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.cli.flow_manager import FlowProjectManager

class SimpleTestnetDeployment:
    """Test class for simple testnet deployment."""
    
    def __init__(self):
        self.flow_manager = FlowProjectManager()
    
    def check_testnet_credentials(self):
        """Check if testnet credentials are available."""
        account_address = os.getenv("FLOW_ACCOUNT_ADDRESS")
        private_key = os.getenv("FLOW_PRIVATE_KEY")
        
        if not account_address:
            raise Exception("FLOW_ACCOUNT_ADDRESS environment variable not set")
        if not private_key:
            raise Exception("FLOW_PRIVATE_KEY environment variable not set")
        
        print(f"✓ Testnet credentials found")
        print(f"  Account: {account_address}")
        print(f"  Private key: {'*' * 20}...{private_key[-4:] if len(private_key) > 4 else '****'}")
        
        return account_address, private_key
    
    async def create_simple_contract(self) -> str:
        """Create a simple test contract."""
        contract_code = '''
access(all) contract SimpleTestContract {
    
    access(all) var message: String
    
    access(all) event MessageChanged(newMessage: String)
    
    init() {
        self.message = "Hello from Flow Testnet!"
    }
    
    access(all) fun updateMessage(newMessage: String) {
        self.message = newMessage
        emit MessageChanged(newMessage: newMessage)
    }
    
    access(all) fun getMessage(): String {
        return self.message
    }
}
'''
        return contract_code.strip()
    
    async def setup_testnet_project(self, project_name: str, contract_code: str) -> str:
        """Set up a Flow project for testnet deployment."""
        print(f"Setting up testnet project: {project_name}")
        
        # Create project
        result = await self.flow_manager.create_flow_project(
            project_id=project_name,
            contract_name="SimpleTestContract",
            contract_content=contract_code,
            network="testnet"
        )
        
        if result.get("status") != "success":
            raise Exception(f"Failed to create project: {result.get('error', 'Unknown error')}")
        
        project_dir = Path(result["project_dir"])
        print(f"✓ Project created with SimpleTestContract.cdc")
        
        # Configure flow.json for testnet deployment
        await self.configure_testnet_flow_json(project_dir)
        
        return str(project_dir)
    
    async def configure_testnet_flow_json(self, project_dir: Path):
        """Configure flow.json for testnet deployment with proper account and deployment settings."""
        flow_config_file = project_dir / "flow.json"
        
        # Get environment variables
        account_address = os.getenv("FLOW_ACCOUNT_ADDRESS")
        private_key = os.getenv("FLOW_PRIVATE_KEY")
        
        if not account_address or not private_key:
            raise ValueError("FLOW_ACCOUNT_ADDRESS and FLOW_PRIVATE_KEY must be set")
        
        # Create proper testnet configuration
        config = {
            "version": "1.0",
            "contracts": {
                "SimpleTestContract": {
                    "source": "./contracts/SimpleTestContract.cdc",
                    "aliases": {
                        "emulator": "0xf8d6e0586b0a20c7",
                        "testnet": account_address,
                        "mainnet": "0x01"
                    }
                }
            },
            "networks": {
                "emulator": "127.0.0.1:3569",
                "testnet": "access.devnet.nodes.onflow.org:9000",
                "mainnet": "access.mainnet.nodes.onflow.org:9000"
            },
            "accounts": {
                "emulator-account": {
                    "address": "service",
                    "key": {
                        "type": "file",
                        "location": "./emulator-account.pkey"
                    }
                },
                "testnet-account": {
                     "address": account_address,
                     "key": {
                         "type": "hex",
                         "index": 0,
                         "signatureAlgorithm": "ECDSA_secp256k1",
                         "hashAlgorithm": "SHA2_256",
                         "privateKey": private_key
                     }
                 }
            },
            "deployments": {
                "emulator": {
                    "emulator-account": [
                        "SimpleTestContract"
                    ]
                },
                "testnet": {
                    "testnet-account": [
                        "SimpleTestContract"
                    ]
                }
            }
        }
        
        # Write config
        flow_config_file.write_text(json.dumps(config, indent=2), encoding="utf-8")
        print(f"✓ Configured flow.json for testnet deployment")
    
    async def deploy_to_testnet(self, project_name: str) -> dict:
        """Deploy the contract to testnet."""
        print(f"Deploying {project_name} to Flow Testnet...")
        
        result = await self.flow_manager.deploy_contracts(
            project_name=project_name,
            network="testnet"
        )
        
        return result
    
    def validate_deployment_result(self, result: dict) -> bool:
        """Validate the deployment result."""
        print("Validating deployment result...")
        
        if not result.get("success"):
            print(f"❌ Deployment failed: {result.get('error', 'Unknown error')}")
            return False
        
        print(f"✓ Contract deployed successfully!")
        print(f"  Project: {result.get('project_name', 'Unknown')}")
        print(f"  Network: {result.get('network', 'Unknown')}")
        
        # Show transaction hash if available
        if result.get("transaction_hash"):
            print(f"  Transaction Hash: {result['transaction_hash']}")
            # Provide testnet explorer links
            tx_hash = result["transaction_hash"].replace("0x", "")
            print(f"  Testnet Explorer: https://testnet.flowscan.org/transaction/{tx_hash}")
        
        # Show deployment output for additional info
        if result.get("output"):
            print(f"  Deployment Output:")
            for line in result["output"].split('\n'):
                if line.strip():
                    print(f"    {line.strip()}")
        
        return True

async def main():
    """Main test function."""
    print("=" * 60)
    print("SIMPLE FLOW TESTNET DEPLOYMENT TEST")
    print("=" * 60)
    
    test = SimpleTestnetDeployment()
    
    try:
        # Check credentials
        print("\n1. Checking testnet credentials...")
        test.check_testnet_credentials()
        
        # Generate unique project name
        project_id = str(uuid.uuid4())[:8]
        project_name = f"simple-testnet-{project_id}"
        
        # Create contract
        print("\n2. Creating simple test contract...")
        contract_code = await test.create_simple_contract()
        print("✓ Simple test contract created")
        
        # Setup project
        print("\n3. Setting up testnet project...")
        project_dir = await test.setup_testnet_project(project_name, contract_code)
        print(f"✓ Project created at: {project_dir}")
        
        # Deploy to testnet
        print("\n4. Deploying to Flow Testnet...")
        deployment_result = await test.deploy_to_testnet(project_name)
        
        # Validate result
        print("\n5. Validating deployment...")
        success = test.validate_deployment_result(deployment_result)
        
        if success:
            print("\n" + "=" * 60)
            print("✅ SIMPLE TESTNET DEPLOYMENT TEST PASSED!")
            print("=" * 60)
        else:
            print("\n" + "=" * 60)
            print("❌ SIMPLE TESTNET DEPLOYMENT TEST FAILED!")
            print("=" * 60)
            return False
            
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Ensure FLOW_ACCOUNT_ADDRESS and FLOW_PRIVATE_KEY are set")
        print("2. Run: source tests/testnet/.env.testnet")
        print("3. Or run: ./tests/testnet/setup_testnet_env.sh")
        return False
    
    return True

if __name__ == "__main__":
    asyncio.run(main())