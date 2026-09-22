from copy import deepcopy
from datetime import timedelta

import pytest
from pydantic import ValidationError


VALID_TELEMETRY = {
    "schema_version": "1.0",
    "device_id": "FF02",
    "timestamp": "2026-09-20T22:30:00+07:00",
    "source": "SIMULATOR",
    "sensors": {
        "temperature": 32.5,
        "co": 12.0,
        "imu": {
            "ax": 0.12,
            "ay": 0.04,
            "az": 9.68,
            "gx": 0.10,
            "gy": 0.20,
            "gz": 0.10,
        },
    },
    "state": {
        "movement": "WALKING",
        "fall": False,
        "immobile": False,
        "sos": False,
    },
    "risk_level": "NORMAL",
    "device": {
        "battery": 82.0,
        "wifi": "CONNECTED",
        "mqtt": "CONNECTED",
    },
}


def load_model():
    try:
        from app.schemas.telemetry import TelemetryMessage
    except ModuleNotFoundError as exc:
        pytest.fail(f"TelemetryMessage is not implemented: {exc}")
    return TelemetryMessage


def test_valid_telemetry_is_parsed_with_timezone_and_enums() -> None:
    message = load_model().model_validate(VALID_TELEMETRY)

    assert message.device_id == "FF02"
    assert message.timestamp.utcoffset() == timedelta(hours=7)
    assert message.source.value == "SIMULATOR"
    assert message.state.movement.value == "WALKING"
    assert message.sensors.imu.az == 9.68
    assert message.device.battery == 82.0


def test_unavailable_temperature_and_co_are_explicitly_nullable() -> None:
    payload = deepcopy(VALID_TELEMETRY)
    payload["sensors"]["temperature"] = None
    payload["sensors"]["co"] = None

    message = load_model().model_validate(payload)

    assert message.sensors.temperature is None
    assert message.sensors.co is None


@pytest.mark.parametrize(
    ("mutation", "value"),
    [
        (("timestamp",), "20-09-2026 22:30:00"),
        (("timestamp",), "2026-09-20T22:30:00"),
        (("device", "battery"), 120.0),
        (("risk_level",), "DANGER"),
        (("schema_version",), "1.1"),
    ],
)
def test_invalid_telemetry_values_are_rejected(
    mutation: tuple[str, ...],
    value: object,
) -> None:
    payload = deepcopy(VALID_TELEMETRY)
    target = payload
    for key in mutation[:-1]:
        target = target[key]
    target[mutation[-1]] = value

    with pytest.raises(ValidationError):
        load_model().model_validate(payload)


def test_missing_device_id_is_rejected() -> None:
    payload = deepcopy(VALID_TELEMETRY)
    del payload["device_id"]

    with pytest.raises(ValidationError):
        load_model().model_validate(payload)


def test_imu_requires_every_axis() -> None:
    payload = deepcopy(VALID_TELEMETRY)
    del payload["sensors"]["imu"]["gz"]

    with pytest.raises(ValidationError):
        load_model().model_validate(payload)


def test_top_level_and_nested_extra_fields_are_rejected() -> None:
    top_level = deepcopy(VALID_TELEMETRY)
    top_level["unexpected"] = True
    nested = deepcopy(VALID_TELEMETRY)
    nested["state"]["unexpected"] = True

    with pytest.raises(ValidationError):
        load_model().model_validate(top_level)
    with pytest.raises(ValidationError):
        load_model().model_validate(nested)
