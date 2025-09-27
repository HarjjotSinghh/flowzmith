#!/usr/bin/env python3
"""
Test direct deployment with Flow CLI to debug signature issues.
"""

import asyncio
import sys
import os
import tempfile
import subprocess
from pathlib import Path
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.cli.flow_manager import FlowProjectManager

async def test_direct_deploy():
    """Test direct deployment with Flow CLI."""
    flow_manager = FlowProjectManager()
    
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"🧪 Using temp dir: {temp_dir}")
        
        # Create project
        result = await flow_manager.create_flow_project(
            project_id='direct-deploy-test',
            contract_name='TestContract',
            contract_content='access(all) contract TestContract { init() {} }',
            network='testnet'
        )
        
        if result['status'] == 'success':
            project_dir = Path(result['project_dir'])
            print(f"📂 Project created at: {project_dir}")
            
            # Try to deploy using Flow CLI directly
            print("🚀 Attempting direct deployment...")
            
            try:
                # Change to project directory and run flow project deploy
                cmd = ["flow", "project", "deploy", "--network", "testnet"]
                print(f"Running command: {' '.join(cmd)}")
                print(f"Working directory: {project_dir}")
                
                process = subprocess.run(
                    cmd,
                    cwd=project_dir,
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                print(f"Return code: {process.returncode}")
                print(f"STDOUT:\n{process.stdout}")
                print(f"STDERR:\n{process.stderr}")
                
            except subprocess.TimeoutExpired:
                print("❌ Command timed out")
            except Exception as e:
                print(f"❌ Command failed: {e}")
        else:
            print(f"❌ Project creation failed: {result}")

if __name__ == "__main__":
    asyncio.run(test_direct_deploy())