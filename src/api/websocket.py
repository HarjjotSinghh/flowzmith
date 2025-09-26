"""
WebSocket implementation for real-time updates in Smart Contract LLM Builder.
"""

import json
import asyncio
import logging
from typing import Dict, List, Optional, Set
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from ..schemas import (
    WebSocketMessage,
    ProgressUpdate,
    LogUpdate,
    StatusUpdate
)

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections for real-time updates."""

    def __init__(self):
        # Active connections by user_id
        self.active_connections: Dict[str, List[WebSocket]] = {}
        # Active connections by session_id (for anonymous connections)
        self.session_connections: Dict[str, WebSocket] = {}
        # Subscription management
        self.user_subscriptions: Dict[str, Set[str]] = {}
        # Connection metadata
        self.connection_metadata: Dict[str, Dict] = {}

    async def connect(self, websocket: WebSocket, user_id: Optional[str] = None, session_id: Optional[str] = None):
        """Accept a WebSocket connection."""
        logger.info(f"=== ConnectionManager.connect called ===")
        logger.info(f"user_id: {user_id}, session_id: {session_id}")
        logger.info(f"WebSocket state: {websocket.client_state}")
        
        # Note: websocket.accept() should already be called by the endpoint
        logger.info("WebSocket already accepted by endpoint")
            
        connection_id = f"{user_id}_{datetime.utcnow().timestamp()}" if user_id else f"session_{session_id}_{datetime.utcnow().timestamp()}"
        logger.info(f"Generated connection_id: {connection_id}")

        if user_id:
            if user_id not in self.active_connections:
                self.active_connections[user_id] = []
            self.active_connections[user_id].append(websocket)
            self.user_subscriptions[user_id] = set()
            logger.info(f"Added user connection: {user_id}")
        elif session_id:
            self.session_connections[session_id] = websocket
            logger.info(f"Added session connection: {session_id}")

        # Store connection metadata
        self.connection_metadata[connection_id] = {
            "user_id": user_id,
            "session_id": session_id,
            "connected_at": datetime.utcnow(),
            "websocket": websocket
        }

        logger.info(f"WebSocket connected: {connection_id}")

        # Send welcome message
        try:
            await self.send_personal_message(
                WebSocketMessage(
                    type="connection_established",
                    data={"connection_id": connection_id},
                    timestamp=datetime.utcnow().isoformat()
                ).dict(),
                websocket
            )
            logger.info("Welcome message sent successfully")
        except Exception as e:
            logger.error(f"Error sending welcome message: {e}")

        return connection_id

    def disconnect(self, websocket: WebSocket, user_id: Optional[str] = None, session_id: Optional[str] = None):
        """Disconnect a WebSocket connection."""
        if user_id and user_id in self.active_connections:
            if websocket in self.active_connections[user_id]:
                self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
                if user_id in self.user_subscriptions:
                    del self.user_subscriptions[user_id]

        if session_id and session_id in self.session_connections:
            del self.session_connections[session_id]

        # Remove from metadata
        to_remove = []
        for conn_id, metadata in self.connection_metadata.items():
            if metadata["websocket"] == websocket:
                to_remove.append(conn_id)

        for conn_id in to_remove:
            del self.connection_metadata[conn_id]

        logger.info(f"WebSocket disconnected")

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send a message to a specific WebSocket connection."""
        try:
            # Convert datetime objects to ISO strings before JSON serialization
            await websocket.send_text(json.dumps(message, default=str))
        except Exception as e:
            logger.error(f"Failed to send WebSocket message: {e}")
            # Connection might be closed, remove it
            self.disconnect(websocket)

    async def broadcast_to_user(self, message: dict, user_id: str):
        """Broadcast a message to all connections of a specific user."""
        if user_id in self.active_connections:
            disconnected = []
            for websocket in self.active_connections[user_id]:
                try:
                    await websocket.send_text(json.dumps(message))
                except Exception as e:
                    logger.error(f"Failed to send message to user {user_id}: {e}")
                    disconnected.append(websocket)

            # Remove disconnected connections
            for websocket in disconnected:
                self.disconnect(websocket, user_id)

    async def broadcast_to_all(self, message: dict):
        """Broadcast a message to all connected users."""
        disconnected_connections = []
        for user_id, connections in self.active_connections.items():
            for websocket in connections:
                try:
                    await websocket.send_text(json.dumps(message))
                except Exception as e:
                    logger.error(f"Failed to broadcast to user {user_id}: {e}")
                    disconnected_connections.append((user_id, websocket))

        # Remove disconnected connections
        for user_id, websocket in disconnected_connections:
            self.disconnect(websocket, user_id)

    async def broadcast_to_session(self, message: dict, session_id: str):
        """Send a message to a specific session."""
        if session_id in self.session_connections:
            try:
                await self.session_connections[session_id].send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Failed to send message to session {session_id}: {e}")
                self.disconnect(self.session_connections[session_id], session_id=session_id)

    def add_subscription(self, user_id: str, subscription_type: str):
        """Add a subscription for a user."""
        if user_id not in self.user_subscriptions:
            self.user_subscriptions[user_id] = set()
        self.user_subscriptions[user_id].add(subscription_type)

    def remove_subscription(self, user_id: str, subscription_type: str):
        """Remove a subscription for a user."""
        if user_id in self.user_subscriptions:
            self.user_subscriptions[user_id].discard(subscription_type)

    def get_user_subscriptions(self, user_id: str) -> Set[str]:
        """Get user subscriptions."""
        return self.user_subscriptions.get(user_id, set())

    def get_connection_stats(self) -> Dict[str, int]:
        """Get connection statistics."""
        return {
            "total_users": len(self.active_connections),
            "total_sessions": len(self.session_connections),
            "total_connections": sum(len(conns) for conns in self.active_connections.values()) + len(self.session_connections)
        }


