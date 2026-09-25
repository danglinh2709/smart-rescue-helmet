import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { DeviceDetailPage } from './DeviceDetailPage'

describe('DeviceDetailPage', () => {
  it('renders the device route view from normalized runtime state', () => {
    render(<DeviceDetailPage back={() => undefined} device={{ device_id: 'FF01', device_status: 'ONLINE', risk_level: 'NORMAL', movement: 'WALKING', latest_telemetry: { device_id: 'FF01', timestamp: '2026-09-24T10:00:00Z', temperature: 31.5, co: 5, ax: 0, ay: 0, az: 9.81, gx: 0, gy: 0, gz: 0, movement: 'WALKING', fall: false, immobile: false, sos: false, risk_level: 'NORMAL', battery: 84, wifi: 'CONNECTED', mqtt: 'CONNECTED' }, latest_health: { device_id: 'FF01', timestamp: '2026-09-24T10:00:00Z', battery: 84, uptime_seconds: 10, wifi: 'CONNECTED', mqtt: 'CONNECTED', temperature_sensor: 'OK', co_sensor: 'OK', imu_sensor: 'OK' } }} />)
    expect(screen.getByRole('heading', { name: 'FF01' })).toBeInTheDocument()
    expect(screen.getByText('Temperature Sensor')).toBeInTheDocument()
    expect(screen.getByText('9.81')).toBeInTheDocument()
  })
})
