interface EmptyStateProps {
  message: string
}

export function EmptyState({ message }: EmptyStateProps) {
  return (
    <div role="status" className="state state-empty">
      <p>{message}</p>
    </div>
  )
}
