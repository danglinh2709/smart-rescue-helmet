from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    String,
)

from sqlalchemy.orm import relationship

from app.database.db import Base


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True)

    event_id = Column(
        String(64),
        unique=True,
        nullable=False,
    )

    device_id = Column(
        String(32),
        ForeignKey("devices.device_id"),
        nullable=False,
    )

    timestamp = Column(DateTime, nullable=False)

    event_type = Column(String(50))

    severity = Column(String(30))

    data = Column(JSON)

    device = relationship(
        "Device",
        back_populates="events",
    )