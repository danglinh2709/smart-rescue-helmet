import logging
import signal
from threading import Event
from time import monotonic
from typing import Any

from simulator.config import SimulatorConfig
from simulator.contracts.payload_factory import PayloadFactory
from simulator.contracts.validator import ContractValidator
from simulator.mqtt.publisher import MqttPublisher

# ===== Chọn Scenario =====
from simulator.scenarios.normal import NormalScenario
from simulator.scenarios.fall import FallScenario
from simulator.scenarios.fall_immobile import FallImmobileScenario
from simulator.scenarios.sos import SOSScenario
from simulator.scenarios.co_high import COHighScenario
from simulator.scenarios.temperature_high import TemperatureHighScenario
from simulator.scenarios.immobile import ImmobileScenario
from simulator.scenarios.low_battery import LowBatteryScenario

LOGGER = logging.getLogger(__name__)


class SimulatorRunner:
    def __init__(
        self,
        config: Any,
        factory: Any,
        publisher: Any,
    ) -> None:

        self._factory = factory
        self._publisher = publisher

        self._intervals = {
            "telemetry": config.telemetry_interval,
            "status": config.status_interval,
            "health": config.health_interval,
            # Event dùng cùng interval với Telemetry
            "event": config.telemetry_interval,
        }

        self._next_publish: dict[str, float] | None = None

    def publish_due(self, now: float) -> float:

        if self._next_publish is None:
            self._next_publish = {
                message_type: now
                for message_type in self._intervals
            }

        actions = {
            "telemetry": (
                self._factory.create_telemetry,
                self._publisher.publish_telemetry,
            ),
            "status": (
                self._factory.create_status,
                self._publisher.publish_status,
            ),
            "health": (
                self._factory.create_health,
                self._publisher.publish_health,
            ),
            "event": (
                self._factory.create_event,
                self._publisher.publish_event,
            ),
        }

        for message_type in (
            "telemetry",
            "status",
            "health",
            "event",
        ):

            if now < self._next_publish[message_type]:
                continue

            create_payload, publish_payload = actions[message_type]

            payload = create_payload()

            # Event chỉ publish khi có dữ liệu
            if payload:
                publish_payload(payload)

            while self._next_publish[message_type] <= now:
                self._next_publish[message_type] += self._intervals[message_type]

        return min(self._next_publish.values())

    def run(
        self,
        stop_event: Event,
    ) -> None:

        next_deadline = self.publish_due(monotonic())

        while not stop_event.is_set():

            delay = max(
                0.0,
                next_deadline - monotonic(),
            )

            if stop_event.wait(delay):
                break

            next_deadline = self.publish_due(monotonic())


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )


def main() -> None:

    configure_logging()

    config = SimulatorConfig.from_env()

    stop_event = Event()

    def request_shutdown(
        signum: int,
        frame: Any,
    ) -> None:

        LOGGER.info(
            "Simulator shutdown requested signal=%s",
            signum,
        )

        stop_event.set()

    signal.signal(signal.SIGINT, request_shutdown)
    signal.signal(signal.SIGTERM, request_shutdown)

    # =====================================================
    # Chọn Scenario tại đây
    # =====================================================

    scenario = NormalScenario()
    # scenario = FallScenario()
    # scenario = SOSScenario()
    # scenario = COHighScenario()
    # scenario = TemperatureHighScenario()
    # scenario = ImmobileScenario()
    # scenario = FallImmobileScenario()
    # scenario = LowBatteryScenario()

    factory = PayloadFactory(
        device_id=config.device_id,
        source=config.source,
        scenario=scenario,
    )

    validator = ContractValidator(
        config.schema_dir,
    )

    publisher = MqttPublisher(
        host=config.mqtt_host,
        port=config.mqtt_port,
        validator=validator,
    )

    runner = SimulatorRunner(
        config,
        factory,
        publisher,
    )

    LOGGER.info(
        "Simulator started | device=%s | scenario=%s | telemetry=%ss | status=%ss | health=%ss | event=%ss",
        config.device_id,
        scenario.__class__.__name__,
        config.telemetry_interval,
        config.status_interval,
        config.health_interval,
        config.telemetry_interval,
    )

    connected = False

    try:
        publisher.connect()
        connected = True

        runner.run(stop_event)

    except KeyboardInterrupt:
        stop_event.set()

    except Exception:
        LOGGER.exception(
            "Simulator stopped due to unrecoverable error",
        )
        raise

    finally:

        if connected:
            publisher.disconnect()

        LOGGER.info(
            "Simulator stopped device=%s",
            config.device_id,
        )


if __name__ == "__main__":
    main()