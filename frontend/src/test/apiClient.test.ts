import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { apiGet, getHealth } from '../api/client'
import { healthyResponseFixture } from './fixtures/health'

const BASE_URL = 'http://localhost:8000'

describe('apiGet', () => {
  beforeEach(() => {
    vi.stubEnv('VITE_API_BASE_URL', BASE_URL)
  })

  afterEach(() => {
    vi.unstubAllEnvs()
    vi.unstubAllGlobals()
    vi.restoreAllMocks()
  })

  it('resolves parsed JSON on a successful response', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue(
        new Response(JSON.stringify(healthyResponseFixture), {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        }),
      ),
    )

    const result = await getHealth()

    expect(result).toEqual(healthyResponseFixture)
    expect(fetch).toHaveBeenCalledWith(`${BASE_URL}/health/live`, expect.objectContaining({ signal: expect.anything() }))
  })

  it('throws a config ApiError when the base URL is not set', async () => {
    vi.unstubAllEnvs()

    await expect(apiGet('/health/live')).rejects.toMatchObject({ kind: 'config' })
  })

  it('throws an http ApiError for non-2xx responses', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response('', { status: 503 })))

    await expect(apiGet('/health/ready')).rejects.toMatchObject({ kind: 'http', status: 503 })
  })

  it('throws a parse ApiError when the response body is not valid JSON', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response('not json', { status: 200 })))

    await expect(apiGet('/health/live')).rejects.toMatchObject({ kind: 'parse' })
  })

  it('throws a network ApiError when the fetch call itself rejects', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new TypeError('Failed to fetch')))

    await expect(apiGet('/health/live')).rejects.toMatchObject({ kind: 'network' })
  })

  it('throws a timeout ApiError when the request is aborted', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockImplementation(() => Promise.reject(new DOMException('The operation was aborted.', 'AbortError'))),
    )

    await expect(apiGet('/health/live', 5)).rejects.toMatchObject({ kind: 'timeout' })
  })
})
