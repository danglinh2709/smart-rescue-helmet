import json
import logging
from uuid import uuid4

from pydantic import ValidationError

from app.core.enums import EventSeverity, EventType, RiskLevel
from app.database.db import SessionLocal

from app.schemas.telemetry import TelemetryMessage
from app.schemas.device_status import DeviceStatusMessage
from app.schemas.device_health import DeviceHealthMessage
from app.schemas.event import EventMessage

from app.services.device_service import ensure_device_exists
from app.services.telemetry_service import save_telemetry
from app.services.status_service import save_status
from app.services.device_state import update_device
from app.services.health_service import save_health
from app.services.event_service import save_event

from app.safety.engine import SafetyEngine


logger = logging.getLogger(__name__)

# ============================================================
# M6 - SAFETY ENGINE
# ============================================================

safety_engine = SafetyEngine()


def create_event_from_safety_result(
    device_id: str,
    telemetry: TelemetryMessage,
    risk_level: RiskLevel,
    reasons: list[str],
) -> EventMessage | None:
    """
    Tạo Event từ kết quả của Safety Engine.

    Safety Engine chịu trách nhiệm:
        - quyết định RiskLevel
        - xác định Reasons

    Hàm này chuyển Reasons thành EventMessage
    để lưu vào PostgreSQL.
    """

    # NORMAL -> không có safety event
    if risk_level == RiskLevel.NORMAL:
        return None

    event_type = None

    # ========================================================
    # Xác định EventType từ Safety Reason
    # ========================================================

    for reason in reasons:

        if reason == "SOS_PRESSED":
            event_type = EventType.SOS_PRESSED
            break

        if reason in {
            "FALL_DETECTED",
            "FALL_AND_IMMOBILE",
        }:
            event_type = EventType.FALL_DETECTED
            break

        if reason in {
            "CRITICAL_CO",
            "HIGH_CO",
        }:
            event_type = EventType.CO_HIGH
            break

        if reason in {
            "CRITICAL_TEMPERATURE",
            "HIGH_TEMPERATURE",
        }:
            event_type = EventType.TEMPERATURE_HIGH
            break

        if reason == "LOW_BATTERY":
            event_type = EventType.LOW_BATTERY
            break

    # Không có reason nào tương ứng với EventType
    if event_type is None:
        return None

    # ========================================================
    # Xác định Event Severity
    # ========================================================

    if risk_level == RiskLevel.CRITICAL:
        severity = EventSeverity.CRITICAL
    else:
        severity = EventSeverity.WARNING

    # ========================================================
    # Tạo EventMessage
    # ========================================================

    return EventMessage(
        schema_version="1.0",
        device_id=device_id,
        timestamp=telemetry.timestamp,
        source=telemetry.source,
        event_id=uuid4(),
        event_type=event_type,
        severity=severity,
        data={
            "temperature": telemetry.sensors.temperature,
            "co": telemetry.sensors.co,
            "movement": telemetry.state.movement,
            "fall": telemetry.state.fall,
            "immobile": telemetry.state.immobile,
            "sos": telemetry.state.sos,
            "battery": telemetry.device.battery,
            "risk_level": risk_level.value,
            "reasons": reasons,
        },
    )


