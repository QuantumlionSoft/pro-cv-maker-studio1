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
  created: 'Oluşturuldu',
  updated: 'Güncellendi',
  deleted: 'Silindi',
  duplicated: 'Kopyalandı',
  password_changed: 'Şifre değiştirildi',
}
const OBJECT_LABEL = { cv: 'CV', portfolio: 'Portfolyo', account: 'Hesap' }

const stats = computed(() => [
  { key: 'cvs', label: 'Toplam CV', value: summary.value?.counts.cvs, icon: 'bi-file-earmark-person', to: { name: 'cvs' } },
  { key: 'portfolios', label: 'Portfolyolar', value: summary.value?.counts.portfolios, icon: 'bi-window-sidebar', to: { name: 'portfolios' } },
  { key: 'projects', label: 'Projeler', value: null, icon: 'bi-kanban', phase: 3 },
  { key: 'certificates', label: 'Sertifikalar', value: null, icon: 'bi-award', phase: 3 },
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
  ui.toast(`${kind === 'cv' ? 'CV' : 'Portfolyo'} “${doc.title}” oluşturuldu.`, 'success')
  router.push(`/${kind === 'cv' ? 'cvs' : 'portfolios'}/${doc.id}`)
}

onMounted(load)
</script>

<template>
  <div>
    <section class="dashboard-welcome">
      <div class="dashboard-welcome-copy">
        <p class="dashboard-eyebrow"><i class="bi bi-stars"></i> Kariyer çalışma alanınız</p>
        <h2 class="page-title">Tekrar hoş geldiniz, {{ auth.displayName }}</h2>
        <p>Kaldığınız yerden devam edin veya profesyonel şablonlarla yeni bir çalışma başlatın.</p>
        <div class="d-flex flex-wrap gap-2 mt-4">
          <button type="button" class="btn btn-light" @click="openCreate('cv')"><i class="bi bi-plus-lg me-1 text-primary"></i>Yeni CV oluştur</button>
          <button type="button" class="btn dashboard-secondary-btn" @click="openCreate('portfolio')"><i class="bi bi-window-plus me-1"></i>Yeni portfolyo</button>
        </div>
      </div>
      <div class="dashboard-welcome-art" aria-hidden="true"><i class="bi bi-file-earmark-person"></i><span><i class="bi bi-check2-circle"></i> Başarıya bir adım daha yakın</span></div>
    </section>

    <div v-if="error" class="alert alert-danger d-flex justify-content-between align-items-center" role="alert">
      <span>Kontrol paneli yüklenemedi: {{ error }}</span>
      <button type="button" class="btn btn-sm btn-outline-danger" @click="load">Tekrar dene</button>
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
            <div v-if="stat.phase" class="small text-secondary">Faz {{ stat.phase }}</div>
          </div>
        </component>
      </div>
    </div>

    <div class="row g-4">
      <div class="col-lg-7">
        <section class="card h-100">
          <div class="card-header d-flex justify-content-between align-items-center">
            <h3 class="h6 mb-0">Son düzenlenenler</h3>
          </div>
          <div class="card-body p-0">
            <div v-if="loading" class="p-4 text-center text-secondary"><span class="spinner-border spinner-border-sm me-2"></span>Yükleniyor…</div>
            <EmptyState
              v-else-if="summary && summary.recent_documents.length === 0"
              icon="bi-stars"
              title="Henüz bir çalışmanız yok"
              description="İlk CV’nizi veya portfolyonuzu oluşturun; son çalışmalarınız burada görünsün."
            >
              <div class="d-flex gap-2 justify-content-center">
                <button type="button" class="btn btn-primary btn-sm" @click="openCreate('cv')">Yeni CV</button>
                <button type="button" class="btn btn-outline-primary btn-sm" @click="openCreate('portfolio')">Yeni portfolyo</button>
              </div>
            </EmptyState>
            <ul v-else class="list-group list-group-flush">
              <li v-for="doc in summary?.recent_documents" :key="`${doc.kind}-${doc.id}`" class="list-group-item d-flex justify-content-between align-items-center gap-3">
                <div class="min-w-0">
                  <RouterLink :to="doc.route" class="fw-semibold text-truncate d-block">{{ doc.title }}</RouterLink>
                  <span class="small text-secondary">{{ doc.kind === 'cv' ? 'CV' : 'Portfolio' }} · {{ timeAgo(doc.updated_at) }}</span>
                </div>
                <RouterLink :to="doc.route" class="btn btn-sm btn-outline-secondary flex-shrink-0">Aç</RouterLink>
              </li>
            </ul>
          </div>
        </section>
      </div>

      <div class="col-lg-5">
        <section class="card h-100">
          <div class="card-header"><h3 class="h6 mb-0">Son hareketler</h3></div>
          <div class="card-body p-0">
            <p v-if="!loading && summary && summary.recent_activity.length === 0" class="p-4 text-secondary mb-0">
              Hesap hareketleriniz burada görünecek.
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

<style scoped>
.dashboard-welcome { position: relative; display: flex; align-items: center; justify-content: space-between; gap: 2rem; min-height: 245px; margin-bottom: 1.5rem; padding: 2.25rem 2.5rem; overflow: hidden; color: #fff; border-radius: 18px; background: radial-gradient(circle at 85% 10%, rgba(131,123,255,.38), transparent 36%), linear-gradient(120deg,#172038,#24244d); box-shadow: 0 14px 30px rgba(28,33,65,.12); }
.dashboard-welcome::before { content: ''; position: absolute; right: -70px; bottom: -140px; width: 330px; height: 330px; border: 1px solid rgba(255,255,255,.08); border-radius: 50%; box-shadow: 0 0 0 45px rgba(255,255,255,.025), 0 0 0 90px rgba(255,255,255,.018); }
.dashboard-welcome-copy { position: relative; z-index: 1; }
.dashboard-eyebrow { margin-bottom: .75rem; color: #b9b4ff; font-size: .67rem; font-weight: 750; letter-spacing: .06em; text-transform: uppercase; }
.dashboard-eyebrow i { margin-right: .35rem; }
.dashboard-welcome h2 { margin-bottom: .65rem; font-size: clamp(1.55rem,3vw,2.15rem); font-weight: 760; letter-spacing: -.045em; }
.dashboard-welcome-copy > p:not(.dashboard-eyebrow) { max-width: 560px; margin: 0; color: #b8c2d5; font-size: .85rem; line-height: 1.7; }
.dashboard-welcome .btn-light { color: #34309a; }
.dashboard-secondary-btn { color: #fff; border: 1px solid rgba(255,255,255,.2); background: rgba(255,255,255,.06); }
.dashboard-secondary-btn:hover { color: #fff; border-color: rgba(255,255,255,.35); background: rgba(255,255,255,.11); }
.dashboard-welcome-art { position: relative; z-index: 1; display: grid; place-items: center; flex: 0 0 240px; }
.dashboard-welcome-art > i { display: grid; place-items: center; width: 125px; height: 155px; color: #8e88ed; border: 1px solid rgba(255,255,255,.18); border-radius: 10px; background: rgba(255,255,255,.94); box-shadow: 14px 15px 0 rgba(255,255,255,.07); font-size: 3.5rem; transform: rotate(4deg); }
.dashboard-welcome-art > span { position: absolute; right: -10px; bottom: -5px; padding: .55rem .7rem; color: #29354a; border-radius: 9px; background: #fff; box-shadow: 0 8px 20px rgba(0,0,0,.15); font-size: .62rem; font-weight: 700; white-space: nowrap; }
.dashboard-welcome-art > span i { color: #12a17a; margin-right: .25rem; }
@media (max-width: 767.98px) { .dashboard-welcome { min-height: 0; padding: 1.75rem 1.4rem; } .dashboard-welcome-art { display: none; } }
</style>
