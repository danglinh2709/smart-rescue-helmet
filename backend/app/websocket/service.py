from __future__ import annotations

from typing import Any

from app.services.device_state import devices
from app.websocket.manager import ConnectionManager
from app.websocket.schemas import RealtimeMessageType, build_realtime_message


manager = ConnectionManager()


async def publish_realtime_message(
    message_type: RealtimeMessageType,
    *,
    device_id: str,
    timestamp: str,
    data: dict[str, Any],
) -> None:
    await manager.broadcast(
        build_realtime_message(
            message_type,
            device_id=device_id,
            timestamp=timestamp,
            data=data,
        )
    )


def build_device_state_snapshot(device_id: str) -> dict[str, Any]:
    state = devices.get(device_id, {})
    telemetry = state.get("telemetry")
    status = state.get("status")
    health = state.get("health")

    return {
        "device_id": device_id,
        "device_status": state.get("device_status") or (
            status.get("device_status") if status else None
        ),
        "last_seen": state.get("last_seen"),
        "risk_level": (
            telemetry.get("risk_level")
            if telemetry
            else status.get("risk_level") if status else None
        ),
        "movement": (
            telemetry.get("state", {}).get("movement")
            if telemetry
            else status.get("movement") if status else None
        ),
        "latest_telemetry": telemetry,
        "latest_health": health,
        "latest_event": state.get("event"),
        "actuators": state.get("actuators"),
    }


async def publish_device_state(device_id: str) -> None:
    state = devices.get(device_id, {})
    timestamp = ""
    for field in ("telemetry", "status", "health", "event"):
        value = state.get(field)
        if value and value.get("timestamp"):
            timestamp = value["timestamp"]
            break

    await publish_realtime_message(
        "device_state",
        device_id=device_id,
        timestamp=timestamp,
        data=build_device_state_snapshot(device_id),
    )
