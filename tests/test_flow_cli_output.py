#!/usr/bin/env python3
"""
Test script to capture actual Flow CLI deployment output using proper flow init.
"""

import subprocess
import tempfile
import shutil
import os
from pathlib import Path

def test_flow_cli_output():
    """Test Flow CLI output using proper flow init."""
    print("🔍 Testing Flow CLI Output with proper flow init")
    print("=" * 50)
    
    # Create a temporary directory for testing
    temp_dir = tempfile.mkdtemp()
    print(f"📁 Using temporary directory: {temp_dir}")
    
    try:
        # Change to temp directory
        original_cwd = os.getcwd()
        os.chdir(temp_dir)
        
        # Step 1: Initialize a new Flow project
        print("\n1️⃣ Initializing Flow project...")
        init_result = subprocess.run(
            ["flow", "init"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        print(f"Init stdout: {init_result.stdout}")
        print(f"Init stderr: {init_result.stderr}")
        print(f"Init return code: {init_result.returncode}")
        
        if init_result.returncode != 0:
            print("❌ Flow init failed")
            return False
        
        # Step 2: Create a simple HelloWorld contract
        print("\n2️⃣ Creating HelloWorld contract...")
        contracts_dir = Path("cadence/contracts")
        contracts_dir.mkdir(parents=True, exist_ok=True)
        
        hello_world_content = '''
access(all) contract HelloWorld {
    access(all) var greeting: String
    
    access(all) fun changeGreeting(newGreeting: String) {
        self.greeting = newGreeting
    }
    
    access(all) fun hello(): String {
        return self.greeting
    }
    
    init() {
        self.greeting = "Hello, World!"
    }
}
'''
        
        hello_world_file = contracts_dir / "HelloWorld.cdc"
        hello_world_file.write_text(hello_world_content.strip())
        print(f"✅ Created contract: {hello_world_file}")
        
        # Step 3: Update flow.json to include the contract
        print("\n3️⃣ Updating flow.json...")
        flow_json_path = Path("flow.json")
        if flow_json_path.exists():
            import json
            with open(flow_json_path, 'r') as f:
                config = json.load(f)
            
            # Add contract
            if "contracts" not in config:
                config["contracts"] = {}
            config["contracts"]["HelloWorld"] = "./cadence/contracts/HelloWorld.cdc"
            
            # Add deployment
            if "deployments" not in config:
                config["deployments"] = {}
            if "emulator" not in config["deployments"]:
                config["deployments"]["emulator"] = {}
            config["deployments"]["emulator"]["emulator-account"] = ["HelloWorld"]
            
            with open(flow_json_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            print("✅ Updated flow.json")
        
        # Step 4: Start emulator
        print("\n4️⃣ Starting emulator...")
        emulator_process = subprocess.Popen(
            ["flow", "emulator", "start"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait for emulator to start
        import time
        time.sleep(5)
        
        # Step 5: Deploy contract
        print("\n5️⃣ Deploying contract...")
        deploy_result = subprocess.run(
            ["flow", "project", "deploy", "--network=emulator"],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        print(f"\n📋 DEPLOYMENT OUTPUT:")
        print("=" * 50)
        print("STDOUT:")
        print(repr(deploy_result.stdout))  # Use repr to see exact characters
        print("\nSTDOUT (formatted):")
        print(deploy_result.stdout)
        print("\nSTDERR:")
        print(deploy_result.stderr)
        print(f"\nReturn Code: {deploy_result.returncode}")
        print("=" * 50)
        
        # Step 6: Test parsing
        if deploy_result.returncode == 0:
            print(f"\n🔍 Testing parsing patterns...")
            output = deploy_result.stdout
            
            # Test various patterns
            import re
            
            patterns_to_test = [
                (r"Transaction ID:\s*([0-9a-fA-F]+)", "Transaction ID"),
                (r"tx_id:\s*([0-9a-fA-F]+)", "tx_id"),
                (r"transaction_id:\s*([0-9a-fA-F]+)", "transaction_id"),
                (r"Transaction:\s*([0-9a-fA-F]+)", "Transaction"),
                (r"0x([0-9a-fA-F]{64})", "64-char hex"),
                (r"Contract deployed at:\s*(0x[0-9a-fA-F]+)", "Contract deployed at"),
                (r"Account:\s*(0x[0-9a-fA-F]+)", "Account"),
                (r"Deploying to account:\s*(0x[0-9a-fA-F]+)", "Deploying to account"),
                (r"Using account:\s*(0x[0-9a-fA-F]+)", "Using account"),
                (r"Account address:\s*(0x[0-9a-fA-F]+)", "Account address"),
                (r"(\w+)\s*->\s*(0x[0-9a-fA-F]+)", "Contract -> Address"),
                (r"accounts:\s*([^\n]+)", "accounts line"),
            ]
            
            for pattern, name in patterns_to_test:
                matches = re.findall(pattern, output, re.IGNORECASE)
                if matches:
                    print(f"✅ {name}: {matches}")
                else:
                    print(f"❌ {name}: No matches")
        
        # Stop emulator
        emulator_process.terminate()
        emulator_process.wait()
        
        return deploy_result.returncode == 0
        
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
    success = test_flow_cli_output()
    
    if success:
        print("\n🎉 TEST SUCCESSFUL!")
    else:
        print("\n❌ TEST FAILED!")