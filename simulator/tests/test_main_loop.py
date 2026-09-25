import importlib
from types import SimpleNamespace

import pytest


class FakeFactory:
    def create_telemetry(self) -> dict[str, str]:
        return {"kind": "telemetry"}

    def create_status(self) -> dict[str, str]:
        return {"kind": "status"}

    def create_health(self) -> dict[str, str]:
        return {"kind": "health"}

    def create_event(self) -> None:
        return None


class FakePublisher:
    def __init__(self) -> None:
        self.published: list[str] = []

    def publish_telemetry(self, payload: dict[str, str]) -> None:
        self.published.append(payload["kind"])

    def publish_status(self, payload: dict[str, str]) -> None:
        self.published.append(payload["kind"])

    def publish_health(self, payload: dict[str, str]) -> None:
        self.published.append(payload["kind"])

    def publish_event(self, payload: dict[str, str]) -> None:
        self.published.append(payload["kind"])


def load_runner_class():
    try:
        module = importlib.import_module("simulator.main")
    except ModuleNotFoundError as exc:
        pytest.fail(f"simulator.main is not implemented: {exc}")
    return module.SimulatorRunner


def test_runner_publishes_only_due_normal_messages() -> None:
    publisher = FakePublisher()
    runner = load_runner_class()(
        config=SimpleNamespace(
            telemetry_interval=1.0,
            status_interval=2.0,
            health_interval=5.0,
        ),
        factory=FakeFactory(),
        publisher=publisher,
    )

    assert runner.publish_due(0.0) == 1.0
    assert publisher.published == ["telemetry", "status", "health"]

    assert runner.publish_due(0.9) == 1.0
    assert publisher.published == ["telemetry", "status", "health"]

    assert runner.publish_due(1.0) == 2.0
    assert publisher.published[-1] == "telemetry"

    assert runner.publish_due(2.0) == 3.0
    assert publisher.published[-2:] == ["telemetry", "status"]

    assert runner.publish_due(5.0) == 6.0
    assert publisher.published[-3:] == ["telemetry", "status", "health"]
    assert "event" not in publisher.published


def test_runner_keeps_generating_but_does_not_publish_when_mqtt_is_disabled() -> None:
    publisher = FakePublisher()
    runner = load_runner_class()(
        config=SimpleNamespace(
            telemetry_interval=1.0,
            status_interval=2.0,
            health_interval=5.0,
            mqtt_publish_enabled=False,
        ),
        factory=FakeFactory(),
        publisher=publisher,
    )

    runner.publish_due(0.0)
    runner.set_mqtt_publish_enabled(True)
    runner.publish_due(1.0)

    assert publisher.published == ["telemetry"]
