<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { Modal } from 'bootstrap'
import { createDocumentApi } from '@/services/documents'
import { fieldError } from '@/utils/errors'

const props = defineProps({
  open: { type: Boolean, default: false },
  kind: { type: String, required: true },
  document: { type: Object, default: null },
  templates: { type: Array, default: () => [] },
  initialTemplate: { type: String, default: '' },
})
const emit = defineEmits(['close', 'saved'])

const el = ref(null)
let modal = null
const title = ref('')
const template = ref('')
const errors = ref({})
const formError = ref('')
const saving = ref(false)
const isEdit = computed(() => Boolean(props.document))
const api = computed(() => createDocumentApi(props.kind))
const heading = computed(() => {
  const label = props.kind === 'cv' ? 'CV' : 'portfolyo'
  return isEdit.value ? `${label} adını düzenle` : `Yeni ${label} oluştur`
})

let savedDocument = null

// Emit "saved" only after the hide transition completes. Navigating while Bootstrap is
// still animating would unmount the component mid-transition.
function onHidden() {
  emit('close')
  if (savedDocument) {
    const doc = savedDocument
    savedDocument = null
    emit('saved', doc)
  }
}

onMounted(() => {
  modal = new Modal(el.value, { backdrop: 'static' })
  el.value.addEventListener('hidden.bs.modal', onHidden)
})

onBeforeUnmount(() => {
  el.value?.removeEventListener('hidden.bs.modal', onHidden)
  modal?.dispose()
})

watch(
  () => props.open,
  (open) => {
    if (!modal) return
    if (open) {
      reset()
      modal.show()
    } else {
      modal.hide()
    }
  },
)

function reset() {
  title.value = props.document?.title ?? ''
  template.value = props.document?.template ?? props.initialTemplate ?? props.templates[0]?.id ?? ''
  if (!props.document && !props.templates.some((item) => item.id === template.value)) template.value = props.templates[0]?.id ?? ''
  errors.value = {}
  formError.value = ''
}

async function submit() {
  if (!title.value.trim()) {
    errors.value = { title: ['Give it a name.'] }
    return
  }
  saving.value = true
  errors.value = {}
  formError.value = ''
  try {
    const doc = isEdit.value
      ? await api.value.update(props.document.id, { title: title.value.trim(), version: props.document.version })
      : await api.value.create({ title: title.value.trim(), template: template.value })
    savedDocument = doc
    modal.hide()
  } catch (error) {
    errors.value = error.fields || {}
    formError.value = error.message || 'Kaydedilemedi. Lütfen tekrar deneyin.'
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div ref="el" class="modal fade" tabindex="-1" aria-labelledby="doc-form-title" aria-hidden="true">
    <div class="modal-dialog modal-dialog-centered">
      <form class="modal-content" novalidate @submit.prevent="submit">
        <div class="modal-header">
          <h2 id="doc-form-title" class="modal-title h5">{{ heading }}</h2>
          <button type="button" class="btn-close" aria-label="Kapat" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body">
          <div v-if="formError" class="alert alert-danger py-2" role="alert">{{ formError }}</div>
          <div class="mb-3">
            <label for="doc-title" class="form-label">Belge adı</label>
            <input
              id="doc-title"
              v-model="title"
              type="text"
              maxlength="160"
              class="form-control"
              :class="{ 'is-invalid': fieldError(errors, 'title') }"
              placeholder="Örn. Kıdemli Backend Geliştirici CV 2026"
              :aria-describedby="fieldError(errors, 'title') ? 'doc-title-error' : undefined"
              autofocus
            />
            <div v-if="fieldError(errors, 'title')" id="doc-title-error" class="invalid-feedback">
              {{ fieldError(errors, 'title') }}
            </div>
          </div>
          <div v-if="!isEdit">
            <label for="doc-template" class="form-label">Başlangıç şablonu</label>
            <select id="doc-template" v-model="template" class="form-select" :class="{ 'is-invalid': fieldError(errors, 'template') }">
              <option v-for="item in templates" :key="item.id" :value="item.id">{{ item.name }}</option>
            </select>
            <div class="form-text">{{ templates.find((t) => t.id === template)?.description }}</div>
            <div v-if="fieldError(errors, 'template')" class="invalid-feedback d-block">{{ fieldError(errors, 'template') }}</div>
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-outline-secondary" data-bs-dismiss="modal" :disabled="saving">Vazgeç</button>
          <button type="submit" class="btn btn-primary" :disabled="saving">
            <span v-if="saving" class="spinner-border spinner-border-sm me-2" aria-hidden="true"></span>
            {{ isEdit ? 'Adı kaydet' : 'Oluştur' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>
