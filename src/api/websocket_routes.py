"""
WebSocket routes for real-time updates.
"""

import logging
import json
from typing import Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from sqlalchemy.orm import Session

from .websocket import manager, WebSocketHandler, progress_tracker, EventBroadcaster
from ..models.database import get_db

logger = logging.getLogger(__name__)

websocket_router = APIRouter()


@websocket_router.websocket("/api/v1/ws/{user_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    user_id: str,
    db: Session = Depends(get_db)
):
    """WebSocket endpoint for authenticated users."""
    try:
        # Validate user exists
        from ..models import User
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            await websocket.close(code=4001, reason="User not found")
            return

        # Accept connection
        connection_id = await manager.connect(websocket, user_id=user_id)
        handler = WebSocketHandler(db)

        try:
            while True:
                # Wait for messages
                message = await websocket.receive_text()
                await handler.handle_message(websocket, message, connection_id)

        except WebSocketDisconnect:
            manager.disconnect(websocket, user_id=user_id)
            logger.info(f"User {user_id} disconnected from WebSocket")

    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {e}")
        try:
            await websocket.close(code=1011, reason="Internal server error")
        except:
            pass


@websocket_router.websocket("/api/v1/ws/session/{session_id}")
async def session_websocket_endpoint(
    websocket: WebSocket,
    session_id: str,
    db: Session = Depends(get_db)
):
    """WebSocket endpoint for anonymous sessions."""
    try:
        # Accept connection
        connection_id = await manager.connect(websocket, session_id=session_id)
        handler = WebSocketHandler(db)

        try:
            while True:
                # Wait for messages
                message = await websocket.receive_text()
                await handler.handle_message(websocket, message, connection_id)

        except WebSocketDisconnect:
            manager.disconnect(websocket, session_id=session_id)
            logger.info(f"Session {session_id} disconnected from WebSocket")

    except Exception as e:
        logger.error(f"WebSocket error for session {session_id}: {e}")
        try:
            await websocket.close(code=1011, reason="Internal server error")
        except:
            pass


@websocket_router.websocket("/ws")
async def public_websocket_endpoint(
    websocket: WebSocket,
    db: Session = Depends(get_db)
):
    """Public WebSocket endpoint for basic real-time updates without authentication."""
    logger.info("=== WebSocket endpoint reached: /ws ===")
    logger.info(f"WebSocket client: {websocket.client}")
    logger.info(f"WebSocket headers: {dict(websocket.headers)}")
    logger.info(f"WebSocket query params: {websocket.query_params}")
    logger.info(f"WebSocket path: {websocket.url.path}")
    logger.info(f"WebSocket scheme: {websocket.url.scheme}")
    
    try:
        # Generate a random session ID for this connection
        import uuid
        session_id = str(uuid.uuid4())

        # Accept connection
        logger.info(f"Attempting to accept WebSocket connection for session: {session_id}")
        await websocket.accept()
        logger.info(f"WebSocket connection accepted successfully for session: {session_id}")
        
        connection_id = await manager.connect(websocket, session_id=session_id)
        logger.info(f"Manager connected WebSocket with connection_id: {connection_id}")

        logger.info(f"New public WebSocket connection established: {session_id}")

        try:
            while True:
                # Wait for messages
                message = await websocket.receive_text()
                # Handle basic messages without authentication
                try:
                    data = json.loads(message)
                    if data.get('type') == 'ping':
                        await websocket.send_text(json.dumps({'type': 'pong'}))
                    elif data.get('type') == 'subscribe':
                        # Handle subscription to system events
                        await websocket.send_text(json.dumps({
                            'type': 'subscribed',
                            'message': 'Subscribed to system updates'
                        }))
                except:
                    # Send error for invalid JSON
                    await websocket.send_text(json.dumps({
                        'type': 'error',
                        'message': 'Invalid message format'
                    }))

        except WebSocketDisconnect:
            manager.disconnect(websocket, session_id=session_id)
            logger.info(f"Public WebSocket session {session_id} disconnected")

    except Exception as e:
        logger.error(f"Public WebSocket error: {e}")
        try:
            await websocket.close(code=1011, reason="Internal server error")
        except:
            pass


