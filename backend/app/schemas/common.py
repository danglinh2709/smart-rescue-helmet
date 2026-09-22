from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, field_validator

from app.core.enums import DataSource


DeviceId = Annotated[
    str,
    StringConstraints(
        min_length=3,
        max_length=32,
        pattern=r"^[A-Z][A-Z0-9_-]{2,31}$",
    ),
]
BatteryPercent = Annotated[float, Field(strict=True, ge=0, le=100)]
ContractFloat = Annotated[float, Field(strict=True)]


class ContractModel(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)


class MessageBase(ContractModel):
    schema_version: Literal["1.0"]
    device_id: DeviceId
    timestamp: datetime = Field(
        json_schema_extra={"pattern": r"(?:Z|[+-]\d{2}:\d{2})$"}
    )
    source: DataSource

    @field_validator("timestamp")
    @classmethod
    def timestamp_must_include_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("timestamp must include a timezone offset")
        return value
