import { useDashboardData } from '../hooks/useDashboardData'
import { useRecommendationActions } from '../hooks/useRecommendationActions'
import { RecommendationList } from '../components/RecommendationList'
import { ErrorState } from '../components/ErrorState'
import { LoadingState } from '../components/LoadingState'

export function RecommendationsPage() {
  const { state, reload } = useDashboardData()
  const { busyAction, accept } = useRecommendationActions(reload)

  if (state.status === 'loading') {
    return <LoadingState label="Loading recommendations…" />
  }

  if (state.status === 'error') {
    return <ErrorState message={state.message} onRetry={reload} />
  }

  return (
    <section className="ops-section">
      <h2>AI Operations Center</h2>
      <RecommendationList
        recommendations={state.data.recommendations}
        busyAction={busyAction}
        onAccept={accept}
        showAcceptedLog
      />
    </section>
  )
}
