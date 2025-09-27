#!/usr/bin/env python3
"""
Test script to verify API contract submission generates complete Flow project files.
"""

import requests
import json
import time

def test_api_contract_submission():
    """Test the /api/v1/contracts/submit endpoint."""
    
    # API endpoint
    url = "http://localhost:8000/api/v1/contracts/submit"
    
    # Test contract data
    contract_data = {
        "name": "APITestToken",
        "type": "token",
        "description": "A test token contract submitted via API",
        "network": "testnet",
        "content": """
access(all) contract APITestToken {
    access(all) var totalSupply: UFix64
    
    init() {
        self.totalSupply = 1000000.0
    }
    
    access(all) fun getTotalSupply(): UFix64 {
        return self.totalSupply
    }
}
        """.strip(),
        "metadata": {
            "version": "1.0.0",
            "author": "API Test"
        }
    }
    
    print("🚀 Testing API contract submission...")
    print(f"📡 Submitting to: {url}")
    print(f"📄 Contract: {contract_data['name']} ({contract_data['type']})")
    
    try:
        # Submit the contract
        response = requests.post(url, json=contract_data)
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Contract submission successful!")
            print(f"📁 Project Path: {result.get('project_path', 'Not provided')}")
            print(f"⏱️  Generation Time: {result.get('generation_time', 'Not provided')} seconds")
            print(f"🆔 Contract ID: {result.get('contract_id', 'Not provided')}")
            
            # Return the project path for verification
            return result.get('project_path')
        else:
            print(f"❌ Request failed: {response.status_code}")
            print(f"📄 Response: {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed. Make sure the server is running on http://localhost:8000")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    project_path = test_api_contract_submission()
    
    if project_path:
        print(f"\n🔍 You can verify the generated files at: {project_path}")
        print("Expected files:")
        print("  - contracts/APITestToken.cdc")
        print("  - flow.json")
        print("  - transactions/*.cdc")
        print("  - scripts/*.cdc")
        print("  - tests/*.cdc")
        print("  - metadata.json")
        print("  - README.md")