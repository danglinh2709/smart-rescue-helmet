from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
)

from sqlalchemy.orm import relationship

from app.database.db import Base


class Health(Base):
    __tablename__ = "health"

    id = Column(Integer, primary_key=True)

    device_id = Column(
        String(32),
        ForeignKey("devices.device_id"),
        nullable=False,
    )

    timestamp = Column(DateTime, nullable=False)

    battery = Column(Float)

    uptime_seconds = Column(Integer)

    wifi = Column(String(30))

    mqtt = Column(String(30))

    temperature_sensor = Column(String(20))

    co_sensor = Column(String(20))

    imu_sensor = Column(String(20))

    device = relationship(
        "Device",
        back_populates="health_records",
    )