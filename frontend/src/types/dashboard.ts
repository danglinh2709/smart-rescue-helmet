export type RiskLevel = 'NORMAL' | 'WARNING' | 'CRITICAL'
export type DeviceStatus = 'ONLINE' | 'OFFLINE'
export type ConnectionStatus = 'CONNECTED' | 'DISCONNECTED'
export type MovementState = 'UNKNOWN' | 'STATIONARY' | 'WALKING' | 'RUNNING' | 'CRAWLING' | 'UNUSUAL_MOVEMENT' | 'FALL' | 'IMMOBILE'
export type EventSeverity = 'INFO' | 'WARNING' | 'CRITICAL'
export type LedState = 'GREEN' | 'YELLOW' | 'RED'
export interface ActuatorState { led: LedState; buzzer: boolean; vibration: boolean }
export interface Telemetry { device_id: string; timestamp: string; temperature: number | null; co: number | null; ax: number; ay: number; az: number; gx: number; gy: number; gz: number; movement: MovementState; fall: boolean; immobile: boolean; sos: boolean; risk_level: RiskLevel; battery: number | null; wifi: ConnectionStatus; mqtt: ConnectionStatus }
export interface DeviceHealth { device_id: string; timestamp: string; battery: number | null; uptime_seconds: number | null; wifi: ConnectionStatus; mqtt: ConnectionStatus; temperature_sensor: string; co_sensor: string; imu_sensor: string }
export interface DeviceEvent { id?: number; event_id?: string; device_id: string; timestamp: string; event_type: string; severity: EventSeverity; data: Record<string, unknown>; risk_level?: RiskLevel }
export interface DeviceState { device_id: string; device_status: DeviceStatus; risk_level: RiskLevel; movement: MovementState; last_seen?: string | null; latest_telemetry?: Telemetry | null; latest_health?: DeviceHealth | null; latest_event?: DeviceEvent | null; actuators?: ActuatorState | null }
export interface ApiDevicesResponse { count: number; devices: unknown }
export interface WebSocketEnvelope { type: 'initial_state' | 'telemetry' | 'status' | 'health' | 'event' | 'device_state'; device_id?: string; timestamp?: string; data: unknown }
