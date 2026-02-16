"""WebSocket connection manager for real-time timer broadcasts."""

import asyncio
from typing import Any

from fastapi import WebSocket

from app.core.logging import get_logger

logger = get_logger(__name__)


class TimerConnectionManager:
    """Manages WebSocket connections for pomodoro timer sessions."""

    def __init__(self) -> None:
        """Initialize the connection manager."""
        # session_id -> list of WebSocket connections
        self.active_connections: dict[str, list[WebSocket]] = {}
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket, session_id: str) -> None:
        """Accept and register a new WebSocket connection."""
        await websocket.accept()

        async with self._lock:
            if session_id not in self.active_connections:
                self.active_connections[session_id] = []
            self.active_connections[session_id].append(websocket)

        logger.info(
            "pomodoro.websocket.connected",
            session_id=session_id,
            connection_count=len(self.active_connections.get(session_id, [])),
        )

    async def disconnect(self, websocket: WebSocket, session_id: str) -> None:
        """Remove a WebSocket connection from the registry."""
        async with self._lock:
            if session_id in self.active_connections:
                try:
                    self.active_connections[session_id].remove(websocket)
                    if not self.active_connections[session_id]:
                        del self.active_connections[session_id]
                except ValueError:
                    pass  # Connection already removed

        logger.info(
            "pomodoro.websocket.disconnected",
            session_id=session_id,
            remaining_connections=len(self.active_connections.get(session_id, [])),
        )

    async def send_personal(self, message: dict[str, Any], websocket: WebSocket) -> bool:
        """Send a message to a specific WebSocket connection.

        Returns True if successful, False otherwise.
        """
        try:
            await websocket.send_json(message)
            return True
        except Exception as e:
            logger.warning(
                "pomodoro.websocket.send_failed",
                error=str(e),
            )
            return False

    async def broadcast_to_session(self, session_id: str, message: dict[str, Any]) -> None:
        """Broadcast a message to all connections for a session."""
        if session_id not in self.active_connections:
            return

        dead_connections: list[WebSocket] = []

        for connection in self.active_connections[session_id]:
            success = await self.send_personal(message, connection)
            if not success:
                dead_connections.append(connection)

        # Clean up dead connections
        async with self._lock:
            for dead in dead_connections:
                try:
                    self.active_connections[session_id].remove(dead)
                except (ValueError, KeyError):
                    pass

            # Remove session if no connections left
            if session_id in self.active_connections and not self.active_connections[session_id]:
                del self.active_connections[session_id]

    def get_connection_count(self, session_id: str | None = None) -> int:
        """Get the number of active connections.

        If session_id is provided, returns count for that session.
        Otherwise returns total count across all sessions.
        """
        if session_id:
            return len(self.active_connections.get(session_id, []))
        return sum(len(conns) for conns in self.active_connections.values())


# Singleton instance
timer_manager = TimerConnectionManager()
