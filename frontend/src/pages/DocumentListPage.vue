<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import DocumentFormModal from '@/components/dashboard/DocumentFormModal.vue'
import EmptyState from '@/components/common/EmptyState.vue'
import { useDocumentList } from '@/composables/useDocumentList'
import { createDocumentApi } from '@/services/documents'
import { useUiStore } from '@/stores/ui'
import { formatDateTime, timeAgo } from '@/utils/format'

const route = useRoute()
const ui = useUiStore()
const kind = computed(() => route.meta.kind)
const api = computed(() => createDocumentApi(kind.value))
const isCv = computed(() => kind.value === 'cv')
const noun = computed(() => (isCv.value ? 'CV' : 'portfolio'))
const detailBase = computed(() => (isCv.value ? '/cvs' : '/portfolios'))

const list = useDocumentList(api.value)
const templates = ref([])
const createModal = ref({ open: false })
const renameModal = ref({ open: false, document: null })
const busyId = ref(null)

const ORDERING = [
  { value: '-updated_at', label: 'Son düzenlenen' },
  { value: 'updated_at', label: 'En eski düzenlenen' },
  { value: '-created_at', label: 'En yeni' },
  { value: 'created_at', label: 'En eski' },
  { value: 'title', label: 'İsme göre A–Z' },
]

async function loadŞablons() {
  try {
    templates.value = await api.value.templates()
  } catch {
    templates.value = []
  }
}

function openCreate() {
  createModal.value = { open: true }
}

function openRename(doc) {
  renameModal.value = { open: true, document: doc }
}

function onRenamed(doc) {
  ui.toast(`Belge “${doc.title}” olarak yeniden adlandırıldı.`, 'success')
  list.load()
}

function onCreated(doc) {
  ui.toast(`${noun.value === 'CV' ? 'CV' : 'Portfolyo'} “${doc.title}” oluşturuldu.`, 'success')
  list.load()
}

async function duplicate(doc) {
  busyId.value = doc.id
  try {
    const copy = await api.value.duplicate(doc.id)
    ui.toast(`“${copy.title}” kopyası oluşturuldu.`, 'success')
    list.load()
  } catch (error) {
    ui.toast(`Kopyalanamadı: ${error.message}`, 'danger', 0)
  } finally {
    busyId.value = null
  }
}

async function remove(doc) {
  const confirmed = await ui.confirm({
    title: `“${doc.title}” silinsin mi?`,
    message: isCv.value
      ? 'Bu CV çöp kutusuna taşınacak. Daha sonra geri yükleyebilir veya kalıcı olarak silebilirsiniz.'
      : `Bu ${noun.value} ve kayıtlı içeriği kalıcı olarak silinecek. Bu işlem geri alınamaz.`,
    confirmText: isCv.value ? 'Çöp kutusuna taşı' : 'Kalıcı olarak sil',
  })
  if (!confirmed) return
  busyId.value = doc.id
  try {
    await api.value.remove(doc.id)
    ui.toast(`“${doc.title}” silindi.`, 'success')
    if (list.items.value.length === 1 && list.query.page > 1) list.query.page -= 1
    else list.load()
  } catch (error) {
    ui.toast(`Silinemedi: ${error.message}`, 'danger', 0)
  } finally {
    busyId.value = null
  }
}

onMounted(() => {
  loadŞablons()
  list.load()
})
</script>

