from sqlalchemy.orm import Session

from app.models.event import Event


def create_event(
    db: Session,
    event: Event,
):
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


# Lấy toàn bộ lịch sử Event
def get_all_events(db: Session):
    return db.query(Event).all()


# Lấy Event theo Device
def get_events_by_device(
    db: Session,
    device_id: str,
):
    return (
        db.query(Event)
        .filter(Event.device_id == device_id)
        .all()
    )


# Lấy Event mới nhất của Device
def get_latest_event(
    db: Session,
    device_id: str,
):
    return (
        db.query(Event)
        .filter(Event.device_id == device_id)
        .order_by(Event.timestamp.desc())
        .first()
    )