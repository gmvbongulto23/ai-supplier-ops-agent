import { useCallback, useEffect, useState } from 'react'
import { getHealth } from '../api/client'
import { ApiError, type HealthResponse } from '../api/types'
import { EmptyState } from '../components/EmptyState'
import { ErrorState } from '../components/ErrorState'
import { LoadingState } from '../components/LoadingState'

type RequestState =
  | { status: 'loading' }
  | { status: 'success'; data: HealthResponse }
  | { status: 'empty' }
  | { status: 'error'; message: string }

export function DashboardHome() {
  const [state, setState] = useState<RequestState>({ status: 'loading' })

  const loadHealth = useCallback(() => {
    setState({ status: 'loading' })
    getHealth()
      .then((data) => {
        if (!data || !data.status) {
          setState({ status: 'empty' })
          return
        }
        setState({ status: 'success', data })
      })
      .catch((error: unknown) => {
        const message = error instanceof ApiError ? error.message : 'Unable to reach the backend API.'
        setState({ status: 'error', message })
      })
  }, [])

  useEffect(() => {
    loadHealth()
  }, [loadHealth])

  if (state.status === 'loading') {
    return <LoadingState label="Checking backend status…" />
  }

  if (state.status === 'error') {
    return <ErrorState message={state.message} onRetry={loadHealth} />
  }

  if (state.status === 'empty') {
    return <EmptyState message="Backend returned no status information." />
  }

  return (
    <section className="dashboard-summary" aria-label="Backend status">
      <h2>Backend status</h2>
      <dl>
        <dt>Status</dt>
        <dd>{state.data.status}</dd>
        <dt>Service</dt>
        <dd>{state.data.service}</dd>
        <dt>Version</dt>
        <dd>{state.data.version}</dd>
      </dl>
    </section>
  )
}
