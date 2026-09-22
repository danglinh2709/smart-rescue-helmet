from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from app.database.db import Base


class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)

    device_id = Column(
        String(32),
        unique=True,
        nullable=False,
        index=True,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    telemetry = relationship(
        "Telemetry",
        back_populates="device",
        cascade="all, delete-orphan",
    )

    statuses = relationship(
        "DeviceStatus",
        back_populates="device",
        cascade="all, delete-orphan",
    )

    health_records = relationship(
        "Health",
        back_populates="device",
        cascade="all, delete-orphan",
    )

    events = relationship(
        "Event",
        back_populates="device",
        cascade="all, delete-orphan",
    )