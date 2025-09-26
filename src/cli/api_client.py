"""
API client for Smart Contract LLM Builder CLI.

Handles all HTTP and WebSocket communications with the backend server.
"""

import json
import asyncio
import aiohttp
import websockets
from typing import Dict, Any, Optional, List, Callable, Iterator
from datetime import datetime
import uuid
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

from ..config import get_settings

import logging
logger = logging.getLogger(__name__)

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
        logger.info("APIClient session created (base_url=%s, ws_url=%s)", self.base_url, self.ws_url)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        logger.info("APIClient shutting down; closing websocket=%s, session=%s", bool(self.websocket), bool(self.session))
        if self.websocket:
            try:
                await self.websocket.close()
            except Exception:
                logger.exception("Error closing websocket")
        if self.session:
            try:
                await self.session.close()
            except Exception:
                logger.exception("Error closing aiohttp session")

    # HTTP Methods
    async def get(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        url = f"{self.base_url}{endpoint}"
        logger.info("HTTP GET %s params=%s headers=%s", url, kwargs.get("params"), kwargs.get("headers"))
        async with self.session.get(url, **kwargs) as response:
            return await self._handle_response(response)

    async def post(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        url = f"{self.base_url}{endpoint}"
        payload_keys = list(kwargs.get("json", {}).keys()) if kwargs.get("json") else ("form-data" if kwargs.get("data") else None)
        logger.info("HTTP POST %s json_keys=%s has_data=%s headers=%s", url, payload_keys, bool(kwargs.get("data")), kwargs.get("headers"))
        async with self.session.post(url, **kwargs) as response:
            return await self._handle_response(response)

    async def put(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        url = f"{self.base_url}{endpoint}"
        payload_keys = list(kwargs.get("json", {}).keys()) if kwargs.get("json") else ("form-data" if kwargs.get("data") else None)
        logger.info("HTTP PUT %s json_keys=%s has_data=%s headers=%s", url, payload_keys, bool(kwargs.get("data")), kwargs.get("headers"))
        async with self.session.put(url, **kwargs) as response:
            return await self._handle_response(response)

    async def _handle_response(self, response: aiohttp.ClientResponse) -> Dict[str, Any]:
        method = getattr(response.request_info, "method", "?")
        url = str(getattr(response, "url", ""))
        status = response.status
        try:
            data = await response.json()
            logger.debug("HTTP %s %s responded with %s and JSON body", method, url, status)
        except Exception:
            text = await response.text()
            data = {"text": text}
            logger.debug("HTTP %s %s responded with %s and non-JSON body", method, url, status)

        if status >= 400:
            logger.error("API Error %s for %s %s: %s", status, method, url, data)
            raise Exception(f"API Error {status}: {data}")

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
            logger.info("Connecting to WebSocket at %s", self.ws_url)
            self.websocket = await websockets.connect(self.ws_url)
            # Wait for welcome/connection established message
            welcome_msg = await self.websocket.recv()
            welcome_data = json.loads(welcome_msg)
            logger.debug("Received welcome message: %s", welcome_data)

            # Support both legacy and current formats
            if welcome_data.get("type") == "welcome":
                self.connection_id = welcome_data.get("connection_id")
                logger.info("WebSocket connected; connection_id=%s", self.connection_id)
                return self.connection_id

            if welcome_data.get("type") == "connection_established":
                data = welcome_data.get("data", {})
                self.connection_id = data.get("connection_id") or welcome_data.get("connection_id")
                if self.connection_id:
                    logger.info("WebSocket connected; connection_id=%s", self.connection_id)
                    return self.connection_id

            logger.error("Unexpected welcome message format: %s", welcome_data)
            raise Exception("Unexpected welcome message format: " + str(welcome_data))

        except Exception as e:
            logger.exception("WebSocket connection failed")
            raise Exception(f"WebSocket connection failed: {e}")

    async def send_message(self, message: Dict[str, Any]) -> None:
        """Send message through WebSocket."""
        if not self.websocket:
            raise Exception("WebSocket not connected")

        try:
            logger.debug("Sending WebSocket message: %s", message)
            await self.websocket.send(json.dumps(message))
        except Exception:
            logger.exception("Failed to send WebSocket message")
            raise

    async def listen_messages(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """Listen for WebSocket messages and call callback for each."""
        if not self.websocket:
            raise Exception("WebSocket not connected")

        try:
            logger.info("Listening for WebSocket messages...")
            async for message in self.websocket:
                data = json.loads(message)
                logger.debug("Received WebSocket message: %s", data)
                callback(data)
        except websockets.exceptions.ConnectionClosed:
            logger.warning("WebSocket connection closed")
        except Exception:
            logger.exception("Error while listening to WebSocket messages")
            raise

    # Contract API Methods
    async def submit_contract(self, contract_data: Dict[str, Any]) -> Dict[str, Any]:
        """Submit a new contract for processing."""
        # Attach system address for CLI to help backend create/find user
        contract_data = dict(contract_data)
        contract_data.setdefault("system_address", self._get_system_address())
        logger.info("Submitting contract to /api/v1/contracts/submit with keys=%s", list(contract_data.keys()))
        return await self.post("/api/v1/contracts/submit", json=contract_data)

    async def get_contracts(self, status: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Get list of contracts."""
        params = {"limit": limit}
        if status:
            params["status"] = status

        logger.info("Fetching contracts: params=%s", params)
        result = await self.get("/api/v1/contracts", params=params)
        return result.get("contracts", [])

    async def get_contract(self, contract_id: str) -> Dict[str, Any]:
        """Get specific contract details."""
        logger.info("Fetching contract details: contract_id=%s", contract_id)
        return await self.get(f"/api/v1/contracts/{contract_id}")

    # Deployment API Methods
    async def deploy_contract(self, deployment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Deploy a contract to blockchain."""
        logger.info("Deploying contract: keys=%s", list(deployment_data.keys()))
        return await self.post("/api/v1/deployments", json=deployment_data)

    async def get_deployments(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get list of deployments."""
        logger.info("Fetching deployments: limit=%s", limit)
        result = await self.get("/api/v1/deployments", params={"limit": limit})
        return result.get("deployments", [])

    async def get_deployment_status(self, deployment_id: str) -> Dict[str, Any]:
        """Get deployment status."""
        logger.info("Fetching deployment status: deployment_id=%s", deployment_id)
        return await self.get(f"/api/v1/deployments/{deployment_id}/status")

    # Documentation API Methods
    async def search_documentation(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search documentation."""
        logger.info("Searching documentation: query=%s, limit=%s", query, limit)
        result = await self.get("/api/v1/documentation/search", params={"q": query, "limit": limit})
        return result.get("results", [])

    async def upload_documentation(self, file_path: Path, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Upload documentation file."""
        if not file_path.exists():
            raise Exception(f"File not found: {file_path}")

        logger.info("Uploading documentation: file=%s", file_path)
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

        logger.info("Uploading file: type=%s, file=%s", file_type, file_path)
        data = aiohttp.FormData()
        data.add_field("file", open(file_path, "rb"), filename=file_path.name)
        # Include system address for CLI uploads
        data.add_field("system_address", self._get_system_address())

        return await self.post("/api/v1/contracts/file", data=data)

    # System API Methods
    async def health_check(self) -> Dict[str, Any]:
        """Check system health."""
        logger.info("Calling /health endpoint")
        return await self.get("/health")

    async def get_dashboard_stats(self) -> Dict[str, Any]:
        """Get dashboard statistics."""
        logger.info("Calling /api/dashboard/stats endpoint")
        return await self.get("/api/dashboard/stats")

    # Utility Methods
    async def wait_for_operation(self, operation_id: str, timeout: int = 300) -> Dict[str, Any]:
        """Wait for an operation to complete."""
        start_time = datetime.now()
        logger.info("Waiting for operation_id=%s with timeout=%s", operation_id, timeout)

        while (datetime.now() - start_time).total_seconds() < timeout:
            try:
                status = await self.get(f"/api/v1/operations/{operation_id}/status")
                logger.debug("Operation %s status: %s", operation_id, status.get("status"))

                if status.get("status") in ["completed", "failed", "success"]:
                    logger.info("Operation %s finished with status=%s", operation_id, status.get("status"))
                    return status

                await asyncio.sleep(2)
            except Exception as e:
                logger.exception("Error while polling operation %s", operation_id)
                await asyncio.sleep(2)

        logger.error("Operation timeout: %s", operation_id)
        raise Exception(f"Operation timeout: {operation_id}")

    async def stream_operation_progress(self, operation_id: str, callback: Callable[[Dict[str, Any]], None]) -> None:
        """Stream real-time progress for an operation."""
        logger.info("Subscribing to operation progress: operation_id=%s", operation_id)
        await self.send_message({
            "type": "subscribe_operation",
            "operation_id": operation_id
        })

        async def message_handler(data: Dict[str, Any]):
            if data.get("operation_id") == operation_id:
                logger.debug("Progress update for operation %s: %s", operation_id, data)
                callback(data)

        await self.listen_messages(message_handler)

    # Context-based Generation Methods
    async def generate_contract_with_context(self, generation_request: Dict[str, Any]) -> Dict[str, Any]:
        """Generate contract using markdown context and AI."""
        preview = str(generation_request.get("requirements", ""))
        if len(preview) > 80:
            preview = preview[:77] + "..."
        logger.info("Generating contract with context: requirements_preview=%s, has_context=%s", preview, bool(generation_request.get("context")))
        # Pass a synthetic user identifier to satisfy API route requirements
        return await self.post("/api/v1/contracts/generate-with-context", json=generation_request, params={"user_id": self._get_system_address()})

    async def generate_contract_with_context_streaming(self, generation_request: Dict[str, Any], callback: Callable[[str], None]) -> Dict[str, Any]:
        """Generate contract with streaming response (WebSocket-based - legacy)."""
        preview = str(generation_request.get("requirements", ""))
        if len(preview) > 80:
            preview = preview[:77] + "..."
        logger.info("Streaming contract generation: requirements_preview=%s, has_context=%s", preview, bool(generation_request.get("context")))
        
        # Connect WebSocket if not already connected
        if not self.websocket:
            await self.connect_websocket()
        
        # Send streaming generation request
        await self.send_message({
            "type": "generate_contract_streaming",
            "data": generation_request
        })
        
        # Collect streamed chunks
        result = {"content": "", "config": None, "status": None}
        
        async def message_handler(data: Dict[str, Any]):
            if data.get("type") == "stream_chunk":
                chunk = data.get("chunk", "")
                result["content"] += chunk
                callback(chunk)
            elif data.get("type") == "stream_config":
                result["config"] = data.get("config")
            elif data.get("type") == "stream_complete":
                result["status"] = data.get("status")
                result["submission_id"] = data.get("submission_id")
            elif data.get("type") == "stream_error":
                raise Exception(data.get("error", "Streaming error"))
        
        # Listen for streaming messages with timeout
        start_time = datetime.now()
        timeout = 300  # 5 minutes
        
        while not result["status"] and (datetime.now() - start_time).total_seconds() < timeout:
            try:
                message = await asyncio.wait_for(self.websocket.recv(), timeout=2.0)
                data = json.loads(message)
                await message_handler(data)
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error("Error in streaming: %s", e)
                raise
        
        if not result["status"]:
            raise Exception("Streaming timeout")
        
        return result

    async def stream_generate_contract_with_context(self, generation_request: Dict[str, Any]):
        """HTTP streaming generator for contract generation using SSE-like text chunks.
        Yields event dictionaries with keys: type ('content'|'status'|'progress'|'complete'|'error').
        """
        preview = str(generation_request.get("requirements", ""))
        if len(preview) > 80:
            preview = preview[:77] + "..."
        logger.info("HTTP streaming contract generation: requirements_preview=%s, has_context=%s", preview, bool(generation_request.get("context")))

        url = f"{self.base_url}/api/v1/contracts/generate-with-context/streaming"
        params = {"user_id": self._get_system_address()}
        headers = {"Accept": "text/event-stream"}

        async with self.session.post(url, json=generation_request, params=params, headers=headers) as resp:
            status = resp.status
            if status >= 400:
                # Try to read error body
                try:
                    err_text = await resp.text()
                except Exception:
                    err_text = f"HTTP {status}"
                logger.error("Streaming API error: %s", err_text)
                yield {"type": "error", "error": f"API Error {status}: {err_text}"}
                return

            # Stream content
            async for raw_chunk in resp.content.iter_any():
                try:
                    chunk = raw_chunk.decode("utf-8", errors="ignore")
                except Exception:
                    chunk = str(raw_chunk)

                if not chunk:
                    continue

                # Detect special markers for config and final status
                if "<!-- CONFIG_START -->" in chunk and "<!-- CONFIG_END -->" in chunk:
                    # Configuration block present
                    start = chunk.find("<!-- CONFIG_START -->") + len("<!-- CONFIG_START -->")
                    end = chunk.find("<!-- CONFIG_END -->")
                    config_json = chunk[start:end].strip()
                    # Emit a status update
                    yield {"type": "status", "data": {"stage": "Configuration generated"}}
                    # Also emit a progress message
                    yield {"type": "progress", "data": {"message": "Validated generation configuration"}}
                    # Do not emit config markers/content as regular content
                    continue

                if "<!-- FINAL_STATUS:" in chunk:
                    try:
                        marker_start = chunk.find("<!-- FINAL_STATUS:") + len("<!-- FINAL_STATUS:")
                        marker_end = chunk.find("-->", marker_start)
                        final_json = chunk[marker_start:marker_end]
                        final_data = json.loads(final_json)
                    except Exception:
                        final_data = {"status": "completed"}
                    yield {"type": "complete", "data": final_data}
                    return

                if "<!-- ERROR:" in chunk:
                    try:
                        marker_start = chunk.find("<!-- ERROR:") + len("<!-- ERROR:")
                        marker_end = chunk.find("-->", marker_start)
                        err_msg = chunk[marker_start:marker_end]
                    except Exception:
                        err_msg = "Streaming error"
                    yield {"type": "error", "error": err_msg}
                    return

                # Regular content chunk
                yield {"type": "content", "chunk": chunk}