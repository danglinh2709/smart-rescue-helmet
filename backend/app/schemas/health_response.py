from datetime import datetime

from pydantic import BaseModel


class HealthResponse(BaseModel):
    id: int
    device_id: str

    timestamp: datetime

    battery: float | None = None

    uptime_seconds: int | None = None

    wifi: str | None = None

    mqtt: str | None = None

    temperature_sensor: str | None = None

    co_sensor: str | None = None

    imu_sensor: str | None = None

    model_config = {
        "from_attributes": True
    }