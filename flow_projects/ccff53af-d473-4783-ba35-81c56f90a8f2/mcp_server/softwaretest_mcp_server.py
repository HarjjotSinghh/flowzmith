"""
SoftwareTest MCP Server - A Model Context Protocol server for SoftwareTest smart contract interactions.

This server provides tools for interacting with the SoftwareTest smart contract on Flow blockchain.
Generated automatically from contract analysis.

Contract Address: 0x01
Network: testnet
Generated: 2025-09-27T13:03:54.834136
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
mcp = FastMCP("SoftwareTest MCP Server")

# Contract configuration
CONTRACT_NAME = "SoftwareTest"
CONTRACT_ADDRESS = "0x01"
DEFAULT_NETWORK = "testnet"
PROJECT_PATH = "{{PROJECT_PATH}}"


class UpdatetestnameParams(BaseModel):
    """Parameters for updateTestName function."""
    newName: str


class UpdateteststatusParams(BaseModel):
    """Parameters for updateTestStatus function."""
    newStatus: bool


class AddtestParams(BaseModel):
    """Parameters for addTest function."""
    test: Any


class RemovetestParams(BaseModel):
    """Parameters for removeTest function."""
    testID: int


class GettestParams(BaseModel):
    """Parameters for getTest function."""
    testID: int


class MainParams(BaseModel):
    """Parameters for main function."""
    testID: int
    address: str


class TestCreatedEvent(BaseModel):
    """Event data for TestCreated."""
    testID: int
    testName: str


class TestUpdatedEvent(BaseModel):
    """Event data for TestUpdated."""
    testID: int
    testName: str


class TestDeletedEvent(BaseModel):
    """Event data for TestDeleted."""
    testID: int


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
    """Get information about the SoftwareTest contract."""
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
    "name": "updateTestName",
    "parameters": [
      {
        "name": "newName",
        "type": "String"
      }
    ],
    "return_type": null,
    "documentation": "Call updateTestName function on the contract.",
    "is_view": false
  },
  {
    "name": "updateTestStatus",
    "parameters": [
      {
        "name": "newStatus",
        "type": "Bool"
      }
    ],
    "return_type": null,
    "documentation": "Call updateTestStatus function on the contract.",
    "is_view": false
  },
  {
    "name": "addTest",
    "parameters": [
      {
        "name": "test",
        "type": "Test"
      }
    ],
    "return_type": null,
    "documentation": "Function to add a new test",
    "is_view": false
  },
  {
    "name": "removeTest",
    "parameters": [
      {
        "name": "testID",
        "type": "UInt64"
      }
    ],
    "return_type": "Test?",
    "documentation": "Function to remove a test",
    "is_view": false
  },
  {
    "name": "getTest",
    "parameters": [
      {
        "name": "testID",
        "type": "UInt64"
      }
    ],
    "return_type": "&Test?",
    "documentation": "Function to get a test",
    "is_view": false
  },
  {
    "name": "createTestCollection",
    "parameters": [],
    "return_type": "@TestCollection",
    "documentation": "Function to create a new test collection",
    "is_view": false
  },
  {
    "name": "main",
    "parameters": [
      {
        "name": "testID",
        "type": "UInt64"
      },
      {
        "name": "address",
        "type": "Address"
      }
    ],
    "return_type": "String?",
    "documentation": "Example transaction to create a new test collection\ntransaction {\nprepare(signer: AuthAccount) {\nlet collection <- SoftwareTest.createTestCollection()\nsigner.save(<-collection, to: /storage/TestCollection)\nlet cap = signer.link<&SoftwareTest.TestCollection>(/public/TestCollection, target: /storage/TestCollection)\nlog(cap)\n}\n}\nExample transaction to add a new test\ntransaction(testName: String) {\nprepare(signer: AuthAccount) {\nlet collectionRef = signer.borrow<&SoftwareTest.TestCollection>(from: /storage/TestCollection)\n?? panic(\"Could not borrow reference to TestCollection\")\nlet test <- create SoftwareTest.Test(testID: 1, testName: testName)\ncollectionRef.addTest(test: <-test)\n}\n}\nExample script to get a test",
    "is_view": false
  }
],
                "events": [
  {
    "name": "TestCreated",
    "parameters": [
      {
        "name": "testID",
        "type": "UInt64"
      },
      {
        "name": "testName",
        "type": "String"
      }
    ],
    "documentation": "Define events"
  },
  {
    "name": "TestUpdated",
    "parameters": [
      {
        "name": "testID",
        "type": "UInt64"
      },
      {
        "name": "testName",
        "type": "String"
      }
    ],
    "documentation": "TestUpdated event from the contract."
  },
  {
    "name": "TestDeleted",
    "parameters": [
      {
        "name": "testID",
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
    """Get the source code of the SoftwareTest contract."""
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
async def call_updateTestName(arguments: dict) -> str:
    """
    Call updateTestName function on the SoftwareTest contract.
    
    Access Level: all
    Return Type: Void
    View Function: No
    """
    try:
        # Extract parameters
        newName = arguments.get("newName")
        
        # Build Flow CLI command
        if False:
            # View function - use scripts
            cmd = [
                "flow", "scripts", "execute",
                "--network", "testnet",
                "--code", """
                import SoftwareTest from 0x01
                
                transaction(newName: String) {
                    prepare(signer: AuthAccount) {
                        // Transaction logic here
                    }
                    
                    execute {
                        SoftwareTest.updateTestName(newName)
                    }
                }
                """,
                "--arg", "String:newName"
            ]
        else:
            # Transaction function
            cmd = [
                "flow", "transactions", "send",
                "--network", "testnet",
                "--signer", "default",
                "--code", """
                import SoftwareTest from 0x01
                
                transaction(newName: String) {
                    prepare(signer: AuthAccount) {
                        // Transaction logic here
                    }
                    
                    execute {
                        SoftwareTest.updateTestName(newName)
                    }
                }
                """,
                "--arg", "String:newName"
            ]
        
        result = await run_flow_command(cmd)
        return json.dumps({
            "success": True,
            "result": result,
            "function": "updateTestName",
            "parameters": arguments
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e),
            "function": "updateTestName",
            "parameters": arguments
        }, indent=2)


@mcp.tool()
async def call_updateTestStatus(arguments: dict) -> str:
    """
    Call updateTestStatus function on the SoftwareTest contract.
    
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
                import SoftwareTest from 0x01
                
                transaction(newStatus: Bool) {
                    prepare(signer: AuthAccount) {
                        // Transaction logic here
                    }
                    
                    execute {
                        SoftwareTest.updateTestStatus(newStatus)
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
                import SoftwareTest from 0x01
                
                transaction(newStatus: Bool) {
                    prepare(signer: AuthAccount) {
                        // Transaction logic here
                    }
                    
                    execute {
                        SoftwareTest.updateTestStatus(newStatus)
                    }
                }
                """,
                "--arg", "String:newStatus"
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
async def call_addTest(arguments: dict) -> str:
    """
    Function to add a new test
    
    Access Level: all
    Return Type: Void
    View Function: No
    """
    try:
        # Extract parameters
        test = arguments.get("test")
        
        # Build Flow CLI command
        if False:
            # View function - use scripts
            cmd = [
                "flow", "scripts", "execute",
                "--network", "testnet",
                "--code", """
                import SoftwareTest from 0x01
                
                transaction(test: Test) {
                    prepare(signer: AuthAccount) {
                        // Transaction logic here
                    }
                    
                    execute {
                        SoftwareTest.addTest(test)
                    }
                }
                """,
                "--arg", "String:test"
            ]
        else:
            # Transaction function
            cmd = [
                "flow", "transactions", "send",
                "--network", "testnet",
                "--signer", "default",
                "--code", """
                import SoftwareTest from 0x01
                
                transaction(test: Test) {
                    prepare(signer: AuthAccount) {
                        // Transaction logic here
                    }
                    
                    execute {
                        SoftwareTest.addTest(test)
                    }
                }
                """,
                "--arg", "String:test"
            ]
        
        result = await run_flow_command(cmd)
        return json.dumps({
            "success": True,
            "result": result,
            "function": "addTest",
            "parameters": arguments
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e),
            "function": "addTest",
            "parameters": arguments
        }, indent=2)


@mcp.tool()
async def call_removeTest(arguments: dict) -> str:
    """
    Function to remove a test
    
    Access Level: all
    Return Type: Test?
    View Function: No
    """
    try:
        # Extract parameters
        testID = arguments.get("testID")
        
        # Build Flow CLI command
        if False:
            # View function - use scripts
            cmd = [
                "flow", "scripts", "execute",
                "--network", "testnet",
                "--code", """
                import SoftwareTest from 0x01
                
                transaction(testID: UInt64) {
                    prepare(signer: AuthAccount) {
                        // Transaction logic here
                    }
                    
                    execute {
                        SoftwareTest.removeTest(testID)
                    }
                }
                """,
                "--arg", "String:testID"
            ]
        else:
            # Transaction function
            cmd = [
                "flow", "transactions", "send",
                "--network", "testnet",
                "--signer", "default",
                "--code", """
                import SoftwareTest from 0x01
                
                transaction(testID: UInt64) {
                    prepare(signer: AuthAccount) {
                        // Transaction logic here
                    }
                    
                    execute {
                        SoftwareTest.removeTest(testID)
                    }
                }
                """,
                "--arg", "String:testID"
            ]
        
        result = await run_flow_command(cmd)
        return json.dumps({
            "success": True,
            "result": result,
            "function": "removeTest",
            "parameters": arguments
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e),
            "function": "removeTest",
            "parameters": arguments
        }, indent=2)


@mcp.tool()
async def call_getTest(arguments: dict) -> str:
    """
    Function to get a test
    
    Access Level: all
    Return Type: &Test?
    View Function: No
    """
    try:
        # Extract parameters
        testID = arguments.get("testID")
        
        # Build Flow CLI command
        if False:
            # View function - use scripts
            cmd = [
                "flow", "scripts", "execute",
                "--network", "testnet",
                "--code", """
                import SoftwareTest from 0x01
                
                transaction(testID: UInt64) {
                    prepare(signer: AuthAccount) {
                        // Transaction logic here
                    }
                    
                    execute {
                        SoftwareTest.getTest(testID)
                    }
                }
                """,
                "--arg", "String:testID"
            ]
        else:
            # Transaction function
            cmd = [
                "flow", "transactions", "send",
                "--network", "testnet",
                "--signer", "default",
                "--code", """
                import SoftwareTest from 0x01
                
                transaction(testID: UInt64) {
                    prepare(signer: AuthAccount) {
                        // Transaction logic here
                    }
                    
                    execute {
                        SoftwareTest.getTest(testID)
                    }
                }
                """,
                "--arg", "String:testID"
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
async def call_createTestCollection(arguments: dict) -> str:
    """
    Function to create a new test collection
    
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
                import SoftwareTest from 0x01
                
                transaction() {
                    prepare(signer: AuthAccount) {
                        // Transaction logic here
                    }
                    
                    execute {
                        SoftwareTest.createTestCollection()
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
                import SoftwareTest from 0x01
                
                transaction() {
                    prepare(signer: AuthAccount) {
                        // Transaction logic here
                    }
                    
                    execute {
                        SoftwareTest.createTestCollection()
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
    Example transaction to create a new test collection
transaction {
prepare(signer: AuthAccount) {
let collection <- SoftwareTest.createTestCollection()
signer.save(<-collection, to: /storage/TestCollection)
let cap = signer.link<&SoftwareTest.TestCollection>(/public/TestCollection, target: /storage/TestCollection)
log(cap)
}
}
Example transaction to add a new test
transaction(testName: String) {
prepare(signer: AuthAccount) {
let collectionRef = signer.borrow<&SoftwareTest.TestCollection>(from: /storage/TestCollection)
?? panic("Could not borrow reference to TestCollection")
let test <- create SoftwareTest.Test(testID: 1, testName: testName)
collectionRef.addTest(test: <-test)
}
}
Example script to get a test
    
    Access Level: all
    Return Type: String?
    View Function: No
    """
    try:
        # Extract parameters
        testID = arguments.get("testID")
        address = arguments.get("address")
        
        # Build Flow CLI command
        if False:
            # View function - use scripts
            cmd = [
                "flow", "scripts", "execute",
                "--network", "testnet",
                "--code", """
                import SoftwareTest from 0x01
                
                transaction(testID: UInt64, address: Address) {
                    prepare(signer: AuthAccount) {
                        // Transaction logic here
                    }
                    
                    execute {
                        SoftwareTest.main(testID, address)
                    }
                }
                """,
                "--arg", "String:testID", "--arg", "String:address"
            ]
        else:
            # Transaction function
            cmd = [
                "flow", "transactions", "send",
                "--network", "testnet",
                "--signer", "default",
                "--code", """
                import SoftwareTest from 0x01
                
                transaction(testID: UInt64, address: Address) {
                    prepare(signer: AuthAccount) {
                        // Transaction logic here
                    }
                    
                    execute {
                        SoftwareTest.main(testID, address)
                    }
                }
                """,
                "--arg", "String:testID", "--arg", "String:address"
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
    Get recent events emitted by the SoftwareTest contract.
    
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
            f"SoftwareTest.*"
        ]
        
        result = await run_flow_command(cmd)
        
        return json.dumps({
            "success": True,
            "events": result,
            "contract": "SoftwareTest",
            "limit": limit,
            "event_type": event_type
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e),
            "contract": "SoftwareTest"
        }, indent=2)


@mcp.resource(f"flow://contract/{CONTRACT_ADDRESS}/{CONTRACT_NAME}")
async def get_contract_resource() -> str:
    """Get contract resource information."""
    return f"SoftwareTest contract at {CONTRACT_ADDRESS}"


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
    """Generate a prompt for analyzing the SoftwareTest contract."""
    contract_path = Path(PROJECT_PATH) / "contracts" / f"{CONTRACT_NAME}.cdc"
    
    if contract_path.exists():
        code = contract_path.read_text()
        return f"""
Please analyze the following SoftwareTest smart contract for {analysis_type}:

Contract Name: SoftwareTest
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