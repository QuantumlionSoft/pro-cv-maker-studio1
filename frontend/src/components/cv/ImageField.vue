<script setup>
import { ref } from 'vue'
import { mediaApi, mediaFileUrl } from '@/services/media'
import { useUiStore } from '@/stores/ui'

const props = defineProps({
  modelValue: { type: Number, default: null },
  purpose: { type: String, default: 'general' },
  label: { type: String, required: true },
  inputId: { type: String, required: true },
  round: { type: Boolean, default: false },
})
const emit = defineEmits(['update:modelValue'])

const ui = useUiStore()
const busy = ref(false)
const error = ref('')
const broken = ref(false)
const ACCEPT = 'image/jpeg,image/png,image/webp'

async function onFile(event) {
  const file = event.target.files && event.target.files[0]
  event.target.value = ''
  if (!file) return
  error.value = ''
  busy.value = true
  try {
    const asset = await mediaApi.upload(file, props.purpose)
    broken.value = false
    emit('update:modelValue', asset.id)
  } catch (err) {
    error.value = err.message || 'Görsel yüklenemedi.'
    ui.toast(error.value, 'danger')
  } finally {
    busy.value = false
  }
}

function clear() {
  emit('update:modelValue', null)
}
</script>

<template>
  <div class="cv-image-field">
    <label class="form-label small fw-bold d-block">{{ label }}</label>
    <div class="d-flex align-items-center gap-3 flex-wrap">
      <img
        v-if="modelValue && !broken"
        :src="mediaFileUrl(modelValue)"
        alt=""
        class="border bg-white object-fit-contain"
        :class="round ? 'rounded-circle' : 'rounded'"
        style="width: 64px; height: 64px; object-fit: cover"
        @error="broken = true"
      >
      <div v-else class="border rounded bg-light text-secondary d-flex align-items-center justify-content-center" style="width: 64px; height: 64px">
        <i class="bi bi-image"></i>
      </div>
      <div class="d-flex gap-2">
        <label :for="inputId" class="btn btn-sm btn-outline-secondary mb-0" :class="{ disabled: busy }">
          <span v-if="busy" class="spinner-border spinner-border-sm me-1" aria-hidden="true"></span>
          <i v-else class="bi bi-upload me-1"></i>{{ modelValue ? 'Değiştir' : 'Yükle' }}
        </label>
        <input :id="inputId" type="file" :accept="ACCEPT" class="visually-hidden" :disabled="busy" @change="onFile">
        <button v-if="modelValue" type="button" class="btn btn-sm btn-outline-danger" @click="clear">
          <i class="bi bi-trash me-1"></i>Kaldır
        </button>
      </div>
    </div>
    <div v-if="error" class="form-text text-danger">{{ error }}</div>
    <div v-else class="form-text">JPG, PNG veya WEBP.</div>
  </div>
</template>
