<script setup>
import { useUiStore } from '@/stores/ui'
const ui = useUiStore()
</script>

<template>
  <div class="toast-host" aria-live="polite" aria-atomic="false">
    <div
      v-for="toast in ui.toasts"
      :key="toast.id"
      class="toast-item"
      :class="`toast-item--${toast.variant}`"
      role="status"
    >
      <span class="flex-grow-1">{{ toast.message }}</span>
      <button type="button" class="btn-close btn-close-sm" aria-label="Dismiss notification" @click="ui.dismissToast(toast.id)"></button>
    </div>
  </div>
</template>
