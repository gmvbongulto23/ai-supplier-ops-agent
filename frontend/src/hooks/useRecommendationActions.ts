import { useState } from 'react'
import { apiPost } from '../api/client'

export function useRecommendationActions(reload: () => void) {
  const [busyAction, setBusyAction] = useState<string | null>(null)

  const accept = async (id: string) => {
    setBusyAction(`accept:${id}`)
    try {
      await apiPost(`/ops/recommendations/${id}/accept`)
      reload()
    } finally {
      setBusyAction(null)
    }
  }

  return { busyAction, accept }
}
