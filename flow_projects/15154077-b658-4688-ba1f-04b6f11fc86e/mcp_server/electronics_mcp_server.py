"""
Electronics MCP Server - A Model Context Protocol server for Electronics smart contract interactions.

This server provides tools for interacting with the Electronics smart contract on Flow blockchain.
Generated automatically from contract analysis.

Contract Address: 0x01
Network: emulator
Generated: 2025-09-27T13:50:41.000224
"""

import asyncio
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from mcp.server.fastmcp import FastMCP, Context
from mcp.server.session import ServerSession
from pydantic import BaseModel, Field

# Create MCP server
mcp = FastMCP("Electronics MCP Server")

# Contract configuration
CONTRACT_NAME = "Electronics"
CONTRACT_ADDRESS = "0x01"
DEFAULT_NETWORK = "emulator"
PROJECT_PATH = "{{PROJECT_PATH}}"


class AdddeviceParams(BaseModel):
    """Parameters for addDevice function."""
    device: Any


class RemovedeviceParams(BaseModel):
    """Parameters for removeDevice function."""
    id: int


class GetdeviceParams(BaseModel):
    """Parameters for getDevice function."""
    id: int


class DeviceAddedEvent(BaseModel):
    """Event data for DeviceAdded."""
    deviceId: int
    owner: str


class DeviceRemovedEvent(BaseModel):
    """Event data for DeviceRemoved."""
    deviceId: int
    owner: str


async def run_flow_command(args: List[str], cwd: Optional[Path] = None) -> Dict[str, Any]:
    """Run a Flow CLI command and return the result."""
    try:
        cmd = ["/opt/homebrew/bin/flow"] + args

        # Set environment variables
        env = {}
        if cwd:
            env = {"FLOW_CONFIG_PATH": str(cwd)}

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=cwd or PROJECT_PATH,
            env=env,
            timeout=30
        )

        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "stdout": "",
            "stderr": "Command timed out",
            "returncode": -1
        }
    except Exception as e:
        return {
            "success": False,
            "stdout": "",
            "stderr": str(e),
            "returncode": -1
        }


@mcp.tool()
async def view_contract_info(
    ctx: Context[ServerSession, None],
    network: str = DEFAULT_NETWORK
) -> Dict[str, Any]:
    """Get information about the Electronics contract."""
    try:
        result = await run_flow_command([
            "accounts", "get", CONTRACT_ADDRESS,
            "--network", network
        ])
        
        if result["success"]:
            return {
                "success": True,
                "contract_name": CONTRACT_NAME,
                "contract_address": CONTRACT_ADDRESS,
                "network": network,
                "account_info": result["stdout"],
                "functions": [
  {
    "name": "addDevice",
    "parameters": [
      {
        "name": "device",
        "type": "ElectronicDevice"
      }
    ],
    "return_type": null,
    "documentation": "Add a device to the collection",
    "is_view": false
  },
  {
    "name": "removeDevice",
    "parameters": [
      {
        "name": "id",
        "type": "UInt64"
      }
    ],
    "return_type": "ElectronicDevice?",
    "documentation": "Remove a device from the collection",
    "is_view": false
  },
  {
    "name": "getDevice",
    "parameters": [
      {
        "name": "id",
        "type": "UInt64"
      }
    ],
    "return_type": "ElectronicDevice?",
    "documentation": "Get a device from the collection",
    "is_view": false
  }
],
                "events": [
  {
    "name": "DeviceAdded",
    "parameters": [
      {
        "name": "deviceId",
        "type": "UInt64"
      },
      {
        "name": "owner",
        "type": "Address"
      }
    ],
    "documentation": "Event emitted when a device is added to a collection"
  },
  {
    "name": "DeviceRemoved",
    "parameters": [
      {
        "name": "deviceId",
        "type": "UInt64"
      },
      {
        "name": "owner",
        "type": "Address"
      }
    ],
    "documentation": "Event emitted when a device is removed from a collection"
  }
]
            }
        else:
            return {
                "success": False,
                "error": f"Failed to get contract info: {result['stderr']}"
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Error getting contract info: {str(e)}"
        }


@mcp.tool()
async def view_contract_code(
    ctx: Context[ServerSession, None]
) -> Dict[str, Any]:
    """Get the source code of the Electronics contract."""
    try:
        contract_path = Path(PROJECT_PATH) / "contracts" / f"{CONTRACT_NAME}.cdc"
        if contract_path.exists():
            code = contract_path.read_text()
            return {
                "success": True,
                "contract_name": CONTRACT_NAME,
                "source_code": code,
                "file_path": str(contract_path)
            }
        else:
            return {
                "success": False,
                "error": f"Contract file not found at {contract_path}"
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Error reading contract code: {str(e)}"
        }



@mcp.tool()
async def call_addDevice(arguments: dict) -> str:
    """
    Add a device to the collection
    
    Access Level: all
    Return Type: Void
    View Function: No
    """
    try:
        # Extract parameters
        device = arguments.get("device")
        
        # Build Flow CLI command
        if False:
            # View function - use scripts
            cmd = [
                "flow", "scripts", "execute",
                "--network", "emulator",
                "--code", """
                import Electronics from 0x01
                
                transaction(device: ElectronicDevice) {
                    prepare(signer: AuthAccount) {
                        // Transaction logic here
                    }
                    
                    execute {
                        Electronics.addDevice(device)
                    }
                }
                """,
                "--arg", "String:device"
            ]
        else:
            # Transaction function
            cmd = [
                "flow", "transactions", "send",
                "--network", "emulator",
                "--signer", "default",
                "--code", """
                import Electronics from 0x01
                
                transaction(device: ElectronicDevice) {
                    prepare(signer: AuthAccount) {
                        // Transaction logic here
                    }
                    
                    execute {
                        Electronics.addDevice(device)
                    }
                }
                """,
                "--arg", "String:device"
            ]
        
        result = await run_flow_command(cmd)
        return json.dumps({
            "success": True,
            "result": result,
            "function": "addDevice",
            "parameters": arguments
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e),
            "function": "addDevice",
            "parameters": arguments
        }, indent=2)


