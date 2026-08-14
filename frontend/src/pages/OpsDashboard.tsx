import { useState } from 'react'
import { apiPost } from '../api/client'
import { useDashboardData } from '../hooks/useDashboardData'
import { useRecommendationActions } from '../hooks/useRecommendationActions'
import { InventoryTable } from '../components/InventoryTable'
import { OrdersTable } from '../components/OrdersTable'
import { RecommendationList } from '../components/RecommendationList'
import { ErrorState } from '../components/ErrorState'
import { LoadingState } from '../components/LoadingState'

const SCENARIOS: { key: string; label: string }[] = [
  { key: 'normal', label: 'Normal Day' },
  { key: 'supplier_delay', label: 'Supplier Delay' },
  { key: 'multiple_delays', label: 'Multiple Delays' },
  { key: 'inventory_shortage', label: 'Inventory Shortage' },
]

export function OpsDashboard() {
  const { state, reload } = useDashboardData()
  const { busyAction: acceptBusyAction, accept } = useRecommendationActions(reload)
  const [scenarioBusy, setScenarioBusy] = useState<string | null>(null)

  const triggerScenario = async (name: string) => {
    setScenarioBusy(name)
    try {
      await apiPost(`/ops/scenarios/${name}/trigger`)
      reload()
    } finally {
      setScenarioBusy(null)
    }
  }

  if (state.status === 'loading') {
    return <LoadingState label="Loading operations dashboard…" />
  }

  if (state.status === 'error') {
    return <ErrorState message={state.message} onRetry={reload} />
  }

  const { delivery_summary, inventory, orders, recommendations } = state.data
  const busyAction = scenarioBusy ? `scenario:${scenarioBusy}` : acceptBusyAction

  return (
    <>
      <section className="ops-section">
        <h2>Run a scenario</h2>
        <div className="scenario-buttons">
          {SCENARIOS.map((scenario) => (
            <button
              key={scenario.key}
              type="button"
              disabled={busyAction !== null}
              onClick={() => triggerScenario(scenario.key)}
            >
              {scenarioBusy === scenario.key ? 'Running…' : scenario.label}
            </button>
          ))}
        </div>
      </section>

      <section className="ops-section">
        <h2>Delivery summary</h2>
        <div className="badge-row">
          {['on_time', 'delayed', 'at_risk', 'delivered'].map((key) => (
            <span key={key} className={`badge badge-${key}`}>
              {key.replace('_', ' ')}: {delivery_summary[key] ?? 0}
            </span>
          ))}
        </div>
      </section>

      <section className="ops-section">
        <h2>Inventory status</h2>
        <InventoryTable items={inventory} />
      </section>

      <section className="ops-section">
        <h2>Orders</h2>
        <OrdersTable orders={orders} />
      </section>

      <section className="ops-section">
        <h2>AI Operations Center</h2>
        <RecommendationList recommendations={recommendations} busyAction={busyAction} onAccept={accept} showAcceptedLog />
      </section>
    </>
  )
}
