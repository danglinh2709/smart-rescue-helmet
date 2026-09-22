from app.core.enums import RiskLevel
from app.schemas.telemetry import TelemetryMessage
from app.safety.result import SafetyResult
from app.safety.rules import (
    CO_CRITICAL,
    CO_WARNING,
    LOW_BATTERY,
    TEMPERATURE_CRITICAL,
    TEMPERATURE_WARNING,
)


class SafetyEngine:
    def evaluate(self, telemetry: TelemetryMessage) -> SafetyResult:
        reasons: list[str] = []

        sensors = telemetry.sensors
        state = telemetry.state
        device = telemetry.device

        # =========================================================
        # CRITICAL CONDITIONS
        # =========================================================

        if state.sos:
            reasons.append("SOS_PRESSED")

        if state.fall and state.immobile:
            reasons.append("FALL_AND_IMMOBILE")
        elif state.fall:
            reasons.append("FALL_DETECTED")

        if (
            sensors.temperature is not None
            and sensors.temperature >= TEMPERATURE_CRITICAL
        ):
            reasons.append("CRITICAL_TEMPERATURE")

        if sensors.co is not None and sensors.co >= CO_CRITICAL:
            reasons.append("CRITICAL_CO")

        # =========================================================
        # WARNING CONDITIONS
        # =========================================================

        if (
            sensors.temperature is not None
            and sensors.temperature >= TEMPERATURE_WARNING
            and sensors.temperature < TEMPERATURE_CRITICAL
        ):
            reasons.append("HIGH_TEMPERATURE")

        if (
            sensors.co is not None
            and sensors.co >= CO_WARNING
            and sensors.co < CO_CRITICAL
        ):
            reasons.append("HIGH_CO")

        if device.battery <= LOW_BATTERY:
            reasons.append("LOW_BATTERY")

        # =========================================================
        # FINAL RISK LEVEL
        # =========================================================

        critical_reasons = {
            "SOS_PRESSED",
            "FALL_DETECTED",
            "FALL_AND_IMMOBILE",
            "CRITICAL_TEMPERATURE",
            "CRITICAL_CO",
        }

        if any(reason in critical_reasons for reason in reasons):
            return SafetyResult(
                risk_level=RiskLevel.CRITICAL,
                reasons=reasons,
            )

        if reasons:
            return SafetyResult(
                risk_level=RiskLevel.WARNING,
                reasons=reasons,
            )

        return SafetyResult(
            risk_level=RiskLevel.NORMAL,
            reasons=[],
        )