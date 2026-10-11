<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { onBeforeRouteLeave, RouterLink, useRoute } from 'vue-router'
import CvFormPanel from '@/components/cv/CvFormPanel.vue'
import CvPreview from '@/components/cv/CvPreview.vue'
import { SECTION_TABS } from '@/components/cv/cvSections'
import SaveStatus from '@/components/common/SaveStatus.vue'
import { useCvBuilder } from '@/composables/useCvBuilder'
import { cvApi } from '@/services/documents'
import { useUiStore } from '@/stores/ui'
import { buildExport, parseImport } from '@/utils/cvContent'
import '@/assets/css/cv-print.css'

const route = useRoute()
const ui = useUiStore()
const builder = useCvBuilder({ id: route.params.id })
const { status, errorMessage, lastSavedAt, title, template, content, design, hasUnsaved } = builder

const activeTab = ref('personal')
const mobileView = ref('form')
const templates = ref([])
const docShell = ref(null)
const previewCol = ref(null)
const zoom = ref(1)
const importInput = ref(null)
const DOC_WIDTH_PX = 794 // 210mm at 96dpi

const isReady = computed(() => content.value !== null)
const templateOptions = computed(() => {
  const available = templates.value.filter((t) => t.available)
  if (available.length) return available
  return [{ id: template.value, name: template.value, available: true }]
})
const currentTabLabel = computed(() => SECTION_TABS.find((t) => t.id === activeTab.value)?.label || '')

async function loadTemplates() {
  try {
    templates.value = await cvApi.templates()
  } catch {
    templates.value = []
  }
}

/* ---------- Zoom: keep the A4 page fully visible on narrow screens ---------- */
let resizeObserver = null
function updateZoom() {
  const el = previewCol.value
  if (!el) return
  const available = el.clientWidth - 48
  zoom.value = Math.min(1, Math.max(0.35, available / DOC_WIDTH_PX))
}

/* ---------- JSON import / export ---------- */
function exportJson() {
  try {
    const data = buildExport({
      title: title.value,
      template: template.value,
      content: content.value,
      design: design.value,
    })
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `${slug(title.value) || 'cv'}-${new Date().toISOString().slice(0, 10)}.json`
    document.body.appendChild(link)
    link.click()
    link.remove()
    setTimeout(() => URL.revokeObjectURL(url), 1000)
    ui.toast('JSON dosyası indirildi. Fotoğraflar dosyaya dahil edilmez.', 'success')
  } catch {
    ui.toast('JSON dışa aktarılamadı.', 'danger')
  }
}

function slug(value) {
  return String(value || '')
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '')
}

function pickImportFile() {
  importInput.value?.click()
}

async function onImportFile(event) {
  const file = event.target.files && event.target.files[0]
  event.target.value = ''
  if (!file) return
  let parsed
  try {
    parsed = parseImport(await file.text())
  } catch (error) {
    ui.toast(error.message || 'Geçersiz JSON dosyası.', 'danger')
    return
  }
  const ok = await ui.confirm({
    title: 'JSON içe aktarılsın mı?',
    message: 'Mevcut içerik ve tasarım bu dosyadaki verilerle değiştirilecek.',
    confirmText: 'İçe aktar',
    cancelText: 'Vazgeç',
    danger: true,
  })
  if (!ok) return
  builder.replaceFromImport(parsed)
  parsed.warnings.forEach((message) => ui.toast(message, 'warning', 8000))
  ui.toast('Veriler içe aktarıldı ve kaydediliyor.', 'success')
}

/* ---------- Print / PDF ---------- */
function waitForImages(root) {
  const images = Array.from(root?.querySelectorAll('img') || [])
  return Promise.all(
    images.map((img) => {
      if (img.complete) return Promise.resolve()
      return new Promise((resolve) => {
        img.addEventListener('load', resolve, { once: true })
        img.addEventListener('error', resolve, { once: true })
        setTimeout(resolve, 5000)
      })
    }),
  )
}

async function printCv() {
  await nextTick()
  await waitForImages(docShell.value)
  window.print()
}

/* ---------- Conflict and reload ---------- */
async function reloadServerCopy() {
  const ok = await ui.confirm({
    title: 'Sunucudaki sürüm yüklensin mi?',
    message: 'Bu ekrandaki kaydedilmemiş değişiklikler kaybolacak.',
    confirmText: 'Sunucu sürümünü yükle',
    cancelText: 'Vazgeç',
    danger: true,
  })
  if (ok) await builder.reloadLatest()
}

/* ---------- Keyboard, unload guard, route guard ---------- */
function onKeydown(event) {
  if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 's') {
    event.preventDefault()
    builder.save()
  }
}
function onBeforeUnload(event) {
  if (hasUnsaved.value) {
    event.preventDefault()
    event.returnValue = ''
  }
}

