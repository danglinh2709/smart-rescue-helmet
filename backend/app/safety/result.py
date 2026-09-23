from dataclasses import dataclass, field

from app.core.enums import RiskLevel


@dataclass
class SafetyResult:
    risk_level: RiskLevel
    reasons: list[str] = field(default_factory=list)