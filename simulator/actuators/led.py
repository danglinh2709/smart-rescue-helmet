from enum import Enum


class LedState(str, Enum):
    GREEN = "GREEN"
    YELLOW = "YELLOW"
    RED = "RED"


class VirtualLED:
    def __init__(self) -> None:
        self.state = LedState.GREEN

    def set(self, state: LedState) -> None:
        self.state = state
