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
from app.services.device_state import (
    record_safety_event,
    should_emit_safety_event,
    touch_device,
    update_device,
)
from app.services.health_service import save_health
from app.services.event_service import save_event

from app.safety.engine import SafetyEngine
from app.websocket.service import publish_device_state, publish_realtime_message
from app.reliability.offline_monitor import handle_device_recovery


logger = logging.getLogger(__name__)

# ============================================================
# M6 - SAFETY ENGINE
# ============================================================

safety_engine = SafetyEngine()


async def _touch_valid_device(device_id: str) -> None:
    if touch_device(device_id):
        await handle_device_recovery(device_id)


def _matches_topic_device(device_id: str, payload_device_id: str) -> bool:
    if device_id == payload_device_id:
        return True
    logger.warning(
        "Ignoring MQTT topic/payload device mismatch topic_device=%s payload_device=%s",
        device_id,
        payload_device_id,
    )
    return False


def _actuator_state(risk_level: RiskLevel) -> dict[str, object]:
    if risk_level == RiskLevel.CRITICAL:
        return {"led": "RED", "buzzer": True, "vibration": True}
    if risk_level == RiskLevel.WARNING:
        return {"led": "YELLOW", "buzzer": False, "vibration": False}
    return {"led": "GREEN", "buzzer": False, "vibration": False}


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


async def handle_message(topic: str, payload: str) -> None:
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
            if not _matches_topic_device(device_id, obj.device_id):
                return
            await _touch_valid_device(device_id)

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

            telemetry_data = obj.model_dump(mode="json")

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
            event = None
            event_saved = False

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
                    if should_emit_safety_event(
                        device_id,
                        event.event_type.value,
                        event.severity.value,
                    ):
                        save_event(
                            db,
                            event.model_dump(),
                        )
                        event_saved = True
                        record_safety_event(
                            device_id,
                            event.event_type.value,
                            event.severity.value,
                        )

                        logger.info(
                            "Safety event created "
                            "device=%s type=%s severity=%s",
                            device_id,
                            event.event_type,
                            event.severity,
                        )
                    else:
                        event = None
                else:
                    record_safety_event(device_id, None, None)

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
            update_device(
                device_id,
                "actuators",
                _actuator_state(safety_result.risk_level),
            )

            await publish_realtime_message(
                "telemetry",
                device_id=device_id,
                timestamp=telemetry_data["timestamp"],
                data=telemetry_data,
            )

            if event is not None and event_saved:
                event_data = event.model_dump(mode="json")
                update_device(device_id, "event", event_data)
                await publish_realtime_message(
                    "event",
                    device_id=device_id,
                    timestamp=event_data["timestamp"],
                    data=event_data,
                )

            await publish_device_state(device_id)

        # ====================================================
        # STATUS
        # ====================================================

        elif message_type == "status":

            obj = DeviceStatusMessage.model_validate(data)
            if not _matches_topic_device(device_id, obj.device_id):
                return
            await _touch_valid_device(device_id)

            status_data = obj.model_dump(mode="json")
            update_device(device_id, "status", status_data)

            db = SessionLocal()

            try:

                ensure_device_exists(
                    db,
                    device_id,
                )

                save_status(
                    db,
                    status_data,
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

            await publish_realtime_message(
                "status",
                device_id=device_id,
                timestamp=status_data["timestamp"],
                data=status_data,
            )
            await publish_device_state(device_id)

        # ====================================================
        # HEALTH
        # ====================================================

        elif message_type == "health":

            obj = DeviceHealthMessage.model_validate(data)
            if not _matches_topic_device(device_id, obj.device_id):
                return
            await _touch_valid_device(device_id)

            health_data = obj.model_dump(mode="json")
            update_device(device_id, "health", health_data)

            db = SessionLocal()

            try:

                ensure_device_exists(
                    db,
                    device_id,
                )

                save_health(
                    db,
                    health_data,
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

            await publish_realtime_message(
                "health",
                device_id=device_id,
                timestamp=health_data["timestamp"],
                data=health_data,
            )
            await publish_device_state(device_id)

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