# Helper functions for WebSocket operations
async def broadcast_progress_update(
    operation_id: str,
    current_step: int,
    message: str = None
):
    """Update progress for an operation."""
    progress_tracker.update_progress(operation_id, current_step, message)


async def complete_operation(
    operation_id: str,
    success: bool = True,
    result: dict = None
):
    """Mark an operation as completed."""
    progress_tracker.complete_operation(operation_id, success, result)


async def start_operation(
    operation_id: str,
    operation_type: str,
    user_id: str,
    total_steps: int = 100
):
    """Start tracking a new operation."""
    progress_tracker.start_operation(operation_id, operation_type, user_id, total_steps)


# Utility functions for different operation types
async def track_contract_generation(user_id: str, submission_id: str):
    """Track contract generation progress."""
    operation_id = f"contract_gen_{submission_id}"
    await start_operation(operation_id, "contract_generation", user_id, total_steps=5)

    # Progress updates would be called from the generation process
    await broadcast_progress_update(operation_id, 1, "Analyzing requirements")
    await broadcast_progress_update(operation_id, 2, "Generating contract code")
    await broadcast_progress_update(operation_id, 3, "Creating configuration")
    await broadcast_progress_update(operation_id, 4, "Validating output")
    await broadcast_progress_update(operation_id, 5, "Generation complete")

    await complete_operation(operation_id, True, {"submission_id": submission_id})


async def track_deployment(user_id: str, deployment_id: str):
    """Track deployment progress."""
    operation_id = f"deployment_{deployment_id}"
    await start_operation(operation_id, "deployment", user_id, total_steps=4)

    # Progress updates would be called from the deployment process
    await broadcast_progress_update(operation_id, 1, "Preparing deployment")
    await broadcast_progress_update(operation_id, 2, "Executing deployment")
    await broadcast_progress_update(operation_id, 3, "Confirming transaction")
    await broadcast_progress_update(operation_id, 4, "Deployment complete")

    await complete_operation(operation_id, True, {"deployment_id": deployment_id})


# WebSocket management endpoints
@websocket_router.get("/api/v1/ws/stats")
async def get_websocket_stats():
    """Get WebSocket connection statistics."""
    return manager.get_connection_stats()


@websocket_router.get("/api/v1/ws/operations/{operation_id}")
async def get_operation_status(operation_id: str):
    """Get the status of a specific operation."""
    status = progress_tracker.get_operation_status(operation_id)
    if not status:
        raise HTTPException(status_code=404, detail="Operation not found")
    return status


# Event broadcasting utilities
class WebSocketEvents:
    """Utility class for broadcasting events via WebSocket."""

    @staticmethod
    async def deployment_started(deployment_id: str, user_id: str):
        """Broadcast deployment started event."""
        await EventBroadcaster.broadcast_deployment_update(
            deployment_id, user_id, "started", "Deployment started"
        )

    @staticmethod
    async def deployment_completed(deployment_id: str, user_id: str, success: bool):
        """Broadcast deployment completed event."""
        status = "success" if success else "failed"
        await EventBroadcaster.broadcast_deployment_update(
            deployment_id, user_id, status, f"Deployment {status}"
        )

    @staticmethod
    async def learning_pattern_detected(user_id: str, pattern_type: str, insights: dict):
        """Broadcast new learning pattern detected."""
        await EventBroadcaster.broadcast_learning_update(user_id, pattern_type, insights)

    @staticmethod
    async def system_notification(message: str, level: str = "INFO"):
        """Broadcast system-wide notification."""
        await EventBroadcaster.broadcast_system_notification(message, level)

    @staticmethod
    async def user_activity(user_id: str, activity_type: str, details: dict):
        """Broadcast user activity update."""
        await EventBroadcaster.broadcast_user_activity(user_id, activity_type, details)