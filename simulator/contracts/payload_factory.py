from datetime import datetime, timezone
from time import monotonic as system_monotonic
from typing import Callable

from simulator.scenarios.normal import NormalScenario


class PayloadFactory:
    def __init__(
        self,
        device_id: str,
        source: str,
        scenario: NormalScenario,
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
        uptime_seconds = max(0, int(self._monotonic() - self._started_at))
        return {
            **self._message_base(),
            "battery": self._scenario.battery.read(),
            "uptime_seconds": uptime_seconds,
            "wifi": "CONNECTED",
            "mqtt": "CONNECTED",
            "sensors": {
                "temperature": "OK",
                "co": "OK",
                "imu": "OK",
            },
        }
