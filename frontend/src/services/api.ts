<<<<<<< HEAD
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
=======
/**
 * Base API Client
 * 
 * This module provides a simple fetch wrapper for making HTTP requests
 * to the backend API. It handles JSON serialization/deserialization
 * and basic error handling.
 */

// Base URL for API requests
// Uses environment variable or defaults to localhost
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

/**
 * Custom error class for API responses
 * Includes HTTP status code for better error handling
 */
class ApiError extends Error {
  constructor(
    public status: number,
    message: string
  ) {
    super(message)
    this.name = 'ApiError'
  }
}

/**
 * Helper function to handle fetch responses
 * 
 * @param response - The fetch Response object
 * @returns Parsed JSON data or undefined for 204 responses
 * @throws ApiError if response is not OK
 */
async function handleResponse<T>(response: Response): Promise<T> {
  // Check if response status is not successful
  if (!response.ok) {
    // Try to get error text from response body
    const error = await response.text()
    throw new ApiError(
      response.status,
      error || `HTTP ${response.status}`
    )
  }

  // Handle 204 No Content - return undefined
  if (response.status === 204) {
    return undefined as T
  }

  // Parse and return JSON response
  return response.json()
}

/**
 * API client with HTTP methods
 * 
 * Usage:
 *   const data = await api.get('/tables')
 *   const result = await api.post('/tables', { name: 'Table 1' })
 */
export const api = {
  /**
   * Perform GET request
   * @param endpoint - API endpoint path (e.g., '/tables')
   */
  get: async <T>(endpoint: string): Promise<T> => {
    const response = await fetch(`${API_BASE_URL}${endpoint}`)
    return handleResponse<T>(response)
  },

  /**
   * Perform POST request
   * @param endpoint - API endpoint path
   * @param body - Request body object (optional)
   */
  post: async <T>(
    endpoint: string,
    body?: unknown
  ): Promise<T> => {
    const response = await fetch(
      `${API_BASE_URL}${endpoint}`,
      {
        method: 'POST',
        headers: body
          ? { 'Content-Type': 'application/json' }
          : undefined,
        body: body
          ? JSON.stringify(body)
          : undefined,
      }
    )
    return handleResponse<T>(response)
  },

  /**
   * Perform PUT request
   * @param endpoint - API endpoint path
   * @param body - Request body object
   */
  put: async <T>(
    endpoint: string,
    body: unknown
  ): Promise<T> => {
    const response = await fetch(
      `${API_BASE_URL}${endpoint}`,
      {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      }
    )
    return handleResponse<T>(response)
  },

  /**
   * Perform DELETE request
   * @param endpoint - API endpoint path
   */
  delete: async <T>(endpoint: string): Promise<T> => {
    const response = await fetch(
      `${API_BASE_URL}${endpoint}`,
      {
        method: 'DELETE',
      }
    )
    return handleResponse<T>(response)
  },
>>>>>>> df712ff (frontend_backend)
}
