#!/usr/bin/env python3
"""
Comprehensive testnet deployment test for multiple contracts.
Tests deployment of both simple and complex contracts to Flow Testnet.
"""

import sys
import os
import asyncio
import uuid
import json
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv
load_dotenv()

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.cli.flow_manager import FlowProjectManager

def check_testnet_credentials():
    """Check if testnet credentials are available."""
    flow_account_address = os.getenv("FLOW_ACCOUNT_ADDRESS")
    flow_private_key = os.getenv("FLOW_PRIVATE_KEY")
    
    if not flow_account_address or not flow_private_key:
        print("❌ Testnet credentials not found!")
        print("Please set the following environment variables:")
        print("  export FLOW_ACCOUNT_ADDRESS=0x1234567890abcdef")
        print("  export FLOW_PRIVATE_KEY=your_private_key_here")
        print("\nOr run the setup script:")
        print("  ./tests/testnet/setup_testnet_env.sh")
        return False, None, None
    
    return True, flow_account_address, flow_private_key

async def deploy_simple_contract(manager, unique_id):
    """Deploy a simple test contract to testnet."""
    print("\n🔧 DEPLOYING SIMPLE CONTRACT")
    print("=" * 40)
    
    contract_name = f"TestContract{unique_id}"
    timestamp = datetime.now().isoformat()
    
    # Create the simple contract content (same as test_complete_workflow.py)
    contract_content = f'''
// Generated at {timestamp}
access(all) contract {contract_name} {{
    access(all) var message: String
    
    access(all) fun getMessage(): String {{
        return self.message
    }}
    
    access(all) fun setMessage(newMessage: String) {{
        self.message = newMessage
    }}
    
    init() {{
        self.message = "Hello from {contract_name} on Testnet!"
    }}
}}
'''.strip()
    
    print(f"📝 Contract: {contract_name}")
    
    # Step 1: Create project
    project_result = await manager.create_flow_project(
        project_id=f"testnet-simple-{unique_id}",
        contract_name=contract_name,
        contract_content=contract_content
    )
    
    if project_result.get("status") != "success":
        print(f"❌ Project creation failed: {project_result}")
        return None
    
    project_id = project_result["project_id"]
    print(f"✅ Project created: {project_id}")
    
    # Step 2: Configure flow.json for testnet
    project_dir = manager.base_projects_dir / project_id
    configure_testnet_flow_json(project_dir, [contract_name])
    
    # Step 3: Deploy to testnet
    print(f"🚀 Deploying to Flow Testnet...")
    deployment_result = await manager.deploy_contracts(
        project_name=project_id,
        network="testnet"
    )
    
    print(f"\n📋 SIMPLE CONTRACT DEPLOYMENT RESULT:")
    print("-" * 40)
    for key, value in deployment_result.items():
        print(f"  {key}: {value}")
    print("-" * 40)
    
    return deployment_result

async def deploy_organization_contract(manager, unique_id):
    """Deploy the Organization contract to testnet."""
    print("\n🏢 DEPLOYING ORGANIZATION CONTRACT")
    print("=" * 40)
    
    contract_name = f"Organization{unique_id}"
    
    # Read the Organization contract content
    org_contract_path = Path("/Users/harjjotsinghh/Desktop/Main/D Drive/Projects/smart-contract-llm/contracts/Organization_v1.cdc")
    
    if not org_contract_path.exists():
        print(f"❌ Organization contract not found at: {org_contract_path}")
        return None
    
    with open(org_contract_path, 'r') as f:
        original_content = f.read()
    
    # Modify the contract name and storage paths to make them unique
    contract_content = original_content.replace("contract Organization", f"contract {contract_name}")
    contract_content = contract_content.replace("/storage/Organization", f"/storage/{contract_name}")
    contract_content = contract_content.replace("/public/Organization", f"/public/{contract_name}")
    
    print(f"📝 Contract: {contract_name}")
    
    # Step 1: Create project
    project_result = await manager.create_flow_project(
        project_id=f"testnet-org-{unique_id}",
        contract_name=contract_name,
        contract_content=contract_content
    )

    if project_result.get("status") != "success":
        print(f"❌ Project creation failed: {project_result}")
        return None

    project_id = project_result["project_id"]
    print(f"✅ Project created: {project_id}")
    
    # Step 2: Configure flow.json for testnet
    project_dir = manager.base_projects_dir / project_id
    configure_testnet_flow_json(project_dir, [contract_name])
    
    # Step 3: Deploy to testnet
    print(f"🚀 Deploying to Flow Testnet...")
    deployment_result = await manager.deploy_contracts(
        project_name=project_id,
        network="testnet"
    )
    
    print(f"\n📋 ORGANIZATION CONTRACT DEPLOYMENT RESULT:")
    print("-" * 40)
    for key, value in deployment_result.items():
        print(f"  {key}: {value}")
    print("-" * 40)
    
    return deployment_result

