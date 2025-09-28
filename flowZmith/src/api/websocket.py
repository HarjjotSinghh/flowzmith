from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List
import json
import asyncio
from src.config import settings

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)

    def disconnect(self, websocket: WebSocket, user_id: int):
        if user_id in self.active_connections:
            self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

    async def send_personal_message(self, message: str, user_id: int):
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_text(message)
                except:
                    # Connection might be closed, remove it
                    self.active_connections[user_id].remove(connection)

    async def broadcast(self, message: str):
        for user_connections in self.active_connections.values():
            for connection in user_connections:
                try:
                    await connection.send_text(message)
                except:
                    # Connection might be closed
                    pass

manager = ConnectionManager()

async def websocket_endpoint(websocket: WebSocket, token: str = None):
    # In a real implementation, you would validate the JWT token here
    # For now, we'll use a simple user_id from the token
    user_id = 1  # Default user for demo purposes

    await manager.connect(websocket, user_id)
    try:
        while True:
            # Keep connection alive and listen for messages
            data = await websocket.receive_text()
            message_data = json.loads(data)

            # Handle different message types
            if message_data.get("type") == "ping":
                await websocket.send_text(json.dumps({"type": "pong"}))
            elif message_data.get("type") == "subscribe_updates":
                # Handle subscription to specific updates
                await manager.send_personal_message(
                    json.dumps({"type": "subscription_confirmed", "subscription_id": message_data.get("subscription_id")}),
                    user_id
                )

    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)

# Helper functions to send updates via WebSocket
async def send_deployment_update(user_id: int, deployment_data: dict):
    """Send deployment status update to user"""
    message = json.dumps({
        "type": "deployment_update",
        "data": deployment_data
    })
    await manager.send_personal_message(message, user_id)

async def send_generation_progress(user_id: int, progress_data: dict):
    """Send contract generation progress update to user"""
    message = json.dumps({
        "type": "generation_progress",
        "data": progress_data
    })
    await manager.send_personal_message(message, user_id)

async def send_system_notification(user_id: int, notification: dict):
    """Send system notification to user"""
    message = json.dumps({
        "type": "notification",
        "data": notification
    })
    await manager.send_personal_message(message, user_id)