def handle_message(topic: str, payload: str) -> None:
    """
    Xử lý message nhận từ MQTT Broker.

    M5:
        MQTT
          ↓
        JSON
          ↓
        Pydantic
          ↓
        Runtime State
          ↓
        PostgreSQL

    M6 bổ sung:

        Telemetry
          ↓
        Safety Engine
          ↓
        Risk Level + Reasons
          ↓
        Telemetry DB + Safety Event
    """

    # ========================================================
    # 1. KIỂM TRA MQTT TOPIC
    # ========================================================

    parts = topic.split("/")

    # Topic chuẩn:
    # helmet/{device_id}/{message_type}

    if len(parts) != 3 or parts[0] != "helmet":
        logger.warning(
            "Invalid topic: %s",
            topic,
        )
        return

    _, device_id, message_type = parts

    # ========================================================
    # 2. PARSE JSON
    # ========================================================

    try:
        data = json.loads(payload)

    except json.JSONDecodeError:
        logger.error(
            "Invalid JSON received on topic %s",
            topic,
        )
        return

    # ========================================================
    # 3. VALIDATE + XỬ LÝ MESSAGE
    # ========================================================

    try:

        # ====================================================
        # TELEMETRY
        # ====================================================

        if message_type == "telemetry":

            # ------------------------------------------------
            # M5 - Pydantic validation
            # ------------------------------------------------

            obj = TelemetryMessage.model_validate(data)

            # ------------------------------------------------
            # M6 - SAFETY ENGINE
            # ------------------------------------------------

            safety_result = safety_engine.evaluate(obj)

            logger.info(
                "Safety evaluation "
                "device=%s risk=%s reasons=%s",
                device_id,
                safety_result.risk_level,
                safety_result.reasons,
            )

            # ------------------------------------------------
            # M6 - Backend tự quyết định risk_level
            #
            # Không tin risk_level từ Simulator.
            # ------------------------------------------------

            telemetry_data = obj.model_dump()

            telemetry_data["risk_level"] = (
                safety_result.risk_level
            )

            # ------------------------------------------------
            # Runtime State
            # ------------------------------------------------

            update_device(
                device_id,
                "telemetry",
                telemetry_data,
            )

            # ------------------------------------------------
            # PostgreSQL
            # ------------------------------------------------

            db = SessionLocal()

            try:

                logger.info(
                    "Saving telemetry to PostgreSQL..."
                )

                ensure_device_exists(
                    db,
                    device_id,
                )

                save_telemetry(
                    db,
                    telemetry_data,
                )

                logger.info(
                    "Telemetry saved successfully."
                )

                # --------------------------------------------
                # M6 - CREATE SAFETY EVENT
                # --------------------------------------------

                event = create_event_from_safety_result(
                    device_id=device_id,
                    telemetry=obj,
                    risk_level=safety_result.risk_level,
                    reasons=safety_result.reasons,
                )

                if event is not None:

                    save_event(
                        db,
                        event.model_dump(),
                    )

                    logger.info(
                        "Safety event created "
                        "device=%s type=%s severity=%s",
                        device_id,
                        event.event_type,
                        event.severity,
                    )

            except Exception:

                logger.exception(
                    "Failed to save telemetry/event"
                )

            finally:

                db.close()

            logger.info(
                "Telemetry received [%s]",
                device_id,
            )

        # ====================================================
        # STATUS
        # ====================================================

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

            except Exception:

                logger.exception(
                    "Failed to save status"
                )

            finally:

                db.close()

            logger.info(
                "Status received [%s]",
                device_id,
            )

        # ====================================================
        # HEALTH
        # ====================================================

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

            except Exception:

                logger.exception(
                    "Failed to save health"
                )

            finally:

                db.close()

            logger.info(
                "Health received [%s]",
                device_id,
            )

        # ====================================================
        # EVENT
        # ====================================================

        elif message_type == "event":

            # ------------------------------------------------
            # M6:
            #
            # Event không còn được tin từ Simulator.
            #
            # Safety Engine của Backend tự tạo Event.
            #
            # Nếu vẫn nhận event từ Simulator thì bỏ qua
            # để tránh tạo event trùng.
            # ------------------------------------------------

            logger.warning(
                "Ignoring simulator event. "
                "Events are generated by Safety Engine."
            )

        # ====================================================
        # UNSUPPORTED MESSAGE
        # ====================================================

        else:

            logger.warning(
                "Unsupported message type: %s",
                message_type,
            )

    # ========================================================
    # 4. PYDANTIC VALIDATION ERROR
    # ========================================================

    except ValidationError as ex:

        logger.error(
            "Validation failed on topic %s\n%s",
            topic,
            ex,
        )