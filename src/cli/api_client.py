"""
API client for Smart Contract LLM Builder CLI.

Handles all HTTP and WebSocket communications with the backend server.
"""

import json
import asyncio
import aiohttp
import websockets
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
import uuid
from pathlib import Path

from ..config import get_settings

class APIClient:
    """Async HTTP and WebSocket client for API interactions."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.ws_url = f"ws://localhost:8000/ws"
        self.session: Optional[aiohttp.ClientSession] = None
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.connection_id: Optional[str] = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=300)
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.websocket:
            await self.websocket.close()
        if self.session:
            await self.session.close()

    # HTTP Methods
    async def get(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        async with self.session.get(f"{self.base_url}{endpoint}", **kwargs) as response:
            return await self._handle_response(response)

    async def post(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        async with self.session.post(f"{self.base_url}{endpoint}", **kwargs) as response:
            return await self._handle_response(response)

    async def put(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        async with self.session.put(f"{self.base_url}{endpoint}", **kwargs) as response:
            return await self._handle_response(response)

    async def _handle_response(self, response: aiohttp.ClientResponse) -> Dict[str, Any]:
        try:
            data = await response.json()
        except:
            data = {"text": await response.text()}

        if response.status >= 400:
            raise Exception(f"API Error {response.status}: {data}")

        return data

    def _get_system_address(self) -> str:
        """Return a stable identifier for this machine (MAC-like)."""
        try:
            node = uuid.getnode()
            mac_hex = ":".join(f"{(node >> ele) & 0xff:02x}" for ele in range(40, -1, -8))
            return mac_hex
        except Exception:
            return str(uuid.uuid4())

    # WebSocket Methods
    async def connect_websocket(self) -> str:
        """Connect to WebSocket and return connection ID."""
        try:
            self.websocket = await websockets.connect(self.ws_url)
            # Wait for welcome/connection established message
            welcome_msg = await self.websocket.recv()
            welcome_data = json.loads(welcome_msg)

            # Support both legacy and current formats
            if welcome_data.get("type") == "welcome":
                self.connection_id = welcome_data.get("connection_id")
                return self.connection_id

            if welcome_data.get("type") == "connection_established":
                data = welcome_data.get("data", {})
                self.connection_id = data.get("connection_id") or welcome_data.get("connection_id")
                if self.connection_id:
                    return self.connection_id

            raise Exception("Unexpected welcome message format: " + str(welcome_data))

        except Exception as e:
            raise Exception(f"WebSocket connection failed: {e}")

    async def send_message(self, message: Dict[str, Any]) -> None:
        """Send message through WebSocket."""
        if not self.websocket:
            raise Exception("WebSocket not connected")

        await self.websocket.send(json.dumps(message))

    async def listen_messages(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """Listen for WebSocket messages and call callback for each."""
        if not self.websocket:
            raise Exception("WebSocket not connected")

        try:
            async for message in self.websocket:
                data = json.loads(message)
                callback(data)
        except websockets.exceptions.ConnectionClosed:
            pass

    # Contract API Methods
    async def submit_contract(self, contract_data: Dict[str, Any]) -> Dict[str, Any]:
        """Submit a new contract for processing."""
        # Attach system address for CLI to help backend create/find user
        contract_data = dict(contract_data)
        contract_data.setdefault("system_address", self._get_system_address())
        return await self.post("/api/v1/contracts/submit", json=contract_data)

    async def get_contracts(self, status: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Get list of contracts."""
        params = {"limit": limit}
        if status:
            params["status"] = status

        result = await self.get("/api/v1/contracts", params=params)
        return result.get("contracts", [])

    async def get_contract(self, contract_id: str) -> Dict[str, Any]:
        """Get specific contract details."""
        return await self.get(f"/api/v1/contracts/{contract_id}")

    # Deployment API Methods
    async def deploy_contract(self, deployment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Deploy a contract to blockchain."""
        return await self.post("/api/v1/deployments", json=deployment_data)

    async def get_deployments(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get list of deployments."""
        result = await self.get("/api/v1/deployments", params={"limit": limit})
        return result.get("deployments", [])

    async def get_deployment_status(self, deployment_id: str) -> Dict[str, Any]:
        """Get deployment status."""
        return await self.get(f"/api/v1/deployments/{deployment_id}/status")

    # Documentation API Methods
    async def search_documentation(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search documentation."""
        result = await self.get("/api/v1/documentation/search", params={"q": query, "limit": limit})
        return result.get("results", [])

    async def upload_documentation(self, file_path: Path, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Upload documentation file."""
        if not file_path.exists():
            raise Exception(f"File not found: {file_path}")

        data = aiohttp.FormData()
        data.add_field("file", open(file_path, "rb"), filename=file_path.name)
        data.add_field("metadata", json.dumps(metadata))
        # Include system address for CLI uploads
        data.add_field("system_address", self._get_system_address())

        return await self.post("/api/v1/documentation/upload", data=data)

    # File Upload Methods
    async def upload_file(self, file_path: Path, file_type: str) -> Dict[str, Any]:
        """Upload contract file."""
        if not file_path.exists():
            raise Exception(f"File not found: {file_path}")

        data = aiohttp.FormData()
        data.add_field("file", open(file_path, "rb"), filename=file_path.name)
        # Include system address for CLI uploads
        data.add_field("system_address", self._get_system_address())

        return await self.post("/api/v1/contracts/file", data=data)

    # System API Methods
    async def health_check(self) -> Dict[str, Any]:
        """Check system health."""
        return await self.get("/health")

    async def get_dashboard_stats(self) -> Dict[str, Any]:
        """Get dashboard statistics."""
        return await self.get("/api/dashboard/stats")

    # Utility Methods
    async def wait_for_operation(self, operation_id: str, timeout: int = 300) -> Dict[str, Any]:
        """Wait for an operation to complete."""
        start_time = datetime.now()

        while (datetime.now() - start_time).total_seconds() < timeout:
            try:
                status = await self.get(f"/api/v1/operations/{operation_id}/status")

                if status.get("status") in ["completed", "failed", "success"]:
                    return status

                await asyncio.sleep(2)
            except Exception as e:
                await asyncio.sleep(2)

        raise Exception(f"Operation timeout: {operation_id}")

    async def stream_operation_progress(self, operation_id: str, callback: Callable[[Dict[str, Any]], None]) -> None:
        """Stream real-time progress for an operation."""
        await self.send_message({
            "type": "subscribe_operation",
            "operation_id": operation_id
        })

        async def message_handler(data: Dict[str, Any]):
            if data.get("operation_id") == operation_id:
                callback(data)

        await self.listen_messages(message_handler)