<script setup>
import { ref, watch } from 'vue'
import { cvApi } from '@/services/documents'
import { useUiStore } from '@/stores/ui'
import { formatDateTime } from '@/utils/format'

const props = defineProps({
  open: { type: Boolean, default: false },
  documentId: { type: [String, Number], required: true },
  currentVersion: { type: Number, default: 0 },
})
const emit = defineEmits(['close', 'restored'])
const ui = useUiStore()
const loading = ref(false)
const error = ref('')
const revisions = ref([])
const restoringId = ref(null)

watch(() => props.open, async (open) => {
  if (!open) return
  loading.value = true
  error.value = ''
  try {
    revisions.value = await cvApi.revisions(props.documentId)
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
})

async function restore(revision) {
  const ok = await ui.confirm({
    title: `Sürüm ${revision.version} geri yüklensin mi?`,
    message: 'Mevcut içerik bu sürümle değiştirilecek. Geri yüklemeden önceki durum da sürüm geçmişinde kalır.',
    confirmText: 'Bu sürümü geri yükle',
    cancelText: 'Vazgeç',
  })
  if (!ok) return
  restoringId.value = revision.id
  try {
    const document = await cvApi.restoreRevision(props.documentId, revision.id)
    ui.toast(`Sürüm ${revision.version} geri yüklendi.`, 'success')
    emit('restored', document)
  } catch (err) {
    ui.toast(err.message, 'danger')
  } finally {
    restoringId.value = null
  }
}
</script>

<template>
  <Teleport to="body">
    <div v-if="open" class="history-backdrop cv-no-print" @click.self="emit('close')">
      <aside class="history-drawer" aria-label="CV sürüm geçmişi">
        <header><div><p class="eyebrow">Otomatik kayıtlar</p><h2>Sürüm geçmişi</h2><p>Son 20 kayıt saklanır.</p></div><button type="button" class="btn btn-light btn-icon" aria-label="Kapat" @click="emit('close')"><i class="bi bi-x-lg"></i></button></header>
        <div class="history-content">
          <div v-if="loading" class="history-state"><span class="spinner-border spinner-border-sm"></span> Sürümler yükleniyor…</div>
          <div v-else-if="error" class="alert alert-danger">{{ error }}</div>
          <div v-else-if="!revisions.length" class="history-state"><i class="bi bi-clock-history"></i><p>Henüz kayıtlı bir sürüm yok.</p></div>
          <ol v-else class="history-list">
            <li v-for="revision in revisions" :key="revision.id">
              <span class="history-dot"></span>
              <div class="history-info"><div><strong>Sürüm {{ revision.version }}</strong><span v-if="revision.version === currentVersion" class="history-current">Geçerli</span></div><p>{{ revision.title }}</p><small>{{ formatDateTime(revision.created_at) }}</small></div>
              <button type="button" class="btn btn-sm btn-outline-primary" :disabled="revision.version === currentVersion || restoringId !== null" @click="restore(revision)"><span v-if="restoringId === revision.id" class="spinner-border spinner-border-sm"></span><i v-else class="bi bi-arrow-counterclockwise"></i><span class="ms-1">Geri yükle</span></button>
            </li>
          </ol>
        </div>
        <footer><i class="bi bi-info-circle"></i> Her geri yükleme yeni bir sürüm oluşturur; önceki kayıtlar silinmez.</footer>
      </aside>
    </div>
  </Teleport>
</template>

<style scoped>
.history-backdrop { position: fixed; inset: 0; z-index: 1080; background: rgba(17,24,43,.35); backdrop-filter: blur(2px); }
.history-drawer { position: absolute; top: 0; right: 0; display: flex; flex-direction: column; width: min(440px,100%); height: 100%; background: #fff; box-shadow: -20px 0 50px rgba(17,24,43,.16); }
.history-drawer header { display: flex; justify-content: space-between; gap: 1rem; padding: 1.4rem; border-bottom: 1px solid #e6e9f0; }
.history-drawer header .eyebrow { margin: 0 0 .3rem; }
.history-drawer h2 { margin: 0; font-size: 1.25rem; font-weight: 750; }
.history-drawer header p:last-child { margin: .25rem 0 0; color: #667085; font-size: .72rem; }
.history-content { flex: 1; overflow-y: auto; padding: 1.25rem; }
.history-state { padding: 3rem 1rem; color: #667085; text-align: center; }
.history-state > i { display: block; margin-bottom: .75rem; color: #8b84e8; font-size: 2rem; }
.history-list { margin: 0; padding: 0; list-style: none; }
.history-list li { position: relative; display: flex; align-items: center; gap: .75rem; padding: 0 0 1.4rem .9rem; border-left: 1px solid #e0e4ec; }
.history-list li:last-child { border-left-color: transparent; }
.history-dot { position: absolute; top: .35rem; left: -5px; width: 9px; height: 9px; border: 2px solid #fff; border-radius: 50%; background: #7168e5; box-shadow: 0 0 0 1px #7168e5; }
.history-info { min-width: 0; flex: 1; }
.history-info > div { display: flex; align-items: center; gap: .4rem; }
.history-info strong { color: #29354a; font-size: .78rem; }
.history-info p { overflow: hidden; margin: .25rem 0; color: #596579; font-size: .72rem; text-overflow: ellipsis; white-space: nowrap; }
.history-info small { color: #98a2b3; font-size: .62rem; }
.history-current { padding: .12rem .35rem; color: #087153; border-radius: 999px; background: #edf9f4; font-size: .55rem; }
.history-list .btn { font-size: .64rem; white-space: nowrap; }
.history-drawer footer { padding: .85rem 1.25rem; color: #667085; border-top: 1px solid #e6e9f0; background: #fafbfc; font-size: .65rem; line-height: 1.5; }
.history-drawer footer i { margin-right: .35rem; }
</style>
