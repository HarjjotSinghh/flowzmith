#!/usr/bin/env python3

import sys
import json
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.cli.file_generators import FlowFileGenerator

def test_flow_json_generation():
    """Test FlowFileGenerator.generate_flow_json with different networks."""
    generator = FlowFileGenerator()
    
    print("Testing FlowFileGenerator.generate_flow_json...")
    
    # Test with emulator network
    print("\n=== Testing with emulator network ===")
    emulator_config = generator.generate_flow_json("TestContract", "Token", "emulator")
    print("Generated config:")
    print(json.dumps(emulator_config, indent=2))
    
    # Test with testnet network
    print("\n=== Testing with testnet network ===")
    testnet_config = generator.generate_flow_json("TestContract", "Token", "testnet")
    print("Generated config:")
    print(json.dumps(testnet_config, indent=2))
    
    # Verify emulator configuration
    print("\n=== Verification ===")
    print(f"Emulator config has emulator network: {'emulator' in emulator_config.get('networks', {})}")
    print(f"Emulator config has emulator account: {'emulator-account' in emulator_config.get('accounts', {})}")
    print(f"Emulator config has emulator deployment: {'emulator' in emulator_config.get('deployments', {})}")

if __name__ == "__main__":
    test_flow_json_generation()