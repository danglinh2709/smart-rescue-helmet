from simulator.sensors.battery import BatterySimulator
from simulator.sensors.co import COSensorSimulator
from simulator.sensors.imu import IMUSensorSimulator
from simulator.sensors.temperature import TemperatureSensorSimulator


class LowBatteryScenario:
    def __init__(
        self,
        temperature: TemperatureSensorSimulator | None = None,
        co: COSensorSimulator | None = None,
        imu: IMUSensorSimulator | None = None,
        battery: BatterySimulator | None = None,
    ) -> None:
        self.temperature = temperature or TemperatureSensorSimulator()
        self.co = co or COSensorSimulator()
        self.imu = imu or IMUSensorSimulator()
        self.battery = battery or BatterySimulator()

    def read(self) -> dict[str, object]:
        return {
            "temperature": self.temperature.read(),
            "co": self.co.read(),
            "imu": self.imu.read(),
            "battery": 10,
            "movement": "WALKING",
            "risk_level": "WARNING",
            "fall": False,
            "immobile": False,
            "sos": False,
        }
