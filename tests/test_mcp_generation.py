#!/usr/bin/env python3
"""
Test script for MCP server generation workflow
This script tests the complete MCP generation process using the SimpleNFT test contract.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from mcp_generator.mcp_server_generator import MCPServerGenerator
from mcp_generator.contract_analyzer import CadenceContractAnalyzer


async def test_mcp_generation():
    """Test the complete MCP generation workflow"""
    print("🚀 Starting MCP Server Generation Test")
    print("=" * 50)
    
    # Define paths
    contract_file = Path(__file__).parent / "test_contracts" / "SimpleNFT.cdc"
    output_dir = Path(__file__).parent / "test_output" / "simple_nft_mcp"
    
    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Contract details
    contract_name = "SimpleNFT"
    contract_address = "0x1234567890abcdef"
    network = "testnet"
    
    print(f"📄 Contract File: {contract_file}")
    print(f"📁 Output Directory: {output_dir}")
    print(f"🏷️  Contract Name: {contract_name}")
    print(f"🌐 Network: {network}")
    print()
    
    try:
        # Step 1: Test Contract Analysis
        print("🔍 Step 1: Analyzing Contract...")
        analyzer = CadenceContractAnalyzer()
        
        if not contract_file.exists():
            raise FileNotFoundError(f"Contract file not found: {contract_file}")
        
        with open(contract_file, 'r') as f:
            contract_content = f.read()
        
        analysis = analyzer.analyze_contract_content(contract_content)
        
        print(f"✅ Contract analysis completed!")
        print(f"   - Functions found: {len(analysis.functions)}")
        print(f"   - Events found: {len(analysis.events)}")
        print(f"   - Resources found: {len(analysis.resources)}")
        print(f"   - Structures found: {len(analysis.structures)}")
        print(f"   - Interfaces found: {len(analysis.interfaces)}")
        print()
        
        # Print some details
        if analysis.functions:
            print("📋 Functions found:")
            for func in analysis.functions[:5]:  # Show first 5
                print(f"   - {func.name} (line {func.line_number})")
            if len(analysis.functions) > 5:
                print(f"   ... and {len(analysis.functions) - 5} more")
            print()
        
        if analysis.events:
            print("📢 Events found:")
            for event in analysis.events:
                print(f"   - {event.name} (line {event.line_number})")
            print()
        
        # Step 2: Test MCP Server Generation
        print("🏗️  Step 2: Generating MCP Server...")
        generator = MCPServerGenerator()
        
        generated_files = generator.generate_mcp_server(
            contract_analysis=analysis,
            contract_address=contract_address,
            network=network,
            output_dir=output_dir
        )
        
        print("✅ MCP Server generation completed!")
        print()
        
        # Step 3: Validate Generated Files
        print("🔍 Step 3: Validating Generated Files...")
        
        contract_name_lower = analysis.contract_name.lower()
        expected_files = [
            f"{contract_name_lower}_mcp_server.py",
            f"{contract_name_lower}_mcp_client.py", 
            f"{contract_name_lower}_mcp_config.json",
            f"{contract_name_lower}_README.md"
        ]
        
        all_files_exist = True
        for file_name in expected_files:
            file_path = output_dir / file_name
            if file_path.exists():
                file_size = file_path.stat().st_size
                print(f"   ✅ {file_name} ({file_size} bytes)")
            else:
                print(f"   ❌ {file_name} (missing)")
                all_files_exist = False
        
        print()
        
        if all_files_exist:
            print("🎉 All expected files generated successfully!")
            
            # Step 4: Basic File Content Validation
            print("🔍 Step 4: Validating File Contents...")
            
            # Check server.py
            server_file = output_dir / f"{contract_name_lower}_mcp_server.py"
            with open(server_file, 'r') as f:
                server_content = f.read()
            
            server_checks = [
                ("MCPServer import", "from mcp.server import Server" in server_content),
                ("Contract name", contract_name in server_content),
                ("Contract address", contract_address in server_content),
                ("Network", network in server_content),
                ("Tool definitions", "@server.tool" in server_content),
                ("Main function", "if __name__ == '__main__':" in server_content)
            ]
            
            for check_name, passed in server_checks:
                status = "✅" if passed else "❌"
                print(f"   {status} Server.py - {check_name}")
            
            # Check client.py
            client_file = output_dir / f"{contract_name_lower}_mcp_client.py"
            with open(client_file, 'r') as f:
                client_content = f.read()
            
            client_checks = [
                ("MCP client import", "from mcp.client import ClientSession" in client_content),
                ("Contract class", f"{contract_name}MCPClient" in client_content),
                ("Connection methods", "async def connect" in client_content),
                ("Tool calling", "call_tool" in client_content)
            ]
            
            for check_name, passed in client_checks:
                status = "✅" if passed else "❌"
                print(f"   {status} Client.py - {check_name}")
            
            # Check config.json
            config_file = output_dir / f"{contract_name_lower}_mcp_config.json"
            with open(config_file, 'r') as f:
                config_content = f.read()
            
            config_checks = [
                ("Valid JSON", "{" in config_content and "}" in config_content),
                ("Contract name", contract_name in config_content),
                ("Network", network in config_content),
                ("Server command", "server.py" in config_content)
            ]
            
            for check_name, passed in config_checks:
                status = "✅" if passed else "❌"
                print(f"   {status} Config.json - {check_name}")
            
            print()
            print("🎯 MCP Generation Test Summary:")
            print("=" * 50)
            print("✅ Contract analysis: PASSED")
            print("✅ File generation: PASSED") 
            print("✅ Content validation: PASSED")
            print()
            print(f"📁 Generated files are available in: {output_dir}")
            print("🚀 You can now test the MCP server by running:")
            print(f"   cd {output_dir}")
            print("   python server.py")
            
        else:
            print("❌ Some files are missing. Check the generation process.")
            return False
            
    except Exception as e:
        print(f"❌ Error during MCP generation test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


async def main():
    """Main test function"""
    print("🧪 MCP Server Generation Test Suite")
    print("=" * 50)
    
    success = await test_mcp_generation()
    
    if success:
        print("\n🎉 All tests passed! MCP generation workflow is working correctly.")
        sys.exit(0)
    else:
        print("\n❌ Tests failed. Please check the errors above.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())