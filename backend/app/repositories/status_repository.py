from sqlalchemy.orm import Session

from app.models.device_status import DeviceStatus


def create_status(
    db: Session,
    status: DeviceStatus,
):
    db.add(status)

    db.commit()

    db.refresh(status)

    return status