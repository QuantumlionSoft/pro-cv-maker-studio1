import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { apiRequest, ApiError } from '@/services/api'

function jsonResponse(status, body) {
  return {
    ok: status >= 200 && status < 300,
    status,
    text: async () => (body === undefined ? '' : JSON.stringify(body)),
  }
}

describe('apiRequest', () => {
  beforeEach(() => {
    document.cookie = 'csrftoken=test-token; path=/'
  })
  afterEach(() => {
    vi.restoreAllMocks()
    document.cookie = 'csrftoken=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/'
  })

  it('sends the CSRF token on unsafe requests and parses JSON', async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse(200, { id: 1 }))
    vi.stubGlobal('fetch', fetchMock)
    const data = await apiRequest('PATCH', '/cvs/1/', { body: { title: 'X' } })
    expect(data).toEqual({ id: 1 })
    const [url, options] = fetchMock.mock.calls[0]
    expect(url).toBe('/api/cvs/1/')
    expect(options.headers['X-CSRFToken']).toBe('test-token')
    expect(options.credentials).toBe('same-origin')
  })

  it('normalises server errors into ApiError with field messages', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(jsonResponse(400, {
      error: { code: 'invalid', message: 'Please correct the highlighted fields.', fields: { title: ['Give it a name.'] } },
    })))
    const error = await apiRequest('POST', '/cvs/', { body: {} }).catch((e) => e)
    expect(error).toBeInstanceOf(ApiError)
    expect(error.status).toBe(400)
    expect(error.fields.title).toEqual(['Give it a name.'])
  })

  it('reports a 409 conflict with the server message', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(jsonResponse(409, {
      error: { code: 'conflict', message: 'Changed elsewhere.', fields: {} },
    })))
    const error = await apiRequest('PATCH', '/cvs/1/', { body: { version: 1 } }).catch((e) => e)
    expect(error.status).toBe(409)
    expect(error.message).toBe('Changed elsewhere.')
  })

  it('maps unauthenticated responses to a session-ended error', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(jsonResponse(403, {
      error: { code: 'not_authenticated', message: 'Authentication credentials were not provided.', fields: {} },
    })))
    const error = await apiRequest('GET', '/cvs/').catch((e) => e)
    expect(error.code).toBe('not_authenticated')
    expect(error.message).toMatch(/session has ended/i)
  })

  it('retries once after refreshing a stale CSRF token', async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(jsonResponse(403, { error: { code: 'permission_denied', message: 'CSRF Failed: token missing.', fields: {} } }))
      .mockResolvedValueOnce(jsonResponse(200, { detail: 'ok' })) // csrf refresh
      .mockResolvedValueOnce(jsonResponse(201, { id: 9 }))
    vi.stubGlobal('fetch', fetchMock)
    const data = await apiRequest('POST', '/cvs/', { body: { title: 'A' } })
    expect(data).toEqual({ id: 9 })
    expect(fetchMock.mock.calls[1][0]).toBe('/api/auth/csrf/')
  })

  it('reports network failures clearly', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new TypeError('Failed to fetch')))
    const error = await apiRequest('GET', '/cvs/').catch((e) => e)
    expect(error.code).toBe('network')
    expect(error.message).toMatch(/cannot reach the server/i)
  })
})