# Global connection manager
manager = ConnectionManager()


class WebSocketHandler:
    """Handles WebSocket messages and events."""

    def __init__(self, db_session: Session):
        self.db_session = db_session

    async def handle_message(self, websocket: WebSocket, message: str, connection_id: str):
        """Handle incoming WebSocket messages."""
        try:
            data = json.loads(message)
            message_type = data.get("type")

            if message_type == "subscribe":
                await self._handle_subscribe(websocket, data, connection_id)
            elif message_type == "unsubscribe":
                await self._handle_unsubscribe(websocket, data, connection_id)
            elif message_type == "ping":
                await self._handle_ping(websocket, connection_id)
            elif message_type == "get_status":
                await self._handle_get_status(websocket, connection_id)
            else:
                await self._handle_unknown_message(websocket, message_type)

        except json.JSONDecodeError:
            await manager.send_personal_message(
                WebSocketMessage(
                    type="error",
                    data={"message": "Invalid JSON format"},
                    timestamp=datetime.utcnow().isoformat()
                ).dict(),
                websocket
            )
        except Exception as e:
            logger.error(f"Error handling WebSocket message: {e}")
            await manager.send_personal_message(
                WebSocketMessage(
                    type="error",
                    data={"message": "Internal server error"},
                    timestamp=datetime.utcnow().isoformat()
                ).dict(),
                websocket
            )

    async def _handle_subscribe(self, websocket: WebSocket, data: dict, connection_id: str):
        """Handle subscription requests."""
        subscription_type = data.get("subscription_type")
        metadata = manager.connection_metadata.get(connection_id, {})
        user_id = metadata.get("user_id")

        if user_id:
            manager.add_subscription(user_id, subscription_type)
            await manager.send_personal_message(
                WebSocketMessage(
                    type="subscription_confirmed",
                    data={"subscription_type": subscription_type},
                    timestamp=datetime.utcnow().isoformat()
                ).dict(),
                websocket
            )
        else:
            await manager.send_personal_message(
                WebSocketMessage(
                    type="error",
                    data={"message": "Authentication required for subscriptions"},
                    timestamp=datetime.utcnow().isoformat()
                ).dict(),
                websocket
            )

    async def _handle_unsubscribe(self, websocket: WebSocket, data: dict, connection_id: str):
        """Handle unsubscription requests."""
        subscription_type = data.get("subscription_type")
        metadata = manager.connection_metadata.get(connection_id, {})
        user_id = metadata.get("user_id")

        if user_id:
            manager.remove_subscription(user_id, subscription_type)
            await manager.send_personal_message(
                WebSocketMessage(
                    type="unsubscription_confirmed",
                    data={"subscription_type": subscription_type},
                    timestamp=datetime.utcnow().isoformat()
                ).dict(),
                websocket
            )

    async def _handle_ping(self, websocket: WebSocket, connection_id: str):
        """Handle ping messages."""
        await manager.send_personal_message(
            WebSocketMessage(
                type="pong",
                data={"timestamp": datetime.utcnow().isoformat()},
                timestamp=datetime.utcnow().isoformat()
            ).dict(),
            websocket
        )

    async def _handle_get_status(self, websocket: WebSocket, connection_id: str):
        """Handle status requests."""
        metadata = manager.connection_metadata.get(connection_id, {})
        user_id = metadata.get("user_id")

        status_data = {
            "connection_id": connection_id,
            "connected_at": metadata.get("connected_at").isoformat(),
            "subscriptions": list(manager.get_user_subscriptions(user_id)) if user_id else []
        }

        await manager.send_personal_message(
            WebSocketMessage(
                type="status",
                data=status_data,
                timestamp=datetime.utcnow().isoformat()
            ).dict(),
            websocket
        )

    async def _handle_unknown_message(self, websocket: WebSocket, message_type: str):
        """Handle unknown message types."""
        await manager.send_personal_message(
            WebSocketMessage(
                type="error",
                data={"message": f"Unknown message type: {message_type}"},
                timestamp=datetime.utcnow().isoformat()
            ).dict(),
            websocket
        )


