from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
)

from sqlalchemy.orm import relationship

from app.database.db import Base


class Telemetry(Base):
    __tablename__ = "telemetry"

    id = Column(Integer, primary_key=True)

    device_id = Column(
        String(32),
        ForeignKey("devices.device_id"),
        nullable=False,
    )

    timestamp = Column(DateTime, nullable=False)

    temperature = Column(Float)

    co = Column(Float)

    ax = Column(Float)
    ay = Column(Float)
    az = Column(Float)

    gx = Column(Float)
    gy = Column(Float)
    gz = Column(Float)

    movement = Column(String(30))

    fall = Column(Boolean)

    immobile = Column(Boolean)

    sos = Column(Boolean)

    risk_level = Column(String(30))

    battery = Column(Float)

    wifi = Column(String(30))

    mqtt = Column(String(30))

    device = relationship(
        "Device",
        back_populates="telemetry",
    )