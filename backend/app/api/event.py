from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.dependencies import get_db

from app.schemas.event_response import EventResponse

from app.services.event_service import (
    get_all_event_history,
    get_device_event_history,
    get_latest_device_event,
)

router = APIRouter(
    prefix="/api/v1/events",
    tags=["Events"],
)


@router.get(
    "",
    response_model=list[EventResponse],
)
def get_all_events(
    db: Session = Depends(get_db),
):
    return get_all_event_history(db)


@router.get(
    "/{device_id}",
    response_model=list[EventResponse],
)
def get_device_events(
    device_id: str,
    db: Session = Depends(get_db),
):
    return get_device_event_history(
        db,
        device_id,
    )


@router.get(
    "/latest/{device_id}",
    response_model=EventResponse | None,
)
def get_latest_event(
    device_id: str,
    db: Session = Depends(get_db),
):
    return get_latest_device_event(
        db,
        device_id,
    )