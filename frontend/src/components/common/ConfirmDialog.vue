<script setup>
import { computed, nextTick, ref, watch } from 'vue'
import { useUiStore } from '@/stores/ui'

const ui = useUiStore()
const request = computed(() => ui.confirmRequest)
const dialog = ref(null)
const cancelButton = ref(null)

watch(request, (value) => {
  if (value) nextTick(() => cancelButton.value?.focus())
})

function onKeydown(event) {
  if (event.key === 'Escape') ui.resolveConfirm(false)
}
</script>

<template>
  <div v-if="request" class="confirm-backdrop">
    <div
      ref="dialog"
      class="confirm-dialog"
      role="alertdialog"
      aria-modal="true"
      aria-labelledby="confirm-title"
      aria-describedby="confirm-message"
      tabindex="-1"
      @keydown="onKeydown"
    >
      <h2 id="confirm-title" class="h5">{{ request.title }}</h2>
      <p id="confirm-message" class="text-secondary">{{ request.message }}</p>
      <div class="d-flex justify-content-end gap-2 mt-4">
        <button ref="cancelButton" type="button" class="btn btn-outline-secondary" @click="ui.resolveConfirm(false)">
          {{ request.cancelText }}
        </button>
        <button type="button" class="btn" :class="request.danger ? 'btn-danger' : 'btn-primary'" @click="ui.resolveConfirm(true)">
          {{ request.confirmText }}
        </button>
      </div>
    </div>
  </div>
</template>
