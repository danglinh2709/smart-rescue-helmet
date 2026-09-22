from datetime import timedelta

import pytest
from pydantic import ValidationError


VALID_HEALTH = {
    "schema_version": "1.0",
    "device_id": "RESCUE_TEAM_3",
    "timestamp": "2026-09-20T22:30:20+07:00",
    "source": "HARDWARE",
    "battery": 82.0,
    "uptime_seconds": 12345,
    "wifi": "CONNECTED",
    "mqtt": "CONNECTED",
    "sensors": {"temperature": "OK", "co": "OK", "imu": "OK"},
}


def load_model():
    try:
        from app.schemas.device_health import DeviceHealthMessage
    except ModuleNotFoundError as exc:
        pytest.fail(f"DeviceHealthMessage is not implemented: {exc}")
    return DeviceHealthMessage


def test_valid_device_health_is_parsed() -> None:
    message = load_model().model_validate(VALID_HEALTH)

    assert message.device_id == "RESCUE_TEAM_3"
    assert message.timestamp.utcoffset() == timedelta(hours=7)
    assert message.battery == 82.0
    assert message.uptime_seconds == 12345
    assert message.sensors.imu.value == "OK"


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("battery", -0.1),
        ("battery", 120.0),
        ("uptime_seconds", -1),
        ("wifi", "UNKNOWN"),
    ],
)
def test_invalid_device_health_values_are_rejected(
    field: str,
    value: object,
) -> None:
    payload = {**VALID_HEALTH, field: value}

    with pytest.raises(ValidationError):
        load_model().model_validate(payload)


def test_invalid_or_incomplete_sensor_health_is_rejected() -> None:
    invalid = {**VALID_HEALTH, "sensors": {**VALID_HEALTH["sensors"], "imu": "BROKEN"}}
    incomplete = {**VALID_HEALTH, "sensors": {"temperature": "OK", "co": "OK"}}

    with pytest.raises(ValidationError):
        load_model().model_validate(invalid)
    with pytest.raises(ValidationError):
        load_model().model_validate(incomplete)


def test_device_health_rejects_extra_fields() -> None:
    with pytest.raises(ValidationError):
        load_model().model_validate({**VALID_HEALTH, "unexpected": True})
