import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.services.device_state import devices
from app.websocket.service import manager


LOGGER = logging.getLogger(__name__)
router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    await manager.connect(websocket)
    await manager.send_initial_state(websocket, list(devices.values()))

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception:
        LOGGER.warning("WebSocket connection ended unexpectedly")
        manager.disconnect(websocket)
