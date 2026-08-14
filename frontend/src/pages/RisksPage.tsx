import { useDashboardData } from '../hooks/useDashboardData'
import { useRecommendationActions } from '../hooks/useRecommendationActions'
import { InventoryTable } from '../components/InventoryTable'
import { RecommendationList } from '../components/RecommendationList'
import { ErrorState } from '../components/ErrorState'
import { LoadingState } from '../components/LoadingState'

export function RisksPage() {
  const { state, reload } = useDashboardData()
  const { busyAction, accept } = useRecommendationActions(reload)

  if (state.status === 'loading') {
    return <LoadingState label="Loading risks…" />
  }

  if (state.status === 'error') {
    return <ErrorState message={state.message} onRetry={reload} />
  }

  const atRiskInventory = state.data.inventory.filter((item) => item.status !== 'healthy')

  return (
    <>
      <section className="ops-section">
        <h2>At-risk inventory</h2>
        <InventoryTable items={atRiskInventory} emptyMessage="No inventory currently at risk." />
      </section>

      <section className="ops-section">
        <h2>Open recommendations</h2>
        <RecommendationList
          recommendations={state.data.recommendations}
          busyAction={busyAction}
          onAccept={accept}
          emptyMessage="No open recommendations. All clear."
        />
      </section>
    </>
  )
}
