import { useCallback, useEffect, useState } from 'react'
import { apiPost, apiGet } from '../api/client'
import { ApiError, type DashboardResponse } from '../api/types'
import { EmptyState } from '../components/EmptyState'
import { ErrorState } from '../components/ErrorState'
import { LoadingState } from '../components/LoadingState'

type RequestState =
  | { status: 'loading' }
  | { status: 'success'; data: DashboardResponse }
  | { status: 'error'; message: string }

const SCENARIOS: { key: string; label: string }[] = [
  { key: 'normal', label: 'Normal Day' },
  { key: 'supplier_delay', label: 'Supplier Delay' },
  { key: 'multiple_delays', label: 'Multiple Delays' },
  { key: 'inventory_shortage', label: 'Inventory Shortage' },
]

function formatTime(iso: string): string {
  return new Date(iso).toLocaleString(undefined, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}

export function OpsDashboard() {
  const [state, setState] = useState<RequestState>({ status: 'loading' })
  const [busyAction, setBusyAction] = useState<string | null>(null)

  const loadDashboard = useCallback(() => {
    setState({ status: 'loading' })
    apiGet<DashboardResponse>('/ops/dashboard')
      .then((data) => setState({ status: 'success', data }))
      .catch((error: unknown) => {
        const message = error instanceof ApiError ? error.message : 'Unable to reach the backend API.'
        setState({ status: 'error', message })
      })
  }, [])

  useEffect(() => {
    loadDashboard()
  }, [loadDashboard])

  const triggerScenario = async (name: string) => {
    setBusyAction(`scenario:${name}`)
    try {
      await apiPost(`/ops/scenarios/${name}/trigger`)
      await refreshQuietly()
    } finally {
      setBusyAction(null)
    }
  }

  const acceptRecommendation = async (id: string) => {
    setBusyAction(`accept:${id}`)
    try {
      await apiPost(`/ops/recommendations/${id}/accept`)
      await refreshQuietly()
    } finally {
      setBusyAction(null)
    }
  }

  const refreshQuietly = async () => {
    try {
      const data = await apiGet<DashboardResponse>('/ops/dashboard')
      setState({ status: 'success', data })
    } catch (error: unknown) {
      const message = error instanceof ApiError ? error.message : 'Unable to reach the backend API.'
      setState({ status: 'error', message })
    }
  }

  if (state.status === 'loading') {
    return <LoadingState label="Loading operations dashboard…" />
  }

  if (state.status === 'error') {
    return <ErrorState message={state.message} onRetry={loadDashboard} />
  }

  const { delivery_summary, inventory, orders, recommendations } = state.data
  const pendingRecommendations = recommendations.filter((r) => r.status === 'pending')

  return (
    <div className="ops-dashboard">
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
              {busyAction === `scenario:${scenario.key}` ? 'Running…' : scenario.label}
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
        {inventory.length === 0 ? (
          <EmptyState message="No inventory records yet." />
        ) : (
          <table>
            <thead>
              <tr>
                <th>Product</th>
                <th>Current qty</th>
                <th>Usage/hr</th>
                <th>Min required</th>
                <th>Est. remaining</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {inventory.map((item) => (
                <tr key={item.product}>
                  <td>{item.product}</td>
                  <td>{item.current_quantity}</td>
                  <td>{item.avg_usage_per_hour}</td>
                  <td>{item.minimum_required_quantity}</td>
                  <td>{item.estimated_remaining_hours}h</td>
                  <td>
                    <span className={`status-pill status-${item.status}`}>{item.status.replace('_', ' ')}</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>

      <section className="ops-section">
        <h2>Orders</h2>
        {orders.length === 0 ? (
          <EmptyState message="No orders yet." />
        ) : (
          <table>
            <thead>
              <tr>
                <th>Supplier</th>
                <th>Product</th>
                <th>Qty</th>
                <th>Expected</th>
                <th>Current ETA</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {orders.map((order) => (
                <tr key={order.id}>
                  <td>{order.supplier_name}</td>
                  <td>{order.product}</td>
                  <td>{order.quantity}</td>
                  <td>{formatTime(order.expected_delivery)}</td>
                  <td>{formatTime(order.current_eta)}</td>
                  <td>
                    <span className={`status-pill status-${order.status}`}>{order.status.replace('_', ' ')}</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>

      <section className="ops-section">
        <h2>AI Operations Center</h2>
        {pendingRecommendations.length === 0 ? (
          <EmptyState message="No pending recommendations. All clear." />
        ) : (
          <ul className="recommendation-list">
            {pendingRecommendations.map((rec) => (
              <li key={rec.id} className={`recommendation recommendation-${rec.severity}`}>
                <div className="recommendation-header">
                  <span className={`severity-pill severity-${rec.severity}`}>{rec.severity}</span>
                  <strong>{rec.message}</strong>
                </div>
                <p className="recommendation-reason">{rec.reason}</p>
                <button type="button" disabled={busyAction !== null} onClick={() => acceptRecommendation(rec.id)}>
                  {busyAction === `accept:${rec.id}` ? 'Applying…' : 'Accept Recommendation'}
                </button>
              </li>
            ))}
          </ul>
        )}

        {recommendations.some((r) => r.status === 'accepted') && (
          <div className="accepted-log">
            <h3>Accepted</h3>
            <ul>
              {recommendations
                .filter((r) => r.status === 'accepted')
                .map((r) => (
                  <li key={r.id}>{r.message}</li>
                ))}
            </ul>
          </div>
        )}
      </section>
    </div>
  )
}
