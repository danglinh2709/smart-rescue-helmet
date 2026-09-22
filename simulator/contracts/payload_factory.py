from datetime import datetime, timezone
from time import monotonic as system_monotonic
from typing import Any, Callable
from uuid import uuid4


class PayloadFactory:
    def __init__(
        self,
        device_id: str,
        source: str,
        scenario: Any,
        clock: Callable[[], datetime] | None = None,
        monotonic: Callable[[], float] | None = None,
    ) -> None:
        self._device_id = device_id
        self._source = source
        self._scenario = scenario
        self._clock = clock or (lambda: datetime.now(timezone.utc))
        self._monotonic = monotonic or system_monotonic
        self._started_at = self._monotonic()

    def _message_base(self) -> dict[str, object]:
        return {
            "schema_version": "1.0",
            "device_id": self._device_id,
            "timestamp": self._clock().isoformat(),
            "source": self._source,
        }

    def create_telemetry(self) -> dict[str, object]:
        reading = self._scenario.read()

        return {
            **self._message_base(),
            "sensors": {
                "temperature": reading["temperature"],
                "co": reading["co"],
                "imu": reading["imu"],
            },
            "state": {
                "movement": reading["movement"],
                "fall": reading["fall"],
                "immobile": reading["immobile"],
                "sos": reading["sos"],
            },
            "risk_level": reading["risk_level"],
            "device": {
                "battery": reading["battery"],
                "wifi": "CONNECTED",
                "mqtt": "CONNECTED",
            },
        }

    def create_status(self) -> dict[str, object]:
        reading = self._scenario.read()

        return {
            **self._message_base(),
            "device_status": "ONLINE",
            "risk_level": reading["risk_level"],
            "movement": reading["movement"],
            "fall": reading["fall"],
            "immobile": reading["immobile"],
            "sos": reading["sos"],
        }

    def create_health(self) -> dict[str, object]:
        reading = self._scenario.read()

        uptime_seconds = max(
            0,
            int(self._monotonic() - self._started_at),
        )

        return {
            **self._message_base(),
            "battery": reading["battery"],
            "uptime_seconds": uptime_seconds,
            "wifi": "CONNECTED",
            "mqtt": "CONNECTED",
            "sensors": {
                "temperature": "OK",
                "co": "OK",
                "imu": "OK",
            },
        }

    def create_event(self) -> dict[str, object] | None:
        reading = self._scenario.read()

        event_type = None
        severity = None

        if reading["fall"]:
            event_type = "FALL_DETECTED"
            severity = "CRITICAL"

        elif reading["sos"]:
            event_type = "SOS_PRESSED"
            severity = "CRITICAL"

        elif reading["co"] >= 100:
            event_type = "CO_HIGH"
            severity = "CRITICAL"

        elif reading["temperature"] >= 60:
            event_type = "TEMPERATURE_HIGH"
            severity = "WARNING"

        elif reading["immobile"]:
            event_type = "IMMOBILE"
            severity = "WARNING"

        elif reading["battery"] <= 20:
            event_type = "LOW_BATTERY"
            severity = "WARNING"

        if event_type is None:
            return None

        return {
            **self._message_base(),
            "event_id": str(uuid4()),
            "event_type": event_type,
            "severity": severity,
            "data": {
                "temperature": reading["temperature"],
                "co": reading["co"],
                "movement": reading["movement"],
                "battery": reading["battery"],
                "risk_level": reading["risk_level"],
            },
        }