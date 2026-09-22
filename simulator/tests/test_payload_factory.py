import importlib
from datetime import datetime, timedelta, timezone

import pytest


FIXED_TIME = datetime(
    2026,
    9,
    21,
    10,
    30,
    0,
    tzinfo=timezone(timedelta(hours=7)),
)


def load_class(module_name: str, class_name: str):
    try:
        module = importlib.import_module(module_name)
    except ModuleNotFoundError as exc:
        pytest.fail(f"{module_name} is not implemented: {exc}")
    return getattr(module, class_name)


def make_factory():
    scenario_class = load_class("simulator.scenarios.normal", "NormalScenario")
    factory_class = load_class(
        "simulator.contracts.payload_factory", "PayloadFactory"
    )
    monotonic_values = iter([100.0, 112.8])
    return factory_class(
        device_id="FF02",
        source="SIMULATOR",
        scenario=scenario_class(),
        clock=lambda: FIXED_TIME,
        monotonic=lambda: next(monotonic_values),
    )


def test_factory_builds_contract_shaped_telemetry() -> None:
    payload = make_factory().create_telemetry()

    assert payload["schema_version"] == "1.0"
    assert payload["device_id"] == "FF02"
    assert payload["timestamp"] == "2026-09-21T10:30:00+07:00"
    assert payload["source"] == "SIMULATOR"
    assert payload["state"] == {
        "movement": "WALKING",
        "fall": False,
        "immobile": False,
        "sos": False,
    }
    assert payload["risk_level"] == "NORMAL"
    assert payload["device"]["wifi"] == "CONNECTED"
    assert payload["device"]["mqtt"] == "CONNECTED"
    assert set(payload["sensors"]["imu"]) == {"ax", "ay", "az", "gx", "gy", "gz"}


def test_factory_builds_normal_online_status() -> None:
    payload = make_factory().create_status()

    assert payload == {
        "schema_version": "1.0",
        "device_id": "FF02",
        "timestamp": "2026-09-21T10:30:00+07:00",
        "source": "SIMULATOR",
        "device_status": "ONLINE",
        "risk_level": "NORMAL",
        "movement": "WALKING",
        "fall": False,
        "immobile": False,
        "sos": False,
    }


def test_factory_builds_healthy_device_payload_with_uptime() -> None:
    payload = make_factory().create_health()

    assert payload["device_id"] == "FF02"
    assert payload["uptime_seconds"] == 12
    assert 0.0 <= payload["battery"] <= 100.0
    assert payload["wifi"] == "CONNECTED"
    assert payload["mqtt"] == "CONNECTED"
    assert payload["sensors"] == {
        "temperature": "OK",
        "co": "OK",
        "imu": "OK",
    }


def test_topic_helper_uses_the_contract_device_id() -> None:
    try:
        module = importlib.import_module("simulator.mqtt.topics")
    except ModuleNotFoundError as exc:
        pytest.fail(f"simulator.mqtt.topics is not implemented: {exc}")

    assert module.build_topic("FF02", "telemetry") == "helmet/FF02/telemetry"
    assert module.build_topic("HELMET-04", "status") == "helmet/HELMET-04/status"

    with pytest.raises(ValueError):
        module.build_topic("FF/02", "health")
