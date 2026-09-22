import importlib

import pytest


def load_config_class():
    try:
        module = importlib.import_module("simulator.config")
    except ModuleNotFoundError as exc:
        pytest.fail(f"simulator.config is not implemented: {exc}")
    return module.SimulatorConfig


def test_config_reads_device_broker_and_intervals_from_environment() -> None:
    config = load_config_class().from_env(
        {
            "SIMULATOR_DEVICE_ID": "FF03",
            "MQTT_HOST": "broker.internal",
            "MQTT_PORT": "2883",
            "SIMULATOR_TELEMETRY_INTERVAL": "0.5",
            "SIMULATOR_STATUS_INTERVAL": "3",
            "SIMULATOR_HEALTH_INTERVAL": "9",
            "SIMULATOR_SOURCE": "SIMULATOR",
        }
    )

    assert config.device_id == "FF03"
    assert config.mqtt_host == "broker.internal"
    assert config.mqtt_port == 2883
    assert config.telemetry_interval == 0.5
    assert config.status_interval == 3.0
    assert config.health_interval == 9.0


@pytest.mark.parametrize(
    ("name", "value"),
    [
        ("SIMULATOR_TELEMETRY_INTERVAL", "0"),
        ("SIMULATOR_STATUS_INTERVAL", "-1"),
        ("SIMULATOR_HEALTH_INTERVAL", "not-a-number"),
        ("MQTT_PORT", "70000"),
        ("SIMULATOR_SOURCE", "HARDWARE"),
    ],
)
def test_config_rejects_invalid_runtime_values(name: str, value: str) -> None:
    with pytest.raises(ValueError):
        load_config_class().from_env({name: value})
