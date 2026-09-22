from datetime import timedelta

import pytest
from pydantic import ValidationError


VALID_STATUS = {
    "schema_version": "1.0",
    "device_id": "HELMET-04",
    "timestamp": "2026-09-20T22:30:15+07:00",
    "source": "SIMULATOR",
    "device_status": "ONLINE",
    "risk_level": "NORMAL",
    "movement": "WALKING",
    "fall": False,
    "immobile": False,
    "sos": False,
}


def load_model():
    try:
        from app.schemas.device_status import DeviceStatusMessage
    except ModuleNotFoundError as exc:
        pytest.fail(f"DeviceStatusMessage is not implemented: {exc}")
    return DeviceStatusMessage


def test_valid_device_status_is_parsed() -> None:
    message = load_model().model_validate(VALID_STATUS)

    assert message.device_id == "HELMET-04"
    assert message.timestamp.utcoffset() == timedelta(hours=7)
    assert message.device_status.value == "ONLINE"
    assert message.risk_level.value == "NORMAL"
    assert message.movement.value == "WALKING"


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("device_status", "SLEEPING"),
        ("movement", "JUMPING"),
        ("source", "TEST"),
        ("device_id", "helmet/04"),
    ],
)
def test_invalid_device_status_values_are_rejected(
    field: str,
    value: object,
) -> None:
    payload = {**VALID_STATUS, field: value}

    with pytest.raises(ValidationError):
        load_model().model_validate(payload)


def test_device_status_rejects_extra_fields() -> None:
    with pytest.raises(ValidationError):
        load_model().model_validate({**VALID_STATUS, "unexpected": True})
