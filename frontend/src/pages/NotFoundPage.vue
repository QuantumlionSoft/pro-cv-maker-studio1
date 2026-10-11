<script setup>
import { RouterLink } from 'vue-router'
</script>

<template>
  <div class="not-found">
    <p class="display-6 mb-2">404</p>
    <h1 class="h4">We could not find that page.</h1>
    <p class="text-secondary">The link may be outdated, or the address may be mistyped.</p>
    <RouterLink :to="{ name: 'landing' }" class="btn btn-primary">Go to the home page</RouterLink>
  </div>
</template>
