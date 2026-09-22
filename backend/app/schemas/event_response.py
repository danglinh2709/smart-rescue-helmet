from datetime import datetime

from pydantic import BaseModel


class EventResponse(BaseModel):
    id: int
    event_id: str
    device_id: str

    timestamp: datetime

    event_type: str

    severity: str

    data: dict | None = None

    model_config = {
        "from_attributes": True
    }