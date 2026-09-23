from datetime import datetime

from pydantic import BaseModel


class TelemetryResponse(BaseModel):
    id: int
    device_id: str
    timestamp: datetime

    temperature: float | None = None
    co: float | None = None

    ax: float | None = None
    ay: float | None = None
    az: float | None = None

    gx: float | None = None
    gy: float | None = None
    gz: float | None = None

    movement: str | None = None

    fall: bool | None = None
    immobile: bool | None = None
    sos: bool | None = None

    risk_level: str | None = None

    battery: float | None = None

    wifi: str | None = None

    mqtt: str | None = None

    model_config = {
        "from_attributes": True
    }