from datetime import datetime, timezone
from typing import Any

# Runtime state của tất cả thiết bị
devices: dict[str, dict[str, Any]] = {}


def get_or_create_device(device_id: str) -> dict[str, Any]:
    """Lấy hoặc tạo mới trạng thái của thiết bị."""
    if device_id not in devices:
        devices[device_id] = {
            "device_id": device_id,
            "telemetry": None,
            "status": None,
            "health": None,
            "event": None,
            "last_seen": None,
            "device_status": "ONLINE",
            "actuators": None,
            "active_safety_event": None,
        }
    return devices[device_id]


def update_device(device_id: str, field: str, value: dict) -> None:
    """Cập nhật trạng thái mới nhất của thiết bị."""
    device = get_or_create_device(device_id)
    device[field] = value


def should_emit_safety_event(
    device_id: str,
    event_type: str | None,
    severity: str | None,
) -> bool:
    """Return whether a safety condition is a new transition for a device."""
    if event_type is None or severity is None:
        return False
    return get_or_create_device(device_id)["active_safety_event"] != {
        "event_type": event_type,
        "severity": severity,
    }


def record_safety_event(
    device_id: str,
    event_type: str | None,
    severity: str | None,
) -> None:
    """Record the active safety condition after its persistence succeeds."""
    device = get_or_create_device(device_id)
    if event_type is None or severity is None:
        device["active_safety_event"] = None
        return
    device["active_safety_event"] = {
        "event_type": event_type,
        "severity": severity,
    }


def touch_device(device_id: str, *, now: datetime | None = None) -> bool:
    """Record a valid device message and return whether it recovered."""
    device = get_or_create_device(device_id)
    was_offline = device["device_status"] == "OFFLINE"
    observed_at = now or datetime.now(timezone.utc)
    device["last_seen"] = observed_at.isoformat()
    device["device_status"] = "ONLINE"
    return was_offline


def check_offline_devices(
    *, now: datetime | None = None, timeout_seconds: float
) -> list[str]:
    """Transition stale online devices once and return their identifiers."""
    current = now or datetime.now(timezone.utc)
    transitioned: list[str] = []
    for device_id, device in devices.items():
        last_seen = device.get("last_seen")
        if device.get("device_status") != "ONLINE" or not last_seen:
            continue
        observed_at = datetime.fromisoformat(last_seen)
        if (current - observed_at).total_seconds() > timeout_seconds:
            device["device_status"] = "OFFLINE"
            transitioned.append(device_id)
    return transitioned
