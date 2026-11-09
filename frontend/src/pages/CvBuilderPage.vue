<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { onBeforeRouteLeave, RouterLink, useRoute } from 'vue-router'
import CvFormPanel from '@/components/cv/CvFormPanel.vue'
import CvPreview from '@/components/cv/CvPreview.vue'
import CvHistoryDrawer from '@/components/cv/CvHistoryDrawer.vue'
import { SECTION_TABS } from '@/components/cv/cvSections'
import SaveStatus from '@/components/common/SaveStatus.vue'
import { useCvBuilder } from '@/composables/useCvBuilder'
import { cvApi } from '@/services/documents'
import { mediaApi } from '@/services/media'
import { useUiStore } from '@/stores/ui'
import { buildExport } from '@/utils/cvContent'
import { createCvBackup, parseDocumentFile } from '@/utils/cvImport'
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
const historyOpen = ref(false)
const importing = ref(false)
const backupBusy = ref(false)
const isPrinting = ref(false)
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

/* ---------- JSON / ZIP / Office import and portable export ---------- */
function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  link.remove()
  setTimeout(() => URL.revokeObjectURL(url), 1000)
}

function exportJson() {
  try {
    const data = buildExport({
      title: title.value,
      template: template.value,
      content: content.value,
      design: design.value,
    })
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
    downloadBlob(blob, `${slug(title.value) || 'cv'}-${new Date().toISOString().slice(0, 10)}.json`)
    ui.toast('JSON dosyası indirildi. Fotoğraflar dosyaya dahil edilmez.', 'success')
  } catch {
    ui.toast('JSON dışa aktarılamadı.', 'danger')
  }
}

