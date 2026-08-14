import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { EmptyState } from '../components/EmptyState'
import { ErrorState } from '../components/ErrorState'
import { LoadingState } from '../components/LoadingState'

describe('LoadingState', () => {
  it('renders a status region with the given label', () => {
    render(<LoadingState label="Checking backend status…" />)

    expect(screen.getByRole('status')).toHaveTextContent('Checking backend status…')
  })

  it('falls back to a default label', () => {
    render(<LoadingState />)

    expect(screen.getByRole('status')).toHaveTextContent('Loading…')
  })
})

describe('EmptyState', () => {
  it('renders the provided message', () => {
    render(<EmptyState message="Nothing to show yet." />)

    expect(screen.getByRole('status')).toHaveTextContent('Nothing to show yet.')
  })
})

describe('ErrorState', () => {
  it('renders the error message and triggers retry on click', async () => {
    const user = userEvent.setup()
    const onRetry = vi.fn()
    render(<ErrorState message="Backend unavailable." onRetry={onRetry} />)

    expect(screen.getByRole('alert')).toHaveTextContent('Backend unavailable.')

    await user.click(screen.getByRole('button', { name: /retry/i }))

    expect(onRetry).toHaveBeenCalledTimes(1)
  })
})
