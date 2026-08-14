import { ApiError, type HealthResponse } from './types'

const DEFAULT_TIMEOUT_MS = 8000

function getBaseUrl(): string {
  const baseUrl = import.meta.env.VITE_API_BASE_URL
  if (!baseUrl) {
    throw new ApiError(
      'VITE_API_BASE_URL is not configured. Set it in your environment to point at the backend API.',
      'config',
    )
  }
  return baseUrl
}

async function apiFetch<T>(path: string, init: RequestInit, timeoutMs: number = DEFAULT_TIMEOUT_MS): Promise<T> {
  const baseUrl = getBaseUrl()
  const controller = new AbortController()
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs)

  let response: Response
  try {
    response = await fetch(`${baseUrl}${path}`, { ...init, signal: controller.signal })
  } catch (error) {
    if (error instanceof DOMException && error.name === 'AbortError') {
      throw new ApiError(`Request to ${path} timed out after ${timeoutMs}ms`, 'timeout')
    }
    throw new ApiError(`Could not reach the backend at ${path}`, 'network')
  } finally {
    clearTimeout(timeoutId)
  }

  if (!response.ok) {
    throw new ApiError(`Request to ${path} failed with status ${response.status}`, 'http', response.status)
  }

  try {
    return (await response.json()) as T
  } catch {
    throw new ApiError(`Response from ${path} was not valid JSON`, 'parse')
  }
}

export function apiGet<T>(path: string, timeoutMs: number = DEFAULT_TIMEOUT_MS): Promise<T> {
  return apiFetch<T>(path, {}, timeoutMs)
}

export function apiPost<T>(path: string, body?: unknown, timeoutMs: number = DEFAULT_TIMEOUT_MS): Promise<T> {
  return apiFetch<T>(
    path,
    {
      method: 'POST',
      headers: body === undefined ? undefined : { 'Content-Type': 'application/json' },
      body: body === undefined ? undefined : JSON.stringify(body),
    },
    timeoutMs,
  )
}

export function getHealth(): Promise<HealthResponse> {
  return apiGet<HealthResponse>('/health/live')
}
