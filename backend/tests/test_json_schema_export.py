import json

import pytest


def load_exporter():
    try:
        from scripts.export_json_schemas import export_json_schemas
    except ModuleNotFoundError as exc:
        pytest.fail(f"JSON Schema exporter is not implemented: {exc}")
    return export_json_schemas


def test_exporter_writes_all_contract_schemas_from_pydantic_models(tmp_path) -> None:
    written = load_exporter()(tmp_path)

    assert {path.name for path in written} == {
        "telemetry.schema.json",
        "event.schema.json",
        "status.schema.json",
        "health.schema.json",
    }
    telemetry = json.loads((tmp_path / "telemetry.schema.json").read_text())
    assert telemetry["title"] == "TelemetryMessage"
    assert telemetry["properties"]["schema_version"]["const"] == "1.0"
    assert telemetry["additionalProperties"] is False
