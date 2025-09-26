"""
SimpleNFT MCP Server - A Model Context Protocol server for SimpleNFT smart contract interactions.

This server provides tools for interacting with the SimpleNFT smart contract on Flow blockchain.
Generated automatically from contract analysis.

Contract Address: 0x1234567890abcdef
Network: testnet
Generated: 2025-09-27T04:51:25.000110
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
mcp = FastMCP("SimpleNFT MCP Server")

# Contract configuration
CONTRACT_NAME = "SimpleNFT"
CONTRACT_ADDRESS = "0x1234567890abcdef"
DEFAULT_NETWORK = "testnet"
PROJECT_PATH = "{{PROJECT_PATH}}"


class ResolveviewParams(BaseModel):
    """Parameters for resolveView function."""
    view: Any  # Label: _


class WithdrawParams(BaseModel):
    """Parameters for withdraw function."""
    withdrawID: int


class DepositParams(BaseModel):
    """Parameters for deposit function."""
    token: Any


class BorrownftParams(BaseModel):
    """Parameters for borrowNFT function."""
    id: int


class BorrowsimplenftParams(BaseModel):
    """Parameters for borrowSimpleNFT function."""
    id: int


class BorrowviewresolverParams(BaseModel):
    """Parameters for borrowViewResolver function."""
    id: int


class MintnftParams(BaseModel):
    """Parameters for mintNFT function."""
    recipient: Any
    metadata: Any


class WithdrawEvent(BaseModel):
    """Event data for Withdraw."""
    id: int
    from: Optional[str]


class DepositEvent(BaseModel):
    """Event data for Deposit."""
    id: int
    to: Optional[str]


class MintedEvent(BaseModel):
    """Event data for Minted."""
    id: int
    recipient: str
    metadata: Any


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
    """Get information about the SimpleNFT contract."""
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
                "functions": 
# getViews function
async def getViews():
    """
    / Function that returns all the Metadata Views implemented by a Non Fungible Token
    """
    # Implementation will be generated in tools
    pass


# resolveView function
async def resolveView(view):
    """
    / Function that resolves a metadata view for this token
    """
    # Implementation will be generated in tools
    pass


# getIDs function
async def getIDs():
    """
    Call getIDs function on the contract.
    """
    # Implementation will be generated in tools
    pass


# withdraw function
async def withdraw(withdrawID):
    """
    / Removes an NFT from the collection and moves it to the caller
    """
    # Implementation will be generated in tools
    pass


# deposit function
async def deposit(token):
    """
    / Adds an NFT to the collections dictionary and adds the ID to the id array
    """
    # Implementation will be generated in tools
    pass


# borrowNFT function
async def borrowNFT(id):
    """
    / Gets a reference to an NFT in the collection so that
/ the caller can read its metadata and call its methods
    """
    # Implementation will be generated in tools
    pass


# borrowSimpleNFT function
async def borrowSimpleNFT(id):
    """
    / Gets a reference to an NFT in the collection as a SimpleNFT,
/ This is safe as there are no functions that can be called on the SimpleNFT
    """
    # Implementation will be generated in tools
    pass


# borrowViewResolver function
async def borrowViewResolver(id):
    """
    / Gets a reference to the NFT only conforming to the `{MetadataViews.Resolver}`
/ interface so that the caller can retrieve the views that the NFT
/ is implementing and resolve them
    """
    # Implementation will be generated in tools
    pass


# createEmptyCollection function
async def createEmptyCollection():
    """
    / Allows anyone to create a new empty collection
    """
    # Implementation will be generated in tools
    pass


# mintNFT function
async def mintNFT(recipient, metadata):
    """
    / Mints a new NFT with a new ID and deposit it in the
