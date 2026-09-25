class VirtualBuzzer:
    def __init__(self) -> None:
        self.on = False

    def set(self, enabled: bool) -> None:
        self.on = enabled
