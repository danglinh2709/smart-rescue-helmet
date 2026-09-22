from sqlalchemy.orm import Session

from app.models.device import Device


def get_device(db: Session, device_id: str):
    return (
        db.query(Device)
        .filter(Device.device_id == device_id)
        .first()
    )


def create_device(db: Session, device_id: str):
    device = Device(device_id=device_id)

    db.add(device)

    db.commit()

    db.refresh(device)

    return device