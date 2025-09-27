"""
UnknownContract MCP Client - Test client for UnknownContract MCP Server

This client provides a simple interface to test the UnknownContract MCP server tools.
Generated automatically from contract analysis.

Contract Address: 0x01
Network: emulator
Generated: 2025-09-27T13:31:39.387166
"""

import asyncio
import json
from typing import Any, Dict, List, Optional

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class ContractMCPClient:
    """Client for interacting with UnknownContract MCP Server."""
    
    def __init__(self, server_script_path: str):
        self.server_script_path = server_script_path
        self.session: Optional[ClientSession] = None
    
    async def connect(self):
        """Connect to the MCP server."""
        server_params = StdioServerParameters(
            command="python",
            args=[self.server_script_path]
        )
        
        self.stdio_client = stdio_client(server_params)
        self.read, self.write = await self.stdio_client.__aenter__()
        self.session = ClientSession(self.read, self.write)
        
        await self.session.initialize()
        
        # List available tools
        tools_result = await self.session.list_tools()
        print(f"Available tools for UnknownContract:")
        for tool in tools_result.tools:
            print(f"  - {tool.name}: {tool.description}")
        
        return self.session
    
    async def disconnect(self):
        """Disconnect from the MCP server."""
        if self.session:
            await self.stdio_client.__aexit__(None, None, None)
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any] = None) -> Any:
        """Call a tool on the MCP server."""
        if not self.session:
            raise RuntimeError("Not connected to server")
        
        arguments = arguments or {}
        result = await self.session.call_tool(tool_name, arguments)
        return result.content
    
    async def view_contract_info(self, network: str = "emulator") -> Dict[str, Any]:
        """Get contract information."""
        return await self.call_tool("view_contract_info", {"network": network})
    
    async def view_contract_code(self) -> Dict[str, Any]:
        """Get contract source code."""
        return await self.call_tool("view_contract_code")
    
    {{GENERATED_CLIENT_METHODS}}


async def main():
    """Example usage of the UnknownContract MCP Client."""
    import sys
    from pathlib import Path
    
    # Determine server script path
    if len(sys.argv) > 1:
        server_path = sys.argv[1]
    else:
        # Default to generated server in the same directory
        server_path = Path(__file__).parent / "{{CONTRACT_NAME_LOWER}}_mcp_server.py"
    
    client = ContractMCPClient(str(server_path))
    
    try:
        print(f"Connecting to UnknownContract MCP Server...")
        await client.connect()
        
        print("\n" + "="*50)
        print("UnknownContract MCP Client Test Suite")
        print("="*50)
        
        # Test contract info
        print("\n1. Getting contract information...")
        info_result = await client.view_contract_info()
        print(json.dumps(info_result, indent=2))
        
        # Test contract code
        print("\n2. Getting contract source code...")
        code_result = await client.view_contract_code()
        if code_result[0].get("success"):
            print(f"Contract code length: {len(code_result[0].get('source_code', ''))} characters")
        else:
            print(f"Error: {code_result[0].get('error')}")
        
        {{GENERATED_CLIENT_TESTS}}
        
        print("\n" + "="*50)
        print("Test suite completed!")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())