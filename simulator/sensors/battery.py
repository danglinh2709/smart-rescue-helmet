class BatterySimulator:
    def __init__(
        self,
        initial_level: float = 85.0,
        drain_per_read: float = 0.001,
    ) -> None:
        if not 0 <= initial_level <= 100:
            raise ValueError("initial_level must be between 0 and 100")
        if drain_per_read < 0:
            raise ValueError("drain_per_read cannot be negative")
        self._level = float(initial_level)
        self._drain_per_read = float(drain_per_read)

    def read(self) -> float:
        current = round(self._level, 2)
        self._level = max(0.0, self._level - self._drain_per_read)
        return current
