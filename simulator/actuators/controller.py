from dataclasses import dataclass
import logging

from simulator.actuators.buzzer import VirtualBuzzer
from simulator.actuators.led import LedState, VirtualLED
from simulator.actuators.vibration import VirtualVibration
from simulator.safety.local_engine import LocalSafetyResult

LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class ActuatorState:
    led: str
    buzzer: bool
    vibration: bool


class ActuatorController:
    def __init__(self) -> None:
        self.led = VirtualLED()
        self.buzzer = VirtualBuzzer()
        self.vibration = VirtualVibration()

    @property
    def state(self) -> ActuatorState:
        return ActuatorState(self.led.state.value, self.buzzer.on, self.vibration.on)

    def apply(self, result: LocalSafetyResult) -> ActuatorState:
        previous = self.state
        if result.risk_level == "CRITICAL":
            self.led.set(LedState.RED)
            self.buzzer.set(True)
            self.vibration.set(True)
        elif result.risk_level == "WARNING":
            self.led.set(LedState.YELLOW)
            self.buzzer.set(False)
            self.vibration.set(False)
        else:
            self.led.set(LedState.GREEN)
            self.buzzer.set(False)
            self.vibration.set(False)
        if previous != self.state:
            LOGGER.info("local actuator state changed state=%s", self.state)
        return self.state
