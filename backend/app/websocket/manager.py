from __future__ import annotations

import logging
from typing import Any

from fastapi import WebSocket

from app.websocket.schemas import build_realtime_message


LOGGER = logging.getLogger(__name__)


class ConnectionManager:
    """Own active WebSocket connections and best-effort realtime delivery."""

    def __init__(self) -> None:
        self._connections: list[WebSocket] = []

    @property
    def connection_count(self) -> int:
        return len(self._connections)

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self._connections.append(websocket)
        LOGGER.info("WebSocket connected active_connections=%s", self.connection_count)

    def disconnect(self, websocket: WebSocket) -> None:
        if websocket in self._connections:
            self._connections.remove(websocket)
            LOGGER.info(
                "WebSocket disconnected active_connections=%s",
                self.connection_count,
            )

    def clear(self) -> None:
        """Clear tracked connections; intended for application shutdown and tests."""
        self._connections.clear()

    async def send_initial_state(
        self,
        websocket: WebSocket,
        devices: list[dict[str, Any]],
    ) -> None:
        await websocket.send_json(
            build_realtime_message("initial_state", data=devices)
        )

    async def broadcast(self, message: dict[str, Any]) -> None:
        """Deliver a message without allowing dead clients to stop processing."""
        disconnected: list[WebSocket] = []

        for websocket in list(self._connections):
            try:
                await websocket.send_json(message)
            except Exception:
                LOGGER.warning("WebSocket broadcast failed; removing connection")
                disconnected.append(websocket)

        for websocket in disconnected:
            self.disconnect(websocket)