@mcp.tool()
async def call_removeDevice(arguments: dict) -> str:
    """
    Remove a device from the collection
    
    Access Level: all
    Return Type: ElectronicDevice?
    View Function: No
    """
    try:
        # Extract parameters
        id = arguments.get("id")
        
        # Build Flow CLI command
        if False:
            # View function - use scripts
            cmd = [
                "flow", "scripts", "execute",
                "--network", "emulator",
                "--code", """
                import Electronics from 0x01
                
                transaction(id: UInt64) {
                    prepare(signer: AuthAccount) {
                        // Transaction logic here
                    }
                    
                    execute {
                        Electronics.removeDevice(id)
                    }
                }
                """,
                "--arg", "String:id"
            ]
        else:
            # Transaction function
            cmd = [
                "flow", "transactions", "send",
                "--network", "emulator",
                "--signer", "default",
                "--code", """
                import Electronics from 0x01
                
                transaction(id: UInt64) {
                    prepare(signer: AuthAccount) {
                        // Transaction logic here
                    }
                    
                    execute {
                        Electronics.removeDevice(id)
                    }
                }
                """,
                "--arg", "String:id"
            ]
        
        result = await run_flow_command(cmd)
        return json.dumps({
            "success": True,
            "result": result,
            "function": "removeDevice",
            "parameters": arguments
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e),
            "function": "removeDevice",
            "parameters": arguments
        }, indent=2)


@mcp.tool()
async def call_getDevice(arguments: dict) -> str:
    """
    Get a device from the collection
    
    Access Level: all
    Return Type: ElectronicDevice?
    View Function: No
    """
    try:
        # Extract parameters
        id = arguments.get("id")
        
        # Build Flow CLI command
        if False:
            # View function - use scripts
            cmd = [
                "flow", "scripts", "execute",
                "--network", "emulator",
                "--code", """
                import Electronics from 0x01
                
                transaction(id: UInt64) {
                    prepare(signer: AuthAccount) {
                        // Transaction logic here
                    }
                    
                    execute {
                        Electronics.getDevice(id)
                    }
                }
                """,
                "--arg", "String:id"
            ]
        else:
            # Transaction function
            cmd = [
                "flow", "transactions", "send",
                "--network", "emulator",
                "--signer", "default",
                "--code", """
                import Electronics from 0x01
                
                transaction(id: UInt64) {
                    prepare(signer: AuthAccount) {
                        // Transaction logic here
                    }
                    
                    execute {
                        Electronics.getDevice(id)
                    }
                }
                """,
                "--arg", "String:id"
            ]
        
        result = await run_flow_command(cmd)
        return json.dumps({
            "success": True,
            "result": result,
            "function": "getDevice",
            "parameters": arguments
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e),
            "function": "getDevice",
            "parameters": arguments
        }, indent=2)


@mcp.tool()
async def get_contract_events(arguments: dict) -> str:
    """
    Get recent events emitted by the Electronics contract.
    
    Available events: DeviceAdded, DeviceRemoved
    """
    try:
        limit = arguments.get("limit", 10)
        event_type = arguments.get("event_type", "all")
        
        cmd = [
            "flow", "events", "get",
            "--network", "emulator",
            "--start", "latest",
            "--end", "latest",
            f"Electronics.*"
        ]
        
        result = await run_flow_command(cmd)
        
        return json.dumps({
            "success": True,
            "events": result,
            "contract": "Electronics",
            "limit": limit,
            "event_type": event_type
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e),
            "contract": "Electronics"
        }, indent=2)


@mcp.resource(f"flow://contract/{CONTRACT_ADDRESS}/{CONTRACT_NAME}")
async def get_contract_resource() -> str:
    """Get contract resource information."""
    return f"Electronics contract at {CONTRACT_ADDRESS}"


@mcp.resource(f"flow://contract/{CONTRACT_ADDRESS}/{CONTRACT_NAME}/code")
async def get_contract_code_resource() -> str:
    """Get contract source code as a resource."""
    try:
        contract_path = Path(PROJECT_PATH) / "contracts" / f"{CONTRACT_NAME}.cdc"
        if contract_path.exists():
            return contract_path.read_text()
        else:
            return f"Contract file not found at {contract_path}"
    except Exception as e:
        return f"Error reading contract: {str(e)}"


@mcp.prompt()
def analyze_contract_prompt(analysis_type: str = "security") -> str:
    """Generate a prompt for analyzing the Electronics contract."""
    contract_path = Path(PROJECT_PATH) / "contracts" / f"{CONTRACT_NAME}.cdc"
    
    if contract_path.exists():
        code = contract_path.read_text()
        return f"""
Please analyze the following Electronics smart contract for {analysis_type}:

Contract Name: Electronics
Contract Address: {CONTRACT_ADDRESS}
Network: {DEFAULT_NETWORK}

Source Code:
{code}

Please provide a detailed {analysis_type} analysis including:
1. Potential vulnerabilities or issues
2. Best practices compliance
3. Optimization suggestions
4. Security recommendations
"""
    else:
        return f"Contract file not found at {contract_path}"


if __name__ == "__main__":
    mcp.run()