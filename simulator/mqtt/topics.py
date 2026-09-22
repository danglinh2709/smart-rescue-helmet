import re


_DEVICE_ID = re.compile(r"^[A-Z][A-Z0-9_-]{2,31}$")
_MESSAGE_TYPES = {"telemetry", "event", "status", "health"}


def validate_device_id(device_id: str) -> str:
    if not _DEVICE_ID.fullmatch(device_id):
        raise ValueError(
            "device_id must be 3-32 topic-safe uppercase characters"
        )
    return device_id


def build_topic(device_id: str, message_type: str) -> str:
    validate_device_id(device_id)
    if message_type not in _MESSAGE_TYPES:
        raise ValueError(f"unsupported MQTT message type: {message_type}")
    return f"helmet/{device_id}/{message_type}"
