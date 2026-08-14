interface LoadingStateProps {
  label?: string
}

export function LoadingState({ label = 'Loading…' }: LoadingStateProps) {
  return (
    <div role="status" aria-live="polite" className="state state-loading">
      <span className="spinner" aria-hidden="true" />
      <p>{label}</p>
    </div>
  )
}
