import asyncio
import json

from app.mqtt.handlers import handle_message
from app.services.device_state import devices


def setup_function() -> None:
    devices.clear()


def test_topic_payload_device_mismatch_is_ignored_before_state_or_persistence() -> None:
    payload = {
        "schema_version": "1.0",
        "device_id": "FF02",
        "timestamp": "2026-09-24T10:00:00+00:00",
        "source": "SIMULATOR",
        "sensors": {
            "temperature": 30.0,
            "co": 3.0,
            "imu": {"ax": 0.0, "ay": 0.0, "az": 9.81, "gx": 0.0, "gy": 0.0, "gz": 0.0},
        },
        "state": {"movement": "WALKING", "fall": False, "immobile": False, "sos": False},
        "risk_level": "NORMAL",
        "device": {"battery": 85.0, "wifi": "CONNECTED", "mqtt": "CONNECTED"},
    }

    asyncio.run(handle_message("helmet/FF01/telemetry", json.dumps(payload)))

    assert devices == {}
