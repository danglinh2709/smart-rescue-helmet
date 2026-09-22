import os
import aiomqtt

MQTT_HOST = os.getenv("MQTT_HOST", "mosquitto")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))


def get_mqtt_client() -> aiomqtt.Client:
    """
    Tạo MQTT Client kết nối tới Mosquitto Broker.
    """
    return aiomqtt.Client(
        hostname=MQTT_HOST,
        port=MQTT_PORT,
    )