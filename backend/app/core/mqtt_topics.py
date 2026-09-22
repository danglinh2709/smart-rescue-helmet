from pydantic import TypeAdapter

from app.schemas.common import DeviceId


_DEVICE_ID_ADAPTER = TypeAdapter(DeviceId)


def _build_topic(device_id: str, message_type: str) -> str:
    validated_device_id = _DEVICE_ID_ADAPTER.validate_python(device_id)
    return f"helmet/{validated_device_id}/{message_type}"


def build_telemetry_topic(device_id: str) -> str:
    return _build_topic(device_id, "telemetry")


def build_event_topic(device_id: str) -> str:
    return _build_topic(device_id, "event")


def build_status_topic(device_id: str) -> str:
    return _build_topic(device_id, "status")


def build_health_topic(device_id: str) -> str:
    return _build_topic(device_id, "health")
