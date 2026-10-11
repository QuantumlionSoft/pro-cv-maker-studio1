/**
 * Browser storage is used ONLY for short-lived recovery drafts.
 * The backend remains the source of truth; drafts are removed once saved.
 */
const PREFIX = 'pcms:draft'

export function draftKey(kind, id) {
  return `${PREFIX}:${kind}:${id}`
}

export function saveDraft(kind, id, draft) {
  try {
    localStorage.setItem(draftKey(kind, id), JSON.stringify(draft))
  } catch {
    /* storage full or disabled: recovery is best-effort */
  }
}

export function loadDraft(kind, id) {
  try {
    const raw = localStorage.getItem(draftKey(kind, id))
    return raw ? JSON.parse(raw) : null
  } catch {
    return null
  }
}

export function clearDraft(kind, id) {
  try {
    localStorage.removeItem(draftKey(kind, id))
  } catch {
    /* ignore */
  }
}
