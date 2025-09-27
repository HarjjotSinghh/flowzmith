"""
WalletManager MCP Server - A Model Context Protocol server for WalletManager smart contract interactions.

This server provides tools for interacting with the WalletManager smart contract on Flow blockchain.
Generated automatically from contract analysis.

Contract Address: 0x01
Network: emulator
Generated: 2025-09-27T13:08:05.750859
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
mcp = FastMCP("WalletManager MCP Server")

# Contract configuration
CONTRACT_NAME = "WalletManager"
CONTRACT_ADDRESS = "0x01"
DEFAULT_NETWORK = "emulator"
PROJECT_PATH = "{{PROJECT_PATH}}"


class WithdrawParams(BaseModel):
    """Parameters for withdraw function."""
    amount: float


class DepositParams(BaseModel):
    """Parameters for deposit function."""
    withdraw: Any


class GetwalletcapabilityParams(BaseModel):
    """Parameters for getWalletCapability function."""
    walletID: int


class UpdatewalletbalanceParams(BaseModel):
    """Parameters for updateWalletBalance function."""
    walletID: int
    newBalance: float


class DeletewalletParams(BaseModel):
    """Parameters for deleteWallet function."""
    walletID: int


class MainParams(BaseModel):
    """Parameters for main function."""
    account: str
    walletID: int


class WalletCreatedEvent(BaseModel):
    """Event data for WalletCreated."""
    address: str
    walletID: int


class WalletUpdatedEvent(BaseModel):
    """Event data for WalletUpdated."""
    address: str
    walletID: int
    newBalance: float


class WalletDeletedEvent(BaseModel):
    """Event data for WalletDeleted."""
    address: str
    walletID: int


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
    """Get information about the WalletManager contract."""
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
    "name": "withdraw",
    "parameters": [
      {
        "name": "amount",
        "type": "UFix64"
      }
    ],
    "return_type": "@Token",
    "documentation": "Call withdraw function on the contract.",
    "is_view": false
  },
  {
    "name": "deposit",
    "parameters": [
      {
        "name": "withdraw",
        "type": "@Token"
      }
    ],
    "return_type": null,
    "documentation": "Call deposit function on the contract.",
    "is_view": false
  },
  {
    "name": "getBalance",
    "parameters": [],
    "return_type": "UFix64",
    "documentation": "Call getBalance function on the contract.",
    "is_view": false
  },
  {
    "name": "getID",
    "parameters": [],
    "return_type": "UInt64",
    "documentation": "Call getID function on the contract.",
    "is_view": false
  },
  {
    "name": "createWallet",
    "parameters": [],
    "return_type": "UInt64",
    "documentation": "Function to create a new wallet",
    "is_view": false
  },
  {
    "name": "getWalletCapability",
    "parameters": [
      {
        "name": "walletID",
        "type": "UInt64"
      }
    ],
    "return_type": "Capability<&Wallet>",
    "documentation": "Function to get a wallet capability",
    "is_view": false
  },
  {
    "name": "updateWalletBalance",
    "parameters": [
      {
        "name": "walletID",
        "type": "UInt64"
      },
      {
        "name": "newBalance",
        "type": "UFix64"
      }
    ],
    "return_type": null,
    "documentation": "Function to update a wallet balance",
    "is_view": false
  },
  {
    "name": "deleteWallet",
    "parameters": [
      {
        "name": "walletID",
        "type": "UInt64"
      }
    ],
    "return_type": null,
    "documentation": "Function to delete a wallet",
    "is_view": false
  },
  {
    "name": "main",
    "parameters": [
      {
        "name": "account",
        "type": "Address"
      },
      {
        "name": "walletID",
        "type": "UInt64"
      }
    ],
    "return_type": "UFix64",
    "documentation": "Example script to get a wallet balance",
    "is_view": false
  }
],
                "events": [
  {
    "name": "WalletCreated",
    "parameters": [
      {
        "name": "address",
        "type": "Address"
      },
      {
        "name": "walletID",
        "type": "UInt64"
      }
    ],
    "documentation": "Events"
  },
  {
    "name": "WalletUpdated",
    "parameters": [
      {
        "name": "address",
        "type": "Address"
      },
      {
        "name": "walletID",
        "type": "UInt64"
      },
      {
        "name": "newBalance",
        "type": "UFix64"
      }
    ],
    "documentation": "WalletUpdated event from the contract."
  },
  {
    "name": "WalletDeleted",
    "parameters": [
      {
        "name": "address",
        "type": "Address"
      },
      {
        "name": "walletID",
        "type": "UInt64"
      }
    ],
    "documentation": "WalletDeleted event from the contract."
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
    """Get the source code of the WalletManager contract."""
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
async def call_withdraw(arguments: dict) -> str:
    """
    Call withdraw function on the WalletManager contract.
    
    Access Level: all
    Return Type: @Token
    View Function: No
    """
    try:
        # Extract parameters
        amount = arguments.get("amount")
        
        # Build Flow CLI command
        if False:
            # View function - use scripts
            cmd = [
                "flow", "scripts", "execute",
                "--network", "emulator",
                "--code", """
                import WalletManager from 0x01
                
                transaction(amount: UFix64) {
                    prepare(signer: AuthAccount) {
                        // Transaction logic here
                    }
                    
                    execute {
                        WalletManager.withdraw(amount)
                    }
                }
                """,
                "--arg", "String:amount"
            ]
        else:
            # Transaction function
            cmd = [
                "flow", "transactions", "send",
                "--network", "emulator",
                "--signer", "default",
                "--code", """
                import WalletManager from 0x01
                
                transaction(amount: UFix64) {
                    prepare(signer: AuthAccount) {
                        // Transaction logic here
                    }
                    
                    execute {
                        WalletManager.withdraw(amount)
                    }
                }
                """,
                "--arg", "String:amount"
            ]
        
        result = await run_flow_command(cmd)
        return json.dumps({
            "success": True,
            "result": result,
            "function": "withdraw",
            "parameters": arguments
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e),
            "function": "withdraw",
            "parameters": arguments
        }, indent=2)


@mcp.tool()
async def call_deposit(arguments: dict) -> str:
    """
    Call deposit function on the WalletManager contract.
    
    Access Level: all
    Return Type: Void
    View Function: No
    """
    try:
        # Extract parameters
        withdraw = arguments.get("withdraw")
        
        # Build Flow CLI command
        if False:
            # View function - use scripts
            cmd = [
                "flow", "scripts", "execute",
                "--network", "emulator",
                "--code", """
                import WalletManager from 0x01
                
                transaction(withdraw: @Token) {
                    prepare(signer: AuthAccount) {
                        // Transaction logic here
                    }
                    
                    execute {
                        WalletManager.deposit(withdraw)
                    }
                }
                """,
                "--arg", "String:withdraw"
            ]
        else:
            # Transaction function
            cmd = [
                "flow", "transactions", "send",
                "--network", "emulator",
                "--signer", "default",
                "--code", """
                import WalletManager from 0x01
                
                transaction(withdraw: @Token) {
                    prepare(signer: AuthAccount) {
                        // Transaction logic here
                    }
                    
                    execute {
                        WalletManager.deposit(withdraw)
                    }
                }
                """,
                "--arg", "String:withdraw"
            ]
        
        result = await run_flow_command(cmd)
        return json.dumps({
            "success": True,
            "result": result,
            "function": "deposit",
            "parameters": arguments
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e),
            "function": "deposit",
            "parameters": arguments
        }, indent=2)


@mcp.tool()
async def call_getBalance(arguments: dict) -> str:
    """
    Call getBalance function on the WalletManager contract.
    
    Access Level: all
    Return Type: UFix64
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
                "--network", "emulator",
                "--code", """
                import WalletManager from 0x01
                
                transaction() {
                    prepare(signer: AuthAccount) {
                        // Transaction logic here
                    }
                    
                    execute {
                        WalletManager.getBalance()
                    }
                }
                """,
                
            ]
        else:
            # Transaction function
            cmd = [
                "flow", "transactions", "send",
                "--network", "emulator",
                "--signer", "default",
                "--code", """
                import WalletManager from 0x01
                
                transaction() {
                    prepare(signer: AuthAccount) {
                        // Transaction logic here
                    }
                    
                    execute {
                        WalletManager.getBalance()
                    }
                }
                """,
                
            ]
        
        result = await run_flow_command(cmd)
        return json.dumps({
            "success": True,
            "result": result,
            "function": "getBalance",
            "parameters": arguments
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e),
            "function": "getBalance",
            "parameters": arguments
        }, indent=2)


