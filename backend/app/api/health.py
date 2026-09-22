from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.schemas.health_response import HealthResponse
from app.services.health_service import (
    get_all_health_history,
    get_device_health_history,
    get_latest_device_health,
)

router = APIRouter(
    prefix="/api/v1/health/history",
    tags=["Health"],
)


@router.get(
    "",
    response_model=list[HealthResponse],
)
def get_all_health(
    db: Session = Depends(get_db),
):
    return get_all_health_history(db)


@router.get(
    "/{device_id}",
    response_model=list[HealthResponse],
)
def get_device_health(
    device_id: str,
    db: Session = Depends(get_db),
):
    return get_device_health_history(
        db,
        device_id,
    )


@router.get(
    "/latest/{device_id}",
    response_model=HealthResponse | None,
)
def get_latest_health(
    device_id: str,
    db: Session = Depends(get_db),
):
    return get_latest_device_health(
        db,
        device_id,
    )