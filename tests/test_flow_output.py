#!/usr/bin/env python3
"""
Test script to capture actual Flow CLI deployment output.
"""

import asyncio
import sys
import os
import tempfile
import shutil
import uuid
import subprocess
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.cli.flow_automation_service import FlowAutomationService
from src.models.database import get_db

async def test_flow_output():
    """Test Flow CLI output to understand the format."""
    print("🔍 Testing Flow CLI Output Format")
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
        contract_name = f"HelloWorld{unique_id}"
        
        # Simple HelloWorld contract
        contract_content = f'''
access(all) contract {contract_name} {{
    access(all) var greeting: String
    
    access(all) fun changeGreeting(newGreeting: String) {{
        self.greeting = newGreeting
    }}
    
    access(all) fun hello(): String {{
        return self.greeting
    }}
    
    init() {{
        self.greeting = "Hello, World!"
    }}
}}
'''
        
        print(f"\n✅ Creating project with contract: {contract_name}")
        
        # Create project
        project_result = await flow_service.flow_manager.create_flow_project(
            project_id=f"hello-{unique_id}",
            contract_name=contract_name,
            contract_content=contract_content,
            network="emulator"
        )
        
        if project_result.get("status") != "success":
            print(f"❌ Project creation failed: {project_result.get('error')}")
            return False
        
        project_id = project_result.get("project_id")
        project_dir = Path(temp_dir) / project_id
        print(f"✅ Project created: {project_id}")
        
        # Start emulator manually to capture output
        print(f"\n🚀 Starting emulator...")
        emulator_process = subprocess.Popen(
            ["flow", "emulator", "start"],
            cwd=project_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait for emulator to start
        await asyncio.sleep(5)
        
        # Deploy contract manually to capture exact output
        print(f"\n🚀 Deploying contract manually...")
        deploy_process = subprocess.run(
            ["flow", "project", "deploy", "--network=emulator"],
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        print(f"\n📋 DEPLOYMENT OUTPUT:")
        print("=" * 50)
        print("STDOUT:")
        print(deploy_process.stdout)
        print("\nSTDERR:")
        print(deploy_process.stderr)
        print(f"\nReturn Code: {deploy_process.returncode}")
        print("=" * 50)
        
        # Stop emulator
        emulator_process.terminate()
        emulator_process.wait()
        
        # Also test with our parsing method
        if deploy_process.returncode == 0:
            print(f"\n🔍 Testing our parsing method...")
            sys.path.insert(0, str(Path(__file__).parent / "src"))
            from src.cli.flow_manager import FlowProjectManager
            
            flow_manager = FlowProjectManager()
            parsed_info = flow_manager._parse_deployment_output(deploy_process.stdout)
            print(f"Parsed info: {parsed_info}")
            
            return True
        else:
            print(f"❌ Deployment failed with return code: {deploy_process.returncode}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Cleanup
        os.chdir(original_cwd)
        shutil.rmtree(temp_dir, ignore_errors=True)
        print(f"\n🧹 Cleaned up temporary directory")

if __name__ == "__main__":
    print("🚀 Starting Flow CLI output test...")
    success = asyncio.run(test_flow_output())
    
    if success:
        print("\n🎉 TEST SUCCESSFUL!")
    else:
        print("\n❌ TEST FAILED!")
    
    sys.exit(0 if success else 1)