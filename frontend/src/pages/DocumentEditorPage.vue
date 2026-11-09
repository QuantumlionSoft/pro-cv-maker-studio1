<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink, useRoute, useRouter, onBeforeRouteLeave } from 'vue-router'
import EmptyState from '@/components/common/EmptyState.vue'
import SaveStatus from '@/components/common/SaveStatus.vue'
import { useDocumentEditor } from '@/composables/useDocumentEditor'
import { createDocumentApi } from '@/services/documents'
import { useUiStore } from '@/stores/ui'
import { fieldError } from '@/utils/errors'
import { formatDateTime, timeAgo } from '@/utils/format'

const route = useRoute()
const router = useRouter()
const ui = useUiStore()

const kind = computed(() => route.meta.kind)
const isCv = computed(() => kind.value === 'cv')
const noun = computed(() => (isCv.value ? 'CV' : 'portfolio'))
const listRoute = computed(() => (isCv.value ? '/cvs' : '/portfolios'))
const id = computed(() => route.params.id)
const api = computed(() => createDocumentApi(kind.value))

const templates = ref([])
const editor = useDocumentEditor({
  api: api.value,
  id: Number(route.params.id),
  kind: kind.value,
})

const selectedTemplate = computed(() => templates.value.find((t) => t.id === editor.form.template))

onMounted(async () => {
  try {
    templates.value = await api.value.templates()
  } catch {
    templates.value = []
  }
  editor.load()
})

onBeforeRouteLeave((to, from, next) => {
  if (!editor.hasUnsaved.value) return next()
  ui.confirm({
    title: 'Leave with unsaved changes?',
    message: 'Your latest edits are kept as a local recovery draft, and will be restored the next time you open this document.',
    confirmText: 'Leave',
    cancelText: 'Stay',
    danger: false,
  }).then((ok) => next(ok))
})

async function deleteDocument() {
  const title = editor.document.value?.title || `this ${noun.value}`
  const confirmed = await ui.confirm({
    title: `Delete “${title}”?`,
    message: `This permanently deletes the ${noun.value} and its saved content. This cannot be undone.`,
    confirmText: 'Delete permanently',
  })
  if (!confirmed) return
  try {
    await api.value.remove(Number(id.value))
    ui.toast(`Deleted “${title}”.`, 'success')
    router.push(listRoute.value)
  } catch (error) {
    ui.toast(`Could not delete: ${error.message}`, 'danger', 0)
  }
}

async function duplicateDocument() {
  try {
    const copy = await api.value.duplicate(Number(id.value))
    ui.toast(`Created “${copy.title}”.`, 'success')
    router.push(`${listRoute.value}/${copy.id}`)
  } catch (error) {
    ui.toast(`Could not duplicate: ${error.message}`, 'danger', 0)
  }
}

async function saveNow() {
  await editor.save()
  if (editor.status.value === 'saved') ui.toast('Saved.', 'success', 2500)
}
</script>

