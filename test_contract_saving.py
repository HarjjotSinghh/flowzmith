#!/usr/bin/env python3
"""
Test script to verify contract saving functionality
"""
import asyncio
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.cli.api_client import APIClient
from src.cli.contract_creator import ContractCreator
from src.models.database import get_db
from src.models.generated_contract import GeneratedContract

async def test_contract_saving():
    """Test the contract saving functionality"""
    print("🧪 Testing contract saving functionality...")
    
    # Create API client and contract creator
    api_client = APIClient()
    creator = ContractCreator(api_client)
    
    # Mock requirements and contract content for testing
    requirements = {
        "name": "TestContract",
        "type": "token",
        "description": "A test contract for saving functionality",
        "features": ["minting", "burning"],
        "network": "testnet",
        "generate_flow_project": True
    }
    
    contract_content = """
access(all) contract TestToken {
    access(all) var totalSupply: UFix64
    
    init() {
        self.totalSupply = 1000.0
    }
    
    access(all) fun getTotalSupply(): UFix64 {
        return self.totalSupply
    }
}
"""
    
    # Mock result data that would come from the API
    mock_result = {
        "status": "success",
        "contract": {
            "name": "TestToken",
            "code": contract_content
        },
        "flow_project": {
            "contracts": {"TestToken.cdc": contract_content},
            "transactions": {},
            "scripts": {},
            "tests": {},
            "flow_json": {"contracts": {"TestToken": "./contracts/TestToken.cdc"}},
            "readme": "# TestToken Contract\n\nA simple test token contract."
        }
    }
    
    try:
        # Test filesystem saving
        print("📁 Testing filesystem saving...")
        project_dir = await creator._save_contract_to_filesystem(
            mock_result, requirements, contract_content, "test"
        )
        print(f"✅ Contract saved to filesystem: {project_dir}")
        
        # Test database saving
        print("💾 Testing database saving...")
        await creator._save_contract_to_database(
            mock_result, requirements, contract_content, "test", 2.5
        )
        print("✅ Contract saved to database")
        
        # Verify database entry
        print("🔍 Verifying database entry...")
        db = next(get_db())
        contracts = db.query(GeneratedContract).filter(
            GeneratedContract.name == "TestToken"
        ).all()
        
        if contracts:
            contract = contracts[0]
            print(f"✅ Found contract in database:")
            print(f"   - Name: {contract.name}")
            print(f"   - Type: {contract.contract_type}")
            print(f"   - Network: {contract.network}")
            print(f"   - Generation time: {contract.generation_time_seconds}s")
            print(f"   - Created: {contract.created_at}")
        else:
            print("❌ No contract found in database")
        
        db.close()
        
        # Verify filesystem
        print("📂 Verifying filesystem...")
        if Path(project_dir).exists():
            files = list(Path(project_dir).rglob("*"))
            print(f"✅ Project directory exists with {len(files)} files:")
            for file in files[:10]:  # Show first 10 files
                print(f"   - {file.relative_to(project_dir)}")
        else:
            print("❌ Project directory not found")
            
        print("\n🎉 Contract saving functionality test completed!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_contract_saving())