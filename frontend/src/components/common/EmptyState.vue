<script setup>
defineProps({
  icon: { type: String, default: 'bi-inbox' },
  title: { type: String, required: true },
  description: { type: String, default: '' },
})
</script>

<template>
  <div class="empty-state">
    <i :class="['bi', icon, 'empty-icon']" aria-hidden="true"></i>
    <h2 class="h5 mb-1">{{ title }}</h2>
    <p v-if="description" class="text-secondary mb-3">{{ description }}</p>
    <slot />
  </div>
</template>
