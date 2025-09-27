"""
WalletManager2 MCP Server - A Model Context Protocol server for WalletManager2 smart contract interactions.

This server provides tools for interacting with the WalletManager2 smart contract on Flow blockchain.
Generated automatically from contract analysis.

Contract Address: 0x01
Network: testnet
Generated: 2025-09-27T13:12:39.421472
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
mcp = FastMCP("WalletManager2 MCP Server")

# Contract configuration
CONTRACT_NAME = "WalletManager2"
CONTRACT_ADDRESS = "0x01"
DEFAULT_NETWORK = "testnet"
PROJECT_PATH = "{{PROJECT_PATH}}"


class AddconnectorParams(BaseModel):
    """Parameters for addConnector function."""
    id: str
    name: str


class RemoveconnectorParams(BaseModel):
    """Parameters for removeConnector function."""
    id: str


class CreatewalletParams(BaseModel):
    """Parameters for createWallet function."""
    address: str


class GetwalletcapabilityParams(BaseModel):
    """Parameters for getWalletCapability function."""
    address: str


class ConnectwalletParams(BaseModel):
    """Parameters for connectWallet function."""
    address: str


class DisconnectwalletParams(BaseModel):
    """Parameters for disconnectWallet function."""
    address: str


class MainParams(BaseModel):
    """Parameters for main function."""
    address: str


class WalletConnectedEvent(BaseModel):
    """Event data for WalletConnected."""
    address: str


class WalletDisconnectedEvent(BaseModel):
    """Event data for WalletDisconnected."""
    address: str


class ConnectorAddedEvent(BaseModel):
    """Event data for ConnectorAdded."""
    connectorId: str


class ConnectorRemovedEvent(BaseModel):
    """Event data for ConnectorRemoved."""
    connectorId: str


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
    """Get information about the WalletManager2 contract."""
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
    "name": "getAddress",
    "parameters": [],
    "return_type": "Address",
    "documentation": "Call getAddress function on the contract.",
    "is_view": false
  },
  {
    "name": "isConnected",
    "parameters": [],
    "return_type": "Bool",
    "documentation": "Call isConnected function on the contract.",
    "is_view": false
  },
  {
    "name": "connect",
    "parameters": [],
    "return_type": null,
    "documentation": "Call connect function on the contract.",
    "is_view": false
  },
  {
    "name": "disconnect",
    "parameters": [],
    "return_type": null,
    "documentation": "Call disconnect function on the contract.",
    "is_view": false
  },
  {
    "name": "addConnector",
    "parameters": [
      {
        "name": "id",
        "type": "String"
      },
      {
        "name": "name",
        "type": "String"
      }
    ],
    "return_type": null,
    "documentation": "Function to add a new connector",
    "is_view": false
  },
  {
    "name": "removeConnector",
    "parameters": [
      {
        "name": "id",
        "type": "String"
      }
    ],
    "return_type": null,
    "documentation": "Function to remove a connector",
    "is_view": false
  },
  {
    "name": "createWallet",
    "parameters": [
      {
        "name": "address",
        "type": "Address"
      }
    ],
    "return_type": "Capability<&Wallet>",
    "documentation": "Function to create a new wallet",
    "is_view": false
  },
  {
    "name": "getWalletCapability",
    "parameters": [
      {
        "name": "address",
        "type": "Address"
      }
    ],
    "return_type": "Capability<&Wallet>",
    "documentation": "Function to get a wallet capability",
    "is_view": false
  },
  {
    "name": "connectWallet",
    "parameters": [
      {
        "name": "address",
        "type": "Address"
      }
    ],
    "return_type": null,
    "documentation": "Function to connect a wallet",
    "is_view": false
  },
  {
    "name": "disconnectWallet",
    "parameters": [
      {
        "name": "address",
        "type": "Address"
      }
    ],
    "return_type": null,
    "documentation": "Function to disconnect a wallet",
    "is_view": false
  },
  {
    "name": "main",
    "parameters": [
      {
        "name": "address",
        "type": "Address"
      }
    ],
    "return_type": "Capability<&WalletManager2.Wallet>",
    "documentation": "Example script to get a wallet capability",
    "is_view": true
  }
],
                "events": [
  {
    "name": "WalletConnected",
    "parameters": [
      {
        "name": "address",
        "type": "Address"
      }
    ],
    "documentation": "Events"
  },
  {
    "name": "WalletDisconnected",
    "parameters": [
      {
        "name": "address",
        "type": "Address"
      }
    ],
    "documentation": "WalletDisconnected event from the contract."
  },
  {
    "name": "ConnectorAdded",
    "parameters": [
      {
        "name": "connectorId",
        "type": "String"
      }
    ],
    "documentation": "ConnectorAdded event from the contract."
  },
  {
    "name": "ConnectorRemoved",
    "parameters": [
      {
        "name": "connectorId",
        "type": "String"
      }
    ],
    "documentation": "ConnectorRemoved event from the contract."
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
    """Get the source code of the WalletManager2 contract."""
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
async def call_getAddress(arguments: dict) -> str:
    """
    Call getAddress function on the WalletManager2 contract.
    
    Access Level: all
    Return Type: Address
    View Function: No
    """
    try:
        # Extract parameters
        # No parameters
        
        # Build Flow CLI command
        if False:
            # View function - use scripts
            cmd = [
                "flow", "scripts", "execute",
                "--network", "testnet",
                "--code", """
                import WalletManager2 from 0x01
                
                transaction() {
                    prepare(signer: AuthAccount) {
                        // Transaction logic here
                    }
                    
                    execute {
                        WalletManager2.getAddress()
                    }
                }
                """,
                
            ]
        else:
            # Transaction function
            cmd = [
                "flow", "transactions", "send",
                "--network", "testnet",
                "--signer", "default",
                "--code", """
                import WalletManager2 from 0x01
                
                transaction() {
                    prepare(signer: AuthAccount) {
                        // Transaction logic here
                    }
                    
                    execute {
                        WalletManager2.getAddress()
                    }
                }
                """,
                
            ]
        
        result = await run_flow_command(cmd)
        return json.dumps({
            "success": True,
            "result": result,
            "function": "getAddress",
            "parameters": arguments
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e),
            "function": "getAddress",
            "parameters": arguments
        }, indent=2)


@mcp.tool()
async def call_isConnected(arguments: dict) -> str:
    """
    Call isConnected function on the WalletManager2 contract.
    
    Access Level: all
    Return Type: Bool
    View Function: No
    """
    try:
        # Extract parameters
        # No parameters
        
        # Build Flow CLI command
        if False:
            # View function - use scripts
            cmd = [
                "flow", "scripts", "execute",
                "--network", "testnet",
                "--code", """
                import WalletManager2 from 0x01
                
                transaction() {
                    prepare(signer: AuthAccount) {
                        // Transaction logic here
                    }
                    
                    execute {
                        WalletManager2.isConnected()
                    }
                }
                """,
                
            ]
        else:
            # Transaction function
            cmd = [
                "flow", "transactions", "send",
                "--network", "testnet",
                "--signer", "default",
                "--code", """
                import WalletManager2 from 0x01
                
                transaction() {
                    prepare(signer: AuthAccount) {
                        // Transaction logic here
                    }
                    
                    execute {
                        WalletManager2.isConnected()
                    }
                }
                """,
                
            ]
        
        result = await run_flow_command(cmd)
        return json.dumps({
            "success": True,
            "result": result,
            "function": "isConnected",
            "parameters": arguments
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e),
            "function": "isConnected",
            "parameters": arguments
        }, indent=2)


@mcp.tool()
async def call_connect(arguments: dict) -> str:
    """
    Call connect function on the WalletManager2 contract.
    
    Access Level: all
    Return Type: Void
    View Function: No
    """
    try:
        # Extract parameters
        # No parameters
        
        # Build Flow CLI command
        if False:
            # View function - use scripts
            cmd = [
                "flow", "scripts", "execute",
                "--network", "testnet",
                "--code", """
                import WalletManager2 from 0x01
                
                transaction() {
                    prepare(signer: AuthAccount) {
                        // Transaction logic here
                    }
                    
                    execute {
                        WalletManager2.connect()
                    }
                }
                """,
                
            ]
        else:
            # Transaction function
            cmd = [
                "flow", "transactions", "send",
                "--network", "testnet",
                "--signer", "default",
                "--code", """
                import WalletManager2 from 0x01
                
                transaction() {
                    prepare(signer: AuthAccount) {
                        // Transaction logic here
                    }
                    
                    execute {
                        WalletManager2.connect()
                    }
                }
                """,
                
            ]
        
        result = await run_flow_command(cmd)
        return json.dumps({
            "success": True,
            "result": result,
            "function": "connect",
            "parameters": arguments
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e),
            "function": "connect",
            "parameters": arguments
        }, indent=2)


@mcp.tool()
async def call_disconnect(arguments: dict) -> str:
    """
    Call disconnect function on the WalletManager2 contract.
    
    Access Level: all
    Return Type: Void
    View Function: No
    """
    try:
        # Extract parameters
        # No parameters
        
        # Build Flow CLI command
        if False:
            # View function - use scripts
            cmd = [
                "flow", "scripts", "execute",
                "--network", "testnet",
                "--code", """
                import WalletManager2 from 0x01
                
                transaction() {
                    prepare(signer: AuthAccount) {
                        // Transaction logic here
                    }
                    
                    execute {
                        WalletManager2.disconnect()
                    }
                }
                """,
                
            ]
        else:
            # Transaction function
            cmd = [
                "flow", "transactions", "send",
                "--network", "testnet",
                "--signer", "default",
                "--code", """
                import WalletManager2 from 0x01
                
                transaction() {
                    prepare(signer: AuthAccount) {
                        // Transaction logic here
                    }
                    
                    execute {
                        WalletManager2.disconnect()
                    }
                }
                """,
                
            ]
        
        result = await run_flow_command(cmd)
        return json.dumps({
            "success": True,
            "result": result,
            "function": "disconnect",
            "parameters": arguments
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e),
            "function": "disconnect",
            "parameters": arguments
        }, indent=2)


@mcp.tool()
async def call_addConnector(arguments: dict) -> str:
    """
    Function to add a new connector
    
    Access Level: all
    Return Type: Void
    View Function: No
    """
    try:
        # Extract parameters
        id = arguments.get("id")
        name = arguments.get("name")
        
        # Build Flow CLI command
        if False:
            # View function - use scripts
            cmd = [
                "flow", "scripts", "execute",
                "--network", "testnet",
                "--code", """
                import WalletManager2 from 0x01
                
                transaction(id: String, name: String) {
                    prepare(signer: AuthAccount) {
                        // Transaction logic here
                    }
                    
                    execute {
                        WalletManager2.addConnector(id, name)
                    }
                }
                """,
                "--arg", "String:id", "--arg", "String:name"
            ]
        else:
            # Transaction function
            cmd = [
                "flow", "transactions", "send",
                "--network", "testnet",
                "--signer", "default",
                "--code", """
                import WalletManager2 from 0x01
                
                transaction(id: String, name: String) {
                    prepare(signer: AuthAccount) {
                        // Transaction logic here
                    }
                    
                    execute {
                        WalletManager2.addConnector(id, name)
                    }
                }
                """,
                "--arg", "String:id", "--arg", "String:name"
            ]
        
        result = await run_flow_command(cmd)
        return json.dumps({
            "success": True,
            "result": result,
            "function": "addConnector",
            "parameters": arguments
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e),
            "function": "addConnector",
            "parameters": arguments
        }, indent=2)


@mcp.tool()
async def call_removeConnector(arguments: dict) -> str:
    """
    Function to remove a connector
    
    Access Level: all
    Return Type: Void
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
                "--network", "testnet",
                "--code", """
                import WalletManager2 from 0x01
                
                transaction(id: String) {
                    prepare(signer: AuthAccount) {
                        // Transaction logic here
                    }
                    
                    execute {
                        WalletManager2.removeConnector(id)
                    }
                }
                """,
                "--arg", "String:id"
            ]
        else:
            # Transaction function
            cmd = [
                "flow", "transactions", "send",
                "--network", "testnet",
                "--signer", "default",
                "--code", """
                import WalletManager2 from 0x01
                
                transaction(id: String) {
                    prepare(signer: AuthAccount) {
                        // Transaction logic here
                    }
                    
                    execute {
                        WalletManager2.removeConnector(id)
                    }
                }
                """,
                "--arg", "String:id"
            ]
        
        result = await run_flow_command(cmd)
        return json.dumps({
            "success": True,
            "result": result,
            "function": "removeConnector",
            "parameters": arguments
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e),
            "function": "removeConnector",
            "parameters": arguments
        }, indent=2)


