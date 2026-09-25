from app.services.device_state import (
    devices,
    record_safety_event,
    should_emit_safety_event,
)


def setup_function() -> None:
    devices.clear()


def test_safety_event_is_emitted_once_until_its_condition_recovers() -> None:
    """Repeated critical telemetry must not create an event storm."""
    assert should_emit_safety_event("FF03", "TEMPERATURE_HIGH", "CRITICAL") is True
    record_safety_event("FF03", "TEMPERATURE_HIGH", "CRITICAL")
    assert should_emit_safety_event("FF03", "TEMPERATURE_HIGH", "CRITICAL") is False

    # A NORMAL evaluation clears the active safety condition for this device.
    record_safety_event("FF03", None, None)
    assert should_emit_safety_event("FF03", "TEMPERATURE_HIGH", "CRITICAL") is True


def test_safety_event_is_emitted_when_the_active_severity_changes() -> None:
    assert should_emit_safety_event("FF03", "TEMPERATURE_HIGH", "WARNING") is True
    record_safety_event("FF03", "TEMPERATURE_HIGH", "WARNING")
    assert should_emit_safety_event("FF03", "TEMPERATURE_HIGH", "CRITICAL") is True
