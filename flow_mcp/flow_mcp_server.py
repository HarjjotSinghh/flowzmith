"""
Flow MCP Server - A Model Context Protocol server for Flow blockchain interactions.

This server provides tools for interacting with Flow blockchain smart contracts,
accounts, and transactions using the Flow CLI.
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
mcp = FastMCP("Flow MCP Server")


class ContractCallParams(BaseModel):
    """Parameters for contract function calls."""
    network: str = Field(default="emulator", description="Network to use (emulator, testnet, mainnet)")
    account: str = Field(description="Account name/address to sign with")
    contract_name: str = Field(description="Name of the contract")
    function_name: str = Field(description="Name of the function to call")
    arguments: List[str] = Field(default=[], description="Arguments to pass to the function")


class AccountInfo(BaseModel):
    """Account information structure."""
    address: str
    balance: float
    contracts: List[str]
    keys: List[Dict[str, Any]]


class TransactionInfo(BaseModel):
    """Transaction information structure."""
    tx_id: str
    status: str
    block_height: int
    timestamp: str
    payer: str
    authorizers: List[str]
    events: List[Dict[str, Any]]


class ContractInfo(BaseModel):
    """Contract information structure."""
    name: str
    address: str
    code: str
    deployed_at: str
    updated_at: str


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
            cwd=cwd,
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
async def call_contract(
    params: ContractCallParams,
    ctx: Context[ServerSession, None]
) -> Dict[str, Any]:
    """Call a function on a Flow smart contract."""
    await ctx.info(f"Calling contract function: {params.contract_name}.{params.function_name}")

    # Create temporary directory for Flow project
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Initialize Flow project
        init_result = await run_flow_command(["project", "init"], cwd=temp_path)
        if not init_result["success"]:
            return {
                "success": False,
                "error": f"Failed to initialize Flow project: {init_result['stderr']}"
            }

        # Build transaction command
        tx_args = []
        for arg in params.arguments:
            tx_args.extend(["--arg", arg])

        cmd = [
            "transactions", "send",
            "./transactions/transaction.cdc",
            "--signer", params.account,
            "--network", params.network
        ] + tx_args

        result = await run_flow_command(cmd, cwd=temp_path)

        if result["success"]:
            # Parse transaction ID from output
            import re
            tx_id_match = re.search(r'Transaction ID: ([a-f0-9]+)', result["stdout"])
            tx_id = tx_id_match.group(1) if tx_id_match else None

            return {
                "success": True,
                "transaction_id": tx_id,
                "output": result["stdout"]
            }
        else:
            return {
                "success": False,
                "error": result["stderr"],
                "output": result["stdout"]
            }


@mcp.tool()
async def view_contract(
    contract_address: str,
    contract_name: str,
    ctx: Context[ServerSession, None],
    network: str = "emulator"
) -> Dict[str, Any]:
    """View a deployed smart contract."""
    await ctx.info(f"Viewing contract: {contract_name} at {contract_address}")

    cmd = [
        "accounts", "get",
        contract_address,
        "--network", network,
        "--include", "contracts",
        "--output", "json"
    ]

    result = await run_flow_command(cmd)

    if result["success"]:
        try:
            account_data = json.loads(result["stdout"])
            contracts = account_data.get("code", {})

            if isinstance(contracts, dict) and contract_name in contracts:
                contract_code = contracts[contract_name]
                return {
                    "success": True,
                    "contract": {
                        "address": contract_address,
                        "name": contract_name,
                        "code": contract_code
                    }
                }
            else:
                return {
                    "success": False,
                    "error": f"Contract '{contract_name}' not found at address {contract_address}"
                }
        except json.JSONDecodeError:
            return {
                "success": False,
                "error": "Failed to parse account data"
            }
    else:
        return {
            "success": False,
            "error": result["stderr"]
        }


@mcp.tool()
async def view_account(
    address: str,
    ctx: Context[ServerSession, None],
    network: str = "emulator"
) -> Dict[str, Any]:
    """View account information."""
    await ctx.info(f"Viewing account: {address}")

    cmd = [
        "accounts", "get",
        address,
        "--network", network,
        "--output", "json"
    ]

    result = await run_flow_command(cmd)

    if result["success"]:
        try:
            # Parse account information
            account_data = json.loads(result["stdout"])
            return {
                "success": True,
                "account": account_data
            }
        except json.JSONDecodeError:
            return {
                "success": True,
                "account": {
                    "address": address,
                    "raw_output": result["stdout"]
                }
            }
    else:
        return {
            "success": False,
            "error": result["stderr"]
        }


@mcp.tool()
async def view_transaction(
    tx_id: str,
    ctx: Context[ServerSession, None],
    network: str = "emulator"
) -> Dict[str, Any]:
    """View transaction details."""
    await ctx.info(f"Viewing transaction: {tx_id}")

    cmd = [
        "transactions", "get",
        tx_id,
        "--network", network,
        "--include", "results"
    ]

    result = await run_flow_command(cmd)

    if result["success"]:
        try:
            tx_data = json.loads(result["stdout"])
            return {
                "success": True,
                "transaction": tx_data
            }
        except json.JSONDecodeError:
            return {
                "success": True,
                "transaction": {
                    "id": tx_id,
                    "raw_output": result["stdout"]
                }
            }
    else:
        return {
            "success": False,
            "error": result["stderr"]
        }


@mcp.tool()
async def deploy_contract(
    contract_path: str,
    account: str,
    ctx: Context[ServerSession, None],
    network: str = "emulator"
) -> Dict[str, Any]:
    """Deploy a smart contract."""
    await ctx.info(f"Deploying contract from: {contract_path}")

    contract_file = Path(contract_path)
    if not contract_file.exists():
        return {
            "success": False,
            "error": f"Contract file not found: {contract_path}"
        }

    cmd = [
        "project", "deploy",
        "--network", network,
        "--signer", account
    ]

    result = await run_flow_command(cmd, cwd=contract_file.parent)

    if result["success"]:
        return {
            "success": True,
            "output": result["stdout"]
        }
    else:
        return {
            "success": False,
            "error": result["stderr"]
        }


@mcp.tool()
async def list_accounts(
    ctx: Context[ServerSession, None],
    network: str = "emulator"
) -> Dict[str, Any]:
    """List available accounts."""
    await ctx.info(f"Listing accounts on network: {network}")

    cmd = [
        "accounts", "list",
        "--network", network,
        "--output", "json"
    ]

    result = await run_flow_command(cmd)

    if result["success"]:
        try:
            accounts_data = json.loads(result["stdout"])
            return {
                "success": True,
                "accounts": accounts_data
            }
        except json.JSONDecodeError:
            return {
                "success": True,
                "accounts": {
                    "raw_output": result["stdout"]
                }
            }
    else:
        return {
            "success": False,
            "error": result["stderr"]
        }


@mcp.tool()
async def get_account_balance(
    address: str,
    ctx: Context[ServerSession, None],
    network: str = "emulator"
) -> Dict[str, Any]:
    """Get account balance."""
    await ctx.info(f"Getting balance for account: {address}")

    # Use accounts get to get balance information
    cmd = [
        "accounts", "get",
        address,
        "--network", network,
        "--output", "json"
    ]

    result = await run_flow_command(cmd)

    if result["success"]:
        try:
            account_data = json.loads(result["stdout"])
            return {
                "success": True,
                "balance": {
                    "address": address,
                    "balance": account_data.get("balance", "0"),
                    "network": network
                }
            }
        except json.JSONDecodeError:
            # Parse balance from text output
            lines = result["stdout"].split('\n')
            balance = "0"
            for line in lines:
                if line.startswith('Balance\t'):
                    balance = line.split('\t')[1]
                    break
            return {
                "success": True,
                "balance": {
                    "address": address,
                    "balance": balance,
                    "network": network
                }
            }
    else:
        return {
            "success": False,
            "error": result["stderr"]
        }


@mcp.tool()
async def list_transactions(
    ctx: Context[ServerSession, None],
    limit: int = 10,
    address: Optional[str] = None,
    network: str = "emulator",
) -> Dict[str, Any]:
    """List recent transactions."""
    await ctx.info(f"Listing transactions on network: {network}")

    cmd = [
        "transactions", "list",
        "--network", network,
        "--limit", str(limit)
    ]

    if address:
        cmd.extend(["--address", address])

    result = await run_flow_command(cmd)

    if result["success"]:
        try:
            tx_data = json.loads(result["stdout"])
            return {
                "success": True,
                "transactions": tx_data
            }
        except json.JSONDecodeError:
            return {
                "success": True,
                "transactions": {
                    "raw_output": result["stdout"]
                }
            }
    else:
        return {
            "success": False,
            "error": result["stderr"]
        }


@mcp.resource("flow://contract/{address}/{name}")
async def get_contract_resource(address: str, name: str) -> str:
    """Get contract as a resource."""
    result = await view_contract(address, name)
    if result["success"]:
        return json.dumps(result["contract"], indent=2)
    else:
        return f"Error: {result['error']}"


@mcp.resource("flow://account/{address}")
async def get_account_resource(address: str) -> str:
    """Get account as a resource."""
    result = await view_account(address)
    if result["success"]:
        return json.dumps(result["account"], indent=2)
    else:
        return f"Error: {result['error']}"


@mcp.resource("flow://transaction/{tx_id}")
async def get_transaction_resource(tx_id: str) -> str:
    """Get transaction as a resource."""
    result = await view_transaction(tx_id)
    if result["success"]:
        return json.dumps(result["transaction"], indent=2)
    else:
        return f"Error: {result['error']}"


@mcp.prompt()
def analyze_contract_prompt(contract_code: str, analysis_type: str = "security") -> str:
    """Generate a prompt for contract analysis."""
    analysis_types = {
        "security": "security vulnerabilities and potential risks",
        "performance": "performance optimizations and gas efficiency",
        "architecture": "code architecture and design patterns",
        "compliance": "compliance with Flow blockchain best practices"
    }

    analysis_focus = analysis_types.get(analysis_type, analysis_types["security"])

    return f"""
Please analyze this Flow smart contract code focusing on {analysis_focus}:

```cadence
{contract_code}
```

Please provide:
1. Summary of the contract's purpose
2. Key findings related to {analysis_focus}
3. Recommendations for improvement
4. Potential issues or concerns
"""


if __name__ == "__main__":
    mcp.run()