class IMUSensorSimulator:
    _WALKING_CYCLE = (
        (0.08, 0.02, 9.76, 0.04, 0.08, 0.02),
        (0.16, 0.05, 9.84, 0.07, 0.12, 0.03),
        (0.05, -0.03, 9.88, 0.02, 0.06, -0.01),
        (-0.10, -0.04, 9.80, -0.05, -0.08, -0.02),
        (-0.15, 0.01, 9.72, -0.07, -0.11, 0.01),
        (0.02, 0.03, 9.81, 0.01, 0.04, 0.02),
    )

    def __init__(self) -> None:
        self._sample_index = 0

    def read(self) -> dict[str, float]:
        sample = self._WALKING_CYCLE[self._sample_index % len(self._WALKING_CYCLE)]
        self._sample_index += 1
        return dict(zip(("ax", "ay", "az", "gx", "gy", "gz"), sample))
