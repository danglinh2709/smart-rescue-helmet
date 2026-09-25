import { cleanup, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it } from 'vitest'

import { DeviceCard } from './DeviceCard'

const device = {
  device_id: 'FF01',
  device_status: 'ONLINE' as const,
  risk_level: 'NORMAL' as const,
  movement: 'WALKING' as const,
  latest_telemetry: {
    device_id: 'FF01',
    timestamp: '2026-09-24T10:00:00Z',
    temperature: 31.5,
    co: 5,
    risk_level: 'NORMAL' as const,
    movement: 'WALKING' as const, fall: false, immobile: false, sos: false,
    ax: 0, ay: 0, az: 9.81, gx: 0, gy: 0, gz: 0, battery: 84,
    wifi: 'CONNECTED' as const, mqtt: 'CONNECTED' as const,
  },
  latest_health: { device_id: 'FF01', timestamp: '2026-09-24T10:00:00Z', battery: 84, uptime_seconds: 1, wifi: 'CONNECTED' as const, mqtt: 'CONNECTED' as const, temperature_sensor: 'OK', co_sensor: 'OK', imu_sensor: 'OK' },
  latest_event: null,
}

afterEach(cleanup)

describe('DeviceCard', () => {
  it.each(['NORMAL', 'WARNING', 'CRITICAL'] as const)('renders %s risk as text', (risk) => {
    render(<DeviceCard device={{ ...device, risk_level: risk, latest_telemetry: { ...device.latest_telemetry, risk_level: risk } }} onOpen={() => undefined} />)

    expect(screen.getByText(`Risk: ${risk}`)).toBeInTheDocument()
    expect(screen.getByText('FF01')).toBeInTheDocument()
  })
})
