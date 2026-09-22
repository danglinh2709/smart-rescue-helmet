from sqlalchemy.orm import Session

from app.models.health import Health
from app.repositories.health_repository import (
    create_health,
    get_all_health,
    get_health_by_device,
    get_latest_health,
)

def save_health(
    db: Session,
    payload: dict,
):
    health = Health(
        device_id=payload["device_id"],
        timestamp=payload["timestamp"],
        battery=payload["battery"],
        uptime_seconds=payload["uptime_seconds"],
        wifi=payload["wifi"],
        mqtt=payload["mqtt"],
        temperature_sensor=payload["sensors"]["temperature"],
        co_sensor=payload["sensors"]["co"],
        imu_sensor=payload["sensors"]["imu"],
    )

    return create_health(
        db,
        health,
    )

# Lấy toàn bộ lịch sử Health
def get_all_health_history(
    db: Session,
):
    return get_all_health(db)


# Lấy lịch sử Health theo Device
def get_device_health_history(
    db: Session,
    device_id: str,
):
    return get_health_by_device(
        db,
        device_id,
    )


# Lấy Health mới nhất
def get_latest_device_health(
    db: Session,
    device_id: str,
):
    return get_latest_health(
        db,
        device_id,
    )