@mcp.tool()
async def call_createWallet(arguments: dict) -> str:
    """
    Function to create a new wallet
    
    Access Level: all
    Return Type: Capability<&Wallet>
    View Function: No
    """
    try:
        # Extract parameters
        address = arguments.get("address")
        
        # Build Flow CLI command
        if False:
            # View function - use scripts
            cmd = [
                "flow", "scripts", "execute",
                "--network", "testnet",
                "--code", """
                import WalletManager2 from 0x01
                
                transaction(address: Address) {
                    prepare(signer: AuthAccount) {
                        // Transaction logic here
                    }
                    
                    execute {
                        WalletManager2.createWallet(address)
                    }
                }
                """,
                "--arg", "String:address"
            ]
        else:
            # Transaction function
            cmd = [
                "flow", "transactions", "send",
                "--network", "testnet",
                "--signer", "default",
                "--code", """
                import WalletManager2 from 0x01
                
                transaction(address: Address) {
                    prepare(signer: AuthAccount) {
                        // Transaction logic here
                    }
                    
                    execute {
                        WalletManager2.createWallet(address)
                    }
                }
                """,
                "--arg", "String:address"
            ]
        
        result = await run_flow_command(cmd)
        return json.dumps({
            "success": True,
            "result": result,
            "function": "createWallet",
            "parameters": arguments
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e),
            "function": "createWallet",
            "parameters": arguments
        }, indent=2)


