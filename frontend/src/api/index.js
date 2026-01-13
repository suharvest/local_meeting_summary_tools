/**
 * API client configuration and base functions
 */

// Use relative URL - Vite proxy will forward /api/* to backend
const API_BASE_URL = import.meta.env.VITE_API_URL || ''

/**
 * Make a fetch request with common options
 */
async function fetchAPI(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`

  const response = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ message: response.statusText }))
    throw new Error(error.message || error.detail || 'API request failed')
  }

  return response.json()
}

/**
 * GET request
 */
export async function get(endpoint) {
  return fetchAPI(endpoint, { method: 'GET' })
}

/**
 * POST request
 */
export async function post(endpoint, data) {
  return fetchAPI(endpoint, {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

/**
 * Get SSE stream URL
 */
export function getStreamURL(endpoint) {
  return `${API_BASE_URL}${endpoint}`
}

export { API_BASE_URL }
