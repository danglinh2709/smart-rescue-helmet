from typing import Annotated

from pydantic import Field

from app.core.enums import ConnectionStatus, SensorStatus
from app.schemas.common import BatteryPercent, ContractModel, MessageBase


class SensorHealth(ContractModel):
    temperature: SensorStatus
    co: SensorStatus
    imu: SensorStatus


class DeviceHealthMessage(MessageBase):
    battery: BatteryPercent
    uptime_seconds: Annotated[int, Field(strict=True, ge=0)]
    wifi: ConnectionStatus
    mqtt: ConnectionStatus
    sensors: SensorHealth
