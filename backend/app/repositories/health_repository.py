from sqlalchemy.orm import Session

from app.models.health import Health


def create_health(
    db: Session,
    health: Health,
):
    db.add(health)
    db.commit()
    db.refresh(health)
    return health


# Lấy toàn bộ lịch sử Health
def get_all_health(db: Session):
    return db.query(Health).all()


# Lấy Health theo Device
def get_health_by_device(
    db: Session,
    device_id: str,
):
    return (
        db.query(Health)
        .filter(Health.device_id == device_id)
        .all()
    )


# Lấy Health mới nhất
def get_latest_health(
    db: Session,
    device_id: str,
):
    return (
        db.query(Health)
        .filter(Health.device_id == device_id)
        .order_by(Health.timestamp.desc())
        .first()
    )