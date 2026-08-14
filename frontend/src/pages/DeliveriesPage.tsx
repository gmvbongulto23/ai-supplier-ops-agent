import { useDashboardData } from '../hooks/useDashboardData'
import { DeliveriesTable } from '../components/OrdersTable'
import { ErrorState } from '../components/ErrorState'
import { LoadingState } from '../components/LoadingState'

export function DeliveriesPage() {
  const { state, reload } = useDashboardData()

  if (state.status === 'loading') {
    return <LoadingState label="Loading deliveries…" />
  }

  if (state.status === 'error') {
    return <ErrorState message={state.message} onRetry={reload} />
  }

  return (
    <section className="ops-section">
      <h2>Deliveries</h2>
      <DeliveriesTable orders={state.data.orders} />
    </section>
  )
}