onBeforeRouteLeave(async () => {
  if (!hasUnsaved.value) return true
  return ui.confirm({
    title: 'Kaydedilmemiş değişiklikler var',
    message: 'Son değişiklikler henüz sunucuya kaydedilmedi. Yine de çıkmak istiyor musunuz?',
    confirmText: 'Yine de çık',
    cancelText: 'Düzenlemeye dön',
    danger: true,
  })
})

// The preview column only exists once the CV has loaded, so attach the observer when it appears.
watch(previewCol, (el) => {
  resizeObserver?.disconnect()
  resizeObserver = null
  if (el && typeof ResizeObserver !== 'undefined') {
    resizeObserver = new ResizeObserver(updateZoom)
    resizeObserver.observe(el)
    updateZoom()
  }
})

onMounted(async () => {
  window.addEventListener('keydown', onKeydown)
  window.addEventListener('beforeunload', onBeforeUnload)
  await Promise.all([builder.load(), loadTemplates()])
})

onBeforeUnmount(() => {
  window.removeEventListener('keydown', onKeydown)
  window.removeEventListener('beforeunload', onBeforeUnload)
  resizeObserver?.disconnect()
})

watch(title, (value) => {
  document.title = `${value || 'CV'} · Pro CV Maker Studio`
})
</script>

<template>
  <div class="cv-builder">
    <!-- Loading and error states -->
    <div v-if="status === 'loading'" class="cv-state">
      <div class="spinner-border text-primary" role="status"><span class="visually-hidden">Yükleniyor…</span></div>
    </div>
    <div v-else-if="status === 'not_found'" class="cv-state">
      <div class="text-center">
        <h2 class="h4">CV bulunamadı</h2>
        <p class="text-secondary">Bu CV silinmiş olabilir ya da size ait değil.</p>
        <RouterLink class="btn btn-primary" to="/cvs">CV listesine dön</RouterLink>
      </div>
    </div>
    <div v-else-if="!isReady" class="cv-state">
      <div class="text-center">
        <h2 class="h4">CV yüklenemedi</h2>
        <p class="text-secondary">{{ errorMessage }}</p>
        <div class="d-flex gap-2 justify-content-center">
          <button type="button" class="btn btn-primary" @click="builder.load()">Tekrar dene</button>
          <RouterLink class="btn btn-outline-secondary" to="/cvs">CV listesine dön</RouterLink>
        </div>
      </div>
    </div>

    <!-- Editor -->
    <template v-else>
      <header class="cv-topbar cv-no-print">
        <div class="d-flex align-items-center gap-2 gap-md-3 flex-grow-1 min-w-0">
          <RouterLink to="/cvs" class="btn btn-sm btn-outline-light flex-shrink-0" aria-label="CV listesine dön">
            <i class="bi bi-arrow-left"></i>
          </RouterLink>
          <i class="bi bi-file-earmark-person fs-4 text-primary d-none d-md-inline"></i>
          <input
            v-model="title"
            class="form-control form-control-sm cv-title-input"
            aria-label="CV başlığı"
            maxlength="160"
            placeholder="CV başlığı"
          >
        </div>

        <div class="d-flex align-items-center gap-2 flex-shrink-0">
          <div class="d-none d-xl-block cv-save-wrap">
            <SaveStatus :status="status" :last-saved-at="lastSavedAt" :error="errorMessage" @retry="builder.retry" />
          </div>
          <button
            v-if="status === 'conflict'"
            type="button"
            class="btn btn-sm btn-warning"
            @click="reloadServerCopy"
          >
            <i class="bi bi-arrow-clockwise me-1"></i>Sunucu sürümünü yükle
          </button>
          <button type="button" class="btn btn-sm btn-outline-light" title="JSON olarak indir" @click="exportJson">
            <i class="bi bi-download me-1"></i><span class="d-none d-lg-inline">JSON İndir</span>
          </button>
          <button type="button" class="btn btn-sm btn-outline-light" title="JSON dosyasından yükle" @click="pickImportFile">
            <i class="bi bi-upload me-1"></i><span class="d-none d-lg-inline">JSON Yükle</span>
          </button>
          <input ref="importInput" type="file" accept="application/json,.json" class="visually-hidden" @change="onImportFile">
          <button type="button" class="btn btn-sm btn-primary fw-bold px-3" title="Yazdır veya PDF olarak kaydet" @click="printCv">
            <i class="bi bi-printer-fill me-1"></i>PDF / Yazdır
          </button>
        </div>
      </header>

      <!-- Save status for small screens -->
      <div class="cv-save-bar cv-no-print d-xl-none">
        <SaveStatus :status="status" :last-saved-at="lastSavedAt" :error="errorMessage" @retry="builder.retry" />
      </div>

      <!-- Mobile view switch -->
      <div class="cv-mobile-switch cv-no-print btn-group btn-group-sm d-lg-none" role="group" aria-label="Görünüm">
        <button type="button" class="btn" :class="mobileView === 'form' ? 'btn-primary' : 'btn-outline-light'" @click="mobileView = 'form'">
          <i class="bi bi-pencil-square me-1"></i>Düzenle
        </button>
        <button type="button" class="btn" :class="mobileView === 'preview' ? 'btn-primary' : 'btn-outline-light'" @click="mobileView = 'preview'">
          <i class="bi bi-eye me-1"></i>Önizleme
        </button>
      </div>

      <div ref="docShell" class="cv-workspace">
        <!-- Section navigation -->
        <nav class="cv-nav cv-no-print" aria-label="CV bölümleri">
          <div class="nav flex-column nav-pills">
            <button
              v-for="tab in SECTION_TABS"
              :key="tab.id"
              type="button"
              class="nav-link"
              :class="{ active: activeTab === tab.id, 'mt-2 border-top pt-3': tab.id === 'design' }"
              :aria-current="activeTab === tab.id ? 'page' : undefined"
              @click="activeTab = tab.id; mobileView = 'form'"
            >
              <i :class="['bi', tab.icon, 'me-2']"></i>{{ tab.label }}
            </button>
          </div>
        </nav>

        <!-- Form -->
        <section class="cv-form-col cv-no-print" :class="{ 'cv-hide-sm': mobileView !== 'form' }" :aria-label="currentTabLabel">
          <CvFormPanel
            :active-tab="activeTab"
            :content="content"
            :design="design"
            :template="template"
            :templates="templateOptions"
            @update:template="template = $event"
          />
        </section>

        <!-- Preview -->
        <section ref="previewCol" class="cv-preview-col" :class="{ 'cv-hide-sm': mobileView !== 'preview' }" aria-label="CV önizlemesi">
          <CvPreview :content="content" :design="design" :template="template" :zoom="zoom" />
        </section>
      </div>
    </template>
  </div>
