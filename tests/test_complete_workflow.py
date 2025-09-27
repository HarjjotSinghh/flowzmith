#!/usr/bin/env python3
"""
Test script to verify the complete deployment workflow returns all required fields.
"""

import sys
import os
import asyncio
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.cli.flow_manager import FlowProjectManager

async def test_complete_workflow():
    """Test the complete deployment workflow."""
    print("🔍 Testing Complete Deployment Workflow")
    print("=" * 50)
    
    # Use the regular flow_projects directory for debugging
    base_dir = Path("flow_projects")
    print(f"📁 Using directory: {base_dir}")
    
    try:
        # Create FlowProjectManager with regular directory
        manager = FlowProjectManager(base_projects_dir=base_dir)
        
        # Generate a unique contract name
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        contract_name = f"TestContract{unique_id}"
        timestamp = datetime.now().isoformat()
        
        print(f"✅ Creating project with contract: {contract_name}")
        
        # Step 1: Create project
        project_result = await manager.create_flow_project(
            project_id=f"test-{unique_id}",
            contract_name=contract_name,
            contract_content=f'''
// Generated at {timestamp}
access(all) contract {contract_name} {{
    access(all) var message: String
    
    access(all) fun getMessage(): String {{
        return self.message
    }}
    
    init() {{
        self.message = "Hello from TestContract!"
    }}
}}
'''.strip()
        )
        
        if project_result.get("status") != "success":
            print(f"❌ Project creation failed: {project_result}")
            return False
        
        project_id = project_result["project_id"]
        print(f"✅ Project created: {project_id}")
        
        # Step 2: Deploy contract
        # Test with emulator network (doesn't require credentials)
        network = "emulator"
        print(f"🚀 Deploying contract to emulator...")
        deployment_result = await manager.deploy_contract(
            project_id=project_id,
            network=network,
            update=True  # Force update to generate transaction hash
        )
        
        print(f"\n📋 DEPLOYMENT RESULT:")
        print("=" * 40)
        for key, value in deployment_result.items():
            print(f"  {key}: {value}")
        print("=" * 40)
        
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
            return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # No cleanup needed since we're using the regular directory
        print(f"🧹 Project preserved for examination: {project_id if 'project_id' in locals() else 'N/A'}")

if __name__ == "__main__":
    print("🚀 Starting complete workflow test...")
    success = asyncio.run(test_complete_workflow())
    
    if success:
        print("\n🎉 WORKFLOW TEST SUCCESSFUL!")
        print("✅ Transaction hash, contract address, and account address are all being returned correctly!")
    else:
        print("\n❌ WORKFLOW TEST FAILED!")
        print("❌ Some required fields are still missing from deployment results.")