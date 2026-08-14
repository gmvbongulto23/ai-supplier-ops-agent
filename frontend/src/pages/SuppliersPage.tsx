import { useCallback, useEffect, useState } from 'react'
import { apiGet } from '../api/client'
import { ApiError, type Supplier } from '../api/types'
import { EmptyState } from '../components/EmptyState'
import { ErrorState } from '../components/ErrorState'
import { LoadingState } from '../components/LoadingState'

type State = { status: 'loading' } | { status: 'success'; data: Supplier[] } | { status: 'error'; message: string }

export function SuppliersPage() {
  const [state, setState] = useState<State>({ status: 'loading' })

  const load = useCallback(() => {
    setState({ status: 'loading' })
    apiGet<Supplier[]>('/ops/suppliers')
      .then((data) => setState({ status: 'success', data }))
      .catch((error: unknown) => {
        const message = error instanceof ApiError ? error.message : 'Unable to reach the backend API.'
        setState({ status: 'error', message })
      })
  }, [])

  useEffect(() => {
    load()
  }, [load])

  if (state.status === 'loading') {
    return <LoadingState label="Loading suppliers…" />
  }

  if (state.status === 'error') {
    return <ErrorState message={state.message} onRetry={load} />
  }

  return (
    <section className="ops-section">
      <h2>Suppliers</h2>
      {state.data.length === 0 ? (
        <EmptyState message="No suppliers yet." />
      ) : (
        <table>
          <thead>
            <tr>
              <th>Name</th>
              <th>Products supplied</th>
              <th>Reliability</th>
              <th>Contact</th>
            </tr>
          </thead>
          <tbody>
            {state.data.map((supplier) => (
              <tr key={supplier.id}>
                <td>{supplier.name}</td>
                <td>{supplier.products_supplied.join(', ')}</td>
                <td>
                  <span
                    className={`status-pill ${supplier.reliability_status === 'reliable' ? 'status-healthy' : 'status-at_risk'}`}
                  >
                    {supplier.reliability_status}
                  </span>
                </td>
                <td>{supplier.contact_info}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </section>
  )
}
