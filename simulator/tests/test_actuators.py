from simulator.actuators.controller import ActuatorController
from simulator.contracts.payload_factory import PayloadFactory
from simulator.scenarios.temperature_high import TemperatureHighScenario
from simulator.safety.local_engine import LocalSafetyEngine


def test_normal_local_safety_sets_safe_actuators() -> None:
    controller = ActuatorController()
    result = LocalSafetyEngine().evaluate(
        temperature=30.0,
        co=3.0,
        battery=85.0,
        fall=False,
        immobile=False,
        sos=False,
    )

    state = controller.apply(result)

    assert result.risk_level == "NORMAL"
    assert state.led == "GREEN"
    assert state.buzzer is False
    assert state.vibration is False


def test_critical_fall_sets_red_buzzer_and_vibration_while_offline() -> None:
    controller = ActuatorController()
    result = LocalSafetyEngine().evaluate(
        temperature=30.0,
        co=3.0,
        battery=85.0,
        fall=True,
        immobile=False,
        sos=False,
    )

    state = controller.apply(result)

    assert result.risk_level == "CRITICAL"
    assert state.led == "RED"
    assert state.buzzer is True
    assert state.vibration is True


def test_temperature_critical_updates_local_actuator_before_mqtt_publish() -> None:
    factory = PayloadFactory(
        device_id="FF01",
        source="SIMULATOR",
        scenario=TemperatureHighScenario(),
    )

    factory.create_telemetry()

    assert factory.actuator_state.led == "RED"
    assert factory.actuator_state.buzzer is True
    assert factory.actuator_state.vibration is True
