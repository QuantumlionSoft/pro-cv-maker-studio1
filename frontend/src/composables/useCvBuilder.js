import { computed, ref, watch } from 'vue'
import { ApiError } from '@/services/api'
import { cvApi } from '@/services/documents'

export const AUTOSAVE_DELAY_MS = 800

/**
 * Autosave state machine for one CV. Content lives on the server only; nothing is
 * kept in localStorage.
 *
 * States: loading | ready | dirty | saving | saved | error | conflict | not_found | load_error
 *
 * - Edits are saved after a short debounce; at most one request is in flight.
 * - The server version is sent with each save. A stale version yields 409 -> 'conflict'
 *   and autosave pauses until the user chooses to reload the server copy.
 * - A failed save keeps the local edits on screen and reports the error.
 */
export function useCvBuilder({ id, api = cvApi, scheduleDelay = AUTOSAVE_DELAY_MS }) {
  const status = ref('loading')
  const errorMessage = ref('')
  const lastSavedAt = ref(null)
  const title = ref('')
  const template = ref('modern')
  const content = ref(null)
  const design = ref(null)

  let version = 1
  let savedSnapshot = ''
  let timer = null
  let inFlight = false
  let pending = false

  const snapshot = () =>
    JSON.stringify({ title: title.value, template: template.value, content: content.value, design: design.value })

  const hasUnsaved = computed(() => ['dirty', 'saving', 'error'].includes(status.value))

  function applyServerDocument(doc) {
    title.value = doc.title
    template.value = doc.template
    content.value = structuredClone(doc.content)
    design.value = structuredClone(doc.design)
    version = doc.version
    savedSnapshot = snapshot()
  }

  function scheduleSave() {
    clearTimeout(timer)
    timer = setTimeout(save, scheduleDelay)
  }

  async function save() {
    clearTimeout(timer)
    if (status.value === 'conflict' || status.value === 'not_found') return
    if (inFlight) {
      pending = true
      return
    }
    const current = snapshot()
    if (current === savedSnapshot) return

    inFlight = true
    status.value = 'saving'
    errorMessage.value = ''
    try {
      const updated = await api.update(id, { ...JSON.parse(current), version })
      version = updated.version
      savedSnapshot = current
      lastSavedAt.value = new Date()
      status.value = snapshot() === current ? 'saved' : 'dirty'
    } catch (error) {
      if (error instanceof ApiError && error.status === 409) {
        status.value = 'conflict'
        errorMessage.value = 'Bu CV başka bir yerde değişti. Otomatik kayıt durduruldu.'
      } else if (error instanceof ApiError && error.status === 404) {
        status.value = 'not_found'
      } else {
        status.value = 'error'
        errorMessage.value = firstFieldMessage(error) || error.message || 'Kayıt başarısız oldu.'
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
    if (['loading', 'not_found', 'load_error', 'conflict'].includes(status.value)) return
    if (current === savedSnapshot) {
      if (!inFlight && status.value !== 'error') status.value = lastSavedAt.value ? 'saved' : 'ready'
      return
    }
    if (!inFlight) status.value = 'dirty'
    scheduleSave()
  })

  async function load() {
    status.value = 'loading'
    errorMessage.value = ''
    try {
      applyServerDocument(await api.get(id))
      status.value = 'ready'
    } catch (error) {
      status.value = error instanceof ApiError && error.status === 404 ? 'not_found' : 'load_error'
      errorMessage.value = error.message || 'CV yüklenemedi.'
    }
  }

  /** Discard local unsaved edits and load the server copy. */
  async function reloadLatest() {
    clearTimeout(timer)
    try {
      applyServerDocument(await api.get(id))
      status.value = 'ready'
      errorMessage.value = ''
    } catch (error) {
      status.value = 'load_error'
      errorMessage.value = error.message || 'Sunucu sürümü yüklenemedi.'
    }
  }

  /** Replace content and design (JSON import). Autosave will persist it. */
  function replaceFromImport({ content: newContent, design: newDesign }) {
    content.value = newContent
    design.value = { ...design.value, ...newDesign }
  }

  return {
    status,
    errorMessage,
    lastSavedAt,
    title,
    template,
    content,
    design,
    hasUnsaved,
    load,
    save,
    retry: save,
    reloadLatest,
    replaceFromImport,
  }
}

function firstFieldMessage(error) {
  const fields = error && error.fields
  if (!fields) return ''
  for (const messages of Object.values(fields)) {
    if (Array.isArray(messages) && messages.length) return messages[0]
  }
  return ''
}
