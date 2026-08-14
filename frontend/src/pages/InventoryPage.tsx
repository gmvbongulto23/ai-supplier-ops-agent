import { useDashboardData } from '../hooks/useDashboardData'
import { InventoryTable } from '../components/InventoryTable'
import { ErrorState } from '../components/ErrorState'
import { LoadingState } from '../components/LoadingState'

export function InventoryPage() {
  const { state, reload } = useDashboardData()

  if (state.status === 'loading') {
    return <LoadingState label="Loading inventory…" />
  }

  if (state.status === 'error') {
    return <ErrorState message={state.message} onRetry={reload} />
  }

  return (
    <section className="ops-section">
      <h2>Inventory status</h2>
      <InventoryTable items={state.data.inventory} />
    </section>
  )
}
