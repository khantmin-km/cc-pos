const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export class ApiError extends Error {
  status: number
  body?: string

  constructor(status: number, message: string, body?: string) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.body = body
  }
}

async function parseResponse<T>(response: Response): Promise<T> {
  if (response.status === 204) return undefined as T

  const contentType = response.headers.get('content-type') || ''
  if (contentType.includes('application/json')) {
    return response.json()
  }

  return (await response.text()) as unknown as T
}

async function request<T>(
  method: 'GET' | 'POST' | 'PUT' | 'DELETE',
  endpoint: string,
  body?: unknown
): Promise<T> {
  let response: Response

  try {
    response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method,
      headers: body ? { 'Content-Type': 'application/json' } : undefined,
      body: body ? JSON.stringify(body) : undefined,
    })
  } catch (e) {
    const msg = e instanceof Error ? e.message : 'Network error'
    throw new ApiError(0, msg)
  }

  if (!response.ok) {
    let text: string | undefined
    try {
      text = await response.text()
    } catch {
      text = undefined
    }
    throw new ApiError(response.status, `HTTP ${response.status}`, text)
  }

  return parseResponse<T>(response)
}

export const api = {
  get: async <T>(endpoint: string): Promise<T> => request<T>('GET', endpoint),
  post: async <T>(endpoint: string, body?: unknown): Promise<T> =>
    request<T>('POST', endpoint, body),
  put: async <T>(endpoint: string, body: unknown): Promise<T> =>
    request<T>('PUT', endpoint, body),
  delete: async <T>(endpoint: string): Promise<T> => request<T>('DELETE', endpoint),
}
