from pydantic import StrictBool

from app.core.enums import DeviceStatus, MovementState, RiskLevel
from app.schemas.common import MessageBase


class DeviceStatusMessage(MessageBase):
    device_status: DeviceStatus
    risk_level: RiskLevel
    movement: MovementState
    fall: StrictBool
    immobile: StrictBool
    sos: StrictBool