<template>
  <div>
    <nav aria-label="Breadcrumb" class="small mb-2">
      <RouterLink :to="listRoute">{{ isCv ? 'My CVs' : 'My Portfolios' }}</RouterLink>
      <span class="text-secondary"> / </span>
      <span class="text-secondary">{{ editor.form.title || 'Loading…' }}</span>
    </nav>

    <div v-if="editor.status.value === 'loading'" class="py-5 text-center text-secondary">
      <span class="spinner-border spinner-border-sm me-2"></span>Loading {{ noun }}…
    </div>

    <EmptyState
      v-else-if="editor.status.value === 'not_found'"
      icon="bi-question-circle"
      :title="`This ${noun} does not exist or is not yours`"
      description="It may have been deleted, or the link is incorrect."
    >
      <RouterLink :to="listRoute" class="btn btn-primary">Back to list</RouterLink>
    </EmptyState>

    <div v-else-if="editor.status.value === 'load_error'" class="alert alert-danger d-flex justify-content-between align-items-center" role="alert">
      <span>{{ editor.errorMessage.value }}</span>
      <button type="button" class="btn btn-sm btn-outline-danger" @click="editor.load">Try again</button>
    </div>

    <template v-else>
      <div class="page-header align-items-start">
        <div class="min-w-0 flex-grow-1">
          <h2 class="page-title text-truncate mb-1">{{ editor.form.title }}</h2>
          <SaveStatus
            :status="editor.status.value"
            :last-saved-at="editor.lastSavedAt.value"
            :error="editor.errorMessage.value"
            @retry="editor.save"
          />
        </div>
        <div class="d-flex flex-wrap gap-2">
          <button type="button" class="btn btn-primary" :disabled="!editor.hasUnsaved.value || editor.status.value === 'saving'" @click="saveNow">
            <i class="bi bi-floppy me-1" aria-hidden="true"></i>Save now
          </button>
          <button type="button" class="btn btn-outline-secondary" @click="duplicateDocument"><i class="bi bi-files me-1" aria-hidden="true"></i>Duplicate</button>
          <button type="button" class="btn btn-outline-danger" @click="deleteDocument"><i class="bi bi-trash3 me-1" aria-hidden="true"></i>Delete</button>
        </div>
      </div>

      <div v-if="editor.recoverableDraft.value" class="alert alert-warning d-flex flex-wrap justify-content-between align-items-center gap-2" role="alert">
        <span>You have unsaved changes from {{ timeAgo(editor.recoverableDraft.value.savedAt) }}. Restore them?</span>
        <div class="d-flex gap-2">
          <button type="button" class="btn btn-sm btn-warning" @click="editor.restoreDraft">Restore</button>
          <button type="button" class="btn btn-sm btn-outline-secondary" @click="editor.discardDraft">Discard</button>
        </div>
      </div>

      <div v-if="editor.status.value === 'conflict'" class="alert alert-danger" role="alert">
        <p class="fw-semibold mb-1">This {{ noun }} was changed in another tab or window.</p>
        <p class="mb-2 small">Your latest edits were not saved. Choose which version to keep.</p>
        <div class="d-flex flex-wrap gap-2">
          <button type="button" class="btn btn-sm btn-outline-danger" @click="editor.reloadLatest">Load the saved version</button>
          <button type="button" class="btn btn-sm btn-danger" @click="editor.keepMyChanges">Keep my changes</button>
        </div>
      </div>

      <div class="row g-4">
        <div class="col-lg-7">
          <section class="card">
            <div class="card-body">
              <h3 class="h6 mb-3">Document settings</h3>
              <div class="mb-3">
                <label for="editor-title" class="form-label">Name</label>
                <input
                  id="editor-title"
                  v-model="editor.form.title"
                  type="text"
                  maxlength="160"
                  class="form-control"
                  :class="{ 'is-invalid': fieldError(editor.fieldErrors.value, 'title') }"
                />
                <div v-if="fieldError(editor.fieldErrors.value, 'title')" class="invalid-feedback">{{ fieldError(editor.fieldErrors.value, 'title') }}</div>
              </div>
              <div>
                <label for="editor-template" class="form-label">Template</label>
                <select id="editor-template" v-model="editor.form.template" class="form-select" :class="{ 'is-invalid': fieldError(editor.fieldErrors.value, 'template') }">
                  <option v-for="t in templates" :key="t.id" :value="t.id">{{ t.name }}</option>
                </select>
                <div class="form-text">{{ selectedTemplate?.description }}</div>
                <div v-if="fieldError(editor.fieldErrors.value, 'template')" class="invalid-feedback d-block">{{ fieldError(editor.fieldErrors.value, 'template') }}</div>
              </div>
            </div>
          </section>
        </div>
        <div class="col-lg-5">
          <section class="card mb-3">
            <div class="card-body small">
              <h3 class="h6">Details</h3>
              <dl class="row mb-0">
                <dt class="col-5 text-secondary">Created</dt><dd class="col-7">{{ formatDateTime(editor.document.value?.created_at) }}</dd>
                <dt class="col-5 text-secondary">Last saved</dt><dd class="col-7">{{ formatDateTime(editor.document.value?.updated_at) }}</dd>
                <dt class="col-5 text-secondary">Version</dt><dd class="col-7">{{ editor.document.value?.version }}</dd>
                <dt class="col-5 text-secondary">Slug</dt><dd class="col-7 text-break">{{ editor.document.value?.slug }}</dd>
              </dl>
            </div>
          </section>
          <section class="card border-0 bg-light-subtle">
            <div class="card-body small text-secondary">
              <strong class="d-block text-body mb-1">The full {{ noun }} editor is still being built.</strong>
              {{ isCv
                ? 'The full CV editor is available from the CV workspace with live A4 preview and PDF export.'
                : 'The block-based portfolio builder and website preview are under active development.' }}
              Your name and template are already saved and will carry over.
            </div>
          </section>
        </div>
      </div>
    </template>
  </div>
</template>
