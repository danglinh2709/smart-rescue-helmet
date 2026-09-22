from uuid import UUID

from pydantic import JsonValue

from app.core.enums import EventSeverity, EventType
from app.schemas.common import MessageBase


class EventMessage(MessageBase):
    event_id: UUID
    event_type: EventType
    severity: EventSeverity
    data: dict[str, JsonValue]
