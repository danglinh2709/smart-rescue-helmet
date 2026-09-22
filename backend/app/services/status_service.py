from sqlalchemy.orm import Session

from app.models.device_status import DeviceStatus
from app.repositories.status_repository import create_status


def save_status(
    db: Session,
    payload: dict,
):
    status = DeviceStatus(
        device_id=payload["device_id"],
        timestamp=payload["timestamp"],
        device_status=payload["device_status"],
        risk_level=payload["risk_level"],
        movement=payload["movement"],
        fall=payload["fall"],
        immobile=payload["immobile"],
        sos=payload["sos"],
    )

    return create_status(
        db,
        status,
    )