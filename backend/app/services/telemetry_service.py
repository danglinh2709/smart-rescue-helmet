from datetime import datetime

from sqlalchemy.orm import Session

from app.models.telemetry import Telemetry
from app.repositories.telemetry_repository import (
    create_telemetry,
    get_all_telemetry,
    get_telemetry_by_device,
    get_latest_telemetry,
)


def save_telemetry(
    db: Session,
    payload: dict,
):
    telemetry = Telemetry(
        device_id=payload["device_id"],
        timestamp=payload["timestamp"],
        temperature=payload["sensors"]["temperature"],
        co=payload["sensors"]["co"],
        ax=payload["sensors"]["imu"]["ax"],
        ay=payload["sensors"]["imu"]["ay"],
        az=payload["sensors"]["imu"]["az"],
        gx=payload["sensors"]["imu"]["gx"],
        gy=payload["sensors"]["imu"]["gy"],
        gz=payload["sensors"]["imu"]["gz"],
        movement=payload["state"]["movement"],
        fall=payload["state"]["fall"],
        immobile=payload["state"]["immobile"],
        sos=payload["state"]["sos"],
        risk_level=payload["risk_level"],
        battery=payload["device"]["battery"],
        wifi=payload["device"]["wifi"],
        mqtt=payload["device"]["mqtt"],
    )

    return create_telemetry(db, telemetry)

# Lấy toàn bộ lịch sử telemetry
def get_all_telemetry_history(db: Session):
    return get_all_telemetry(db)


# Lấy lịch sử theo device
def get_device_telemetry_history(db: Session, device_id: str):
    return get_telemetry_by_device(db, device_id)


# Lấy bản ghi mới nhất
def get_latest_device_telemetry(db: Session, device_id: str):
    return get_latest_telemetry(db, device_id)