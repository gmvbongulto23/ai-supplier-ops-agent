import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import App from '../App'
import { healthyResponseFixture } from './fixtures/health'

const BASE_URL = 'http://localhost:8000'

describe('App shell', () => {
  beforeEach(() => {
    vi.stubEnv('VITE_API_BASE_URL', BASE_URL)
  })

  afterEach(() => {
    vi.unstubAllEnvs()
    vi.unstubAllGlobals()
    vi.restoreAllMocks()
  })

  it('renders navigation placeholders for every core operational area', () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response(JSON.stringify(healthyResponseFixture), { status: 200 })))

    render(<App />)

    for (const label of ['Suppliers', 'Orders', 'Deliveries', 'Inventory', 'Risks', 'Recommendations']) {
      expect(screen.getByText(label)).toBeInTheDocument()
    }
  })

  it('loads backend status through the API client and renders it, not a hardcoded fixture', async () => {
    const fetchMock = vi.fn().mockResolvedValue(new Response(JSON.stringify(healthyResponseFixture), { status: 200 }))
    vi.stubGlobal('fetch', fetchMock)

    render(<App />)

    expect(screen.getByRole('status')).toHaveTextContent('Checking backend status…')

    await waitFor(() => expect(screen.getByText(healthyResponseFixture.service)).toBeInTheDocument())

    expect(fetchMock).toHaveBeenCalledWith(`${BASE_URL}/health/live`, expect.objectContaining({ signal: expect.anything() }))
    expect(screen.getByText(healthyResponseFixture.status)).toBeInTheDocument()
    expect(screen.getByText(healthyResponseFixture.version)).toBeInTheDocument()
  })

  it('shows an error state with retry when the backend call fails, then recovers on retry', async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(new Response('', { status: 503 }))
      .mockResolvedValueOnce(new Response(JSON.stringify(healthyResponseFixture), { status: 200 }))
    vi.stubGlobal('fetch', fetchMock)
    const user = userEvent.setup()

    render(<App />)

    await waitFor(() => expect(screen.getByRole('alert')).toBeInTheDocument())

    await user.click(screen.getByRole('button', { name: /retry/i }))

    await waitFor(() => expect(screen.getByText(healthyResponseFixture.service)).toBeInTheDocument())
    expect(fetchMock).toHaveBeenCalledTimes(2)
  })
})
