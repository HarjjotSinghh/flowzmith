#!/usr/bin/env python3
"""
Test script to verify Flow deployment improvements.
Tests the complete workflow including:
1. Flow project creation with proper key generation
2. Contract deployment with transaction hash capture
3. Database storage of deployment information
"""

import asyncio
import sys
import os
import tempfile
import shutil
from pathlib import Path
from sqlalchemy.orm import Session
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.cli.flow_automation_service import FlowAutomationService
from src.models.database import get_db, engine
from src.models.deployment import DeploymentLog, DeploymentStatus

async def test_deployment_workflow():
    """Test the complete deployment workflow."""
    print("🧪 Testing Flow Deployment Improvements")
    print("=" * 50)
    
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        print(f"📁 Using temporary directory: {temp_path}")
        
        # Get database session
        db_session = next(get_db())
        
        try:
            # Initialize the Flow automation service
            flow_service = FlowAutomationService(
                base_projects_dir=temp_path,
                db_session=db_session
            )
            
            print("\n1️⃣ Testing Flow CLI availability...")
            cli_available = await flow_service.flow_manager.check_flow_cli_installed()
            if not cli_available:
                print("❌ Flow CLI not available")
                return False
            print("✅ Flow CLI available")
            
            # Using testnet - no need to start emulator
            print("Using Flow testnet for deployment...")
            
            print("\n2️⃣ Testing Flow project creation with proper keys...")
            
            # Create a simple test contract content
            contract_content = '''
access(all) contract TestContract {
    access(all) var greeting: String
    
    init() {
        self.greeting = "Hello, Flow!"
    }
    
    access(all) fun updateGreeting(newGreeting: String) {
        self.greeting = newGreeting
    }
    
    access(all) fun getGreeting(): String {
        return self.greeting
    }
}
'''
            
            project_result = await flow_service.flow_manager.create_flow_project(
                project_id="test-deployment-123",
                contract_name="TestContract",
                contract_content=contract_content,
                network="testnet"
            )
            
            print(f"📋 Project result: {project_result}")
            
            if project_result.get("status") != "success":
                print(f"❌ Project creation failed: {project_result.get('error', 'Unknown error')}")
                return False
            
            project_id = project_result.get("project_id")
            project_path = project_result.get("project_dir")
            print(f"✅ Project created: {project_id}")
            print(f"📂 Project path: {project_path}")
            
            # Check if flow.json was created with proper keys
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
                    else:
                        private_key = key_config
                    
                    # Check if we have a proper private key (not the default placeholder)
                    if private_key and private_key != "your_private_key_here":
                        print(f"✅ Proper private key generated: {private_key[:20]}...")
                    else:
                        print(f"⚠️ Default private key found: {private_key}")
                else:
                    print("⚠️ No accounts found in flow.json")
            else:
                print("❌ flow.json not found")
                return False
            
            print("\n3️⃣ Testing contract deployment...")
            deployment_result = await flow_service.flow_manager.deploy_contracts(
                project_name=project_id,
                network="testnet"
            )
            
            print(f"📋 Deployment result: {deployment_result}")
            
            if deployment_result.get("success"):
                print("✅ Contract deployment successful!")
                print(f"📋 Transaction hash: {deployment_result.get('transaction_hash', 'N/A')}")
                print(f"📍 Contract address: {deployment_result.get('contract_address', 'N/A')}")
                print(f"👤 Account address: {deployment_result.get('account_address', 'N/A')}")
                print(f"⏱️ Execution time: {deployment_result.get('execution_time_ms', 0)}ms")
            else:
                print(f"❌ Contract deployment failed: {deployment_result.get('error')}")
                print(f"📋 Output: {deployment_result.get('output', 'N/A')}")
                return False
            
            print("\n4️⃣ Testing database storage...")
            # Store deployment info manually to test the method
            await flow_service._store_deployment_info(
                project_id=project_id,
                deploy_result=deployment_result,
                network="emulator",
                contract_name="TestContract"
            )
            
            # Query the database to verify storage
            deployment_logs = db_session.query(DeploymentLog).filter(
                DeploymentLog.deployment_id == project_id
            ).all()
            
            if deployment_logs:
                log = deployment_logs[0]
                print(f"✅ Deployment stored in database!")
                print(f"📋 Log ID: {log.id}")
                print(f"🌐 Network: {log.network}")
                print(f"📊 Status: {log.status}")
                print(f"🔗 Transaction hash: {log.transaction_hash}")
                print(f"⏱️ Execution time: {log.execution_time_ms}ms")
            else:
                print("❌ No deployment logs found in database")
                return False
            
            print("\n🎉 All tests passed! Deployment improvements are working correctly.")
            return True
            
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            # Close database session
            db_session.close()

if __name__ == "__main__":
    # Run the test
    success = asyncio.run(test_deployment_workflow())
    sys.exit(0 if success else 1)