</template>

<style scoped>
.cv-builder {
  height: 100vh;
  height: 100dvh;
  display: flex;
  flex-direction: column;
  background: #e2e8f0;
  overflow: hidden;
}
.cv-state { flex: 1; display: flex; align-items: center; justify-content: center; padding: 2rem; }
.cv-topbar {
  height: 60px;
  flex-shrink: 0;
  background: #0f172a;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  padding: 0 1rem;
  border-bottom: 1px solid #1e293b;
}
.cv-title-input { background: #1e293b; color: #fff; border-color: #334155; max-width: 360px; min-width: 120px; }
.cv-title-input::placeholder { color: #94a3b8; }
.cv-title-input:focus { background: #1e293b; color: #fff; }
.cv-save-wrap :deep(.save-status) { color: #cbd5e1; }
.cv-save-bar { padding: 0.35rem 1rem; background: #fff; border-bottom: 1px solid #e2e8f0; }
.cv-mobile-switch { display: flex; margin: 0.5rem auto; width: max-content; }
.cv-workspace { flex: 1; display: flex; min-height: 0; }
.cv-nav {
  width: 220px;
  flex-shrink: 0;
  background: #fff;
  border-right: 1px solid #e2e8f0;
  overflow-y: auto;
}
.cv-nav :deep(.nav-link) {
  color: #475569;
  border-radius: 0;
  padding: 0.85rem 1.25rem;
  border-left: 3px solid transparent;
  text-align: left;
  font-weight: 500;
  white-space: nowrap;
  width: 100%;
}
.cv-nav :deep(.nav-link:hover) { background: #f1f5f9; }
.cv-nav :deep(.nav-link.active) { background: #eff6ff; color: #2563eb; border-left-color: #2563eb; }
.cv-form-col {
  width: 380px;
  flex-shrink: 0;
  background: #fff;
  border-right: 1px solid #e2e8f0;
  overflow-y: auto;
}
.cv-preview-col {
  flex: 1 1 auto;
  min-width: 0;
  background: #525659;
  overflow: auto;
  padding: 2rem 1.5rem;
}
.cv-preview-col :deep(.cv-document) { margin-left: auto; margin-right: auto; }

@media (max-width: 991.98px) {
  .cv-workspace { flex-direction: column; }
  .cv-nav {
    width: 100%;
    border-right: 0;
    border-bottom: 1px solid #e2e8f0;
    overflow-x: auto;
    overflow-y: hidden;
    flex-shrink: 0;
  }
  .cv-nav .nav { flex-direction: row !important; flex-wrap: nowrap; }
  .cv-nav :deep(.nav-link) { border-left: 0; border-bottom: 3px solid transparent; padding: 0.65rem 0.9rem; }
  .cv-nav :deep(.nav-link.active) { border-left: 0; border-bottom-color: #2563eb; }
  .cv-nav :deep(.nav-link.mt-2) { margin-top: 0 !important; border-top: 0 !important; padding-top: 0.65rem !important; }
  .cv-form-col, .cv-preview-col { flex: 1 1 auto; width: 100%; min-height: 0; border-right: 0; }
  .cv-preview-col { padding: 1rem 0.5rem; }
  .cv-hide-sm { display: none !important; }
}
</style>
