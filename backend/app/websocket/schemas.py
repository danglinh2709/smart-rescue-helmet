from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from fastapi.encoders import jsonable_encoder


RealtimeMessageType = Literal[
    "telemetry",
    "status",
    "health",
    "event",
    "device_state",
    "initial_state",
]


def _to_json_safe(data: Any) -> Any:
    try:
        return jsonable_encoder(data)
    except (TypeError, ValueError):
        return {"serialization_error": "unsupported_payload"}


def build_realtime_message(
    message_type: RealtimeMessageType,
    *,
    device_id: str | None = None,
    timestamp: datetime | str | None = None,
    data: Any,
) -> dict[str, Any]:
    """Build a JSON-safe frontend realtime message."""
    message: dict[str, Any] = {
        "type": message_type,
        "data": _to_json_safe(data),
    }

    if device_id is not None:
        message["device_id"] = device_id

    if timestamp is not None:
        message["timestamp"] = (
            timestamp.isoformat()
            if isinstance(timestamp, datetime)
            else timestamp
        )

    return message
