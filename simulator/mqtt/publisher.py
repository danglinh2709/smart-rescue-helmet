import json
import logging
from threading import Event
from typing import Any

import paho.mqtt.client as mqtt

from simulator.contracts.validator import ContractValidator
from simulator.mqtt.topics import build_topic


LOGGER = logging.getLogger(__name__)


class MqttPublisher:
    def __init__(
        self,
        host: str,
        port: int,
        validator: ContractValidator,
        client: Any | None = None,
        connect_timeout: float = 10.0,
    ) -> None:
        self._host = host
        self._port = port
        self._validator = validator
        self._connect_timeout = connect_timeout
        self._connected_event = Event()
        self._connected = False
        self._connection_error: str | None = None

        self._client = client or mqtt.Client(
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2
        )

        self._client.on_connect = self._on_connect
        self._client.on_disconnect = self._on_disconnect

    def _on_connect(
        self,
        client: Any,
        userdata: Any,
        flags: Any,
        reason_code: Any,
        properties: Any,
    ) -> None:
        if getattr(reason_code, "is_failure", reason_code != 0):
            self._connection_error = str(reason_code)
        else:
            self._connected = True
            LOGGER.info(
                "mqtt connected host=%s port=%s",
                self._host,
                self._port,
            )

        self._connected_event.set()

    def _on_disconnect(
        self,
        client: Any,
        userdata: Any,
        disconnect_flags: Any,
        reason_code: Any,
        properties: Any,
    ) -> None:
        self._connected = False

        if getattr(reason_code, "is_failure", reason_code != 0):
            LOGGER.warning(
                "mqtt disconnected reason=%s",
                reason_code,
            )
        else:
            LOGGER.info("mqtt disconnected")

    def connect(self) -> None:
        self._connected_event.clear()
        self._connection_error = None

        result = self._client.connect(
            self._host,
            self._port,
            keepalive=60,
        )

        if result != mqtt.MQTT_ERR_SUCCESS:
            raise ConnectionError(
                f"MQTT connect failed with code {result}"
            )

        self._client.loop_start()

        if not self._connected_event.wait(self._connect_timeout):
            self.disconnect()
            raise TimeoutError(
                f"MQTT connection timed out for {self._host}:{self._port}"
            )

        if self._connection_error is not None:
            self.disconnect()
            raise ConnectionError(
                f"MQTT connection rejected: {self._connection_error}"
            )

    def disconnect(self) -> None:
        try:
            self._client.disconnect()
        finally:
            self._client.loop_stop()
            self._connected = False

    def _ensure_connected(self) -> bool:
        if self._connected:
            return True
        LOGGER.info("mqtt reconnecting host=%s port=%s", self._host, self._port)
        self._connected_event.clear()
        try:
            result = self._client.reconnect()
        except Exception as exc:
            LOGGER.warning("mqtt reconnect failed error=%s", exc)
            return False
        if result != mqtt.MQTT_ERR_SUCCESS:
            LOGGER.warning("mqtt reconnect failed code=%s", result)
            return False
        if not self._connected_event.wait(self._connect_timeout):
            LOGGER.warning("mqtt reconnect timed out")
            return False
        return self._connected

    def _publish(
        self,
        message_type: str,
        payload: dict[str, Any],
        qos: int,
    ) -> bool:
        if not self._ensure_connected():
            return False

        validator = getattr(
            self._validator,
            f"validate_{message_type}",
        )

        validator(payload)

        topic = build_topic(
            str(payload["device_id"]),
            message_type,
        )

        encoded = json.dumps(
            payload,
            separators=(",", ":"),
            ensure_ascii=False,
        )

        publish_result = self._client.publish(
            topic,
            encoded,
            qos=qos,
            retain=False,
        )

        if publish_result.rc != mqtt.MQTT_ERR_SUCCESS:
            raise RuntimeError(
                f"MQTT publish failed topic={topic} code={publish_result.rc}"
            )

        publish_result.wait_for_publish(timeout=5.0)
        return True

    def publish_telemetry(
        self,
        payload: dict[str, Any],
    ) -> None:
        self._publish(
            "telemetry",
            payload,
            qos=0,
        )

        LOGGER.info(
            "telemetry published device=%s temp=%s co=%s movement=%s",
            payload["device_id"],
            payload["sensors"]["temperature"],
            payload["sensors"]["co"],
            payload["state"]["movement"],
        )

    def publish_status(
        self,
        payload: dict[str, Any],
    ) -> None:
        self._publish(
            "status",
            payload,
            qos=1,
        )

        LOGGER.info(
            "status published device=%s risk=%s",
            payload["device_id"],
            payload["risk_level"],
        )

    def publish_health(
        self,
        payload: dict[str, Any],
    ) -> None:
        self._publish(
            "health",
            payload,
            qos=1,
        )

        LOGGER.info(
            "health published device=%s battery=%s",
            payload["device_id"],
            payload["battery"],
        )

    def publish_event(
        self,
        payload: dict[str, Any],
    ) -> None:
        # Không có event thì không publish
        if not payload:
            return

        self._publish(
            "event",
            payload,
            qos=1,
        )

        LOGGER.info(
            "event published device=%s type=%s severity=%s",
            payload["device_id"],
            payload["event_type"],
            payload["severity"],
        )
