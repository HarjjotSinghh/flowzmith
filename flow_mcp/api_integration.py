"""
API Integration for MCP Server with existing flowzmith API
"""

import json
from typing import Any, Dict, Optional
from fastapi import APIRouter, HTTPException
from mcp.mcp_client import MCPFlowClient

router = APIRouter(prefix="/mcp", tags=["mcp"])


@router.get("/health")
async def mcp_health_check():
    """Check MCP server health."""
    try:
        client = MCPFlowClient()
        await client.connect()
        await client.disconnect()
        return {"status": "healthy", "message": "MCP server is accessible"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"MCP server unavailable: {str(e)}")


@router.get("/accounts")
async def list_accounts(network: str = "emulator"):
    """List available accounts."""
    try:
        client = MCPFlowClient()
        await client.connect()
        result = await client.list_accounts(network)
        await client.disconnect()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list accounts: {str(e)}")


@router.get("/accounts/{address}")
async def get_account(address: str, network: str = "emulator"):
    """Get account details."""
    try:
        client = MCPFlowClient()
        await client.connect()
        result = await client.view_account(address, network)
        await client.disconnect()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get account: {str(e)}")


@router.get("/accounts/{address}/balance")
async def get_account_balance(address: str, network: str = "emulator"):
    """Get account balance."""
    try:
        client = MCPFlowClient()
        await client.connect()
        result = await client.get_account_balance(address, network)
        await client.disconnect()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get account balance: {str(e)}")


@router.get("/contracts/{address}/{name}")
async def get_contract(address: str, name: str, network: str = "emulator"):
    """Get contract details."""
    try:
        client = MCPFlowClient()
        await client.connect()
        result = await client.view_contract(address, name, network)
        await client.disconnect()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get contract: {str(e)}")


@router.post("/contracts/deploy")
async def deploy_contract(contract_path: str, account: str, network: str = "emulator"):
    """Deploy a contract."""
    try:
        client = MCPFlowClient()
        await client.connect()
        result = await client.deploy_contract(contract_path, account, network)
        await client.disconnect()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to deploy contract: {str(e)}")


@router.get("/transactions")
async def list_transactions(
    address: Optional[str] = None,
    network: str = "emulator",
    limit: int = 10
):
    """List transactions."""
    try:
        client = MCPFlowClient()
        await client.connect()
        result = await client.list_transactions(address, network, limit)
        await client.disconnect()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list transactions: {str(e)}")


@router.get("/transactions/{tx_id}")
async def get_transaction(tx_id: str, network: str = "emulator"):
    """Get transaction details."""
    try:
        client = MCPFlowClient()
        await client.connect()
        result = await client.view_transaction(tx_id, network)
        await client.disconnect()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get transaction: {str(e)}")


@router.post("/contracts/call")
async def call_contract(params: Dict[str, Any]):
    """Call a contract function."""
    try:
        client = MCPFlowClient()
        await client.connect()
        result = await client.call_contract(params)
        await client.disconnect()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to call contract: {str(e)}")