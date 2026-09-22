from datetime import timedelta
from uuid import UUID

import pytest
from pydantic import ValidationError


VALID_EVENT = {
    "schema_version": "1.0",
    "event_id": "7f3d9f8b-82c7-46ce-9b6e-84fa53eb4991",
    "device_id": "FF01",
    "timestamp": "2026-09-20T22:30:10+07:00",
    "source": "HARDWARE",
    "event_type": "FALL_DETECTED",
    "severity": "CRITICAL",
    "data": {"ax": 10.2, "ay": 1.1, "az": 3.4},
}


def load_model():
    try:
        from app.schemas.event import EventMessage
    except ModuleNotFoundError as exc:
        pytest.fail(f"EventMessage is not implemented: {exc}")
    return EventMessage


def test_valid_event_parses_uuid_timestamp_and_context_data() -> None:
    message = load_model().model_validate(VALID_EVENT)

    assert message.event_id == UUID("7f3d9f8b-82c7-46ce-9b6e-84fa53eb4991")
    assert message.timestamp.utcoffset() == timedelta(hours=7)
    assert message.event_type.value == "FALL_DETECTED"
    assert message.severity.value == "CRITICAL"
    assert message.data == {"ax": 10.2, "ay": 1.1, "az": 3.4}


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("event_id", "not-a-uuid"),
        ("event_type", "UNKNOWN_EVENT"),
        ("severity", "EMERGENCY"),
        ("timestamp", "2026-09-20T22:30:10"),
    ],
)
def test_invalid_event_fields_are_rejected(field: str, value: object) -> None:
    payload = {**VALID_EVENT, field: value}

    with pytest.raises(ValidationError):
        load_model().model_validate(payload)


def test_event_rejects_extra_top_level_fields_but_allows_flexible_data() -> None:
    flexible = {
        **VALID_EVENT,
        "data": {"reason": "manual", "samples": [1, 2, 3], "confirmed": True},
    }
    message = load_model().model_validate(flexible)
    assert message.data["reason"] == "manual"

    with pytest.raises(ValidationError):
        load_model().model_validate({**VALID_EVENT, "unexpected": "value"})
