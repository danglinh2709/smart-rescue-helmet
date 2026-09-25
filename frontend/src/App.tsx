import { Shell } from './components/Shell'
import { useDashboard } from './hooks/useDashboard'
import { useRoute } from './hooks/useRoute'
import { DeviceDetailPage } from './pages/DeviceDetailPage'
import { DevicesPage } from './pages/DevicesPage'
import { EventsPage } from './pages/EventsPage'
import { HistoryPage } from './pages/HistoryPage'
import { OverviewPage } from './pages/OverviewPage'
import { SystemPage } from './pages/SystemPage'

export default function App() {
  const dashboard = useDashboard()
  const { path, navigate } = useRoute()
  const detailId = path.match(/^\/devices\/([^/]+)$/)?.[1]
  const section = detailId || path === '/devices' ? 'devices' : path === '/events' ? 'events' : path === '/history' ? 'history' : path === '/system' ? 'system' : 'overview'
  let page = <OverviewPage devices={dashboard.devices} navigate={navigate} />
  if (detailId) page = <DeviceDetailPage device={dashboard.devices.find((device) => device.device_id === decodeURIComponent(detailId))} back={() => navigate('/devices')} />
  else if (path === '/devices') page = <DevicesPage devices={dashboard.devices} navigate={navigate} />
  else if (path === '/events') page = <EventsPage events={dashboard.events} />
  else if (path === '/history') page = <HistoryPage devices={dashboard.devices} />
  else if (path === '/system') page = <SystemPage devices={dashboard.devices} wsStatus={dashboard.wsStatus} apiOnline={dashboard.apiOnline} />
  return <Shell section={section} navigate={navigate} wsStatus={dashboard.wsStatus} deviceCount={dashboard.devices.length}>{dashboard.loading && <p className="loading-state">Loading command center…</p>}{dashboard.error && <p className="error-state" role="alert">{dashboard.error}</p>}{page}</Shell>
}
