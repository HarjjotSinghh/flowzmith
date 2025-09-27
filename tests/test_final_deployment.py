#!/usr/bin/env python3
"""
Final test for Flow deployment workflow with unique contract names.
"""

import asyncio
import sys
import os
import tempfile
import shutil
import uuid
from pathlib import Path
from sqlalchemy.orm import Session
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.cli.flow_automation_service import FlowAutomationService
from src.models.database import get_db, engine
from src.models.deployment import DeploymentLog, DeploymentStatus

async def test_final_deployment():
    """Test the complete deployment workflow with a unique contract."""
    print("🧪 Testing Final Flow Deployment Workflow")
    print("=" * 50)
    
    # Create a temporary directory for testing
    temp_dir = tempfile.mkdtemp()
    print(f"📁 Using temporary directory: {temp_dir}")
    
    try:
        # Change to temp directory
        original_cwd = os.getcwd()
        os.chdir(temp_dir)
        
        # Initialize database session
        db_session = next(get_db())
        
        # Initialize Flow service
        flow_service = FlowAutomationService(
            base_projects_dir=Path(temp_dir),
            db_session=db_session
        )
        
        # Test 1: Flow CLI availability
        print("\n1️⃣ Testing Flow CLI availability...")
        cli_check = await flow_service.flow_manager._run_command(["flow", "version"], cwd=temp_dir)
        if cli_check.get("returncode") != 0:
            print("❌ Flow CLI not available")
            return False
        print("✅ Flow CLI available")
        
        # Use testnet for deployment
        network = "testnet"
        print(f"Using Flow {network} for deployment...")
        
        # Test 2: Create project with unique contract name
        print(f"\n2️⃣ Testing Flow project creation with unique contract...")
        
        # Generate unique contract name
        unique_id = str(uuid.uuid4())[:8]
        contract_name = f"UniqueContract{unique_id}"
        
        contract_content = f'''
access(all) contract {contract_name} {{
    access(all) var greeting: String
    
    init() {{
        self.greeting = "Hello from {contract_name}!"
    }}
    
    access(all) fun updateGreeting(newGreeting: String) {{
        self.greeting = newGreeting
    }}
    
    access(all) fun getGreeting(): String {{
        return self.greeting
    }}
}}
'''
        
        project_result = await flow_service.flow_manager.create_flow_project(
            project_id=f"final-test-{unique_id}",
            contract_name=contract_name,
            contract_content=contract_content,
            network=network
        )
        
        print(f"📋 Project result: {project_result}")
        
        if project_result.get("status") != "success":
            print(f"❌ Project creation failed: {project_result.get('error', 'Unknown error')}")
            return False
        
        project_id = project_result.get("project_id")
        project_path = project_result.get("project_dir")
        print(f"✅ Project created: {project_id}")
        print(f"📂 Project path: {project_path}")
        
        # Verify flow.json configuration
        flow_json_path = Path(project_path) / "flow.json"
        if flow_json_path.exists():
            import json
            with open(flow_json_path) as f:
                flow_config = json.load(f)
            
            accounts = flow_config.get("accounts", {})
            if accounts:
                account_name = list(accounts.keys())[0]
                account_config = accounts[account_name]
                key_config = account_config.get("key")
                
                # Handle both simple and detailed key formats
                if isinstance(key_config, dict):
                    private_key = key_config.get("privateKey")
                    print(f"✅ Detailed key format configured with algorithms")
                else:
                    private_key = key_config
                    print(f"✅ Simple key format configured")
                
                # Check if we have a proper private key
                if private_key and private_key != "your_private_key_here":
                    print(f"✅ Proper private key configured: {private_key[:20]}...")
                else:
                    print(f"⚠️ Default private key found: {private_key}")
            else:
                print("⚠️ No accounts found in flow.json")
        else:
            print("❌ flow.json not found")
            return False
        
        # Test 3: Deploy contract
        print(f"\n3️⃣ Testing contract deployment...")
        deployment_result = await flow_service.flow_manager.deploy_contract(
            project_id=project_id,
            network=network
        )
        
        print(f"📋 Deployment result: {deployment_result}")
        
        if deployment_result.get("status") == "success":
            print(f"✅ Contract {contract_name} deployed successfully!")
            print(f"📍 Transaction Hash: {deployment_result.get('transaction_hash', 'N/A')}")
            print(f"🏠 Contract Address: {deployment_result.get('contract_address', 'N/A')}")
            print(f"🏠 Account Address: {deployment_result.get('account_address', 'N/A')}")
            
            # Test 4: Verify database logging
            print(f"\n4️⃣ Testing database logging...")
            
            # Check if deployment was logged
            deployment_logs = db_session.query(DeploymentLog).filter_by(
                project_id=project_id
            ).all()
            
            if deployment_logs:
                latest_log = deployment_logs[-1]
                print(f"✅ Deployment logged in database")
                print(f"📊 Status: {latest_log.status}")
                print(f"🌐 Network: {latest_log.network}")
                print(f"📝 Contract: {latest_log.contract_name}")
                
                if latest_log.status == DeploymentStatus.SUCCESS:
                    print("✅ Deployment status is SUCCESS")
                    return True
                else:
                    print(f"⚠️ Deployment status is {latest_log.status}")
                    return False
            else:
                print("⚠️ No deployment logs found in database")
                return False
        else:
            print(f"❌ Contract deployment failed: {deployment_result.get('error', 'Unknown error')}")
            print(f"📋 Output: {deployment_result.get('deployment_output', 'No output')}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Cleanup
        os.chdir(original_cwd)
        shutil.rmtree(temp_dir, ignore_errors=True)
        print(f"\n🧹 Cleaned up temporary directory: {temp_dir}")

if __name__ == "__main__":
    print("🚀 Starting final deployment test...")
    success = asyncio.run(test_final_deployment())
    
    if success:
        print("\n🎉 All tests passed! The deployment workflow is working correctly.")
    else:
        print("\n❌ Some tests failed. Please check the output above.")
    
    sys.exit(0 if success else 1)