@mcp.tool()
async def call_getID(arguments: dict) -> str:
    """
    Call getID function on the WalletManager contract.
    
    Access Level: all
    Return Type: UInt64
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
                "--network", "emulator",
                "--code", """
                import WalletManager from 0x01
                
                transaction() {
                    prepare(signer: AuthAccount) {
                        // Transaction logic here
                    }
                    
                    execute {
                        WalletManager.getID()
                    }
                }
                """,
                
            ]
        else:
            # Transaction function
            cmd = [
                "flow", "transactions", "send",
                "--network", "emulator",
                "--signer", "default",
                "--code", """
                import WalletManager from 0x01
                
                transaction() {
                    prepare(signer: AuthAccount) {
                        // Transaction logic here
                    }
                    
                    execute {
                        WalletManager.getID()
                    }
                }
                """,
                
            ]
        
        result = await run_flow_command(cmd)
        return json.dumps({
            "success": True,
            "result": result,
            "function": "getID",
            "parameters": arguments
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e),
            "function": "getID",
            "parameters": arguments
        }, indent=2)


@mcp.tool()
async def call_createWallet(arguments: dict) -> str:
    """
    Function to create a new wallet
    
    Access Level: all
    Return Type: UInt64
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
                "--network", "emulator",
                "--code", """
                import WalletManager from 0x01
                
                transaction() {
                    prepare(signer: AuthAccount) {
                        // Transaction logic here
                    }
                    
                    execute {
                        WalletManager.createWallet()
                    }
                }
                """,
                
            ]
        else:
            # Transaction function
            cmd = [
                "flow", "transactions", "send",
                "--network", "emulator",
                "--signer", "default",
                "--code", """
                import WalletManager from 0x01
                
                transaction() {
                    prepare(signer: AuthAccount) {
                        // Transaction logic here
                    }
                    
                    execute {
                        WalletManager.createWallet()
                    }
                }
                """,
                
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
        walletID = arguments.get("walletID")
        
        # Build Flow CLI command
        if False:
            # View function - use scripts
            cmd = [
                "flow", "scripts", "execute",
                "--network", "emulator",
                "--code", """
                import WalletManager from 0x01
                
                transaction(walletID: UInt64) {
                    prepare(signer: AuthAccount) {
                        // Transaction logic here
                    }
                    
                    execute {
                        WalletManager.getWalletCapability(walletID)
                    }
                }
                """,
                "--arg", "String:walletID"
            ]
        else:
            # Transaction function
            cmd = [
                "flow", "transactions", "send",
                "--network", "emulator",
                "--signer", "default",
                "--code", """
                import WalletManager from 0x01
                
                transaction(walletID: UInt64) {
                    prepare(signer: AuthAccount) {
                        // Transaction logic here
                    }
                    
                    execute {
                        WalletManager.getWalletCapability(walletID)
                    }
                }
                """,
                "--arg", "String:walletID"
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
async def call_updateWalletBalance(arguments: dict) -> str:
    """
    Function to update a wallet balance
    
    Access Level: all
    Return Type: Void
    View Function: No
    """
    try:
        # Extract parameters
        walletID = arguments.get("walletID")
        newBalance = arguments.get("newBalance")
        
        # Build Flow CLI command
        if False:
            # View function - use scripts
            cmd = [
                "flow", "scripts", "execute",
                "--network", "emulator",
                "--code", """
                import WalletManager from 0x01
                
                transaction(walletID: UInt64, newBalance: UFix64) {
                    prepare(signer: AuthAccount) {
                        // Transaction logic here
                    }
                    
                    execute {
                        WalletManager.updateWalletBalance(walletID, newBalance)
                    }
                }
                """,
                "--arg", "String:walletID", "--arg", "String:newBalance"
            ]
        else:
            # Transaction function
            cmd = [
                "flow", "transactions", "send",
                "--network", "emulator",
                "--signer", "default",
                "--code", """
                import WalletManager from 0x01
                
                transaction(walletID: UInt64, newBalance: UFix64) {
                    prepare(signer: AuthAccount) {
                        // Transaction logic here
                    }
                    
                    execute {
                        WalletManager.updateWalletBalance(walletID, newBalance)
                    }
                }
                """,
                "--arg", "String:walletID", "--arg", "String:newBalance"
            ]
        
        result = await run_flow_command(cmd)
        return json.dumps({
            "success": True,
            "result": result,
            "function": "updateWalletBalance",
            "parameters": arguments
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e),
            "function": "updateWalletBalance",
            "parameters": arguments
        }, indent=2)


@mcp.tool()
async def call_deleteWallet(arguments: dict) -> str:
    """
    Function to delete a wallet
    
    Access Level: all
    Return Type: Void
    View Function: No
    """
    try:
        # Extract parameters
        walletID = arguments.get("walletID")
        
        # Build Flow CLI command
        if False:
            # View function - use scripts
            cmd = [
                "flow", "scripts", "execute",
                "--network", "emulator",
                "--code", """
                import WalletManager from 0x01
                
                transaction(walletID: UInt64) {
                    prepare(signer: AuthAccount) {
                        // Transaction logic here
                    }
                    
                    execute {
                        WalletManager.deleteWallet(walletID)
                    }
                }
                """,
                "--arg", "String:walletID"
            ]
        else:
            # Transaction function
            cmd = [
                "flow", "transactions", "send",
                "--network", "emulator",
                "--signer", "default",
                "--code", """
                import WalletManager from 0x01
                
                transaction(walletID: UInt64) {
                    prepare(signer: AuthAccount) {
                        // Transaction logic here
                    }
                    
                    execute {
                        WalletManager.deleteWallet(walletID)
                    }
                }
                """,
                "--arg", "String:walletID"
            ]
        
        result = await run_flow_command(cmd)
        return json.dumps({
            "success": True,
            "result": result,
            "function": "deleteWallet",
            "parameters": arguments
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e),
            "function": "deleteWallet",
            "parameters": arguments
        }, indent=2)


