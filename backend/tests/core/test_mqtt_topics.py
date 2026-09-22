import pytest
from pydantic import ValidationError


def load_topic_builders():
    try:
        from app.core.mqtt_topics import (
            build_event_topic,
            build_health_topic,
            build_status_topic,
            build_telemetry_topic,
        )
    except ModuleNotFoundError as exc:
        pytest.fail(f"MQTT topic helpers are not implemented: {exc}")

    return (
        build_telemetry_topic,
        build_event_topic,
        build_status_topic,
        build_health_topic,
    )


def test_topic_builders_use_the_shared_device_namespace() -> None:
    telemetry, event, status, health = load_topic_builders()

    assert telemetry("FF01") == "helmet/FF01/telemetry"
    assert event("FF02") == "helmet/FF02/event"
    assert status("RESCUE_TEAM_3") == "helmet/RESCUE_TEAM_3/status"
    assert health("HELMET-04") == "helmet/HELMET-04/health"


@pytest.mark.parametrize("device_id", ["ff01", "FF/01", "FF+01", "FF#01", "A"])
def test_topic_builders_reject_device_ids_that_are_not_topic_safe(
    device_id: str,
) -> None:
    telemetry, _, _, _ = load_topic_builders()

    with pytest.raises(ValidationError):
        telemetry(device_id)
