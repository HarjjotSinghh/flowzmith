#!/usr/bin/env python3
"""
Debug script to check the flow.json configuration.
"""

import asyncio
import sys
import os
import tempfile
import shutil
from pathlib import Path
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.cli.flow_manager import FlowProjectManager

async def debug_flow_config():
    """Debug the flow.json configuration."""
    flow_manager = FlowProjectManager()
    
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"🧪 Using temp dir: {temp_dir}")
        
        # Create project
        result = await flow_manager.create_flow_project(
            project_id='debug-config-123',
            contract_name='TestContract',
            contract_content='access(all) contract TestContract { init() {} }',
            network='testnet'
        )
        
        print(f"📋 Project creation result: {result}")
        
        if result['status'] == 'success':
            project_dir = Path(result['project_dir'])
            flow_json_path = project_dir / 'flow.json'
            
            if flow_json_path.exists():
                print(f"📄 Reading flow.json from: {flow_json_path}")
                with open(flow_json_path, 'r') as f:
                    flow_config = json.load(f)
                
                print("🔧 Flow.json configuration:")
                print(json.dumps(flow_config, indent=2))
                
                # Check specific sections
                print("\n🔍 Analysis:")
                print(f"- Networks: {list(flow_config.get('networks', {}).keys())}")
                print(f"- Accounts: {list(flow_config.get('accounts', {}).keys())}")
                print(f"- Deployments: {flow_config.get('deployments', {})}")
                print(f"- Contracts: {flow_config.get('contracts', {})}")
                
            else:
                print("❌ flow.json not found")
        else:
            print(f"❌ Project creation failed: {result}")

if __name__ == "__main__":
    asyncio.run(debug_flow_config())