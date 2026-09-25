from datetime import datetime, timezone
from time import monotonic as system_monotonic
from typing import Any, Callable

from simulator.actuators.controller import ActuatorController, ActuatorState
from simulator.safety.local_engine import LocalSafetyEngine


class PayloadFactory:
    def __init__(
        self,
        device_id: str,
        source: str,
        scenario: Any,
        clock: Callable[[], datetime] | None = None,
        monotonic: Callable[[], float] | None = None,
        local_safety: LocalSafetyEngine | None = None,
        actuators: ActuatorController | None = None,
    ) -> None:
        self._device_id = device_id
        self._source = source
        self._scenario = scenario
        self._clock = clock or (lambda: datetime.now(timezone.utc))
        self._monotonic = monotonic or system_monotonic
        self._started_at = self._monotonic()
        self._local_safety = local_safety or LocalSafetyEngine()
        self._actuators = actuators or ActuatorController()

    @property
    def actuator_state(self) -> ActuatorState:
        return self._actuators.state

    def _read(self) -> dict[str, object]:
        reading = self._scenario.read()
        result = self._local_safety.evaluate(
            temperature=reading["temperature"],
            co=reading["co"],
            battery=reading["battery"],
            fall=reading["fall"],
            immobile=reading["immobile"],
            sos=reading["sos"],
        )
        self._actuators.apply(result)
        return reading

    def _message_base(self) -> dict[str, object]:
        return {
            "schema_version": "1.0",
            "device_id": self._device_id,
            "timestamp": self._clock().isoformat(),
            "source": self._source,
        }

    def create_telemetry(self) -> dict[str, object]:
        reading = self._read()

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
            # Giữ NORMAL để tương thích contract hiện tại.
            # Backend M6 sẽ ghi đè bằng kết quả Safety Engine.
            "risk_level": "NORMAL",
            "device": {
                "battery": reading["battery"],
                "wifi": "CONNECTED",
                "mqtt": "CONNECTED",
            },
        }

    def create_status(self) -> dict[str, object]:
        reading = self._read()

        return {
            **self._message_base(),
            "device_status": "ONLINE",
            # Contract hiện tại vẫn yêu cầu risk_level.
            # Không dùng giá trị này để quyết định Safety.
            "risk_level": "NORMAL",
            "movement": reading["movement"],
            "fall": reading["fall"],
            "immobile": reading["immobile"],
            "sos": reading["sos"],
        }

    def create_health(self) -> dict[str, object]:
        reading = self._read()

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

    def create_event(self) -> None:
        """
        Event không còn được tạo ở Simulator.

        Backend Safety Engine là nguồn sự thật duy nhất
        để quyết định Risk và Event.
        """
        return None
