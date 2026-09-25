import type { EventSeverity, RiskLevel } from '../types/dashboard'
export function RiskBadge({ level }: { level: RiskLevel }) { return <span className={`badge risk-${level.toLowerCase()}`}>Risk: {level}</span> }
export function SeverityBadge({ severity }: { severity: EventSeverity }) { return <span className={`badge severity-${severity.toLowerCase()}`}>Severity: {severity}</span> }
