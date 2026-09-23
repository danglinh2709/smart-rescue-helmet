from datetime import datetime, timezone

from app.core.enums import RiskLevel
from app.safety.engine import SafetyEngine
from app.schemas.telemetry import TelemetryMessage


def create_telemetry(
    temperature=30.0,
    co=10.0,
    battery=90.0,
    fall=False,
    immobile=False,
    sos=False,
):
    return TelemetryMessage.model_validate(
        {
            "schema_version": "1.0",
            "device_id": "FF01",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "SIMULATOR",
            "sensors": {
                "temperature": temperature,
                "co": co,
                "imu": {
                    "ax": 0.0,
                    "ay": 0.0,
                    "az": 1.0,
                    "gx": 0.0,
                    "gy": 0.0,
                    "gz": 0.0,
                },
            },
            "state": {
                "movement": "WALKING",
                "fall": fall,
                "immobile": immobile,
                "sos": sos,
            },
            "risk_level": "NORMAL",
            "device": {
                "battery": battery,
                "wifi": "CONNECTED",
                "mqtt": "CONNECTED",
            },
        }
    )


def test_normal():
    telemetry = create_telemetry()

    result = SafetyEngine().evaluate(telemetry)

    assert result.risk_level == RiskLevel.NORMAL
    assert result.reasons == []


def test_high_temperature_warning():
    telemetry = create_telemetry(
        temperature=55.0,
    )

    result = SafetyEngine().evaluate(telemetry)

    assert result.risk_level == RiskLevel.WARNING
    assert "HIGH_TEMPERATURE" in result.reasons


def test_critical_temperature():
    telemetry = create_telemetry(
        temperature=65.0,
    )

    result = SafetyEngine().evaluate(telemetry)

    assert result.risk_level == RiskLevel.CRITICAL
    assert "CRITICAL_TEMPERATURE" in result.reasons


def test_high_co_warning():
    telemetry = create_telemetry(
        co=60.0,
    )

    result = SafetyEngine().evaluate(telemetry)

    assert result.risk_level == RiskLevel.WARNING
    assert "HIGH_CO" in result.reasons


def test_critical_co():
    telemetry = create_telemetry(
        co=120.0,
    )

    result = SafetyEngine().evaluate(telemetry)

    assert result.risk_level == RiskLevel.CRITICAL
    assert "CRITICAL_CO" in result.reasons


def test_sos_is_critical():
    telemetry = create_telemetry(
        sos=True,
    )

    result = SafetyEngine().evaluate(telemetry)

    assert result.risk_level == RiskLevel.CRITICAL
    assert "SOS_PRESSED" in result.reasons


def test_fall_is_critical():
    telemetry = create_telemetry(
        fall=True,
    )

    result = SafetyEngine().evaluate(telemetry)

    assert result.risk_level == RiskLevel.CRITICAL
    assert "FALL_DETECTED" in result.reasons


def test_fall_and_immobile_is_critical():
    telemetry = create_telemetry(
        fall=True,
        immobile=True,
    )

    result = SafetyEngine().evaluate(telemetry)

    assert result.risk_level == RiskLevel.CRITICAL
    assert "FALL_AND_IMMOBILE" in result.reasons


def test_low_battery_warning():
    telemetry = create_telemetry(
        battery=15.0,
    )

    result = SafetyEngine().evaluate(telemetry)

    assert result.risk_level == RiskLevel.WARNING
    assert "LOW_BATTERY" in result.reasons

def test_low_battery_at_threshold():
    telemetry = create_telemetry(
        battery=20.0,
    )

    result = SafetyEngine().evaluate(telemetry)

    assert result.risk_level == RiskLevel.WARNING
    assert "LOW_BATTERY" in result.reasons

def test_temperature_and_co_warning():
    telemetry = create_telemetry(
        temperature=55.0,
        co=60.0,
    )

    result = SafetyEngine().evaluate(telemetry)

    assert result.risk_level == RiskLevel.WARNING

    assert "HIGH_TEMPERATURE" in result.reasons
    assert "HIGH_CO" in result.reasons


def test_critical_temperature_and_co():
    telemetry = create_telemetry(
        temperature=65.0,
        co=120.0,
    )

    result = SafetyEngine().evaluate(telemetry)

    assert result.risk_level == RiskLevel.CRITICAL

    assert "CRITICAL_TEMPERATURE" in result.reasons
    assert "CRITICAL_CO" in result.reasons


def test_sos_overrides_warning_conditions():
    telemetry = create_telemetry(
        temperature=55.0,
        co=60.0,
        battery=15.0,
        sos=True,
    )

    result = SafetyEngine().evaluate(telemetry)

    assert result.risk_level == RiskLevel.CRITICAL

    assert "SOS_PRESSED" in result.reasons
    assert "HIGH_TEMPERATURE" in result.reasons
    assert "HIGH_CO" in result.reasons
    assert "LOW_BATTERY" in result.reasons


def test_fall_with_other_critical_conditions():
    telemetry = create_telemetry(
        temperature=65.0,
        co=120.0,
        fall=True,
    )

    result = SafetyEngine().evaluate(telemetry)

    assert result.risk_level == RiskLevel.CRITICAL

    assert "FALL_DETECTED" in result.reasons
    assert "CRITICAL_TEMPERATURE" in result.reasons
    assert "CRITICAL_CO" in result.reasons


def test_fall_and_immobile_with_sos():
    telemetry = create_telemetry(
        fall=True,
        immobile=True,
        sos=True,
    )

    result = SafetyEngine().evaluate(telemetry)

    assert result.risk_level == RiskLevel.CRITICAL

    assert "SOS_PRESSED" in result.reasons
    assert "FALL_AND_IMMOBILE" in result.reasons