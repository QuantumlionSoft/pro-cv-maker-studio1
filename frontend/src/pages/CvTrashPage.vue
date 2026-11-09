<script setup>
import { onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import EmptyState from '@/components/common/EmptyState.vue'
import { cvApi } from '@/services/documents'
import { useUiStore } from '@/stores/ui'
import { formatDateTime } from '@/utils/format'

const ui = useUiStore()
const items = ref([])
const loading = ref(true)
const error = ref('')
const busyId = ref(null)

async function load() {
  loading.value = true
  error.value = ''
  try { items.value = await cvApi.trash() }
  catch (err) { error.value = err.message }
  finally { loading.value = false }
}
async function restore(doc) {
  busyId.value = doc.id
  try {
    await cvApi.restore(doc.id)
    items.value = items.value.filter((item) => item.id !== doc.id)
    ui.toast(`“${doc.title}” geri yüklendi.`, 'success')
  } catch (err) { ui.toast(err.message, 'danger') }
  finally { busyId.value = null }
}
async function permanentRemove(doc) {
  const ok = await ui.confirm({ title: 'CV kalıcı olarak silinsin mi?', message: `“${doc.title}”, tüm sürümleri ve bağlantılarıyla kalıcı silinecek. Bu işlem geri alınamaz.`, confirmText: 'Kalıcı olarak sil', cancelText: 'Vazgeç' })
  if (!ok) return
  busyId.value = doc.id
  try {
    await cvApi.permanentRemove(doc.id)
    items.value = items.value.filter((item) => item.id !== doc.id)
    ui.toast(`“${doc.title}” kalıcı olarak silindi.`, 'success')
  } catch (err) { ui.toast(err.message, 'danger') }
  finally { busyId.value = null }
}
onMounted(load)
</script>

<template>
  <div>
    <section class="page-header"><div><p class="eyebrow">Geri alınabilir silme</p><h2 class="page-title">CV Çöp Kutusu</h2><p class="text-secondary mb-0">Silinen CV’leri geri yükleyin veya tüm sürümleriyle kalıcı olarak kaldırın.</p></div><RouterLink to="/cvs" class="btn btn-outline-secondary"><i class="bi bi-arrow-left me-1"></i>CV’lerime dön</RouterLink></section>
    <div class="card"><div class="card-body">
      <div v-if="loading" class="py-5 text-center text-secondary"><span class="spinner-border spinner-border-sm me-2"></span>Çöp kutusu yükleniyor…</div>
      <div v-else-if="error" class="alert alert-danger d-flex justify-content-between"><span>{{ error }}</span><button class="btn btn-sm btn-outline-danger" @click="load">Tekrar dene</button></div>
      <EmptyState v-else-if="!items.length" icon="bi-trash3" title="Çöp kutusu boş" description="Sildiğiniz CV’ler burada görünür. Henüz geri yüklenecek bir belge yok."><RouterLink to="/cvs" class="btn btn-primary">CV’lerime dön</RouterLink></EmptyState>
      <div v-else class="table-responsive"><table class="table align-middle doc-table mb-0"><thead><tr><th>Belge</th><th>Silinme tarihi</th><th>Sürüm</th><th class="text-end">İşlemler</th></tr></thead><tbody><tr v-for="doc in items" :key="doc.id"><td><strong>{{ doc.title }}</strong><div class="small text-secondary">{{ doc.template }}</div></td><td class="small">{{ formatDateTime(doc.deleted_at) }}</td><td><span class="template-badge">v{{ doc.version }}</span></td><td class="text-end text-nowrap"><button type="button" class="btn btn-sm btn-outline-primary me-2" :disabled="busyId === doc.id" @click="restore(doc)"><i class="bi bi-arrow-counterclockwise me-1"></i>Geri yükle</button><button type="button" class="btn btn-sm btn-outline-danger" :disabled="busyId === doc.id" @click="permanentRemove(doc)"><i class="bi bi-trash3 me-1"></i>Kalıcı sil</button></td></tr></tbody></table></div>
    </div></div>
    <p class="small text-secondary mt-3"><i class="bi bi-shield-check me-1"></i>Kalıcı silme işlemi yalnızca bu sayfada ve açık onayınızla yapılır.</p>
  </div>
</template>
