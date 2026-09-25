import type { DeviceEvent, DeviceHealth, DeviceState, Telemetry, WebSocketEnvelope } from '../types/dashboard'
const mapDevices = (devices: DeviceState[]) => new Map(devices.map((device) => [device.device_id, device]))
type RecordValue = Record<string, unknown>
const record = (value: unknown): RecordValue => value !== null && typeof value === 'object' ? value as RecordValue : {}
const string = (value: unknown, fallback = 'UNKNOWN') => typeof value === 'string' ? value : fallback
function telemetryFrom(data: unknown): Telemetry {
  const value = record(data); const sensors = record(value.sensors); const imu = record(sensors.imu); const state = record(value.state); const device = record(value.device)
  return { device_id: string(value.device_id), timestamp: string(value.timestamp, ''), temperature: (sensors.temperature ?? value.temperature ?? null) as number | null, co: (sensors.co ?? value.co ?? null) as number | null, ax: Number(imu.ax ?? value.ax ?? 0), ay: Number(imu.ay ?? value.ay ?? 0), az: Number(imu.az ?? value.az ?? 0), gx: Number(imu.gx ?? value.gx ?? 0), gy: Number(imu.gy ?? value.gy ?? 0), gz: Number(imu.gz ?? value.gz ?? 0), movement: string(state.movement ?? value.movement) as Telemetry['movement'], fall: Boolean(state.fall ?? value.fall), immobile: Boolean(state.immobile ?? value.immobile), sos: Boolean(state.sos ?? value.sos), risk_level: string(value.risk_level, 'NORMAL') as Telemetry['risk_level'], battery: (device.battery ?? value.battery ?? null) as number | null, wifi: string(device.wifi ?? value.wifi, 'DISCONNECTED') as Telemetry['wifi'], mqtt: string(device.mqtt ?? value.mqtt, 'DISCONNECTED') as Telemetry['mqtt'] }
}
function healthFrom(data: unknown): DeviceHealth { const value = record(data); const sensors = record(value.sensors); return { device_id: string(value.device_id), timestamp: string(value.timestamp, ''), battery: (value.battery ?? null) as number | null, uptime_seconds: (value.uptime_seconds ?? null) as number | null, wifi: string(value.wifi, 'DISCONNECTED') as DeviceHealth['wifi'], mqtt: string(value.mqtt, 'DISCONNECTED') as DeviceHealth['mqtt'], temperature_sensor: string(sensors.temperature ?? value.temperature_sensor, 'UNAVAILABLE'), co_sensor: string(sensors.co ?? value.co_sensor, 'UNAVAILABLE'), imu_sensor: string(sensors.imu ?? value.imu_sensor, 'UNAVAILABLE') } }
function stateFrom(data: unknown, fallbackId?: string): DeviceState { const value = record(data); const telemetry = value.latest_telemetry ?? value.telemetry; const status = record(value.status); const health = value.latest_health ?? value.health; const event = value.latest_event ?? value.event; const parsedTelemetry = telemetry ? telemetryFrom(telemetry) : null; const parsedHealth = health ? healthFrom(health) : null; return { device_id: string(value.device_id, fallbackId ?? ''), device_status: string(value.device_status ?? status.device_status, 'OFFLINE') as DeviceState['device_status'], risk_level: string(value.risk_level ?? parsedTelemetry?.risk_level ?? status.risk_level, 'NORMAL') as DeviceState['risk_level'], movement: string(value.movement ?? parsedTelemetry?.movement ?? status.movement) as DeviceState['movement'], last_seen: string(value.last_seen ?? parsedTelemetry?.timestamp ?? parsedHealth?.timestamp ?? null, '' ) || null, latest_telemetry: parsedTelemetry, latest_health: parsedHealth, latest_event: event ? { device_id: string(record(event).device_id, fallbackId ?? ''), ...(record(event) as Omit<DeviceEvent, 'device_id'>) } : null, actuators: value.actuators as DeviceState['actuators'] } }
export const devicesFromInitialState = (data: unknown): DeviceState[] => Array.isArray(data) ? data.map((item) => stateFrom(item)) : Object.entries(record(data)).map(([deviceId, value]) => stateFrom(value, deviceId))
export function applyRealtimeMessage(current: DeviceState[], message: WebSocketEnvelope): DeviceState[] {
  if (message.type === 'initial_state') return devicesFromInitialState(message.data)
  if (!message.device_id) return current
  const devices = mapDevices(current)
  const existing = devices.get(message.device_id) ?? { device_id: message.device_id, device_status: 'ONLINE', risk_level: 'NORMAL', movement: 'UNKNOWN' } as DeviceState
  let next: DeviceState
  if (message.type === 'device_state') next = stateFrom(message.data, message.device_id)
  else if (message.type === 'telemetry') { const telemetry = telemetryFrom(message.data); next = { ...existing, risk_level: telemetry.risk_level, movement: telemetry.movement, last_seen: telemetry.timestamp, latest_telemetry: telemetry } }
  else if (message.type === 'health') { const health = healthFrom(message.data); next = { ...existing, last_seen: health.timestamp, latest_health: health } }
  else if (message.type === 'status') next = { ...existing, ...(message.data as Partial<DeviceState>), last_seen: message.timestamp ?? existing.last_seen }
  else if (message.type === 'event') next = { ...existing, last_seen: message.timestamp ?? existing.last_seen, latest_event: { device_id: message.device_id, ...(message.data as Omit<DeviceEvent, 'device_id'>) } }
  else return current
  devices.set(message.device_id, next); return [...devices.values()]
}
