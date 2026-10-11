import { computed, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'
import { ApiError } from '@/services/api'
import { clearDraft, loadDraft, saveDraft } from '@/utils/draftStorage'

export const AUTOSAVE_DELAY_MS = 800

/**
 * Autosave state machine for a single document.
 *
 * States: loading | ready | dirty | saving | saved | error | conflict | not_found | load_error
 *
 * - Edits are saved after a short debounce; manual save and retry call save() directly.
 * - Only one request is in flight at a time; edits made meanwhile trigger one follow-up save.
 * - The server version is sent with every save. A stale version yields 409 -> 'conflict'
 *   and nothing is overwritten silently.
 * - Local recovery drafts are kept until the server confirms the same content.
 */
export function useDocumentEditor({ api, id, kind, scheduleDelay = AUTOSAVE_DELAY_MS }) {
  const status = ref('loading')
  const errorMessage = ref('')
  const fieldErrors = ref({})
  const lastSavedAt = ref(null)
  const document = ref(null)
  const recoverableDraft = ref(null)
  const form = reactive({ title: '', template: '' })

  let version = 1
  let savedSnapshot = ''
  let timer = null
  let inFlight = false
  let pending = false

  const snapshot = () => JSON.stringify({ title: form.title, template: form.template })
  const hasUnsaved = computed(() => ['dirty', 'saving', 'error', 'conflict'].includes(status.value))

  function applyServerDocument(doc) {
    document.value = doc
    version = doc.version
    form.title = doc.title
    form.template = doc.template
    savedSnapshot = snapshot()
  }

  function scheduleSave() {
    clearTimeout(timer)
    timer = setTimeout(save, scheduleDelay)
  }

  async function save() {
    clearTimeout(timer)
    if (inFlight) {
      pending = true
      return
    }
    const current = snapshot()
    if (current === savedSnapshot) return

    inFlight = true
    status.value = 'saving'
    errorMessage.value = ''
    fieldErrors.value = {}
    try {
      const updated = await api.update(id, { ...JSON.parse(current), version })
      version = updated.version
      document.value = updated
      savedSnapshot = current
      lastSavedAt.value = new Date()
      if (snapshot() === current) {
        clearDraft(kind, id)
        status.value = 'saved'
      } else {
        status.value = 'dirty'
      }
    } catch (error) {
      if (error instanceof ApiError && error.status === 409) {
        status.value = 'conflict'
        errorMessage.value = error.message
      } else if (error instanceof ApiError && error.status === 404) {
        status.value = 'not_found'
      } else {
        status.value = 'error'
        errorMessage.value = error.message || 'Save failed.'
        fieldErrors.value = error.fields || {}
      }
    } finally {
      inFlight = false
    }

    if (pending) {
      pending = false
      save()
    }
  }

  watch(snapshot, (current) => {
    if (['loading', 'not_found', 'load_error'].includes(status.value)) return
    if (current === savedSnapshot) {
      // Back to the saved content (or a server copy was just applied): nothing to recover.
      clearDraft(kind, id)
      if (!inFlight) status.value = lastSavedAt.value ? 'saved' : 'ready'
      return
    }
    saveDraft(kind, id, { baseVersion: version, data: JSON.parse(current), savedAt: Date.now() })
    if (!inFlight) status.value = 'dirty'
    scheduleSave()
  })

  async function load() {
    status.value = 'loading'
    try {
      const doc = await api.get(id)
      applyServerDocument(doc)
      const draft = loadDraft(kind, id)
      const differs = draft && draft.data && (draft.data.title !== doc.title || draft.data.template !== doc.template)
      if (differs && draft.baseVersion === doc.version) {
        recoverableDraft.value = draft
      } else if (draft) {
        clearDraft(kind, id)
      }
      status.value = 'ready'
    } catch (error) {
      status.value = error instanceof ApiError && error.status === 404 ? 'not_found' : 'load_error'
      errorMessage.value = error.message || 'Could not load this document.'
    }
  }

  function restoreDraft() {
    const draft = recoverableDraft.value
    if (!draft) return
    form.title = draft.data.title
    form.template = draft.data.template
    recoverableDraft.value = null
  }

  function discardDraft() {
    clearDraft(kind, id)
    recoverableDraft.value = null
  }

  /** Reload the server copy and drop local unsaved edits (the draft stays until overwritten). */
  async function reloadLatest() {
    status.value = 'loading'
    try {
      const doc = await api.get(id)
      applyServerDocument(doc)
      clearDraft(kind, id)
      status.value = 'ready'
      errorMessage.value = ''
    } catch (error) {
      status.value = 'load_error'
      errorMessage.value = error.message
    }
  }

  /** After a conflict, adopt the latest server version number and save local edits on top of it. */
  async function keepMyChanges() {
    try {
      const doc = await api.get(id)
      version = doc.version
      document.value = doc
      status.value = 'dirty'
      await save()
    } catch (error) {
      status.value = 'error'
      errorMessage.value = error.message
    }
  }

  function onBeforeUnload(event) {
    if (hasUnsaved.value) {
      event.preventDefault()
      event.returnValue = ''
    }
  }

  onMounted(() => window.addEventListener('beforeunload', onBeforeUnload))
  onBeforeUnmount(() => {
    window.removeEventListener('beforeunload', onBeforeUnload)
    if (status.value === 'dirty') save()
    clearTimeout(timer)
  })

  return {
    status,
    errorMessage,
    fieldErrors,
    lastSavedAt,
    document,
    form,
    hasUnsaved,
    recoverableDraft,
    load,
    save,
    restoreDraft,
    discardDraft,
    reloadLatest,
    keepMyChanges,
  }
}