@mcp.tool()
async def call_main(arguments: dict) -> str:
    """
    Example script to get a wallet balance
    
    Access Level: all
    Return Type: UFix64
    View Function: No
    """
    try:
        # Extract parameters
        account = arguments.get("account")
        walletID = arguments.get("walletID")
        
        # Build Flow CLI command
        if False:
            # View function - use scripts
            cmd = [
                "flow", "scripts", "execute",
                "--network", "emulator",
                "--code", """
                import WalletManager from 0x01
                
                transaction(account: Address, walletID: UInt64) {
                    prepare(signer: AuthAccount) {
                        // Transaction logic here
                    }
                    
                    execute {
                        WalletManager.main(account, walletID)
                    }
                }
                """,
                "--arg", "String:account", "--arg", "String:walletID"
            ]
        else:
            # Transaction function
            cmd = [
                "flow", "transactions", "send",
                "--network", "emulator",
                "--signer", "default",
                "--code", """
                import WalletManager from 0x01
                
                transaction(account: Address, walletID: UInt64) {
                    prepare(signer: AuthAccount) {
                        // Transaction logic here
                    }
                    
                    execute {
                        WalletManager.main(account, walletID)
                    }
                }
                """,
                "--arg", "String:account", "--arg", "String:walletID"
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
    Get recent events emitted by the WalletManager contract.
    
    Available events: WalletCreated, WalletUpdated, WalletDeleted
    """
    try:
        limit = arguments.get("limit", 10)
        event_type = arguments.get("event_type", "all")
        
        cmd = [
            "flow", "events", "get",
            "--network", "emulator",
            "--start", "latest",
            "--end", "latest",
            f"WalletManager.*"
        ]
        
        result = await run_flow_command(cmd)
        
        return json.dumps({
            "success": True,
            "events": result,
            "contract": "WalletManager",
            "limit": limit,
            "event_type": event_type
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e),
            "contract": "WalletManager"
        }, indent=2)


@mcp.resource(f"flow://contract/{CONTRACT_ADDRESS}/{CONTRACT_NAME}")
async def get_contract_resource() -> str:
    """Get contract resource information."""
    return f"WalletManager contract at {CONTRACT_ADDRESS}"


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
    """Generate a prompt for analyzing the WalletManager contract."""
    contract_path = Path(PROJECT_PATH) / "contracts" / f"{CONTRACT_NAME}.cdc"
    
    if contract_path.exists():
        code = contract_path.read_text()
        return f"""
Please analyze the following WalletManager smart contract for {analysis_type}:

Contract Name: WalletManager
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