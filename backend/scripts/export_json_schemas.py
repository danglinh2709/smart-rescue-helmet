import json
from pathlib import Path

from pydantic import BaseModel

from app.schemas.device_health import DeviceHealthMessage
from app.schemas.device_status import DeviceStatusMessage
from app.schemas.event import EventMessage
from app.schemas.telemetry import TelemetryMessage


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "shared" / "contracts"

SCHEMA_MODELS: tuple[tuple[str, type[BaseModel]], ...] = (
    ("telemetry.schema.json", TelemetryMessage),
    ("event.schema.json", EventMessage),
    ("status.schema.json", DeviceStatusMessage),
    ("health.schema.json", DeviceHealthMessage),
)


def export_json_schemas(output_dir: Path = DEFAULT_OUTPUT_DIR) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []

    for filename, model in SCHEMA_MODELS:
        output_path = output_dir / filename
        schema = model.model_json_schema(mode="validation")
        output_path.write_text(
            json.dumps(schema, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        written.append(output_path)

    return written


def main() -> None:
    for path in export_json_schemas():
        print(path.relative_to(PROJECT_ROOT))


if __name__ == "__main__":
    main()