def configure_testnet_flow_json(project_dir, contracts):
    """Configure flow.json for testnet deployment"""
    flow_json_path = os.path.join(project_dir, "flow.json")
    
    # Get environment variables
    account_address = os.getenv("FLOW_ACCOUNT_ADDRESS")
    private_key = os.getenv("FLOW_PRIVATE_KEY")
    
    if not account_address or not private_key:
        raise ValueError("FLOW_ACCOUNT_ADDRESS and FLOW_PRIVATE_KEY must be set")
    
    # Create contracts configuration
    contracts_config = {}
    for contract_name in contracts:
        contracts_config[contract_name] = {
            "source": f"./contracts/{contract_name}.cdc",
            "aliases": {
                "emulator": "0xf8d6e0586b0a20c7",
                "testnet": account_address,
                "mainnet": "0x01"
            }
        }
    
    flow_config = {
        "version": "1.0",
        "contracts": contracts_config,
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
                "emulator-account": contracts
            },
            "testnet": {
                "testnet-account": contracts
            }
        }
    }
    
    with open(flow_json_path, 'w') as f:
        json.dump(flow_config, f, indent=2)
    
    print(f"✅ Configured flow.json for testnet deployment")
    return flow_json_path

def validate_deployment_result(deployment_result, contract_type):
    """Validate that deployment result contains all required fields."""
    if not deployment_result.get("success"):
        print(f"❌ {contract_type} deployment failed")
        print(f"  Output: {deployment_result.get('output', 'No output available')}")
        return False
    
    print(f"✅ {contract_type} deployment successful!")
    print(f"  Project: {deployment_result.get('project_name', 'Unknown')}")
    print(f"  Network: {deployment_result.get('network', 'Unknown')}")
    if deployment_result.get('transaction_hash'):
        print(f"  Transaction Hash: {deployment_result['transaction_hash']}")
    print(f"  Output: {deployment_result.get('output', 'No output available')}")
    return True



async def main():
    """Main test function."""
    print("🌐 Flow Testnet Dual Contract Deployment Test")
    print("=" * 50)
    
    # Check credentials
    creds_valid, account_address, private_key = check_testnet_credentials()
    if not creds_valid:
        return False
    
    print(f"✅ Using testnet account: {account_address}")
    
    # Create manager with testnet projects directory
    base_dir = Path("flow_projects_testnet")
    manager = FlowProjectManager(base_projects_dir=base_dir)
    
    # Generate unique ID for this test run
    unique_id = str(uuid.uuid4())[:8]
    print(f"🔑 Test run ID: {unique_id}")
    
    try:
        # Deploy simple contract
        simple_result = await deploy_simple_contract(manager, unique_id)
        if not simple_result:
            print("❌ Simple contract deployment failed")
            return False
        
        simple_success = validate_deployment_result(simple_result, "Simple Contract")
        
        # Deploy organization contract
        org_result = await deploy_organization_contract(manager, unique_id)
        if not org_result:
            print("❌ Organization contract deployment failed")
            return False
        
        org_success = validate_deployment_result(org_result, "Organization Contract")
        
        # Overall result
        overall_success = simple_success and org_success
        
        print(f"\n🎯 FINAL RESULTS:")
        print("=" * 30)
        print(f"Simple Contract:      {'✅ SUCCESS' if simple_success else '❌ FAILED'}")
        print(f"Organization Contract: {'✅ SUCCESS' if org_success else '❌ FAILED'}")
        print(f"Overall Test:         {'✅ SUCCESS' if overall_success else '❌ FAILED'}")
        
        if overall_success:
            print(f"\n🎉 Both contracts successfully deployed to Flow Testnet!")
            print(f"📊 Test Summary:")
            print(f"  - Simple Contract TX: {simple_result.get('transaction_hash', 'N/A')}")
            print(f"  - Organization Contract TX: {org_result.get('transaction_hash', 'N/A')}")
            print(f"  - Account Used: {os.getenv('FLOW_ACCOUNT_ADDRESS', 'N/A')}")
        
        return overall_success
        
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting dual contract testnet deployment test...")
    success = asyncio.run(main())
    
    if success:
        print("\n🎉 TESTNET DEPLOYMENT TEST SUCCESSFUL!")
        print("✅ Both contracts deployed successfully to Flow Testnet!")
    else:
        print("\n❌ TESTNET DEPLOYMENT TEST FAILED!")
        print("❌ One or more deployments failed.")
    
    sys.exit(0 if success else 1)