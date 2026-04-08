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
  method: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE',
  endpoint: string,
  body?: unknown
): Promise<T> {
  let response: Response

  try {
    // Initialize headers
    const headers: Record<string, string> = {}
    
    // Add Content-Type if there's a body
    if (body) {
      headers['Content-Type'] = 'application/json'
    }
    
    // Add Authorization token if available
    try {
      const sessionStr = localStorage.getItem('currentSession')
      if (sessionStr) {
        const session = JSON.parse(sessionStr)
        if (session && session.token) {
          headers['Authorization'] = `Bearer ${session.token}`
        }
      }
    } catch (e) {
      // Ignore session read errors
    }

    response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method,
      headers,
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

    // Only log unexpected errors (not 404s for optional endpoints)
    if (response.status !== 404 && response.status !== 403) {
      console.error(`[API ERROR] ${response.status} on ${method} ${endpoint}:`, text)
    }

    // If 401 Unauthorized and not already on login page, clear session and redirect
    if (response.status === 401 && !window.location.pathname.includes('/login')) {
      console.warn('[API] Session expired, redirecting to login')
      localStorage.removeItem('currentSession')
      window.location.href = '/login'
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
  patch: async <T>(endpoint: string, body: unknown): Promise<T> =>
    request<T>('PATCH', endpoint, body),
  delete: async <T>(endpoint: string): Promise<T> => request<T>('DELETE', endpoint),
}
