from app.services.device_state import devices, get_or_create_device
from app.websocket.service import build_device_state_snapshot


def setup_function() -> None:
    devices.clear()


def test_offline_snapshot_includes_backend_status_and_actuators() -> None:
    device = get_or_create_device("FF01")
    device["device_status"] = "OFFLINE"
    device["last_seen"] = "2026-09-24T10:00:00+00:00"
    device["actuators"] = {"led": "RED", "buzzer": True, "vibration": True}

    snapshot = build_device_state_snapshot("FF01")

    assert snapshot["device_status"] == "OFFLINE"
    assert snapshot["last_seen"] == "2026-09-24T10:00:00+00:00"
    assert snapshot["actuators"] == {"led": "RED", "buzzer": True, "vibration": True}
