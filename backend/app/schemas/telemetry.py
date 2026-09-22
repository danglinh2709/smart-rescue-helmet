from pydantic import StrictBool

from app.core.enums import ConnectionStatus, MovementState, RiskLevel
from app.schemas.common import (
    BatteryPercent,
    ContractFloat,
    ContractModel,
    MessageBase,
)


class ImuReading(ContractModel):
    ax: ContractFloat
    ay: ContractFloat
    az: ContractFloat
    gx: ContractFloat
    gy: ContractFloat
    gz: ContractFloat


class SensorReadings(ContractModel):
    temperature: ContractFloat | None
    co: ContractFloat | None
    imu: ImuReading


class TelemetryState(ContractModel):
    movement: MovementState
    fall: StrictBool
    immobile: StrictBool
    sos: StrictBool


class TelemetryDevice(ContractModel):
    battery: BatteryPercent
    wifi: ConnectionStatus
    mqtt: ConnectionStatus


class TelemetryMessage(MessageBase):
    sensors: SensorReadings
    state: TelemetryState
    risk_level: RiskLevel
    device: TelemetryDevice
