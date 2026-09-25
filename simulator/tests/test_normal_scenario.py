import importlib

import pytest


def load_class(module_name: str, class_name: str):
    try:
        module = importlib.import_module(module_name)
    except ModuleNotFoundError as exc:
        pytest.fail(f"{module_name} is not implemented: {exc}")
    return getattr(module, class_name)


def test_temperature_stays_in_normal_range_and_is_deterministic() -> None:
    sensor_class = load_class(
        "simulator.sensors.temperature", "TemperatureSensorSimulator"
    )
    first = sensor_class()
    second = sensor_class()

    first_values = [first.read() for _ in range(64)]
    second_values = [second.read() for _ in range(64)]

    assert first_values == second_values
    assert all(28.0 <= value <= 32.0 for value in first_values)
    assert len(set(first_values)) > 1


def test_co_stays_low_and_is_deterministic() -> None:
    sensor_class = load_class("simulator.sensors.co", "COSensorSimulator")
    first = sensor_class()
    second = sensor_class()

    first_values = [first.read() for _ in range(64)]
    second_values = [second.read() for _ in range(64)]

    assert first_values == second_values
    assert all(0.0 <= value <= 10.0 for value in first_values)
    assert len(set(first_values)) > 1


def test_imu_models_light_walking_without_fall_acceleration() -> None:
    sensor_class = load_class("simulator.sensors.imu", "IMUSensorSimulator")
    sensor = sensor_class()

    samples = [sensor.read() for _ in range(12)]

    assert all(set(sample) == {"ax", "ay", "az", "gx", "gy", "gz"} for sample in samples)
    assert all(abs(sample["ax"]) < 0.5 for sample in samples)
    assert all(abs(sample["ay"]) < 0.5 for sample in samples)
    assert all(9.5 <= sample["az"] <= 10.1 for sample in samples)
    assert all(abs(sample[axis]) < 0.5 for sample in samples for axis in ("gx", "gy", "gz"))


def test_battery_decreases_slowly_and_never_leaves_valid_range() -> None:
    sensor_class = load_class("simulator.sensors.battery", "BatterySimulator")
    sensor = sensor_class(initial_level=85.0, drain_per_read=0.01)

    values = [sensor.read() for _ in range(100)]

    assert values[0] == 85.0
    assert all(0.0 <= value <= 100.0 for value in values)
    assert all(current >= following for current, following in zip(values, values[1:]))
    assert values[-1] >= 84.0


def test_default_battery_drain_remains_slow_over_many_reads() -> None:
    sensor_class = load_class("simulator.sensors.battery", "BatterySimulator")
    sensor = sensor_class()

    values = [sensor.read() for _ in range(1000)]

    assert values[0] == 85.0
    assert values[-1] >= 84.0


def test_normal_scenario_never_sets_dangerous_state() -> None:
    scenario_class = load_class("simulator.scenarios.normal", "NormalScenario")

    sample = scenario_class().read()

    assert sample["movement"] == "WALKING"
    assert "risk_level" not in sample
    assert sample["fall"] is False
    assert sample["immobile"] is False
    assert sample["sos"] is False
