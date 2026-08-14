import { useCallback, useEffect, useState } from 'react'
import { apiGet } from '../api/client'
import { ApiError, type DashboardResponse } from '../api/types'

export type DashboardState =
  | { status: 'loading' }
  | { status: 'success'; data: DashboardResponse }
  | { status: 'error'; message: string }

export function useDashboardData() {
  const [state, setState] = useState<DashboardState>({ status: 'loading' })

  const load = useCallback(() => {
    setState({ status: 'loading' })
    apiGet<DashboardResponse>('/ops/dashboard')
      .then((data) => setState({ status: 'success', data }))
      .catch((error: unknown) => {
        const message = error instanceof ApiError ? error.message : 'Unable to reach the backend API.'
        setState({ status: 'error', message })
      })
  }, [])

  useEffect(() => {
    load()
  }, [load])

  return { state, reload: load }
}
