<script setup>
import { computed } from 'vue'
import { formatDateTime } from '@/utils/format'

const props = defineProps({
  status: { type: String, required: true },
  lastSavedAt: { type: Date, default: null },
  error: { type: String, default: '' },
})
defineEmits(['retry'])

const view = computed(() => {
  switch (props.status) {
    case 'saving':
      return { icon: 'bi-arrow-repeat spin', text: 'Kaydediliyor…', variant: 'text-secondary' }
    case 'dirty':
      return { icon: 'bi-pencil', text: 'Kaydedilmemiş değişiklikler · otomatik kaydedilecek', variant: 'text-warning-emphasis' }
    case 'saved':
      return { icon: 'bi-check-circle', text: `Tüm değişiklikler kaydedildi${props.lastSavedAt ? ' · ' + formatDateTime(props.lastSavedAt) : ''}`, variant: 'text-success' }
    case 'error':
      return { icon: 'bi-exclamation-triangle', text: props.error || 'Kaydetme başarısız.', variant: 'text-danger' }
    case 'conflict':
      return { icon: 'bi-exclamation-octagon', text: 'Başka bir yerde değiştirildi · kaydedilmedi.', variant: 'text-danger' }
    default:
      return { icon: 'bi-cloud', text: '', variant: 'text-secondary' }
  }
})
</script>

<template>
  <div class="save-status" role="status" aria-live="polite">
    <span v-if="view.text" :class="view.variant" class="d-inline-flex align-items-center gap-2 small">
      <i :class="['bi', view.icon]" aria-hidden="true"></i>{{ view.text }}
    </span>
    <button v-if="status === 'error'" type="button" class="btn btn-sm btn-outline-danger ms-2" @click="$emit('retry')">
      Tekrar kaydet
    </button>
  </div>
</template>