@mcp.tool()
async def call_getWalletCapability(arguments: dict) -> str:
    """
    Function to get a wallet capability
    
    Access Level: all
    Return Type: Capability<&Wallet>
    View Function: No
    """
    try:
        # Extract parameters
        address = arguments.get("address")
        
        # Build Flow CLI command
        if False:
            # View function - use scripts
            cmd = [
                "flow", "scripts", "execute",
                "--network", "testnet",
                "--code", """
                import WalletManager2 from 0x01
                
                transaction(address: Address) {
                    prepare(signer: AuthAccount) {
                        // Transaction logic here
                    }
                    
                    execute {
                        WalletManager2.getWalletCapability(address)
                    }
                }
                """,
                "--arg", "String:address"
            ]
        else:
            # Transaction function
            cmd = [
                "flow", "transactions", "send",
                "--network", "testnet",
                "--signer", "default",
                "--code", """
                import WalletManager2 from 0x01
                
                transaction(address: Address) {
                    prepare(signer: AuthAccount) {
                        // Transaction logic here
                    }
                    
                    execute {
                        WalletManager2.getWalletCapability(address)
                    }
                }
                """,
                "--arg", "String:address"
            ]
        
        result = await run_flow_command(cmd)
        return json.dumps({
            "success": True,
            "result": result,
            "function": "getWalletCapability",
            "parameters": arguments
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e),
            "function": "getWalletCapability",
            "parameters": arguments
        }, indent=2)


