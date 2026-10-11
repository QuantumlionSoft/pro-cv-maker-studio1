<script setup>
import { computed } from 'vue'
import { RouterLink, useRoute } from 'vue-router'

const route = useRoute()

const FEATURES = {
  projects: { title: 'Projects', phase: 3, text: 'A central project manager. Projects can be reused across CVs and portfolios, with galleries, links and case studies.' },
  certificates: { title: 'Certificates', phase: 3, text: 'Store certificates once and attach them to any document. Uploaded files are validated and kept private.' },
  'qr-codes': { title: 'QR Codes', phase: 3, text: 'Locally generated QR codes for CVs, projects and certificates, with PNG and SVG download.' },
  media: { title: 'Media Library', phase: 3, text: 'Central storage for images and files used by your documents, with safe uploads and cleanup.' },
  exports: { title: 'Exports', phase: 5, text: 'PDF, standalone HTML/CSS/JavaScript websites, ZIP bundles and JSON backups.' },
}

const feature = computed(() => FEATURES[route.params.feature] || null)
</script>

<template>
  <div>
    <template v-if="feature">
      <section class="page-header">
        <div>
          <h2 class="page-title">{{ feature.title }}</h2>
          <p class="text-secondary mb-0">Planned for Phase {{ feature.phase }}.</p>
        </div>
      </section>
      <div class="card">
        <div class="card-body py-5 text-center">
          <i class="bi bi-hourglass-split display-5 text-secondary" aria-hidden="true"></i>
          <p class="mt-3 mb-4 mx-auto planned-text">{{ feature.text }}</p>
          <RouterLink :to="{ name: 'dashboard' }" class="btn btn-outline-primary">Back to dashboard</RouterLink>
        </div>
      </div>
    </template>
    <div v-else class="card"><div class="card-body text-center py-5">
      <p class="mb-3">This feature is not available.</p>
      <RouterLink :to="{ name: 'dashboard' }" class="btn btn-outline-primary">Back to dashboard</RouterLink>
    </div></div>
  </div>
</template>
