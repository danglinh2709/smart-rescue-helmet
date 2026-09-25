import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { EventTable } from './EventTable'

describe('EventTable', () => {
  it('renders a realtime safety event with its severity', () => {
    render(<EventTable events={[{ device_id: 'FF01', timestamp: '2026-09-24T10:00:00Z', event_type: 'TEMPERATURE_HIGH', severity: 'CRITICAL', data: { temperature: 48 } }]} />)
    expect(screen.getByText('TEMPERATURE_HIGH')).toBeInTheDocument()
    expect(screen.getByText('Severity: CRITICAL')).toBeInTheDocument()
  })

  it('renders an explicit empty state', () => {
    render(<EventTable events={[]} empty="No backend events." />)
    expect(screen.getByText('No backend events.')).toBeInTheDocument()
  })
})
