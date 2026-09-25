import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))

from app.safety.engine import SafetyEngine
from app.schemas.telemetry import TelemetryMessage
from simulator.safety.local_engine import LocalSafetyEngine


def _backend_risk(temperature: float, co: float, battery: float, fall: bool) -> str:
    telemetry = TelemetryMessage.model_validate({
        "schema_version": "1.0", "device_id": "FF01", "timestamp": "2026-09-24T10:00:00+00:00", "source": "SIMULATOR",
        "sensors": {"temperature": temperature, "co": co, "imu": {"ax": 0, "ay": 0, "az": 9.81, "gx": 0, "gy": 0, "gz": 0}},
        "state": {"movement": "WALKING", "fall": fall, "immobile": False, "sos": False},
        "risk_level": "NORMAL", "device": {"battery": battery, "wifi": "CONNECTED", "mqtt": "CONNECTED"},
    })
    return SafetyEngine().evaluate(telemetry).risk_level.value


def test_local_safety_matches_backend_risk_for_reference_conditions() -> None:
    local = LocalSafetyEngine()
    for temperature, co, battery, fall in [(30.0, 3.0, 85.0, False), (55.0, 3.0, 85.0, False), (30.0, 3.0, 85.0, True)]:
        result = local.evaluate(temperature=temperature, co=co, battery=battery, fall=fall, immobile=False, sos=False)
        assert result.risk_level == _backend_risk(temperature, co, battery, fall)