@mcp.tool()
async def call_connectWallet(arguments: dict) -> str:
    """
    Function to connect a wallet
    
    Access Level: all
    Return Type: Void
    View Function: No
    """
    try:
        # Extract parameters
        address = arguments.get("address")
        
        # Build Flow CLI command
        if False:
            # View function - use scripts
            cmd = [
                "flow", "scripts", "execute",
                "--network", "testnet",
                "--code", """
                import WalletManager2 from 0x01
                
                transaction(address: Address) {
                    prepare(signer: AuthAccount) {
                        // Transaction logic here
                    }
                    
                    execute {
                        WalletManager2.connectWallet(address)
                    }
                }
                """,
                "--arg", "String:address"
            ]
        else:
            # Transaction function
            cmd = [
                "flow", "transactions", "send",
                "--network", "testnet",
                "--signer", "default",
                "--code", """
                import WalletManager2 from 0x01
                
                transaction(address: Address) {
                    prepare(signer: AuthAccount) {
                        // Transaction logic here
                    }
                    
                    execute {
                        WalletManager2.connectWallet(address)
                    }
                }
                """,
                "--arg", "String:address"
            ]
        
        result = await run_flow_command(cmd)
        return json.dumps({
            "success": True,
            "result": result,
            "function": "connectWallet",
            "parameters": arguments
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e),
            "function": "connectWallet",
            "parameters": arguments
        }, indent=2)


