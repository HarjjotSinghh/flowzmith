#!/usr/bin/env python3
"""
Test script to verify the complete deployment workflow returns all required fields on Flow Testnet.
This test requires testnet credentials to be set as environment variables.
"""

import sys
import os
import asyncio
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.cli.flow_manager import FlowProjectManager

def check_testnet_credentials():
    """Check if required testnet credentials are available."""
    flow_account_address = os.getenv("FLOW_ACCOUNT_ADDRESS")
    flow_private_key = os.getenv("FLOW_PRIVATE_KEY")
    
    if not flow_account_address or not flow_private_key:
        print("❌ Missing required testnet credentials!")
        print("Please set the following environment variables:")
        print("  - FLOW_ACCOUNT_ADDRESS: Your testnet account address")
        print("  - FLOW_PRIVATE_KEY: Your testnet account private key")
        print("\nExample:")
        print("  export FLOW_ACCOUNT_ADDRESS=0x1234567890abcdef")
        print("  export FLOW_PRIVATE_KEY=your_private_key_here")
        return False
    
    print(f"✅ Testnet credentials found:")
    print(f"  Account Address: {flow_account_address}")
    print(f"  Private Key: {'*' * (len(flow_private_key) - 8) + flow_private_key[-8:]}")
    return True

async def test_complete_workflow_testnet():
    """Test the complete deployment workflow on Flow Testnet."""
    print("🔍 Testing Complete Deployment Workflow on Flow Testnet")
    print("=" * 60)
    
    # Check credentials first
    if not check_testnet_credentials():
        return False
    
    # Use a separate directory for testnet tests
    base_dir = Path("flow_projects_testnet")
    print(f"📁 Using directory: {base_dir}")
    
    try:
        # Create FlowProjectManager with testnet directory
        manager = FlowProjectManager(base_projects_dir=base_dir)
        
        # Generate a unique contract name
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        contract_name = f"TestnetContract{unique_id}"
        timestamp = datetime.now().isoformat()
        
        print(f"✅ Creating project with contract: {contract_name}")
        
        # Step 1: Create project
        project_result = await manager.create_flow_project(
            project_id=f"testnet-{unique_id}",
            contract_name=contract_name,
            contract_content=f'''
// Generated at {timestamp} for Flow Testnet
access(all) contract {contract_name} {{
    access(all) var message: String
    access(all) var deployedAt: UFix64
    
    access(all) fun getMessage(): String {{
        return self.message
    }}
    
    access(all) fun getDeployedAt(): UFix64 {{
        return self.deployedAt
    }}
    
    access(all) fun updateMessage(newMessage: String) {{
        self.message = newMessage
    }}
    
    init() {{
        self.message = "Hello from Testnet Contract!"
        self.deployedAt = getCurrentBlock().timestamp
    }}
}}
'''.strip()
        )
        
        if project_result.get("status") != "success":
            print(f"❌ Project creation failed: {project_result}")
            return False
        
        project_id = project_result["project_id"]
        print(f"✅ Project created: {project_id}")
        
        # Step 2: Deploy contract to testnet
        network = "testnet"
        print(f"🚀 Deploying contract to Flow Testnet...")
        print("⚠️  This will use real testnet FLOW tokens for gas fees")
        
        deployment_result = await manager.deploy_contract(
            project_id=project_id,
            network=network,
            update=True  # Force update to generate transaction hash
        )
        
        print(f"\n📋 TESTNET DEPLOYMENT RESULT:")
        print("=" * 50)
        for key, value in deployment_result.items():
            print(f"  {key}: {value}")
        print("=" * 50)
        
        # Check if all required fields are present
        required_fields = ["transaction_hash", "contract_address", "account_address"]
        missing_fields = []
        
        for field in required_fields:
            if not deployment_result.get(field):
                missing_fields.append(field)
        
        if missing_fields:
            print(f"❌ Missing fields: {missing_fields}")
            return False
        else:
            print(f"✅ All required fields present!")
            print(f"  Transaction Hash: {deployment_result['transaction_hash']}")
            print(f"  Contract Address: {deployment_result['contract_address']}")
            print(f"  Account Address: {deployment_result['account_address']}")
            
            # Additional testnet-specific validation
            tx_hash = deployment_result['transaction_hash']
            if tx_hash and tx_hash.startswith('0x') and len(tx_hash) == 66:
                print(f"✅ Transaction hash format is valid")
            else:
                print(f"⚠️  Transaction hash format may be invalid: {tx_hash}")
            
            # Provide testnet explorer link
            if tx_hash:
                explorer_url = f"https://testnet.flowscan.org/transaction/{tx_hash}"
                print(f"🔗 View on Testnet Explorer: {explorer_url}")
            
            return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Preserve project for examination
        print(f"🧹 Testnet project preserved for examination: {project_id if 'project_id' in locals() else 'N/A'}")

if __name__ == "__main__":
    print("🚀 Starting complete workflow test on Flow Testnet...")
    print("⚠️  WARNING: This test will deploy to Flow Testnet and consume real testnet FLOW tokens!")
    
    # Ask for confirmation
    try:
        confirmation = input("\nDo you want to proceed with testnet deployment? (yes/no): ").strip().lower()
        if confirmation not in ['yes', 'y']:
            print("❌ Test cancelled by user")
            sys.exit(0)
    except KeyboardInterrupt:
        print("\n❌ Test cancelled by user")
        sys.exit(0)
    
    success = asyncio.run(test_complete_workflow_testnet())
    
    if success:
        print("\n🎉 TESTNET WORKFLOW TEST SUCCESSFUL!")
        print("✅ Transaction hash, contract address, and account address are all being returned correctly!")
        print("✅ Contract successfully deployed to Flow Testnet!")
    else:
        print("\n❌ TESTNET WORKFLOW TEST FAILED!")
        print("❌ Some required fields are still missing from deployment results or deployment failed.")