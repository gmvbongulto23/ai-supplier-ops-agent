import type { Recommendation } from '../api/types'
import { EmptyState } from './EmptyState'

interface RecommendationListProps {
  recommendations: Recommendation[]
  busyAction: string | null
  onAccept: (id: string) => void
  emptyMessage?: string
  showAcceptedLog?: boolean
}

export function RecommendationList({
  recommendations,
  busyAction,
  onAccept,
  emptyMessage = 'No pending recommendations. All clear.',
  showAcceptedLog = false,
}: RecommendationListProps) {
  const pending = recommendations.filter((r) => r.status === 'pending')

  return (
    <>
      {pending.length === 0 ? (
        <EmptyState message={emptyMessage} />
      ) : (
        <ul className="recommendation-list">
          {pending.map((rec) => (
            <li key={rec.id} className={`recommendation recommendation-${rec.severity}`}>
              <div className="recommendation-header">
                <span className={`severity-pill severity-${rec.severity}`}>{rec.severity}</span>
                <strong>{rec.message}</strong>
              </div>
              <p className="recommendation-reason">{rec.reason}</p>
              <button type="button" disabled={busyAction !== null} onClick={() => onAccept(rec.id)}>
                {busyAction === `accept:${rec.id}` ? 'Applying…' : 'Accept Recommendation'}
              </button>
            </li>
          ))}
        </ul>
      )}

      {showAcceptedLog && recommendations.some((r) => r.status === 'accepted') && (
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
    </>
  )
}
