"""
NewTest MCP Server - A Model Context Protocol server for NewTest smart contract interactions.

This server provides tools for interacting with the NewTest smart contract on Flow blockchain.
Generated automatically from contract analysis.

Contract Address: 0x01
Network: testnet
Generated: 2025-09-27T12:54:08.239986
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
mcp = FastMCP("NewTest MCP Server")

# Contract configuration
CONTRACT_NAME = "NewTest"
CONTRACT_ADDRESS = "0x01"
DEFAULT_NETWORK = "testnet"
PROJECT_PATH = "{{PROJECT_PATH}}"


class UpdatestatusParams(BaseModel):
    """Parameters for updateStatus function."""
    newStatus: str


class UpdatedescriptionParams(BaseModel):
    """Parameters for updateDescription function."""
    newDescription: str


class GettestParams(BaseModel):
    """Parameters for getTest function."""
    id: int


class CreatetestParams(BaseModel):
    """Parameters for createTest function."""
    description: str


class UpdateteststatusParams(BaseModel):
    """Parameters for updateTestStatus function."""
    id: int
    newStatus: str


class DeletetestParams(BaseModel):
    """Parameters for deleteTest function."""
    id: int


class MainParams(BaseModel):
    """Parameters for main function."""
    account: str


class TestCreatedEvent(BaseModel):
    """Event data for TestCreated."""
    testId: int


class TestUpdatedEvent(BaseModel):
    """Event data for TestUpdated."""
    testId: int
    newStatus: str


class TestDeletedEvent(BaseModel):
    """Event data for TestDeleted."""
    testId: int


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
    """Get information about the NewTest contract."""
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
    "name": "updateStatus",
    "parameters": [
      {
        "name": "newStatus",
        "type": "String"
      }
    ],
    "return_type": null,
    "documentation": "Call updateStatus function on the contract.",
    "is_view": false
  },
  {
    "name": "updateDescription",
    "parameters": [
      {
        "name": "newDescription",
        "type": "String"
      }
    ],
    "return_type": null,
    "documentation": "Call updateDescription function on the contract.",
    "is_view": false
  },
  {
    "name": "getTest",
    "parameters": [
      {
        "name": "id",
        "type": "UInt64"
      }
    ],
    "return_type": "Test?",
    "documentation": "Call getTest function on the contract.",
    "is_view": false
  },
  {
    "name": "createTest",
    "parameters": [
      {
        "name": "description",
        "type": "String"
      }
    ],
    "return_type": null,
    "documentation": "Call createTest function on the contract.",
    "is_view": false
  },
  {
    "name": "updateTestStatus",
    "parameters": [
      {
        "name": "id",
        "type": "UInt64"
      },
      {
        "name": "newStatus",
        "type": "String"
      }
    ],
    "return_type": null,
    "documentation": "Call updateTestStatus function on the contract.",
    "is_view": false
  },
  {
    "name": "deleteTest",
    "parameters": [
      {
        "name": "id",
        "type": "UInt64"
      }
    ],
    "return_type": null,
    "documentation": "Call deleteTest function on the contract.",
    "is_view": false
  },
  {
    "name": "createTestCollection",
    "parameters": [],
    "return_type": "@TestCollection",
    "documentation": "Public functions",
    "is_view": false
  },
  {
    "name": "main",
    "parameters": [
      {
        "name": "account",
        "type": "Address"
      }
    ],
    "return_type": "String?",
    "documentation": "Example transaction to create a new TestCollection\n\ntransaction {\nprepare(signer: auth(Storage) &Account) {\nlet collection <- NewTest.createTestCollection()\nsigner.save(<-collection, to: /storage/TestCollection)\n}\n}\nExample transaction to create a new Test\n\ntransaction {\nprepare(signer: auth(Storage) &Account) {\nlet collection = signer.borrow<&NewTest.TestCollection>(from: /storage/TestCollection)\n?? panic(\"Could not borrow reference to TestCollection\")\ncollection.createTest(description: \"New Test Description\")\n}\n}\nExample script to read a Test\n",
    "is_view": false
  }
],
                "events": [
  {
    "name": "TestCreated",
    "parameters": [
      {
        "name": "testId",
        "type": "UInt64"
      }
    ],
    "documentation": "Events"
  },
  {
    "name": "TestUpdated",
    "parameters": [
      {
        "name": "testId",
        "type": "UInt64"
      },
      {
        "name": "newStatus",
        "type": "String"
      }
    ],
    "documentation": "TestUpdated event from the contract."
  },
  {
    "name": "TestDeleted",
    "parameters": [
      {
        "name": "testId",
        "type": "UInt64"
      }
    ],
    "documentation": "TestDeleted event from the contract."
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
    """Get the source code of the NewTest contract."""
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
async def call_updateStatus(arguments: dict) -> str:
    """
    Call updateStatus function on the NewTest contract.
    
    Access Level: all
    Return Type: Void
    View Function: No
    """
    try:
        # Extract parameters
        newStatus = arguments.get("newStatus")
        
        # Build Flow CLI command
        if False:
            # View function - use scripts
            cmd = [
                "flow", "scripts", "execute",
                "--network", "testnet",
                "--code", """
                import NewTest from 0x01
                
                transaction(newStatus: String) {
                    prepare(signer: AuthAccount) {
                        // Transaction logic here
                    }
                    
                    execute {
                        NewTest.updateStatus(newStatus)
                    }
                }
                """,
                "--arg", "String:newStatus"
            ]
        else:
            # Transaction function
            cmd = [
                "flow", "transactions", "send",
                "--network", "testnet",
                "--signer", "default",
                "--code", """
                import NewTest from 0x01
                
                transaction(newStatus: String) {
                    prepare(signer: AuthAccount) {
                        // Transaction logic here
                    }
                    
                    execute {
                        NewTest.updateStatus(newStatus)
                    }
                }
                """,
                "--arg", "String:newStatus"
            ]
        
        result = await run_flow_command(cmd)
        return json.dumps({
            "success": True,
            "result": result,
            "function": "updateStatus",
            "parameters": arguments
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e),
            "function": "updateStatus",
            "parameters": arguments
        }, indent=2)


@mcp.tool()
async def call_updateDescription(arguments: dict) -> str:
    """
    Call updateDescription function on the NewTest contract.
    
    Access Level: all
    Return Type: Void
    View Function: No
    """
    try:
        # Extract parameters
        newDescription = arguments.get("newDescription")
        
        # Build Flow CLI command
        if False:
            # View function - use scripts
            cmd = [
                "flow", "scripts", "execute",
                "--network", "testnet",
                "--code", """
                import NewTest from 0x01
                
                transaction(newDescription: String) {
                    prepare(signer: AuthAccount) {
                        // Transaction logic here
                    }
                    
                    execute {
                        NewTest.updateDescription(newDescription)
                    }
                }
                """,
                "--arg", "String:newDescription"
            ]
        else:
            # Transaction function
            cmd = [
                "flow", "transactions", "send",
                "--network", "testnet",
                "--signer", "default",
                "--code", """
                import NewTest from 0x01
                
                transaction(newDescription: String) {
                    prepare(signer: AuthAccount) {
                        // Transaction logic here
                    }
                    
                    execute {
                        NewTest.updateDescription(newDescription)
                    }
                }
                """,
                "--arg", "String:newDescription"
            ]
        
        result = await run_flow_command(cmd)
        return json.dumps({
            "success": True,
            "result": result,
            "function": "updateDescription",
            "parameters": arguments
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e),
            "function": "updateDescription",
            "parameters": arguments
        }, indent=2)


@mcp.tool()
async def call_getTest(arguments: dict) -> str:
    """
    Call getTest function on the NewTest contract.
    
    Access Level: all
    Return Type: Test?
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
                import NewTest from 0x01
                
                transaction(id: UInt64) {
                    prepare(signer: AuthAccount) {
                        // Transaction logic here
                    }
                    
                    execute {
                        NewTest.getTest(id)
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
                import NewTest from 0x01
                
                transaction(id: UInt64) {
                    prepare(signer: AuthAccount) {
                        // Transaction logic here
                    }
                    
                    execute {
                        NewTest.getTest(id)
                    }
                }
                """,
                "--arg", "String:id"
            ]
        
        result = await run_flow_command(cmd)
        return json.dumps({
            "success": True,
            "result": result,
            "function": "getTest",
            "parameters": arguments
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e),
            "function": "getTest",
            "parameters": arguments
        }, indent=2)


@mcp.tool()
async def call_createTest(arguments: dict) -> str:
    """
    Call createTest function on the NewTest contract.
    
    Access Level: all
    Return Type: Void
    View Function: No
    """
    try:
        # Extract parameters
        description = arguments.get("description")
        
        # Build Flow CLI command
        if False:
            # View function - use scripts
            cmd = [
                "flow", "scripts", "execute",
                "--network", "testnet",
                "--code", """
                import NewTest from 0x01
                
                transaction(description: String) {
                    prepare(signer: AuthAccount) {
                        // Transaction logic here
                    }
                    
                    execute {
                        NewTest.createTest(description)
                    }
                }
                """,
                "--arg", "String:description"
            ]
        else:
            # Transaction function
            cmd = [
                "flow", "transactions", "send",
                "--network", "testnet",
                "--signer", "default",
                "--code", """
                import NewTest from 0x01
                
                transaction(description: String) {
                    prepare(signer: AuthAccount) {
                        // Transaction logic here
                    }
                    
                    execute {
                        NewTest.createTest(description)
                    }
                }
                """,
                "--arg", "String:description"
            ]
        
        result = await run_flow_command(cmd)
        return json.dumps({
            "success": True,
            "result": result,
            "function": "createTest",
            "parameters": arguments
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e),
            "function": "createTest",
            "parameters": arguments
        }, indent=2)


@mcp.tool()
async def call_updateTestStatus(arguments: dict) -> str:
    """
    Call updateTestStatus function on the NewTest contract.
    
    Access Level: all
    Return Type: Void
    View Function: No
    """
    try:
        # Extract parameters
        id = arguments.get("id")
        newStatus = arguments.get("newStatus")
        
        # Build Flow CLI command
        if False:
            # View function - use scripts
            cmd = [
                "flow", "scripts", "execute",
                "--network", "testnet",
                "--code", """
                import NewTest from 0x01
                
                transaction(id: UInt64, newStatus: String) {
                    prepare(signer: AuthAccount) {
                        // Transaction logic here
                    }
                    
                    execute {
                        NewTest.updateTestStatus(id, newStatus)
                    }
                }
                """,
                "--arg", "String:id", "--arg", "String:newStatus"
            ]
        else:
            # Transaction function
            cmd = [
                "flow", "transactions", "send",
                "--network", "testnet",
                "--signer", "default",
                "--code", """
                import NewTest from 0x01
                
                transaction(id: UInt64, newStatus: String) {
                    prepare(signer: AuthAccount) {
                        // Transaction logic here
                    }
                    
                    execute {
                        NewTest.updateTestStatus(id, newStatus)
                    }
                }
                """,
                "--arg", "String:id", "--arg", "String:newStatus"
            ]
        
        result = await run_flow_command(cmd)
        return json.dumps({
            "success": True,
            "result": result,
            "function": "updateTestStatus",
            "parameters": arguments
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e),
            "function": "updateTestStatus",
            "parameters": arguments
        }, indent=2)


@mcp.tool()
async def call_deleteTest(arguments: dict) -> str:
    """
    Call deleteTest function on the NewTest contract.
    
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
                import NewTest from 0x01
                
                transaction(id: UInt64) {
                    prepare(signer: AuthAccount) {
                        // Transaction logic here
                    }
                    
                    execute {
                        NewTest.deleteTest(id)
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
                import NewTest from 0x01
                
                transaction(id: UInt64) {
                    prepare(signer: AuthAccount) {
                        // Transaction logic here
                    }
                    
                    execute {
                        NewTest.deleteTest(id)
                    }
                }
                """,
                "--arg", "String:id"
            ]
        
        result = await run_flow_command(cmd)
        return json.dumps({
            "success": True,
            "result": result,
            "function": "deleteTest",
            "parameters": arguments
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e),
            "function": "deleteTest",
            "parameters": arguments
        }, indent=2)


@mcp.tool()
async def call_createTestCollection(arguments: dict) -> str:
    """
    Public functions
    
    Access Level: all
    Return Type: @TestCollection
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
                import NewTest from 0x01
                
                transaction() {
                    prepare(signer: AuthAccount) {
                        // Transaction logic here
                    }
                    
                    execute {
                        NewTest.createTestCollection()
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
                import NewTest from 0x01
                
                transaction() {
                    prepare(signer: AuthAccount) {
                        // Transaction logic here
                    }
                    
                    execute {
                        NewTest.createTestCollection()
                    }
                }
                """,
                
            ]
        
        result = await run_flow_command(cmd)
        return json.dumps({
            "success": True,
            "result": result,
            "function": "createTestCollection",
            "parameters": arguments
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e),
            "function": "createTestCollection",
            "parameters": arguments
        }, indent=2)


@mcp.tool()
async def call_main(arguments: dict) -> str:
    """
    Example transaction to create a new TestCollection

transaction {
prepare(signer: auth(Storage) &Account) {
let collection <- NewTest.createTestCollection()
signer.save(<-collection, to: /storage/TestCollection)
}
}
Example transaction to create a new Test

transaction {
prepare(signer: auth(Storage) &Account) {
let collection = signer.borrow<&NewTest.TestCollection>(from: /storage/TestCollection)
?? panic("Could not borrow reference to TestCollection")
collection.createTest(description: "New Test Description")
}
}
Example script to read a Test

    
    Access Level: all
    Return Type: String?
    View Function: No
    """
    try:
        # Extract parameters
        account = arguments.get("account")
        
        # Build Flow CLI command
        if False:
            # View function - use scripts
            cmd = [
                "flow", "scripts", "execute",
                "--network", "testnet",
                "--code", """
                import NewTest from 0x01
                
                transaction(account: Address) {
                    prepare(signer: AuthAccount) {
                        // Transaction logic here
                    }
                    
                    execute {
                        NewTest.main(account)
                    }
                }
                """,
                "--arg", "String:account"
            ]
        else:
            # Transaction function
            cmd = [
                "flow", "transactions", "send",
                "--network", "testnet",
                "--signer", "default",
                "--code", """
                import NewTest from 0x01
                
                transaction(account: Address) {
                    prepare(signer: AuthAccount) {
                        // Transaction logic here
                    }
                    
                    execute {
                        NewTest.main(account)
                    }
                }
                """,
                "--arg", "String:account"
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
    Get recent events emitted by the NewTest contract.
    
    Available events: TestCreated, TestUpdated, TestDeleted
    """
    try:
        limit = arguments.get("limit", 10)
        event_type = arguments.get("event_type", "all")
        
        cmd = [
            "flow", "events", "get",
            "--network", "testnet",
            "--start", "latest",
            "--end", "latest",
            f"NewTest.*"
        ]
        
        result = await run_flow_command(cmd)
        
        return json.dumps({
            "success": True,
            "events": result,
            "contract": "NewTest",
            "limit": limit,
            "event_type": event_type
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e),
            "contract": "NewTest"
        }, indent=2)


@mcp.resource(f"flow://contract/{CONTRACT_ADDRESS}/{CONTRACT_NAME}")
async def get_contract_resource() -> str:
    """Get contract resource information."""
    return f"NewTest contract at {CONTRACT_ADDRESS}"


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
    """Generate a prompt for analyzing the NewTest contract."""
    contract_path = Path(PROJECT_PATH) / "contracts" / f"{CONTRACT_NAME}.cdc"
    
    if contract_path.exists():
        code = contract_path.read_text()
        return f"""
Please analyze the following NewTest smart contract for {analysis_type}:

Contract Name: NewTest
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