from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.schemas.telemetry_response import TelemetryResponse

from app.services.telemetry_service import (
    get_all_telemetry_history,
    get_device_telemetry_history,
    get_latest_device_telemetry,
)

router = APIRouter(
    prefix="/api/v1/telemetry",
    tags=["Telemetry"],
)


@router.get(
    "",
    response_model=list[TelemetryResponse],
)
def get_all_telemetry(
    db: Session = Depends(get_db),
):
    return get_all_telemetry_history(db)


@router.get(
    "/{device_id}",
    response_model=list[TelemetryResponse],
)
def get_device_telemetry(
    device_id: str,
    db: Session = Depends(get_db),
):
    return get_device_telemetry_history(
        db,
        device_id,
    )


@router.get(
    "/latest/{device_id}",
    response_model=TelemetryResponse | None,
)
def get_latest_telemetry(
    device_id: str,
    db: Session = Depends(get_db),
):
    return get_latest_device_telemetry(
        db,
        device_id,
    )