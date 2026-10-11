<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import DocumentFormModal from '@/components/dashboard/DocumentFormModal.vue'
import EmptyState from '@/components/common/EmptyState.vue'
import { dashboardApi } from '@/services/dashboard'
import { cvApi, portfolioApi } from '@/services/documents'
import { useAuthStore } from '@/stores/auth'
import { useUiStore } from '@/stores/ui'
import { formatDateTime, timeAgo } from '@/utils/format'

const auth = useAuthStore()
const ui = useUiStore()
const router = useRouter()

const summary = ref(null)
const loading = ref(true)
const error = ref('')
const modal = ref({ open: false, kind: 'cv', templates: [] })

const ACTIVITY_LABEL = {
  created: 'Created',
  updated: 'Updated',
  deleted: 'Deleted',
  duplicated: 'Duplicated',
  password_changed: 'Changed password',
}
const OBJECT_LABEL = { cv: 'CV', portfolio: 'Portfolio', account: 'Account' }

const stats = computed(() => [
  { key: 'cvs', label: 'CVs', value: summary.value?.counts.cvs, icon: 'bi-file-earmark-person', to: { name: 'cvs' } },
  { key: 'portfolios', label: 'Portfolios', value: summary.value?.counts.portfolios, icon: 'bi-window-sidebar', to: { name: 'portfolios' } },
  { key: 'projects', label: 'Projects', value: null, icon: 'bi-kanban', phase: 3 },
  { key: 'certificates', label: 'Certificates', value: null, icon: 'bi-award', phase: 3 },
])

async function load() {
  loading.value = true
  error.value = ''
  try {
    summary.value = await dashboardApi.summary()
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

async function openCreate(kind) {
  const api = kind === 'cv' ? cvApi : portfolioApi
  try {
    const templates = await api.templates()
    modal.value = { open: true, kind, templates }
  } catch (err) {
    ui.toast(err.message, 'danger')
  }
}

function onSaved(doc) {
  const kind = modal.value.kind
  ui.toast(`${kind === 'cv' ? 'CV' : 'Portfolio'} “${doc.title}” created.`, 'success')
  router.push(`/${kind === 'cv' ? 'cvs' : 'portfolios'}/${doc.id}`)
}

onMounted(load)
</script>

<template>
  <div>
    <section class="page-header">
      <div>
        <p class="eyebrow mb-1">Welcome back</p>
        <h2 class="page-title">{{ auth.displayName }}</h2>
        <p class="text-secondary mb-0">Continue your work or start something new.</p>
      </div>
      <div class="d-flex flex-wrap gap-2">
        <button type="button" class="btn btn-primary" @click="openCreate('cv')"><i class="bi bi-plus-lg me-1" aria-hidden="true"></i>New CV</button>
        <button type="button" class="btn btn-outline-primary" @click="openCreate('portfolio')"><i class="bi bi-plus-lg me-1" aria-hidden="true"></i>New portfolio</button>
      </div>
    </section>

    <div v-if="error" class="alert alert-danger d-flex justify-content-between align-items-center" role="alert">
      <span>Could not load your dashboard: {{ error }}</span>
      <button type="button" class="btn btn-sm btn-outline-danger" @click="load">Try again</button>
    </div>

    <div class="row g-3 mb-4" aria-busy="loading">
      <div v-for="stat in stats" :key="stat.key" class="col-6 col-xl-3">
        <component :is="stat.to ? RouterLink : 'div'" :to="stat.to" class="card stat-card h-100" :class="{ 'stat-card--planned': stat.phase }">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-start">
              <span class="stat-label">{{ stat.label }}</span>
              <i :class="['bi', stat.icon, 'stat-icon']" aria-hidden="true"></i>
            </div>
            <div v-if="loading && stat.value === undefined" class="placeholder-glow mt-2"><span class="placeholder col-4 rounded"></span></div>
            <div v-else-if="stat.phase" class="stat-value stat-value--muted">—</div>
            <div v-else class="stat-value">{{ stat.value ?? 0 }}</div>
            <div v-if="stat.phase" class="small text-secondary">Available in Phase {{ stat.phase }}</div>
          </div>
        </component>
      </div>
    </div>

    <div class="row g-4">
      <div class="col-lg-7">
        <section class="card h-100">
          <div class="card-header d-flex justify-content-between align-items-center">
            <h3 class="h6 mb-0">Recently edited</h3>
          </div>
          <div class="card-body p-0">
            <div v-if="loading" class="p-4 text-center text-secondary"><span class="spinner-border spinner-border-sm me-2"></span>Loading…</div>
            <EmptyState
              v-else-if="summary && summary.recent_documents.length === 0"
              icon="bi-stars"
              title="Nothing here yet"
              description="Create your first CV or portfolio to see it listed here."
            >
              <div class="d-flex gap-2 justify-content-center">
                <button type="button" class="btn btn-primary btn-sm" @click="openCreate('cv')">New CV</button>
                <button type="button" class="btn btn-outline-primary btn-sm" @click="openCreate('portfolio')">New portfolio</button>
              </div>
            </EmptyState>
            <ul v-else class="list-group list-group-flush">
              <li v-for="doc in summary?.recent_documents" :key="`${doc.kind}-${doc.id}`" class="list-group-item d-flex justify-content-between align-items-center gap-3">
                <div class="min-w-0">
                  <RouterLink :to="doc.route" class="fw-semibold text-truncate d-block">{{ doc.title }}</RouterLink>
                  <span class="small text-secondary">{{ doc.kind === 'cv' ? 'CV' : 'Portfolio' }} · {{ timeAgo(doc.updated_at) }}</span>
                </div>
                <RouterLink :to="doc.route" class="btn btn-sm btn-outline-secondary flex-shrink-0">Open</RouterLink>
              </li>
            </ul>
          </div>
        </section>
      </div>

      <div class="col-lg-5">
        <section class="card h-100">
          <div class="card-header"><h3 class="h6 mb-0">Recent activity</h3></div>
          <div class="card-body p-0">
            <p v-if="!loading && summary && summary.recent_activity.length === 0" class="p-4 text-secondary mb-0">
              Your actions will appear here.
            </p>
            <ul v-else class="list-group list-group-flush activity-list">
              <li v-for="item in summary?.recent_activity" :key="item.id" class="list-group-item">
                <div class="small">
                  <strong>{{ ACTIVITY_LABEL[item.action] || item.action }}</strong>
                  <template v-if="item.object_title"> · {{ item.object_title }}</template>
                  <span class="text-secondary"> · {{ OBJECT_LABEL[item.object_type] || item.object_type }}</span>
                </div>
                <div class="small text-secondary" :title="formatDateTime(item.created_at)">{{ timeAgo(item.created_at) }}</div>
              </li>
            </ul>
          </div>
        </section>
      </div>
    </div>

    <DocumentFormModal
      :open="modal.open"
      :kind="modal.kind"
      :templates="modal.templates"
      @saved="onSaved"
      @close="modal.open = false"
    />
  </div>
</template>
