import json
import logging

from pydantic import ValidationError
from app.database.db import SessionLocal

from app.services.device_service import ensure_device_exists
from app.services.telemetry_service import save_telemetry
from app.schemas.telemetry import TelemetryMessage
from app.schemas.device_status import DeviceStatusMessage
from app.schemas.device_health import DeviceHealthMessage
from app.schemas.event import EventMessage
from app.services.status_service import save_status
from app.services.device_state import update_device
from app.services.health_service import save_health
from app.services.event_service import save_event
logger = logging.getLogger(__name__)


def handle_message(topic: str, payload: str) -> None:
    """
    Xử lý message nhận từ MQTT Broker.

    Luồng xử lý:
        MQTT Message
            ↓
        Parse JSON
            ↓
        Validate bằng Pydantic
            ↓
        Update Runtime State
            ↓
        Ghi log
    """

    parts = topic.split("/")

    # Topic chuẩn:
    # helmet/{device_id}/{message_type}
    if len(parts) != 3 or parts[0] != "helmet":
        logger.warning("Invalid topic: %s", topic)
        return

    _, device_id, message_type = parts

    # Parse JSON
    try:
        data = json.loads(payload)

    except json.JSONDecodeError:
        logger.error("Invalid JSON received on topic %s", topic)
        return

    # Validate + Runtime State
    try:

        if message_type == "telemetry":

            obj = TelemetryMessage.model_validate(data)

            update_device(
                device_id,
                "telemetry",
                obj.model_dump(),
            )
            # Lưu PostgreSQL
            db = SessionLocal()

            try:
                logger.info("Saving telemetry to PostgreSQL...")

                ensure_device_exists(
                    db,
                    device_id,
                )

                save_telemetry(
                    db,
                    obj.model_dump(),
                )

                logger.info("Telemetry saved successfully.")

            except Exception:
                logger.exception("Failed to save telemetry")
            finally:
                db.close()

            logger.info(
                "Telemetry received [%s]",
                device_id,
            )

        elif message_type == "status":

            obj = DeviceStatusMessage.model_validate(data)

            update_device(
                device_id,
                "status",
                obj.model_dump(),
            )

            db = SessionLocal()

            try:
                ensure_device_exists(
                    db,
                    device_id,
                )

                save_status(
                    db,
                    obj.model_dump(),
                )

            finally:
                db.close()

            logger.info(
                "Status received [%s]",
                device_id,
            )

        elif message_type == "health":

            obj = DeviceHealthMessage.model_validate(data)

            update_device(
                device_id,
                "health",
                obj.model_dump(),
            )

            db = SessionLocal()

            try:
                ensure_device_exists(
                    db,
                    device_id,
                )

                save_health(
                    db,
                    obj.model_dump(),
                )

            finally:
                db.close()

            logger.info(
                "Health received [%s]",
                device_id,
            )

        elif message_type == "event":

            obj = EventMessage.model_validate(data)

            update_device(
                device_id,
                "event",
                obj.model_dump(),
            )

            db = SessionLocal()

            try:
                ensure_device_exists(
                    db,
                    device_id,
                )

                save_event(
                    db,
                    obj.model_dump(),
                )

            finally:
                db.close()

            logger.info(
                "Event received [%s]",
                device_id,
            )

        else:

            logger.warning(
                "Unsupported message type: %s",
                message_type,
            )
    except ValidationError as ex:

        logger.error(
            "Validation failed on topic %s\n%s",
            topic,
            ex,
        )