/ recipients collection using their collection reference
    """
    # Implementation will be generated in tools
    pass


# getTotalSupply function
async def getTotalSupply():
    """
    / Get the total supply of NFTs
    """
    # Implementation will be generated in tools
    pass


# getContractInfo function
async def getContractInfo():
    """
    / Get contract information
    """
    # Implementation will be generated in tools
    pass
,
                "events": 
# ContractInitialized event
EVENT_CONTRACTINITIALIZED = "ContractInitialized"


# Withdraw event
EVENT_WITHDRAW = "Withdraw"


# Deposit event
EVENT_DEPOSIT = "Deposit"


# Minted event
EVENT_MINTED = "Minted"

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
    """Get the source code of the SimpleNFT contract."""
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
async def call_getViews(arguments: dict) -> str:
    """
    / Function that returns all the Metadata Views implemented by a Non Fungible Token
    
    Access Level: all
    Return Type: [Type]
    View Function: Yes
    """
    try:
        # Extract parameters
        # No parameters
        
        # Build Flow CLI command
        if true:
            # View function - use scripts
            cmd = [
                "flow", "scripts", "execute",
                "--network", "testnet",
                "--code", f"""
                import SimpleNFT from 0x1234567890abcdef
                
                access(all) fun main(): [Type] {
                    return SimpleNFT.getViews()
                }
                """,
                
            ]
        else:
            # Transaction function
            cmd = [
                "flow", "transactions", "send",
                "--network", "testnet",
                "--signer", "default",
                "--code", f"""
                import SimpleNFT from 0x1234567890abcdef
                
                transaction() {
                    prepare(signer: AuthAccount) {
                        // Transaction logic here
                    }
                    
                    execute {
                        SimpleNFT.getViews()
                    }
                }
                """,
                
            ]
        
        result = await run_flow_command(cmd)
        return json.dumps({
            "success": True,
            "result": result,
            "function": "getViews",
            "parameters": arguments
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e),
            "function": "getViews",
            "parameters": arguments
        }, indent=2)


@mcp.tool()
async def call_resolveView(arguments: dict) -> str:
    """
    / Function that resolves a metadata view for this token
    
    Access Level: all
    Return Type: AnyStruct?
    View Function: No
    """
    try:
        # Extract parameters
                view = arguments.get("view")
        
        # Build Flow CLI command
        if false:
            # View function - use scripts
            cmd = [
                "flow", "scripts", "execute",
                "--network", "testnet",
                "--code", f"""
                import SimpleNFT from 0x1234567890abcdef
                
                access(all) fun main(view: Type): AnyStruct? {
                    return SimpleNFT.resolveView(view)
                }
                """,
                "--arg", "String:view"
            ]
        else:
            # Transaction function
            cmd = [
                "flow", "transactions", "send",
                "--network", "testnet",
                "--signer", "default",
                "--code", f"""
                import SimpleNFT from 0x1234567890abcdef
                
                transaction(view: Type) {
                    prepare(signer: AuthAccount) {
                        // Transaction logic here
                    }
                    
                    execute {
                        SimpleNFT.resolveView(view)
                    }
                }
                """,
                "--arg", "String:view"
            ]
        
        result = await run_flow_command(cmd)
        return json.dumps({
            "success": True,
            "result": result,
            "function": "resolveView",
            "parameters": arguments
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e),
            "function": "resolveView",
            "parameters": arguments
        }, indent=2)


@mcp.tool()
async def call_getIDs(arguments: dict) -> str:
    """
    Call getIDs function on the SimpleNFT contract.
    
    Access Level: all
    Return Type: [UInt64]
        pub fun borrowNFT(id: UInt64): &NonFungibleToken.NFT
        pub fun borrowSimpleNFT(id: UInt64): &SimpleNFT.NFT?
    View Function: Yes
    """
    try:
        # Extract parameters
        # No parameters
        
        # Build Flow CLI command
        if true:
            # View function - use scripts
            cmd = [
                "flow", "scripts", "execute",
                "--network", "testnet",
                "--code", f"""
                import SimpleNFT from 0x1234567890abcdef
                
                access(all) fun main(): [UInt64]
        pub fun borrowNFT(id: UInt64): &NonFungibleToken.NFT
        pub fun borrowSimpleNFT(id: UInt64): &SimpleNFT.NFT? {
                    return SimpleNFT.getIDs()
                }
                """,
                
            ]
        else:
            # Transaction function
            cmd = [
                "flow", "transactions", "send",
                "--network", "testnet",
                "--signer", "default",
                "--code", f"""
                import SimpleNFT from 0x1234567890abcdef
                
                transaction() {
                    prepare(signer: AuthAccount) {
                        // Transaction logic here
                    }
                    
                    execute {
                        SimpleNFT.getIDs()
                    }
                }
                """,
                
            ]
        
        result = await run_flow_command(cmd)
        return json.dumps({
            "success": True,
            "result": result,
            "function": "getIDs",
            "parameters": arguments
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e),
            "function": "getIDs",
            "parameters": arguments
        }, indent=2)


@mcp.tool()
async def call_withdraw(arguments: dict) -> str:
    """
    / Removes an NFT from the collection and moves it to the caller
    
    Access Level: all
    Return Type: @NonFungibleToken.NFT
    View Function: No
    """
    try:
        # Extract parameters
                withdrawID = arguments.get("withdrawID")
        
        # Build Flow CLI command
        if false:
            # View function - use scripts
            cmd = [
                "flow", "scripts", "execute",
                "--network", "testnet",
                "--code", f"""
                import SimpleNFT from 0x1234567890abcdef
                
                access(all) fun main(withdrawID: UInt64): @NonFungibleToken.NFT {
                    return SimpleNFT.withdraw(withdrawID)
                }
                """,
                "--arg", "String:withdrawID"
            ]
        else:
            # Transaction function
            cmd = [
                "flow", "transactions", "send",
                "--network", "testnet",
                "--signer", "default",
                "--code", f"""
                import SimpleNFT from 0x1234567890abcdef
                
                transaction(withdrawID: UInt64) {
                    prepare(signer: AuthAccount) {
                        // Transaction logic here
                    }
                    
                    execute {
                        SimpleNFT.withdraw(withdrawID)
                    }
                }
                """,
                "--arg", "String:withdrawID"
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
    / Adds an NFT to the collections dictionary and adds the ID to the id array
    
    Access Level: all
    Return Type: Void
    View Function: No
    """
    try:
        # Extract parameters
                token = arguments.get("token")
        
        # Build Flow CLI command
        if false:
            # View function - use scripts
            cmd = [
                "flow", "scripts", "execute",
                "--network", "testnet",
                "--code", f"""
                import SimpleNFT from 0x1234567890abcdef
                
                access(all) fun main(token: @NonFungibleToken.NFT): Void {
                    return SimpleNFT.deposit(token)
                }
                """,
                "--arg", "String:token"
            ]
        else:
            # Transaction function
            cmd = [
                "flow", "transactions", "send",
                "--network", "testnet",
                "--signer", "default",
                "--code", f"""
                import SimpleNFT from 0x1234567890abcdef
                
                transaction(token: @NonFungibleToken.NFT) {
                    prepare(signer: AuthAccount) {
                        // Transaction logic here
                    }
                    
                    execute {
                        SimpleNFT.deposit(token)
                    }
                }
                """,
                "--arg", "String:token"
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
async def call_borrowNFT(arguments: dict) -> str:
    """
    / Gets a reference to an NFT in the collection so that
/ the caller can read its metadata and call its methods
    
    Access Level: all
    Return Type: &NonFungibleToken.NFT
    View Function: No
    """
    try:
        # Extract parameters
                id = arguments.get("id")
        
        # Build Flow CLI command
        if false:
            # View function - use scripts
            cmd = [
                "flow", "scripts", "execute",
                "--network", "testnet",
                "--code", f"""
                import SimpleNFT from 0x1234567890abcdef
                
                access(all) fun main(id: UInt64): &NonFungibleToken.NFT {
                    return SimpleNFT.borrowNFT(id)
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
                "--code", f"""
                import SimpleNFT from 0x1234567890abcdef
                
                transaction(id: UInt64) {
                    prepare(signer: AuthAccount) {
                        // Transaction logic here
                    }
                    
                    execute {
                        SimpleNFT.borrowNFT(id)
                    }
                }
                """,
                "--arg", "String:id"
            ]
        
        result = await run_flow_command(cmd)
        return json.dumps({
            "success": True,
            "result": result,
            "function": "borrowNFT",
            "parameters": arguments
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e),
            "function": "borrowNFT",
            "parameters": arguments
        }, indent=2)


@mcp.tool()
async def call_borrowSimpleNFT(arguments: dict) -> str:
    """
    / Gets a reference to an NFT in the collection as a SimpleNFT,
/ This is safe as there are no functions that can be called on the SimpleNFT
    
    Access Level: all
    Return Type: &SimpleNFT.NFT?
    View Function: No
    """
    try:
        # Extract parameters
                id = arguments.get("id")
        
        # Build Flow CLI command
        if false:
            # View function - use scripts
            cmd = [
                "flow", "scripts", "execute",
                "--network", "testnet",
                "--code", f"""
                import SimpleNFT from 0x1234567890abcdef
                
                access(all) fun main(id: UInt64): &SimpleNFT.NFT? {
                    return SimpleNFT.borrowSimpleNFT(id)
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
                "--code", f"""
                import SimpleNFT from 0x1234567890abcdef
                
                transaction(id: UInt64) {
                    prepare(signer: AuthAccount) {
                        // Transaction logic here
                    }
                    
                    execute {
                        SimpleNFT.borrowSimpleNFT(id)
                    }
                }
                """,
                "--arg", "String:id"
            ]
        
        result = await run_flow_command(cmd)
        return json.dumps({
            "success": True,
            "result": result,
            "function": "borrowSimpleNFT",
            "parameters": arguments
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e),
            "function": "borrowSimpleNFT",
            "parameters": arguments
        }, indent=2)


@mcp.tool()
async def call_borrowViewResolver(arguments: dict) -> str:
    """
    / Gets a reference to the NFT only conforming to the `{MetadataViews.Resolver}`
/ interface so that the caller can retrieve the views that the NFT
/ is implementing and resolve them
    
    Access Level: all
    Return Type: &AnyResource
    View Function: Yes
    """
    try:
        # Extract parameters
                id = arguments.get("id")
        
        # Build Flow CLI command
        if true:
            # View function - use scripts
            cmd = [
                "flow", "scripts", "execute",
                "--network", "testnet",
                "--code", f"""
                import SimpleNFT from 0x1234567890abcdef
                
                access(all) fun main(id: UInt64): &AnyResource {
                    return SimpleNFT.borrowViewResolver(id)
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
                "--code", f"""
                import SimpleNFT from 0x1234567890abcdef
                
                transaction(id: UInt64) {
                    prepare(signer: AuthAccount) {
                        // Transaction logic here
                    }
                    
                    execute {
                        SimpleNFT.borrowViewResolver(id)
                    }
                }
                """,
                "--arg", "String:id"
            ]
        
        result = await run_flow_command(cmd)
        return json.dumps({
            "success": True,
            "result": result,
            "function": "borrowViewResolver",
            "parameters": arguments
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e),
            "function": "borrowViewResolver",
            "parameters": arguments
        }, indent=2)


@mcp.tool()
async def call_createEmptyCollection(arguments: dict) -> str:
    """
    / Allows anyone to create a new empty collection
    
    Access Level: all
    Return Type: @NonFungibleToken.Collection
    View Function: No
    """
    try:
        # Extract parameters
        # No parameters
        
        # Build Flow CLI command
        if false:
            # View function - use scripts
            cmd = [
                "flow", "scripts", "execute",
                "--network", "testnet",
                "--code", f"""
                import SimpleNFT from 0x1234567890abcdef
                
                access(all) fun main(): @NonFungibleToken.Collection {
                    return SimpleNFT.createEmptyCollection()
                }
                """,
                
            ]
        else:
            # Transaction function
            cmd = [
                "flow", "transactions", "send",
                "--network", "testnet",
                "--signer", "default",
                "--code", f"""
                import SimpleNFT from 0x1234567890abcdef
                
                transaction() {
                    prepare(signer: AuthAccount) {
                        // Transaction logic here
                    }
                    
                    execute {
                        SimpleNFT.createEmptyCollection()
                    }
                }
                """,
                
            ]
        
        result = await run_flow_command(cmd)
        return json.dumps({
            "success": True,
            "result": result,
            "function": "createEmptyCollection",
            "parameters": arguments
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e),
            "function": "createEmptyCollection",
            "parameters": arguments
        }, indent=2)


@mcp.tool()
async def call_mintNFT(arguments: dict) -> str:
    """
    / Mints a new NFT with a new ID and deposit it in the
/ recipients collection using their collection reference
    
    Access Level: all
    Return Type: UInt64
    View Function: Yes
    """
    try:
        # Extract parameters
                recipient = arguments.get("recipient")
        metadata = arguments.get("metadata")
        
        # Build Flow CLI command
        if true:
            # View function - use scripts
            cmd = [
                "flow", "scripts", "execute",
                "--network", "testnet",
                "--code", f"""
                import SimpleNFT from 0x1234567890abcdef
                
                access(all) fun main(recipient: &{NonFungibleToken.CollectionPublic}, metadata: {String: String}): UInt64 {
                    return SimpleNFT.mintNFT(recipient, metadata)
                }
                """,
                "--arg", "String:recipient", "--arg", "String:metadata"
            ]
        else:
            # Transaction function
            cmd = [
                "flow", "transactions", "send",
                "--network", "testnet",
                "--signer", "default",
                "--code", f"""
                import SimpleNFT from 0x1234567890abcdef
                
                transaction(recipient: &{NonFungibleToken.CollectionPublic}, metadata: {String: String}) {
                    prepare(signer: AuthAccount) {
                        // Transaction logic here
                    }
                    
                    execute {
                        SimpleNFT.mintNFT(recipient, metadata)
                    }
                }
                """,
                "--arg", "String:recipient", "--arg", "String:metadata"
            ]
        
        result = await run_flow_command(cmd)
        return json.dumps({
            "success": True,
            "result": result,
            "function": "mintNFT",
            "parameters": arguments
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e),
            "function": "mintNFT",
            "parameters": arguments
        }, indent=2)


@mcp.tool()
async def call_getTotalSupply(arguments: dict) -> str:
    """
    / Get the total supply of NFTs
    
    Access Level: all
    Return Type: UInt64
    View Function: No
    """
    try:
        # Extract parameters
        # No parameters
        
        # Build Flow CLI command
        if false:
            # View function - use scripts
            cmd = [
                "flow", "scripts", "execute",
                "--network", "testnet",
                "--code", f"""
                import SimpleNFT from 0x1234567890abcdef
                
                access(all) fun main(): UInt64 {
                    return SimpleNFT.getTotalSupply()
                }
                """,
                
            ]
        else:
            # Transaction function
            cmd = [
                "flow", "transactions", "send",
                "--network", "testnet",
                "--signer", "default",
                "--code", f"""
                import SimpleNFT from 0x1234567890abcdef
                
                transaction() {
                    prepare(signer: AuthAccount) {
                        // Transaction logic here
                    }
                    
                    execute {
                        SimpleNFT.getTotalSupply()
                    }
                }
                """,
                
            ]
        
        result = await run_flow_command(cmd)
        return json.dumps({
            "success": True,
            "result": result,
            "function": "getTotalSupply",
            "parameters": arguments
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e),
            "function": "getTotalSupply",
            "parameters": arguments
        }, indent=2)


@mcp.tool()
async def call_getContractInfo(arguments: dict) -> str:
    """
    / Get contract information
    
    Access Level: all
    Return Type: Void
    View Function: Yes
    """
    try:
        # Extract parameters
        # No parameters
        
        # Build Flow CLI command
        if true:
            # View function - use scripts
            cmd = [
                "flow", "scripts", "execute",
                "--network", "testnet",
                "--code", f"""
                import SimpleNFT from 0x1234567890abcdef
                
                access(all) fun main(): Void {
                    return SimpleNFT.getContractInfo()
                }
                """,
                
            ]
        else:
            # Transaction function
            cmd = [
                "flow", "transactions", "send",
                "--network", "testnet",
                "--signer", "default",
                "--code", f"""
                import SimpleNFT from 0x1234567890abcdef
                
                transaction() {
                    prepare(signer: AuthAccount) {
                        // Transaction logic here
                    }
                    
                    execute {
                        SimpleNFT.getContractInfo()
                    }
                }
                """,
                
            ]
        
        result = await run_flow_command(cmd)
        return json.dumps({
            "success": True,
            "result": result,
            "function": "getContractInfo",
            "parameters": arguments
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e),
            "function": "getContractInfo",
            "parameters": arguments
        }, indent=2)


@mcp.tool()
async def get_contract_events(arguments: dict) -> str:
    """
    Get recent events emitted by the SimpleNFT contract.
    
    Available events: ContractInitialized, Withdraw, Deposit, Minted
    """
    try:
        limit = arguments.get("limit", 10)
        event_type = arguments.get("event_type", "all")
        
        cmd = [
            "flow", "events", "get",
            "--network", "testnet",
            "--start", "latest",
            "--end", "latest",
            f"SimpleNFT.*"
        ]
        
        result = await run_flow_command(cmd)
        
        return json.dumps({
            "success": True,
            "events": result,
            "contract": "SimpleNFT",
            "limit": limit,
            "event_type": event_type
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e),
            "contract": "SimpleNFT"
        }, indent=2)


@mcp.resource(f"flow://contract/{CONTRACT_ADDRESS}/{CONTRACT_NAME}")
async def get_contract_resource() -> str:
    """Get contract resource information."""
    return f"SimpleNFT contract at {CONTRACT_ADDRESS}"


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
    """Generate a prompt for analyzing the SimpleNFT contract."""
    contract_path = Path(PROJECT_PATH) / "contracts" / f"{CONTRACT_NAME}.cdc"
    
    if contract_path.exists():
        code = contract_path.read_text()
        return f"""
Please analyze the following SimpleNFT smart contract for {analysis_type}:

Contract Name: SimpleNFT
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