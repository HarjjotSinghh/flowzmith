#!/usr/bin/env python3

import sys
import json
import asyncio
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.cli.api_client import APIClient
from src.cli.contract_creator import ContractCreator

async def debug_workflow():
    """Debug the contract creation workflow to see where network parameter gets lost."""
    
    async with APIClient() as client:
        creator = ContractCreator(client)
        
        # Set the same requirements as flow-auto command
        requirements = {
            "contract_name": "DebugToken",
            "contract_type": "Token", 
            "description": "Debug token contract for Flow emulator",
            "network": "emulator"
        }
        
        print("=== Debug Workflow ===")
        print(f"Initial requirements: {json.dumps(requirements, indent=2)}")
        
        # Test the file generation directly
        flow_json_content = creator.file_generator.generate_flow_json(
            requirements["contract_name"],
            requirements["contract_type"],
            requirements["network"]
        )
        
        print(f"\nDirect file generation result:")
        print(f"Network in flow.json: {flow_json_content.get('networks', {}).keys()}")
        print(f"Accounts in flow.json: {flow_json_content.get('accounts', {}).keys()}")
        print(f"Deployments in flow.json: {flow_json_content.get('deployments', {}).keys()}")
        
        # Test the requirements.get() pattern used in the code
        network_from_requirements = requirements.get("network", "testnet")
        print(f"\nNetwork from requirements.get('network', 'testnet'): {network_from_requirements}")

if __name__ == "__main__":
    asyncio.run(debug_workflow())