<template>
  <div>
    <section class="page-header">
      <div>
        <h2 class="page-title">{{ isCv ? 'CV’lerim' : 'Portfolyolarım' }}</h2>
        <p class="text-secondary mb-0">
          {{ isCv ? 'Her CV ayrı bir belgedir. İçeriğinizi kaybetmeden istediğiniz zaman şablon değiştirin.' : 'Portfolyolarınızı CV’lerinizden ayrı yönetin ve çalışmalarınızı sergileyin.' }}
        </p>
      </div>
      <div class="d-flex gap-2"><RouterLink v-if="isCv" to="/cvs/trash" class="btn btn-outline-secondary"><i class="bi bi-trash3 me-1"></i>Çöp Kutusu</RouterLink><button type="button" class="btn btn-primary" @click="openCreate">
        <i class="bi bi-plus-lg me-1" aria-hidden="true"></i>Yeni {{ noun }}
      </button></div>
    </section>

    <div class="card">
      <div class="card-body">
        <div class="row g-2 align-items-end mb-3 list-toolbar">
          <div class="col-md-5">
            <label for="doc-search" class="form-label small mb-1">İsme göre ara</label>
            <input id="doc-search" v-model="list.query.search" type="search" class="form-control" placeholder="Belgelerde ara…" />
          </div>
          <div class="col-6 col-md-3">
            <label for="doc-template-filter" class="form-label small mb-1">Şablon</label>
            <select id="doc-template-filter" v-model="list.query.template" class="form-select">
              <option value="">Tüm şablonlar</option>
              <option v-for="t in templates" :key="t.id" :value="t.id">{{ t.name }}</option>
            </select>
          </div>
          <div class="col-6 col-md-4">
            <label for="doc-sort" class="form-label small mb-1">Sıralama</label>
            <select id="doc-sort" v-model="list.query.ordering" class="form-select">
              <option v-for="option in ORDERING" :key="option.value" :value="option.value">{{ option.label }}</option>
            </select>
          </div>
        </div>

        <div v-if="list.error.value" class="alert alert-danger d-flex justify-content-between align-items-center" role="alert">
          <span>Belgeler yüklenemedi: {{ list.error.value }}</span>
          <button type="button" class="btn btn-sm btn-outline-danger" @click="list.load">Tekrar dene</button>
        </div>

        <div v-if="list.loading.value && list.items.value.length === 0" class="py-5 text-center text-secondary">
          <span class="spinner-border spinner-border-sm me-2"></span>{{ noun }}ler yükleniyor…
        </div>

        <EmptyState
          v-else-if="!list.loading.value && list.count.value === 0 && !list.query.search && !list.query.template"
          :icon="isCv ? 'bi-file-earmark-person' : 'bi-window-sidebar'"
          :title="`Henüz ${noun} belgeniz yok`"
          :description="`İlk belgenizi oluşturarak düzenlemeye başlayın. Daha sonra yeniden adlandırabilir, kopyalayabilir veya silebilirsiniz.`"
        >
          <button type="button" class="btn btn-primary" @click="openCreate">Yeni {{ noun }}</button>
        </EmptyState>

        <EmptyState
          v-else-if="!list.loading.value && list.count.value === 0"
          icon="bi-search"
          title="Sonuç bulunamadı"
          description="Farklı bir arama yapın veya şablon filtresini temizleyin."
        >
          <button type="button" class="btn btn-outline-secondary" @click="list.query.search = ''; list.query.template = ''">Filtreleri temizle</button>
        </EmptyState>

        <div v-else class="table-responsive">
          <table class="table align-middle doc-table mb-0">
            <caption class="visually-hidden">{{ isCv ? 'CVs' : 'Portfolios' }}</caption>
            <thead>
              <tr>
                <th scope="col">Belge adı</th>
                <th scope="col" class="d-none d-md-table-cell">Şablon</th>
                <th scope="col" class="d-none d-lg-table-cell">Oluşturulma</th>
                <th scope="col">Son düzenleme</th>
                <th scope="col" class="text-end"><span class="visually-hidden">İşlemler</span></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="doc in list.items.value" :key="doc.id">
                <td>
                  <RouterLink :to="`${detailBase}/${doc.id}`" class="fw-semibold">{{ doc.title }}</RouterLink>
                  <div class="small text-secondary d-md-none">{{ templates.find((t) => t.id === doc.template)?.name || doc.template }}</div>
                </td>
                <td class="d-none d-md-table-cell">{{ templates.find((t) => t.id === doc.template)?.name || doc.template }}</td>
                <td class="d-none d-lg-table-cell small">{{ formatDateTime(doc.created_at) }}</td>
                <td class="small" :title="formatDateTime(doc.updated_at)">{{ timeAgo(doc.updated_at) }}</td>
                <td class="text-end text-nowrap">
                  <div class="btn-group btn-group-sm">
                    <RouterLink :to="`${detailBase}/${doc.id}`" class="btn btn-outline-secondary" :aria-label="`“${doc.title}” belgesini aç`" title="Aç">
                      <i class="bi bi-pencil-square" aria-hidden="true"></i><span class="d-none d-xl-inline ms-1">Aç</span>
                    </RouterLink>
                    <button type="button" class="btn btn-outline-secondary" :aria-label="`“${doc.title}” belgesini yeniden adlandır`" title="Yeniden adlandır" @click="openRename(doc)">
                      <i class="bi bi-input-cursor-text" aria-hidden="true"></i>
                    </button>
                    <button type="button" class="btn btn-outline-secondary" :disabled="busyId === doc.id" :aria-label="`“${doc.title}” belgesini kopyala`" title="Kopyala" @click="duplicate(doc)">
                      <i class="bi bi-files" aria-hidden="true"></i>
                    </button>
                    <button type="button" class="btn btn-outline-danger" :disabled="busyId === doc.id" :aria-label="`“${doc.title}” belgesini sil`" title="Sil" @click="remove(doc)">
                      <i class="bi bi-trash3" aria-hidden="true"></i>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <nav v-if="list.count.value > 0" class="d-flex justify-content-between align-items-center mt-3" aria-label="Pagination">
          <span class="small text-secondary">{{ list.count.value }} {{ list.count.value === 1 ? noun : noun + 's' }}</span>
          <div class="btn-group btn-group-sm">
            <button type="button" class="btn btn-outline-secondary" :disabled="!list.hasPrev.value" @click="list.query.page -= 1">Önceki</button>
            <button type="button" class="btn btn-outline-secondary" disabled>Sayfa {{ list.query.page }} / {{ list.totalPages.value }}</button>
            <button type="button" class="btn btn-outline-secondary" :disabled="!list.hasNext.value" @click="list.query.page += 1">Sonraki</button>
          </div>
        </nav>
      </div>
    </div>

    <DocumentFormModal :open="createModal.open" :kind="kind" :templates="templates" @saved="onCreated" @close="createModal.open = false" />
    <DocumentFormModal
      :open="renameModal.open"
      :kind="kind"
      :document="renameModal.document"
      @saved="onRenamed"
      @close="renameModal.open = false"
    />
  </div>
</template>
