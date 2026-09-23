from app.database.db import Base, engine

from app.models.device import Device
from app.models.telemetry import Telemetry
from app.models.device_status import DeviceStatus
from app.models.health import Health
from app.models.event import Event


def init_database():
    print("=== CREATE DATABASE TABLES ===")
    Base.metadata.create_all(bind=engine)
    print("=== DONE ===")