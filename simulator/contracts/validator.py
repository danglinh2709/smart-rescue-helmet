import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker


class ContractValidationError(ValueError):
    """Raised when a simulator payload violates the shared wire contract."""


class ContractValidator:
    _SCHEMA_FILES = {
        "telemetry": "telemetry.schema.json",
        "status": "status.schema.json",
        "health": "health.schema.json",
        "event": "event.schema.json",
    }

    def __init__(self, schema_dir: Path) -> None:
        self._validators: dict[str, Draft202012Validator] = {}

        for message_type, filename in self._SCHEMA_FILES.items():
            schema_path = schema_dir / filename

            try:
                schema = json.loads(
                    schema_path.read_text(encoding="utf-8")
                )
            except (OSError, json.JSONDecodeError) as exc:
                raise RuntimeError(
                    f"Cannot load contract schema: {schema_path}"
                ) from exc

            Draft202012Validator.check_schema(schema)

            self._validators[message_type] = Draft202012Validator(
                schema,
                format_checker=FormatChecker(),
            )

    def _validate(
        self,
        message_type: str,
        payload: dict[str, Any],
    ) -> None:
        errors = sorted(
            self._validators[message_type].iter_errors(payload),
            key=lambda error: [str(part) for part in error.absolute_path],
        )

        if not errors:
            return

        error = errors[0]

        field_path = (
            ".".join(str(part) for part in error.absolute_path)
            or "<root>"
        )

        raise ContractValidationError(
            f"{message_type} payload invalid at {field_path}: {error.message}"
        )

    def validate_telemetry(
        self,
        payload: dict[str, Any],
    ) -> None:
        self._validate("telemetry", payload)

    def validate_status(
        self,
        payload: dict[str, Any],
    ) -> None:
        self._validate("status", payload)

    def validate_health(
        self,
        payload: dict[str, Any],
    ) -> None:
        self._validate("health", payload)

    def validate_event(
        self,
        payload: dict[str, Any],
    ) -> None:
        self._validate("event", payload)