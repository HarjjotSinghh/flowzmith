"""
MCP Client for integrating with the existing CLI and API
"""

import asyncio
import json
from typing import Any, Dict, Optional

from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client


class MCPFlowClient:
    """Client for interacting with the Flow MCP server."""

    def __init__(self, server_path: str = "flow_mcp/flow_mcp_server.py"):
        self.server_path = server_path
        self.session: Optional[ClientSession] = None

    async def connect(self):
        """Connect to the MCP server."""
        server_params = StdioServerParameters(
            command="python3",
            args=[self.server_path],
        )

        read, write = await stdio_client(server_params).__aenter__()
        self.session = ClientSession(read, write)
        await self.session.initialize()

    async def disconnect(self):
        """Disconnect from the MCP server."""
        if self.session:
            await self.session.__aexit__(None, None, None)

    async def call_contract(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Call a contract function."""
        if not self.session:
            raise RuntimeError("Not connected to MCP server")

        result = await self.session.call_tool("call_contract", {"params": params})
        return result.content[0].text if result.content else {}

    async def view_contract(self, address: str, name: str, network: str = "emulator") -> Dict[str, Any]:
        """View a contract."""
        if not self.session:
            raise RuntimeError("Not connected to MCP server")

        result = await self.session.call_tool(
            "view_contract",
            {
                "contract_address": address,
                "contract_name": name,
                "network": network
            }
        )
        return result.content[0].text if result.content else {}

    async def view_account(self, address: str, network: str = "emulator") -> Dict[str, Any]:
        """View an account."""
        if not self.session:
            raise RuntimeError("Not connected to MCP server")

        result = await self.session.call_tool(
            "view_account",
            {"address": address, "network": network}
        )
        return result.content[0].text if result.content else {}

    async def view_transaction(self, tx_id: str, network: str = "emulator") -> Dict[str, Any]:
        """View a transaction."""
        if not self.session:
            raise RuntimeError("Not connected to MCP server")

        result = await self.session.call_tool(
            "view_transaction",
            {"tx_id": tx_id, "network": network}
        )
        return result.content[0].text if result.content else {}

    async def deploy_contract(self, contract_path: str, account: str, network: str = "emulator") -> Dict[str, Any]:
        """Deploy a contract."""
        if not self.session:
            raise RuntimeError("Not connected to MCP server")

        result = await self.session.call_tool(
            "deploy_contract",
            {
                "contract_path": contract_path,
                "account": account,
                "network": network
            }
        )
        return result.content[0].text if result.content else {}

    async def list_accounts(self, network: str = "emulator") -> Dict[str, Any]:
        """List accounts."""
        if not self.session:
            raise RuntimeError("Not connected to MCP server")

        result = await self.session.call_tool("list_accounts", {"network": network})
        return result.content[0].text if result.content else {}

    async def get_account_balance(self, address: str, network: str = "emulator") -> Dict[str, Any]:
        """Get account balance."""
        if not self.session:
            raise RuntimeError("Not connected to MCP server")

        result = await self.session.call_tool(
            "get_account_balance",
            {"address": address, "network": network}
        )
        return result.content[0].text if result.content else {}

    async def list_transactions(self, address: Optional[str] = None, network: str = "emulator", limit: int = 10) -> Dict[str, Any]:
        """List transactions."""
        if not self.session:
            raise RuntimeError("Not connected to MCP server")

        params = {"network": network, "limit": limit}
        if address:
            params["address"] = address

        result = await self.session.call_tool("list_transactions", params)
        return result.content[0].text if result.content else {}