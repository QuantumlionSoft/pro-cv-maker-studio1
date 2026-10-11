<script setup>
import ConfirmDialog from '@/components/common/ConfirmDialog.vue'
import ToastHost from '@/components/common/ToastHost.vue'
</script>

<template>
  <RouterView />
  <ToastHost />
  <ConfirmDialog />
</template>
