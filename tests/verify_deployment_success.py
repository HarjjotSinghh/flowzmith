#!/usr/bin/env python3
"""
Simple verification that the Flow deployment workflow is working.
"""

import asyncio
import sys
import os
import tempfile
import shutil
import uuid
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.cli.flow_automation_service import FlowAutomationService
from src.models.database import get_db

async def verify_deployment():
    """Verify that deployment is working correctly."""
    print("🔍 Verifying Flow Deployment Workflow")
    print("=" * 40)
    
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
        
        # Generate unique contract name
        unique_id = str(uuid.uuid4())[:8]
        contract_name = f"VerifyContract{unique_id}"
        
        contract_content = f'''
access(all) contract {contract_name} {{
    access(all) var message: String
    
    init() {{
        self.message = "Deployment verification successful!"
    }}
    
    access(all) fun getMessage(): String {{
        return self.message
    }}
}}
'''
        
        print(f"\n✅ Creating project with contract: {contract_name}")
        
        # Create project
        project_result = await flow_service.flow_manager.create_flow_project(
            project_id=f"verify-{unique_id}",
            contract_name=contract_name,
            contract_content=contract_content,
            network="testnet"
        )
        
        if project_result.get("status") != "success":
            print(f"❌ Project creation failed: {project_result.get('error')}")
            return False
        
        project_id = project_result.get("project_id")
        print(f"✅ Project created: {project_id}")
        
        # Deploy contract
        print(f"\n🚀 Deploying contract to testnet...")
        deployment_result = await flow_service.flow_manager.deploy_contract(
            project_id=project_id,
            network="testnet"
        )
        print(f"Deployment result: {deployment_result}")
        
        if deployment_result.get("status") == "success":
            print(f"✅ Contract {contract_name} deployed successfully!")
            print(f"📍 Transaction Hash: {deployment_result.get('transaction_hash', 'N/A')}")
            print(f"🏠 Contract Address: {deployment_result.get('contract_address', 'N/A')}")
            print(f"⏱️  Execution Time: {deployment_result.get('execution_time_ms', 'N/A')}ms")
            return True
        else:
            print(f"❌ Deployment failed: {deployment_result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False
    finally:
        # Cleanup
        os.chdir(original_cwd)
        shutil.rmtree(temp_dir, ignore_errors=True)
        print(f"\n🧹 Cleaned up temporary directory")

if __name__ == "__main__":
    print("🚀 Starting deployment verification...")
    success = asyncio.run(verify_deployment())
    
    if success:
        print("\n🎉 VERIFICATION SUCCESSFUL!")
        print("✅ The Flow deployment workflow is working correctly.")
        print("✅ Contracts can be generated, configured, and deployed to testnet.")
        print("✅ Key format issues have been resolved.")
    else:
        print("\n❌ VERIFICATION FAILED!")
        print("❌ There are still issues with the deployment workflow.")
    
    sys.exit(0 if success else 1)