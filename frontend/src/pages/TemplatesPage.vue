<script setup>
import { onMounted, ref } from 'vue'
import { cvApi, portfolioApi } from '@/services/documents'

const cvTemplates = ref([])
const portfolioTemplates = ref([])
const loading = ref(true)
const error = ref('')

onMounted(async () => {
  try {
    ;[cvTemplates.value, portfolioTemplates.value] = await Promise.all([cvApi.templates(), portfolioApi.templates()])
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div>
    <section class="page-header">
      <div>
        <h2 class="page-title">Templates</h2>
        <p class="text-secondary mb-0">A template sets the layout of a document. Changing it never deletes your content.</p>
      </div>
    </section>
    <div v-if="error" class="alert alert-danger" role="alert">{{ error }}</div>
    <div v-if="loading" class="text-secondary"><span class="spinner-border spinner-border-sm me-2"></span>Loading templates…</div>
    <template v-else>
      <h3 class="h6 mt-2">CV templates</h3>
      <div class="row g-3 mb-4">
        <div v-for="t in cvTemplates" :key="t.id" class="col-md-6 col-xl-4">
          <div class="card h-100 template-card">
            <div class="card-body">
              <h4 class="h6 mb-1">{{ t.name }}</h4>
              <p class="small text-secondary mb-0">{{ t.description }}</p>
            </div>
          </div>
        </div>
      </div>
      <h3 class="h6">Portfolio templates</h3>
      <div class="row g-3">
        <div v-for="t in portfolioTemplates" :key="t.id" class="col-md-6 col-xl-4">
          <div class="card h-100 template-card">
            <div class="card-body">
              <h4 class="h6 mb-1">{{ t.name }}</h4>
              <p class="small text-secondary mb-0">{{ t.description }}</p>
            </div>
          </div>
        </div>
      </div>
      <p class="small text-secondary mt-4">
        Layouts for each template are rendered in Phase 2 (CVs) and Phase 4 (portfolios). The template you choose is stored on the document now.
      </p>
    </template>
  </div>
</template>
