import asyncio
import logging
import os
from datetime import datetime, timezone
from uuid import uuid4

from app.core.enums import DataSource, EventSeverity, EventType
from app.database.db import SessionLocal
from app.schemas.event import EventMessage
from app.services.device_state import check_offline_devices, devices, update_device
from app.services.event_service import save_event
from app.websocket.service import publish_device_state, publish_realtime_message

LOGGER = logging.getLogger(__name__)

OFFLINE_TIMEOUT_SECONDS = float(os.getenv("DEVICE_OFFLINE_TIMEOUT_SECONDS", "10"))
OFFLINE_CHECK_INTERVAL_SECONDS = float(
    os.getenv("DEVICE_OFFLINE_CHECK_INTERVAL_SECONDS", "2")
)


def _source_for(device_id: str) -> DataSource:
    telemetry = devices.get(device_id, {}).get("telemetry") or {}
    return DataSource(telemetry.get("source", DataSource.SIMULATOR))


async def _record_transition_event(
    device_id: str, event_type: EventType, severity: EventSeverity
) -> None:
    timestamp = datetime.now(timezone.utc)
    event = EventMessage(
        schema_version="1.0",
        event_id=uuid4(),
        device_id=device_id,
        timestamp=timestamp,
        source=_source_for(device_id),
        event_type=event_type,
        severity=severity,
        data={"reason": event_type.value},
    )
    db = SessionLocal()
    try:
        save_event(db, event.model_dump())
    except Exception:
        LOGGER.exception("Failed to persist device transition event device=%s", device_id)
    finally:
        db.close()
    event_data = event.model_dump(mode="json")
    update_device(device_id, "event", event_data)
    await publish_realtime_message(
        "event", device_id=device_id, timestamp=event_data["timestamp"], data=event_data
    )


async def mark_stale_devices_offline() -> list[str]:
    transitioned = check_offline_devices(timeout_seconds=OFFLINE_TIMEOUT_SECONDS)
    for device_id in transitioned:
        LOGGER.warning("Device offline device=%s", device_id)
        await _record_transition_event(
            device_id, EventType.DEVICE_OFFLINE, EventSeverity.WARNING
        )
        await publish_device_state(device_id)
    return transitioned


async def handle_device_recovery(device_id: str) -> None:
    LOGGER.info("Device recovered device=%s", device_id)
    await _record_transition_event(
        device_id, EventType.MQTT_RECONNECTED, EventSeverity.INFO
    )
    await publish_device_state(device_id)


async def run_offline_monitor() -> None:
    while True:
        try:
            await mark_stale_devices_offline()
        except asyncio.CancelledError:
            raise
        except Exception:
            LOGGER.exception("Device offline monitor check failed")
        await asyncio.sleep(OFFLINE_CHECK_INTERVAL_SECONDS)
