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
        }
    return devices[device_id]


def update_device(device_id: str, field: str, value: dict) -> None:
    """Cập nhật trạng thái mới nhất của thiết bị."""
    device = get_or_create_device(device_id)
    device[field] = value