class ProgressTracker:
    """Tracks and broadcasts progress for long-running operations."""

    def __init__(self):
        self.active_operations: Dict[str, Dict] = {}

    def start_operation(self, operation_id: str, operation_type: str, user_id: str, total_steps: int = 100):
        """Start tracking a new operation."""
        self.active_operations[operation_id] = {
            "type": operation_type,
            "user_id": user_id,
            "current_step": 0,
            "total_steps": total_steps,
            "progress": 0.0,
            "status": "in_progress",
            "started_at": datetime.utcnow(),
            "messages": []
        }

    def update_progress(self, operation_id: str, current_step: int, message: str = None):
        """Update operation progress."""
        if operation_id in self.active_operations:
            operation = self.active_operations[operation_id]
            operation["current_step"] = current_step
            operation["progress"] = (current_step / operation["total_steps"]) * 100

            if message:
                operation["messages"].append({
                    "step": current_step,
                    "message": message,
                    "timestamp": datetime.utcnow()
                })

            # Broadcast progress update
            asyncio.create_task(self._broadcast_progress_update(operation_id))

    def complete_operation(self, operation_id: str, success: bool = True, result: dict = None):
        """Mark an operation as completed."""
        if operation_id in self.active_operations:
            operation = self.active_operations[operation_id]
            operation["status"] = "completed" if success else "failed"
            operation["progress"] = 100.0
            operation["completed_at"] = datetime.utcnow()
            operation["result"] = result

            # Broadcast final update
            asyncio.create_task(self._broadcast_progress_update(operation_id))

            # Remove from active operations after a delay
            asyncio.create_task(self._cleanup_operation(operation_id))

    async def _broadcast_progress_update(self, operation_id: str):
        """Broadcast progress update to subscribed users."""
        if operation_id in self.active_operations:
            operation = self.active_operations[operation_id]
            user_id = operation["user_id"]

            progress_update = ProgressUpdate(
                stage=operation["type"],
                progress=operation["progress"],
                message=f"Step {operation['current_step']} of {operation['total_steps']}",
                data={"operation_id": operation_id}
            )

            await manager.broadcast_to_user(progress_update.dict(), user_id)

    async def _cleanup_operation(self, operation_id: str):
        """Clean up completed operations."""
        await asyncio.sleep(300)  # Keep for 5 minutes
        if operation_id in self.active_operations:
            del self.active_operations[operation_id]

    def get_operation_status(self, operation_id: str) -> Optional[dict]:
        """Get the status of an operation."""
        return self.active_operations.get(operation_id)


# Global progress tracker
progress_tracker = ProgressTracker()


class EventBroadcaster:
    """Broadcasts system events to subscribed users."""

    @staticmethod
    async def broadcast_deployment_update(deployment_id: str, user_id: str, status: str, message: str = None):
        """Broadcast deployment status updates."""
        if "deployments" in manager.get_user_subscriptions(user_id):
            await manager.broadcast_to_user(
                StatusUpdate(
                    status=status,
                    details={
                        "deployment_id": deployment_id,
                        "message": message
                    }
                ).dict(),
                user_id
            )

    @staticmethod
    async def broadcast_learning_update(user_id: str, pattern_type: str, insights: dict):
        """Broadcast learning pattern updates."""
        if "learning" in manager.get_user_subscriptions(user_id):
            await manager.broadcast_to_user(
                StatusUpdate(
                    status="new_learning_pattern",
                    details={
                        "pattern_type": pattern_type,
                        "insights": insights
                    }
                ).dict(),
                user_id
            )

    @staticmethod
    async def broadcast_system_notification(message: str, level: str = "INFO"):
        """Broadcast system-wide notifications."""
        await manager.broadcast_to_all(
            LogUpdate(
                level=level,
                message=message,
                timestamp=datetime.utcnow()
            ).dict()
        )

    @staticmethod
    async def broadcast_user_activity(user_id: str, activity_type: str, details: dict):
        """Broadcast user-specific activity updates."""
        if "activity" in manager.get_user_subscriptions(user_id):
            await manager.broadcast_to_user(
                StatusUpdate(
                    status="user_activity",
                    details={
                        "activity_type": activity_type,
                        "details": details
                    }
                ).dict(),
                user_id
            )