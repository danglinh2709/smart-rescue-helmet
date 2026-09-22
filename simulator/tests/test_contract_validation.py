import importlib
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path

import pytest


SCHEMA_DIR = Path(__file__).resolve().parents[2] / "shared" / "contracts"


def load_components():
    try:
        validator_module = importlib.import_module("simulator.contracts.validator")
        factory_module = importlib.import_module("simulator.contracts.payload_factory")
        scenario_module = importlib.import_module("simulator.scenarios.normal")
    except ModuleNotFoundError as exc:
        pytest.fail(f"Simulator contract components are not implemented: {exc}")
    return validator_module, factory_module.PayloadFactory, scenario_module.NormalScenario


def make_payloads():
    _, factory_class, scenario_class = load_components()
    monotonic_values = iter([10.0, 15.0])
    factory = factory_class(
        device_id="FF01",
        source="SIMULATOR",
        scenario=scenario_class(),
        clock=lambda: datetime(2026, 9, 21, 3, 0, tzinfo=timezone.utc),
        monotonic=lambda: next(monotonic_values),
    )
    return (
        factory.create_telemetry(),
        factory.create_status(),
        factory.create_health(),
    )


def test_all_normal_payloads_validate_against_shared_json_schemas() -> None:
    validator_module, _, _ = load_components()
    validator = validator_module.ContractValidator(SCHEMA_DIR)
    telemetry, status, health = make_payloads()

    validator.validate_telemetry(telemetry)
    validator.validate_status(status)
    validator.validate_health(health)


def test_invalid_payload_is_rejected_with_a_clear_field_path() -> None:
    validator_module, _, _ = load_components()
    validator = validator_module.ContractValidator(SCHEMA_DIR)
    telemetry, _, _ = make_payloads()
    invalid = deepcopy(telemetry)
    invalid["device"]["battery"] = 120.0

    with pytest.raises(validator_module.ContractValidationError, match="device.battery"):
        validator.validate_telemetry(invalid)


def test_invalid_timestamp_format_is_rejected() -> None:
    validator_module, _, _ = load_components()
    validator = validator_module.ContractValidator(SCHEMA_DIR)
    _, status, _ = make_payloads()
    status["timestamp"] = "2026-09-21T03:00:00"

    with pytest.raises(validator_module.ContractValidationError, match="timestamp"):
        validator.validate_status(status)
