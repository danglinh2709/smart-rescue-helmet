from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
)

from sqlalchemy.orm import relationship

from app.database.db import Base


class DeviceStatus(Base):
    __tablename__ = "device_status"

    id = Column(Integer, primary_key=True)

    device_id = Column(
        String(32),
        ForeignKey("devices.device_id"),
        nullable=False,
    )

    timestamp = Column(DateTime, nullable=False)

    device_status = Column(String(30))

    risk_level = Column(String(30))

    movement = Column(String(30))

    fall = Column(Boolean)

    immobile = Column(Boolean)

    sos = Column(Boolean)

    device = relationship(
        "Device",
        back_populates="statuses",
    )