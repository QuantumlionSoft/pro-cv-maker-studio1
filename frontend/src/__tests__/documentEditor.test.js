import { beforeEach, describe, expect, it, vi } from 'vitest'
import { effectScope, nextTick } from 'vue'
import { useDocumentEditor } from '@/composables/useDocumentEditor'
import { ApiError } from '@/services/api'
import { saveDraft, loadDraft, clearDraft } from '@/utils/draftStorage'

const flush = async () => {
  for (let i = 0; i < 5; i++) await Promise.resolve()
  await nextTick()
}

function setup(api, opts = {}) {
  const scope = effectScope()
  const editor = scope.run(() => useDocumentEditor({ api, id: 7, kind: 'cv', scheduleDelay: 100, ...opts }))
  return { editor, scope }
}

describe('useDocumentEditor autosave', () => {
  beforeEach(() => {
    localStorage.clear()
    vi.useFakeTimers()
  })

  it('loads a document and stays clean until the user edits', async () => {
    const api = { get: vi.fn().mockResolvedValue({ id: 7, title: 'Main', template: 'modern', version: 3 }), update: vi.fn() }
    const { editor } = setup(api)
    await editor.load()
    expect(editor.status.value).toBe('ready')
    expect(editor.form.title).toBe('Main')
    vi.advanceTimersByTime(2000)
    expect(api.update).not.toHaveBeenCalled()
  })

  it('debounces edits into one save that sends the current version', async () => {
    const api = {
      get: vi.fn().mockResolvedValue({ id: 7, title: 'Main', template: 'modern', version: 3 }),
      update: vi.fn().mockImplementation(async (id, body) => ({ id, ...body, version: body.version + 1, updated_at: new Date().toISOString() })),
    }
    const { editor } = setup(api)
    await editor.load()
    editor.form.title = 'Main v2'
    await flush()
    editor.form.title = 'Main v3'
    await flush()
    vi.advanceTimersByTime(150)
    await flush()
    expect(api.update).toHaveBeenCalledTimes(1)
    expect(api.update.mock.calls[0][1]).toEqual({ title: 'Main v3', template: 'modern', version: 3 })
    expect(editor.status.value).toBe('saved')
    expect(loadDraft('cv', 7)).toBeNull()
  })

  it('shows a conflict instead of overwriting when the version is stale', async () => {
    const api = {
      get: vi.fn().mockResolvedValue({ id: 7, title: 'Main', template: 'modern', version: 3 }),
      update: vi.fn().mockRejectedValue(new ApiError('This document was changed elsewhere.', { status: 409, code: 'conflict' })),
    }
    const { editor } = setup(api)
    await editor.load()
    editor.form.title = 'Local edit'
    await flush()
    vi.advanceTimersByTime(150)
    await flush()
    expect(editor.status.value).toBe('conflict')
    expect(editor.hasUnsaved.value).toBe(true)
  })

  it('reports save errors visibly and keeps the local draft for recovery', async () => {
    const api = {
      get: vi.fn().mockResolvedValue({ id: 7, title: 'Main', template: 'modern', version: 1 }),
      update: vi.fn().mockRejectedValue(new ApiError('Cannot reach the server.', { code: 'network' })),
    }
    const { editor } = setup(api)
    await editor.load()
    editor.form.title = 'Offline edit'
    await flush()
    vi.advanceTimersByTime(150)
    await flush()
    expect(editor.status.value).toBe('error')
    expect(editor.errorMessage.value).toMatch(/cannot reach/i)
    expect(loadDraft('cv', 7).data.title).toBe('Offline edit')
  })

  it('offers to restore a recovery draft written against the same server version', async () => {
    saveDraft('cv', 7, { baseVersion: 3, data: { title: 'Recovered', template: 'modern' }, savedAt: Date.now() })
    const api = { get: vi.fn().mockResolvedValue({ id: 7, title: 'Main', template: 'modern', version: 3 }), update: vi.fn() }
    const { editor } = setup(api)
    await editor.load()
    expect(editor.recoverableDraft.value).not.toBeNull()
    editor.restoreDraft()
    expect(editor.form.title).toBe('Recovered')
  })

  it('discards drafts that were based on an older version', async () => {
    saveDraft('cv', 7, { baseVersion: 1, data: { title: 'Stale', template: 'modern' }, savedAt: Date.now() })
    const api = { get: vi.fn().mockResolvedValue({ id: 7, title: 'Main', template: 'modern', version: 3 }), update: vi.fn() }
    const { editor } = setup(api)
    await editor.load()
    expect(editor.recoverableDraft.value).toBeNull()
    expect(loadDraft('cv', 7)).toBeNull()
  })

  it('marks missing documents as not found', async () => {
    const api = { get: vi.fn().mockRejectedValue(new ApiError('That item could not be found.', { status: 404 })), update: vi.fn() }
    const { editor } = setup(api)
    await editor.load()
    expect(editor.status.value).toBe('not_found')
  })
})
