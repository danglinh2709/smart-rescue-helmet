import math


class TemperatureSensorSimulator:
    def __init__(
        self,
        baseline: float = 30.0,
        amplitude: float = 1.4,
        phase_step: float = 0.2,
    ) -> None:
        self._baseline = baseline
        self._amplitude = amplitude
        self._phase_step = phase_step
        self._sample_index = 0

    def read(self) -> float:
        value = self._baseline + self._amplitude * math.sin(
            self._sample_index * self._phase_step
        )
        self._sample_index += 1
        return round(value, 2)