async function exportBackup() {
  backupBusy.value = true
  try {
    const result = await createCvBackup({ title: title.value, template: template.value, content: content.value, design: design.value })
    downloadBlob(result.blob, `${slug(title.value) || 'cv'}-yedek-${new Date().toISOString().slice(0, 10)}.zip`)
    result.warnings.forEach((message) => ui.toast(message, 'warning', 8000))
    ui.toast(`Yedek indirildi. ${result.imageCount} görsel pakete eklendi.`, 'success')
  } catch (error) {
    ui.toast(error.message || 'ZIP yedeği oluşturulamadı.', 'danger')
  } finally {
    backupBusy.value = false
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
  importing.value = true
  let parsed
  try {
    parsed = await parseDocumentFile(file)
  } catch (error) {
    ui.toast(error.message || 'Dosya içe aktarılamadı.', 'danger', 0)
    importing.value = false
    return
  }
  const ok = await ui.confirm({
    title: 'Dosya içe aktarılsın mı?',
    message: 'Mevcut içerik ve tasarım dosyadaki verilerle değiştirilecek. Ayrıştırılan alanları daha sonra kontrol edebilirsiniz.',
    confirmText: 'İçe aktar',
    cancelText: 'Vazgeç',
    danger: true,
  })
  if (!ok) { importing.value = false; return }
  try {
    for (const image of parsed.media || []) {
      try {
        const filename = image.path.split('/').pop()
        const asset = await mediaApi.upload(new File([image.blob], filename, { type: image.type || image.blob.type }), image.purpose)
        if (parsed.content.personal.photoId === image.originalId) parsed.content.personal.photoId = asset.id
        for (const section of ['experience', 'education']) {
          for (const item of parsed.content[section] || []) if (item.logoId === image.originalId) item.logoId = asset.id
        }
      } catch {
        parsed.warnings.push(`${image.path} geri yüklenemedi; görseli yeniden seçin.`)
      }
    }
    builder.replaceFromImport(parsed)
    parsed.warnings.forEach((message) => ui.toast(message, 'warning', 8000))
    ui.toast('Veriler içe aktarıldı ve kaydediliyor.', 'success')
  } finally {
    importing.value = false
  }
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

let titleBeforePrint = ''
let printFallback = null
function afterPrint() {
  isPrinting.value = false
  clearTimeout(printFallback)
  if (titleBeforePrint) document.title = titleBeforePrint
}

async function printCv() {
  if (isPrinting.value) return
  isPrinting.value = true
  await nextTick()
  await Promise.all([waitForImages(docShell.value), document.fonts?.ready])
  titleBeforePrint = document.title
  document.title = `${slug(title.value) || 'cv'}.pdf`
  ui.toast('Yazdırma penceresinde “PDF olarak kaydet” ve “Arka plan grafikleri” seçeneklerini kullanabilirsiniz.', 'info', 7000)
  printFallback = setTimeout(afterPrint, 60000)
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
  if (!(event.ctrlKey || event.metaKey)) return
  const key = event.key.toLowerCase()
  if (key === 's') { event.preventDefault(); builder.save() }
  if (key === 'p') { event.preventDefault(); printCv() }
  const editingText = ['INPUT', 'TEXTAREA', 'SELECT'].includes(event.target?.tagName) || event.target?.isContentEditable
  if (!editingText && (key === 'z' || key === 'y')) {
    event.preventDefault()
    if (key === 'y' || event.shiftKey) builder.redo()
    else builder.undo()
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
  window.addEventListener('afterprint', afterPrint)
  await Promise.all([builder.load(), loadTemplates()])
})

onBeforeUnmount(() => {
  window.removeEventListener('keydown', onKeydown)
  window.removeEventListener('beforeunload', onBeforeUnload)
  window.removeEventListener('afterprint', afterPrint)
  clearTimeout(printFallback)
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
          <RouterLink to="/cvs" class="btn btn-sm btn-outline-secondary flex-shrink-0" aria-label="CV listesine dön">
            <i class="bi bi-arrow-left"></i>
          </RouterLink>
          <i class="bi bi-file-earmark-person fs-4 text-primary d-none d-md-inline"></i>
          <input
            id="editor-title"
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
          <button type="button" class="btn btn-sm btn-outline-primary" title="Değişiklikleri şimdi kaydet (Ctrl+S)" :disabled="status === 'saving'" @click="builder.save">
            <i class="bi bi-check2 me-1"></i><span class="d-none d-lg-inline">Kaydet</span>
          </button>
          <button type="button" class="btn btn-sm btn-primary fw-bold px-3" title="Yazdır veya PDF olarak kaydet (Ctrl+P)" :disabled="isPrinting" @click="printCv">
            <span v-if="isPrinting" class="spinner-border spinner-border-sm me-1"></span><i v-else class="bi bi-printer-fill me-1"></i>{{ isPrinting ? 'Hazırlanıyor…' : 'PDF / Yazdır' }}
          </button>
        </div>
      </header>

      <div class="cv-actionbar cv-no-print">
        <div class="cv-action-group">
          <button type="button" class="btn btn-sm btn-light" title="Geri al (Ctrl+Z)" :disabled="!builder.canUndo.value" @click="builder.undo"><i class="bi bi-arrow-counterclockwise"></i><span>Geri al</span></button>
          <button type="button" class="btn btn-sm btn-light" title="Yinele (Ctrl+Shift+Z)" :disabled="!builder.canRedo.value" @click="builder.redo"><i class="bi bi-arrow-clockwise"></i><span>Yinele</span></button>
          <span class="cv-action-divider"></span>
          <button type="button" class="btn btn-sm btn-light" @click="historyOpen = true"><i class="bi bi-clock-history"></i><span>Sürüm geçmişi</span></button>
        </div>
        <div class="cv-action-group">
          <button type="button" class="btn btn-sm btn-light" title="Görsel içermeyen JSON indir" @click="exportJson"><i class="bi bi-filetype-json"></i><span>JSON indir</span></button>
          <button type="button" class="btn btn-sm btn-light" title="Fotoğraf ve logolarla tam ZIP yedeği" :disabled="backupBusy" @click="exportBackup"><span v-if="backupBusy" class="spinner-border spinner-border-sm"></span><i v-else class="bi bi-file-earmark-zip"></i><span>{{ backupBusy ? 'Hazırlanıyor…' : 'Tam yedek' }}</span></button>
          <button type="button" class="btn btn-sm btn-outline-primary" title="JSON, ZIP, PDF, DOCX veya TXT yükle" :disabled="importing" @click="pickImportFile"><span v-if="importing" class="spinner-border spinner-border-sm"></span><i v-else class="bi bi-upload"></i><span>{{ importing ? 'İçe aktarılıyor…' : 'Dosya yükle' }}</span></button>
          <input ref="importInput" type="file" accept=".json,.zip,.pdf,.docx,.txt,application/json,application/pdf" class="visually-hidden" @change="onImportFile">
        </div>
      </div>

      <!-- Save status for small screens -->
      <div class="cv-save-bar cv-no-print d-xl-none">
        <SaveStatus :status="status" :last-saved-at="lastSavedAt" :error="errorMessage" @retry="builder.retry" />
      </div>

      <!-- Mobile view switch -->
      <div class="cv-mobile-switch cv-no-print btn-group btn-group-sm d-lg-none" role="group" aria-label="Görünüm">
        <button type="button" class="btn" :class="mobileView === 'form' ? 'btn-primary' : 'btn-outline-secondary'" @click="mobileView = 'form'">
          <i class="bi bi-pencil-square me-1"></i>Düzenle
        </button>
        <button type="button" class="btn" :class="mobileView === 'preview' ? 'btn-primary' : 'btn-outline-secondary'" @click="mobileView = 'preview'">
          <i class="bi bi-eye me-1"></i>Önizleme
        </button>
      </div>

      <div ref="docShell" class="cv-workspace">
        <!-- Section navigation -->
        <nav class="cv-nav cv-no-print" aria-label="CV bölümleri">
          <div class="cv-nav-label">CV İÇERİĞİ</div>
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
            @update:active-tab="activeTab = $event"
          />
        </section>

        <!-- Preview -->
        <section ref="previewCol" class="cv-preview-col" :class="{ 'cv-hide-sm': mobileView !== 'preview' }" aria-label="CV önizlemesi">
          <div class="cv-preview-toolbar cv-no-print"><span><i class="bi bi-eye me-1"></i>Canlı önizleme <small>A4 · 210 × 297 mm</small></span><span class="cv-zoom-badge">{{ Math.round(zoom * 100) }}%</span></div>
          <CvPreview :content="content" :design="design" :template="template" :zoom="zoom" />
        </section>
      </div>
    </template>
    <CvHistoryDrawer :open="historyOpen" :document-id="route.params.id" :current-version="builder.version.value" @close="historyOpen = false" @restored="historyOpen = false; builder.reloadLatest()" />
  </div>
</template>

<style scoped>
.cv-builder {
  height: 100vh;
  height: 100dvh;
  display: flex;
  flex-direction: column;
  background: #edf0f5;
  overflow: hidden;
}
.cv-state { flex: 1; display: flex; align-items: center; justify-content: center; padding: 2rem; }
.cv-topbar {
  min-height: 64px;
  flex-shrink: 0;
  background: rgba(255,255,255,.97);
  color: #1d2939;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  padding: .55rem 1rem;
  border-bottom: 1px solid #e2e7ef;
  box-shadow: 0 1px 5px rgba(24,33,54,.035);
  z-index: 3;
}
.cv-title-input { background: #f8f9fc; color: #1d2939; border-color: transparent; max-width: 360px; min-width: 120px; font-weight: 650; }
.cv-title-input::placeholder { color: #98a2b3; }
.cv-title-input:hover { background: #f1f3f8; }
.cv-title-input:focus { background: #fff; color: #1d2939; border-color: #a5a0ee; }
.cv-save-wrap :deep(.save-status) { color: #667085; font-size: .72rem; }
.cv-save-bar { padding: 0.35rem 1rem; background: #fff; border-bottom: 1px solid #e2e8f0; }
.cv-actionbar { display: flex; align-items: center; justify-content: space-between; gap: .75rem; padding: .4rem .75rem; border-bottom: 1px solid #e2e7ef; background: #fafbfc; }
.cv-action-group { display: flex; align-items: center; gap: .3rem; }
.cv-action-group .btn { display: inline-flex; align-items: center; gap: .35rem; min-height: 31px; padding: .3rem .55rem; font-size: .66rem; }
.cv-action-group .btn-light { color: #596579; border-color: transparent; }
.cv-action-group .btn-light:hover:not(:disabled) { color: #4038c7; background: #efeeff; }
.cv-action-divider { width: 1px; height: 20px; margin: 0 .2rem; background: #dfe4eb; }
.cv-mobile-switch { display: flex; margin: 0.5rem auto; width: max-content; }
.cv-workspace { flex: 1; display: flex; min-height: 0; }
.cv-nav {
  width: 196px;
  flex-shrink: 0;
  padding: 1rem .65rem;
  background: #fafbfc;
  border-right: 1px solid #e2e7ef;
  overflow-y: auto;
}
.cv-nav-label { padding: .1rem .7rem .75rem; color: #98a2b3; font-size: .58rem; font-weight: 800; letter-spacing: .12em; }
.cv-nav :deep(.nav-link) {
  display: flex;
  align-items: center;
  color: #596579;
  border-radius: 8px;
  margin-bottom: 2px;
  padding: .66rem .7rem;
  border-left: 0;
  text-align: left;
  font-size: .75rem;
  font-weight: 600;
  white-space: nowrap;
  width: 100%;
}
.cv-nav :deep(.nav-link i) { width: 18px; color: #8792a5; text-align: center; }
.cv-nav :deep(.nav-link:hover) { background: #f0f2f7; color: #29354a; }
.cv-nav :deep(.nav-link.active) { background: #eeedff; color: #4f46e5; border-left: 0; }
.cv-nav :deep(.nav-link.active i) { color: #4f46e5; }
.cv-nav :deep(.nav-link.mt-2) { margin-top: .85rem !important; padding-top: .85rem !important; border-color: #e7eaf0 !important; }
.cv-form-col {
  width: 404px;
  flex-shrink: 0;
  background: #fff;
  border-right: 1px solid #e2e8f0;
  overflow-y: auto;
}
.cv-preview-col {
  flex: 1 1 auto;
  min-width: 0;
  background-color: #e9edf3;
  background-image: radial-gradient(#c9d0dc .65px, transparent .65px);
  background-size: 18px 18px;
  overflow: auto;
  padding: 0 1.5rem 2rem;
}
.cv-preview-toolbar { position: sticky; top: 0; z-index: 2; display: flex; align-items: center; justify-content: space-between; margin: 0 -1.5rem 1.5rem; padding: .65rem 1.25rem; color: #596579; border-bottom: 1px solid rgba(210,216,226,.85); background: rgba(244,246,249,.92); backdrop-filter: blur(10px); font-size: .7rem; font-weight: 650; }
.cv-preview-toolbar small { margin-left: .6rem; color: #98a2b3; font-size: .6rem; font-weight: 500; }
.cv-zoom-badge { padding: .2rem .45rem; color: #667085; border: 1px solid #d8dde6; border-radius: 5px; background: rgba(255,255,255,.7); font-size: .62rem; }
.cv-preview-col :deep(.cv-document) { margin-left: auto; margin-right: auto; box-shadow: 0 12px 35px rgba(33,42,62,.16); }

@media (max-width: 991.98px) {
  .cv-actionbar { overflow-x: auto; }
  .cv-action-group { flex-shrink: 0; }
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
  .cv-preview-col { padding: 0 .5rem 1rem; }
  .cv-preview-toolbar { margin: 0 -.5rem 1rem; }
  .cv-nav-label { display: none; }
  .cv-hide-sm { display: none !important; }
}
@media (max-width: 767.98px) {
  .cv-topbar { flex-wrap: wrap; gap: .45rem; }
  .cv-topbar > div { width: 100%; }
  .cv-topbar > div:last-child { justify-content: flex-end; }
  .cv-title-input { max-width: none; }
  .cv-preview-toolbar small { display: none; }
}
</style>
