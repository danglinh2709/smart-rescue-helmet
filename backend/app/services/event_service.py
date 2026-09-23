from sqlalchemy.orm import Session

from app.models.event import Event
from app.repositories.event_repository import (
    create_event,
    get_all_events,
    get_events_by_device,
    get_latest_event,
)

def save_event(
    db: Session,
    payload: dict,
):
    event = Event(
        event_id=str(payload["event_id"]),
        device_id=payload["device_id"],
        timestamp=payload["timestamp"],
        event_type=payload["event_type"],
        severity=payload["severity"],
        data=payload["data"],
    )

    return create_event(
        db,
        event,
    )

# Lấy toàn bộ lịch sử Event
def get_all_event_history(
    db: Session,
):
    return get_all_events(db)


# Lấy lịch sử Event theo Device
def get_device_event_history(
    db: Session,
    device_id: str,
):
    return get_events_by_device(
        db,
        device_id,
    )


# Lấy Event mới nhất
def get_latest_device_event(
    db: Session,
    device_id: str,
):
    return get_latest_event(
        db,
        device_id,
    )