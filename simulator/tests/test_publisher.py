import importlib
import json
from datetime import datetime, timezone
from pathlib import Path

import pytest


SCHEMA_DIR = Path(__file__).resolve().parents[2] / "shared" / "contracts"


class SuccessfulReasonCode:
    is_failure = False

    def __str__(self) -> str:
        return "Success"


class FakeMessageInfo:
    rc = 0

    def __init__(self) -> None:
        self.waited = False

    def wait_for_publish(self, timeout: float) -> None:
        self.waited = True


class FakeMqttClient:
    def __init__(self) -> None:
        self.on_connect = None
        self.on_disconnect = None
        self.published: list[tuple[str, str, int, bool]] = []
        self.loop_started = False
        self.disconnected = False
        self.reconnect_calls = 0

    def connect(self, host: str, port: int, keepalive: int) -> int:
        assert host == "mosquitto"
        assert port == 1883
        assert keepalive == 60
        self.on_connect(self, None, {}, SuccessfulReasonCode(), None)
        return 0

    def loop_start(self) -> None:
        self.loop_started = True

    def publish(self, topic: str, payload: str, qos: int, retain: bool):
        self.published.append((topic, payload, qos, retain))
        return FakeMessageInfo()

    def disconnect(self) -> int:
        self.disconnected = True
        return 0

    def reconnect(self) -> int:
        self.reconnect_calls += 1
        self.on_connect(self, None, {}, SuccessfulReasonCode(), None)
        return 0

    def loop_stop(self) -> None:
        self.loop_started = False


def load_components():
    try:
        publisher_module = importlib.import_module("simulator.mqtt.publisher")
        validator_module = importlib.import_module("simulator.contracts.validator")
        factory_module = importlib.import_module("simulator.contracts.payload_factory")
        scenario_module = importlib.import_module("simulator.scenarios.normal")
    except ModuleNotFoundError as exc:
        pytest.fail(f"Simulator publisher components are not implemented: {exc}")
    return publisher_module, validator_module, factory_module, scenario_module


def make_payloads(factory_module, scenario_module):
    monotonic_values = iter([0.0, 2.0])
    factory = factory_module.PayloadFactory(
        device_id="FF01",
        source="SIMULATOR",
        scenario=scenario_module.NormalScenario(),
        clock=lambda: datetime(2026, 9, 21, 3, 0, tzinfo=timezone.utc),
        monotonic=lambda: next(monotonic_values),
    )
    return factory.create_telemetry(), factory.create_status(), factory.create_health()


def test_publisher_validates_serializes_and_uses_contract_qos() -> None:
    publisher_module, validator_module, factory_module, scenario_module = load_components()
    client = FakeMqttClient()
    publisher = publisher_module.MqttPublisher(
        host="mosquitto",
        port=1883,
        validator=validator_module.ContractValidator(SCHEMA_DIR),
        client=client,
    )
    telemetry, status, health = make_payloads(factory_module, scenario_module)

    publisher.connect()
    publisher.publish_telemetry(telemetry)
    publisher.publish_status(status)
    publisher.publish_health(health)
    publisher.disconnect()

    assert [call[0] for call in client.published] == [
        "helmet/FF01/telemetry",
        "helmet/FF01/status",
        "helmet/FF01/health",
    ]
    assert [call[2] for call in client.published] == [0, 1, 1]
    assert all(call[3] is False for call in client.published)
    assert json.loads(client.published[0][1]) == telemetry
    assert client.disconnected is True
    assert client.loop_started is False


def test_publisher_never_sends_an_invalid_payload() -> None:
    publisher_module, validator_module, factory_module, scenario_module = load_components()
    client = FakeMqttClient()
    validator = validator_module.ContractValidator(SCHEMA_DIR)
    publisher = publisher_module.MqttPublisher(
        host="mosquitto",
        port=1883,
        validator=validator,
        client=client,
    )
    telemetry, _, _ = make_payloads(factory_module, scenario_module)
    telemetry["unexpected"] = True
    publisher.connect()

    with pytest.raises(validator_module.ContractValidationError):
        publisher.publish_telemetry(telemetry)

    assert client.published == []


def test_publisher_reconnects_before_resuming_publish() -> None:
    publisher_module, validator_module, factory_module, scenario_module = load_components()
    client = FakeMqttClient()
    publisher = publisher_module.MqttPublisher(
        host="mosquitto", port=1883,
        validator=validator_module.ContractValidator(SCHEMA_DIR), client=client,
    )
    telemetry, _, _ = make_payloads(factory_module, scenario_module)
    publisher.connect()
    publisher._on_disconnect(client, None, None, RuntimeError("broker restart"), None)

    publisher.publish_telemetry(telemetry)

    assert client.reconnect_calls == 1
    assert client.published[-1][0] == "helmet/FF01/telemetry"
