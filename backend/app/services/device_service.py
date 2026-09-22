from sqlalchemy.orm import Session

from app.repositories.device_repository import (
    create_device,
    get_device,
)


def ensure_device_exists(db: Session, device_id: str):
    device = get_device(db, device_id)

    if device is None:
        device = create_device(db, device_id)

    return device