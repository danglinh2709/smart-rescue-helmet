import { describe, expect, it } from 'vitest'

import { applyRealtimeMessage, devicesFromInitialState } from './dashboard'

describe('dashboard realtime state', () => {
  it('populates devices from an initial state snapshot', () => {
    const devices = devicesFromInitialState([
      { device_id: 'FF01', device_status: 'ONLINE', risk_level: 'NORMAL', movement: 'WALKING', latest_telemetry: null, latest_health: null, latest_event: null },
    ])

    expect(devices[0].device_id).toBe('FF01')
  })

  it('normalizes the runtime-device map returned by the REST API', () => {
    const devices = devicesFromInitialState({
      FF01: {
        device_id: 'FF01',
        telemetry: { device_id: 'FF01', timestamp: '2026-09-24T10:00:00Z', sensors: { temperature: 31.5, co: 5, imu: { ax: 0, ay: 0, az: 9.81, gx: 0, gy: 0, gz: 0 } }, state: { movement: 'WALKING', fall: false, immobile: false, sos: false }, risk_level: 'NORMAL', device: { battery: 84, wifi: 'CONNECTED', mqtt: 'CONNECTED' } },
        status: { device_status: 'ONLINE', risk_level: 'NORMAL', movement: 'WALKING' },
        health: null,
        event: null,
      },
    })

    expect(devices[0]).toMatchObject({ device_id: 'FF01', device_status: 'ONLINE', risk_level: 'NORMAL', movement: 'WALKING' })
    expect(devices[0].latest_telemetry?.temperature).toBe(31.5)
  })

  it('merges telemetry and health updates for the same device', () => {
    const afterTelemetry = applyRealtimeMessage([], {
      type: 'telemetry',
      device_id: 'FF01',
      timestamp: '2026-09-24T10:00:00Z',
      data: { device_id: 'FF01', timestamp: '2026-09-24T10:00:00Z', temperature: 31.5, co: 5, risk_level: 'NORMAL', movement: 'WALKING', fall: false, immobile: false, sos: false, ax: 0, ay: 0, az: 9.81, gx: 0, gy: 0, gz: 0, battery: 84, wifi: 'CONNECTED', mqtt: 'CONNECTED' },
    })
    const afterHealth = applyRealtimeMessage(afterTelemetry, {
      type: 'health',
      device_id: 'FF01',
      timestamp: '2026-09-24T10:00:01Z',
      data: { device_id: 'FF01', timestamp: '2026-09-24T10:00:01Z', battery: 84, uptime_seconds: 1, wifi: 'CONNECTED', mqtt: 'CONNECTED', temperature_sensor: 'OK', co_sensor: 'OK', imu_sensor: 'OK' },
    })

    expect(afterHealth[0].latest_telemetry?.temperature).toBe(31.5)
    expect(afterHealth[0].latest_health?.battery).toBe(84)
  })

  it('stores a realtime safety event for its device', () => {
    const devices = applyRealtimeMessage([], {
      type: 'event',
      device_id: 'FF01',
      timestamp: '2026-09-24T10:00:00Z',
      data: {
        event_id: 'event-1',
        event_type: 'TEMPERATURE_HIGH',
        severity: 'CRITICAL',
        timestamp: '2026-09-24T10:00:00Z',
        data: {},
      },
    })

    expect(devices[0].latest_event?.event_type).toBe('TEMPERATURE_HIGH')
  })
})
