from sqlalchemy.orm import Session
from app.models.telemetry import Telemetry


def create_telemetry(db: Session, telemetry: Telemetry):
    db.add(telemetry)
    db.commit()
    db.refresh(telemetry)
    return telemetry


# Lấy 100 bản ghi mới nhất
def get_all_telemetry(db: Session):
    return (
        db.query(Telemetry)
        .order_by(Telemetry.timestamp.desc())
        .limit(100)
        .all()
    )


# Lấy 100 bản ghi của một thiết bị
def get_telemetry_by_device(db: Session, device_id: str):
    return (
        db.query(Telemetry)
        .filter(Telemetry.device_id == device_id)
        .order_by(Telemetry.timestamp.desc())
        .limit(100)
        .all()
    )


# Lấy bản ghi mới nhất
def get_latest_telemetry(db: Session, device_id: str):
    return (
        db.query(Telemetry)
        .filter(Telemetry.device_id == device_id)
        .order_by(Telemetry.timestamp.desc())
        .first()
    )