@mcp.tool()
async def call_disconnectWallet(arguments: dict) -> str:
    """
    Function to disconnect a wallet
    
    Access Level: all
    Return Type: Void
    View Function: No
    """
    try:
        # Extract parameters
        address = arguments.get("address")
        
        # Build Flow CLI command
        if False:
            # View function - use scripts
            cmd = [
                "flow", "scripts", "execute",
                "--network", "testnet",
                "--code", """
                import WalletManager2 from 0x01
                
                transaction(address: Address) {
                    prepare(signer: AuthAccount) {
                        // Transaction logic here
                    }
                    
                    execute {
                        WalletManager2.disconnectWallet(address)
                    }
                }
                """,
                "--arg", "String:address"
            ]
        else:
            # Transaction function
            cmd = [
                "flow", "transactions", "send",
                "--network", "testnet",
                "--signer", "default",
                "--code", """
                import WalletManager2 from 0x01
                
                transaction(address: Address) {
                    prepare(signer: AuthAccount) {
                        // Transaction logic here
                    }
                    
                    execute {
                        WalletManager2.disconnectWallet(address)
                    }
                }
                """,
                "--arg", "String:address"
            ]
        
        result = await run_flow_command(cmd)
        return json.dumps({
            "success": True,
            "result": result,
            "function": "disconnectWallet",
            "parameters": arguments
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e),
            "function": "disconnectWallet",
            "parameters": arguments
        }, indent=2)


@mcp.tool()
async def call_main(arguments: dict) -> str:
    """
    Example script to get a wallet capability
    
    Access Level: all
    Return Type: Capability<&WalletManager2.Wallet>
    View Function: Yes
    """
    try:
        # Extract parameters
        address = arguments.get("address")
        
        # Build Flow CLI command
        if True:
            # View function - use scripts
            cmd = [
                "flow", "scripts", "execute",
                "--network", "testnet",
                "--code", """
                import WalletManager2 from 0x01
                
                access(all) fun main(address: Address): Capability<&WalletManager2.Wallet> {
                    return WalletManager2.main(address)
                }
                """,
                "--arg", "String:address"
            ]
        else:
            # Transaction function
            cmd = [
                "flow", "transactions", "send",
                "--network", "testnet",
                "--signer", "default",
                "--code", """
                import WalletManager2 from 0x01
                
                access(all) fun main(address: Address): Capability<&WalletManager2.Wallet> {
                    return WalletManager2.main(address)
                }
                """,
                "--arg", "String:address"
            ]
        
        result = await run_flow_command(cmd)
        return json.dumps({
            "success": True,
            "result": result,
            "function": "main",
            "parameters": arguments
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e),
            "function": "main",
            "parameters": arguments
        }, indent=2)


@mcp.tool()
async def get_contract_events(arguments: dict) -> str:
    """
    Get recent events emitted by the WalletManager2 contract.
    
    Available events: WalletConnected, WalletDisconnected, ConnectorAdded, ConnectorRemoved
    """
    try:
        limit = arguments.get("limit", 10)
        event_type = arguments.get("event_type", "all")
        
        cmd = [
            "flow", "events", "get",
            "--network", "testnet",
            "--start", "latest",
            "--end", "latest",
            f"WalletManager2.*"
        ]
        
        result = await run_flow_command(cmd)
        
        return json.dumps({
            "success": True,
            "events": result,
            "contract": "WalletManager2",
            "limit": limit,
            "event_type": event_type
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e),
            "contract": "WalletManager2"
        }, indent=2)


@mcp.resource(f"flow://contract/{CONTRACT_ADDRESS}/{CONTRACT_NAME}")
async def get_contract_resource() -> str:
    """Get contract resource information."""
    return f"WalletManager2 contract at {CONTRACT_ADDRESS}"


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
    """Generate a prompt for analyzing the WalletManager2 contract."""
    contract_path = Path(PROJECT_PATH) / "contracts" / f"{CONTRACT_NAME}.cdc"
    
    if contract_path.exists():
        code = contract_path.read_text()
        return f"""
Please analyze the following WalletManager2 smart contract for {analysis_type}:

Contract Name: WalletManager2
Contract Address: {CONTRACT_ADDRESS}
Network: {DEFAULT_NETWORK}

Source Code:
```cadence
{code}
```

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