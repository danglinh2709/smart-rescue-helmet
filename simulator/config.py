import os
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

from simulator.mqtt.topics import validate_device_id


DEFAULT_SCHEMA_DIR = Path(__file__).resolve().parents[1] / "shared" / "contracts"


def _positive_float(environment: Mapping[str, str], name: str, default: str) -> float:
    try:
        value = float(environment.get(name, default))
    except ValueError as exc:
        raise ValueError(f"{name} must be a number") from exc

    if value <= 0:
        raise ValueError(f"{name} must be greater than zero")

    return value


@dataclass(frozen=True)
class SimulatorConfig:
    device_id: str
    mqtt_host: str
    mqtt_port: int

    telemetry_interval: float
    status_interval: float
    health_interval: float
    event_interval: float

    source: str
    schema_dir: Path

    @classmethod
    def from_env(
        cls,
        environment: Mapping[str, str] | None = None,
    ) -> "SimulatorConfig":

        values = os.environ if environment is None else environment

        try:
            mqtt_port = int(values.get("MQTT_PORT", "1883"))
        except ValueError as exc:
            raise ValueError("MQTT_PORT must be an integer") from exc

        if not 1 <= mqtt_port <= 65535:
            raise ValueError("MQTT_PORT must be between 1 and 65535")

        source = values.get(
            "SIMULATOR_SOURCE",
            "SIMULATOR",
        )

        if source != "SIMULATOR":
            raise ValueError("SIMULATOR_SOURCE must be SIMULATOR")

        return cls(
            device_id=validate_device_id(
                values.get(
                    "SIMULATOR_DEVICE_ID",
                    "FF01",
                )
            ),

            mqtt_host=values.get(
                "MQTT_HOST",
                "mosquitto",
            ),

            mqtt_port=mqtt_port,

            telemetry_interval=_positive_float(
                values,
                "SIMULATOR_TELEMETRY_INTERVAL",
                "1",
            ),

            status_interval=_positive_float(
                values,
                "SIMULATOR_STATUS_INTERVAL",
                "2",
            ),

            health_interval=_positive_float(
                values,
                "SIMULATOR_HEALTH_INTERVAL",
                "5",
            ),

            event_interval=_positive_float(
                values,
                "SIMULATOR_EVENT_INTERVAL",
                "2",
            ),

            source=source,

            schema_dir=DEFAULT_SCHEMA_DIR,
        )