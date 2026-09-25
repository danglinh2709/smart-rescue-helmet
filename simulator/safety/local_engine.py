from dataclasses import dataclass, field

TEMPERATURE_WARNING = 50.0
TEMPERATURE_CRITICAL = 60.0
CO_WARNING = 50.0
CO_CRITICAL = 100.0
LOW_BATTERY = 20.0


@dataclass(frozen=True)
class LocalSafetyResult:
    risk_level: str
    reasons: list[str] = field(default_factory=list)


class LocalSafetyEngine:
    """Device-local reference implementation for fail-safe actuation."""
    def evaluate(
        self,
        *,
        temperature: float | None,
        co: float | None,
        battery: float,
        fall: bool,
        immobile: bool,
        sos: bool,
    ) -> LocalSafetyResult:
        reasons: list[str] = []
        if sos:
            reasons.append("SOS_PRESSED")
        if fall and immobile:
            reasons.append("FALL_AND_IMMOBILE")
        elif fall:
            reasons.append("FALL_DETECTED")
        if temperature is not None and temperature >= TEMPERATURE_CRITICAL:
            reasons.append("CRITICAL_TEMPERATURE")
        if co is not None and co >= CO_CRITICAL:
            reasons.append("CRITICAL_CO")
        if temperature is not None and TEMPERATURE_WARNING <= temperature < TEMPERATURE_CRITICAL:
            reasons.append("HIGH_TEMPERATURE")
        if co is not None and CO_WARNING <= co < CO_CRITICAL:
            reasons.append("HIGH_CO")
        if battery <= LOW_BATTERY:
            reasons.append("LOW_BATTERY")
        critical = {"SOS_PRESSED", "FALL_DETECTED", "FALL_AND_IMMOBILE", "CRITICAL_TEMPERATURE", "CRITICAL_CO"}
        return LocalSafetyResult("CRITICAL" if any(reason in critical for reason in reasons) else "WARNING" if reasons else "NORMAL", reasons)
