import math


class COSensorSimulator:
    def __init__(
        self,
        baseline: float = 3.0,
        amplitude: float = 0.45,
        phase_step: float = 0.17,
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
