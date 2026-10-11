/**
 * Thin fetch wrapper for the Django REST API.
 *
 * - Sends session cookies (same-origin via the Vite proxy).
 * - Attaches the CSRF token to unsafe requests and retries once if the token was stale.
 * - Normalises every error into ApiError so UI code handles one shape.
 */
export const API_BASE = '/api'
const UNSAFE_METHODS = new Set(['POST', 'PUT', 'PATCH', 'DELETE'])

export class ApiError extends Error {
  constructor(message, { status = 0, code = 'error', fields = {} } = {}) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.code = code
    this.fields = fields
  }
}

export function getCookie(name) {
  const entry = document.cookie.split('; ').find((row) => row.startsWith(`${name}=`))
  return entry ? decodeURIComponent(entry.slice(name.length + 1)) : null
}

async function refreshCsrfCookie() {
  await fetch(`${API_BASE}/auth/csrf/`, { credentials: 'same-origin' })
}

async function parseBody(response) {
  if (response.status === 204) return null
  const text = await response.text()
  if (!text) return null
  try {
    return JSON.parse(text)
  } catch {
    return null
  }
}

function fallbackMessage(status) {
  if (status >= 500) return 'The server ran into a problem. Your work is still in the editor; try again shortly.'
  if (status === 404) return 'That item could not be found.'
  return `Request failed (${status}).`
}

/**
 * @param {'GET'|'POST'|'PATCH'|'PUT'|'DELETE'} method
 * @param {string} path  path below /api, e.g. '/cvs/'
 * @param {{ body?: object|FormData, query?: Record<string, any>, retryCsrf?: boolean }} [options]
 */
export async function apiRequest(method, path, { body, query, retryCsrf = true } = {}) {
  let url = API_BASE + path
  if (query) {
    const params = new URLSearchParams()
    Object.entries(query).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') params.set(key, String(value))
    })
    const qs = params.toString()
    if (qs) url += (url.includes('?') ? '&' : '?') + qs
  }

  const headers = { Accept: 'application/json' }
  let payload
  if (body instanceof FormData) {
    payload = body // browser sets the multipart boundary
  } else if (body !== undefined) {
    headers['Content-Type'] = 'application/json'
    payload = JSON.stringify(body)
  }

  if (UNSAFE_METHODS.has(method)) {
    if (!getCookie('csrftoken')) await refreshCsrfCookie()
    headers['X-CSRFToken'] = getCookie('csrftoken') || ''
  }

  let response
  try {
    response = await fetch(url, { method, headers, body: payload, credentials: 'same-origin' })
  } catch {
    throw new ApiError('Cannot reach the server. Check that the backend is running, then try again.', {
      code: 'network',
    })
  }

  const data = await parseBody(response)
  if (response.ok) return data

  const err = (data && data.error) || {}
  const message = err.message || fallbackMessage(response.status)

  if (response.status === 403 && UNSAFE_METHODS.has(method) && retryCsrf && /csrf/i.test(message)) {
    await refreshCsrfCookie()
    return apiRequest(method, path, { body, query, retryCsrf: false })
  }

  if (err.code === 'not_authenticated' || response.status === 401) {
    throw new ApiError('Your session has ended. Please sign in again.', { status: response.status, code: 'not_authenticated' })
  }

  throw new ApiError(message, { status: response.status, code: err.code || 'error', fields: err.fields || {} })
}
