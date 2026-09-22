import pytest


def test_contract_enums_expose_all_supported_wire_values() -> None:
    try:
        from app.core.enums import (
            ConnectionStatus,
            DataSource,
            DeviceStatus,
            EventSeverity,
            EventType,
            MovementState,
            RiskLevel,
            SensorStatus,
        )
    except ModuleNotFoundError as exc:
        pytest.fail(f"Contract enums are not implemented: {exc}")

    assert {item.value for item in RiskLevel} == {
        "NORMAL",
        "WARNING",
        "CRITICAL",
    }
    assert {item.value for item in DeviceStatus} == {"ONLINE", "OFFLINE"}
    assert {item.value for item in ConnectionStatus} == {
        "CONNECTED",
        "DISCONNECTED",
    }
    assert {item.value for item in MovementState} == {
        "UNKNOWN",
        "STATIONARY",
        "WALKING",
        "RUNNING",
        "CRAWLING",
        "UNUSUAL_MOVEMENT",
        "FALL",
        "IMMOBILE",
    }
    assert {item.value for item in EventType} == {
        "TEMPERATURE_HIGH",
        "CO_HIGH",
        "UNUSUAL_MOVEMENT",
        "FALL_DETECTED",
        "IMMOBILE",
        "SOS_PRESSED",
        "LOW_BATTERY",
        "DEVICE_OFFLINE",
        "MQTT_DISCONNECTED",
        "MQTT_RECONNECTED",
    }
    assert {item.value for item in EventSeverity} == {
        "INFO",
        "WARNING",
        "CRITICAL",
    }
    assert {item.value for item in DataSource} == {"SIMULATOR", "HARDWARE"}
    assert {item.value for item in SensorStatus} == {
        "OK",
        "ERROR",
        "UNAVAILABLE",
    }
