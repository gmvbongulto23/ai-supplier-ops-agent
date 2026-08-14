import { useDashboardData } from '../hooks/useDashboardData'
import { OrdersTable } from '../components/OrdersTable'
import { ErrorState } from '../components/ErrorState'
import { LoadingState } from '../components/LoadingState'

export function OrdersPage() {
  const { state, reload } = useDashboardData()

  if (state.status === 'loading') {
    return <LoadingState label="Loading orders…" />
  }

  if (state.status === 'error') {
    return <ErrorState message={state.message} onRetry={reload} />
  }

  return (
    <section className="ops-section">
      <h2>Orders</h2>
      <OrdersTable orders={state.data.orders} />
    </section>
  )
}
