import asyncio
import logging

import aiomqtt

from app.mqtt.client import get_mqtt_client
from app.mqtt.handlers import handle_message

logger = logging.getLogger(__name__)

TOPICS = [
    "helmet/+/telemetry",
    "helmet/+/status",
    "helmet/+/health",
    "helmet/+/event",
]


async def start_subscriber() -> None:
    while True:
        try:
            logger.info("Connecting to MQTT Broker...")

            async with get_mqtt_client() as client:

                # Subscribe các topic
                for topic in TOPICS:
                    await client.subscribe(topic)
                    logger.info("Subscribed: %s", topic)

                logger.info("MQTT Subscriber is running...")

                # Lắng nghe message
                async for message in client.messages:

                    topic = str(message.topic)
                    payload = message.payload.decode("utf-8")

                    logger.info("Received message: %s", topic)

                    # Chuyển cho handler xử lý
                    handle_message(topic, payload)

        except aiomqtt.MqttError as ex:
            logger.error(
                "MQTT connection lost: %s. Reconnecting in 3 seconds...",
                ex,
            )
            await asyncio.sleep(3)

        except asyncio.CancelledError:
            logger.info("MQTT Subscriber stopped.")
            break

        except Exception as ex:
            logger.exception("Unexpected error: %s", ex)
            await asyncio.sleep(3)