<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import CvTemplateLivePreview from '@/components/cv/CvTemplateLivePreview.vue'
import DocumentFormModal from '@/components/dashboard/DocumentFormModal.vue'
import { cvApi, portfolioApi } from '@/services/documents'
import { useUiStore } from '@/stores/ui'

const router = useRouter()
const ui = useUiStore()
const cvTemplates = ref([])
const portfolioTemplates = ref([])
const loading = ref(true)
const error = ref('')
const createOpen = ref(false)
const selectedTemplate = ref('')

function openCreate(templateId = '') {
  selectedTemplate.value = templateId
  createOpen.value = true
}
const ATS_TEMPLATES = ['professional', 'minimal', 'corporate', 'academic', 'compact']
const CATEGORIES = {
  modern: 'Kurumsal', professional: 'Kurumsal', minimal: 'Kurumsal', executive: 'Kurumsal', corporate: 'Kurumsal',
  creative: 'Yaratıcı', developer: 'Teknik', academic: 'Akademik', elegant: 'Yaratıcı', compact: 'Kompakt',
}
const category = ref('')
const onlyFavorites = ref(false)
const favorites = ref([])
try { favorites.value = JSON.parse(localStorage.getItem('pcms:template-favorites') || '[]') } catch { favorites.value = [] }
const filteredTemplates = computed(() => cvTemplates.value.filter((item) => (!category.value || CATEGORIES[item.id] === category.value) && (!onlyFavorites.value || favorites.value.includes(item.id))))
function toggleFavorite(id) {
  favorites.value = favorites.value.includes(id) ? favorites.value.filter((item) => item !== id) : [...favorites.value, id]
  localStorage.setItem('pcms:template-favorites', JSON.stringify(favorites.value))
}

onMounted(async () => {
  try {
    ;[cvTemplates.value, portfolioTemplates.value] = await Promise.all([cvApi.templates(), portfolioApi.templates()])
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
})

function onCreated(doc) {
  ui.toast(`“${doc.title}” oluşturuldu.`, 'success')
  router.push(`/cvs/${doc.id}`)
}
</script>

<template>
  <div>
    <section class="page-header">
      <div class="gallery-intro"><p class="eyebrow mb-1">Tasarım kütüphanesi</p><h2 class="page-title">Şablon Galerisi</h2><p class="text-secondary mb-0">Her düzen aynı içerikle çalışır. Dilediğiniz zaman şablon değiştirin; bilgileriniz ve tasarım tercihleriniz korunsun.</p></div>
      <button type="button" class="btn btn-primary" @click="openCreate()"><i class="bi bi-plus-lg me-1"></i>Yeni CV oluştur</button>
    </section>
    <div v-if="error" class="alert alert-danger d-flex justify-content-between align-items-center" role="alert"><span>Şablonlar yüklenemedi: {{ error }}</span><button class="btn btn-sm btn-outline-danger" @click="$router.go(0)">Tekrar dene</button></div>
    <div v-if="loading" class="py-5 text-center text-secondary"><span class="spinner-border spinner-border-sm me-2"></span>Şablonlar hazırlanıyor…</div>
    <template v-else>
      <div class="gallery-section-title"><i class="bi bi-file-earmark-person text-primary"></i><h3>CV şablonları</h3><span>{{ cvTemplates.length }} kullanılabilir tasarım</span></div>
      <div class="gallery-filters"><div class="gallery-category-list" role="group" aria-label="Şablon kategorisi"><button v-for="item in ['', 'Kurumsal', 'Yaratıcı', 'Teknik', 'Akademik', 'Kompakt']" :key="item" type="button" class="btn btn-sm" :class="category === item ? 'btn-primary' : 'btn-outline-secondary'" @click="category = item">{{ item || 'Tümü' }}</button></div><button type="button" class="btn btn-sm" :class="onlyFavorites ? 'btn-primary' : 'btn-outline-secondary'" @click="onlyFavorites = !onlyFavorites"><i class="bi bi-heart-fill me-1"></i>Favoriler <span>{{ favorites.length }}</span></button></div>
      <div v-if="!filteredTemplates.length" class="alert alert-light border text-center py-4"><i class="bi bi-heart me-2"></i>Bu filtreye uygun şablon bulunamadı.<button type="button" class="btn btn-sm btn-link" @click="category = ''; onlyFavorites = false">Filtreleri temizle</button></div>
      <div class="row g-4 mb-5">
        <div v-for="t in filteredTemplates" :key="t.id" class="col-sm-6 col-xl-4">
          <article class="card h-100 template-card">
            <div class="template-card-top"><span class="template-badge"><i class="bi bi-check-circle-fill text-success"></i>Kullanılabilir</span><span v-if="ATS_TEMPLATES.includes(t.id)" class="template-badge template-badge--ats"><i class="bi bi-shield-check"></i>ATS dostu</span></div>
            <CvTemplateLivePreview :template="t.id" />
            <div class="card-body"><div class="d-flex align-items-center justify-content-between gap-2"><div><span class="gallery-category">{{ CATEGORIES[t.id] }}</span><h4 class="h6 mb-1">{{ t.name }}</h4></div><button type="button" class="gallery-favorite" :class="{ 'is-favorite': favorites.includes(t.id) }" :aria-label="`${t.name} şablonunu favorilere ${favorites.includes(t.id) ? 'ekleme' : 'ekle'}`" @click="toggleFavorite(t.id)"><i :class="['bi', favorites.includes(t.id) ? 'bi-heart-fill' : 'bi-heart']"></i></button></div><p class="small text-secondary">{{ t.description }}</p><button type="button" class="btn btn-sm btn-outline-primary w-100" @click="openCreate(t.id)">Bu şablonla başla <i class="bi bi-arrow-right ms-1"></i></button></div>
          </article>
        </div>
      </div>

      <div class="gallery-section-title"><i class="bi bi-window-sidebar text-primary"></i><h3>Portfolyo şablonları</h3><span>{{ portfolioTemplates.length }} tema</span></div>
      <div class="row g-3">
        <div v-for="(t, index) in portfolioTemplates" :key="t.id" class="col-md-6 col-xl-4"><div class="card h-100"><div class="card-body d-flex gap-3"><span class="stat-icon flex-shrink-0"><i :class="['bi', index % 2 ? 'bi-window-desktop' : 'bi-columns-gap']"></i></span><div><h4 class="h6 mb-1">{{ t.name }}</h4><p class="small text-secondary mb-0">{{ t.description }}</p></div></div></div></div>
      </div>
      <div class="alert alert-info border-0 mt-4 mb-0 small"><i class="bi bi-info-circle me-2"></i>CV şablonlarının tamamı canlı editörde ve PDF çıktısında kullanılabilir. Portfolyo editörü geliştirilmeye devam ediyor.</div>
    </template>
    <DocumentFormModal :open="createOpen" kind="cv" :templates="cvTemplates" :initial-template="selectedTemplate" @saved="onCreated" @close="createOpen = false" />
  </div>
</template>

<style scoped>
.gallery-filters { display: flex; justify-content: space-between; align-items: center; gap: 1rem; margin: 0 0 1.25rem; padding: .65rem; border: 1px solid #e6e9f0; border-radius: 11px; background: #fff; }
.gallery-category-list { display: flex; flex-wrap: wrap; gap: .35rem; }
.gallery-filters .btn { font-size: .68rem; }
.gallery-favorite { width: 32px; height: 32px; display: grid; place-items: center; flex: 0 0 auto; color: #8792a5; border: 1px solid #e3e7ee; border-radius: 9px; background: #fff; }
.gallery-favorite:hover, .gallery-favorite.is-favorite { color: #d63864; border-color: #f0c4d0; background: #fff5f7; }
.gallery-category { display: block; margin-bottom: .2rem; color: #7b8496; font-size: .56rem; font-weight: 700; letter-spacing: .06em; text-transform: uppercase; }
@media (max-width: 767.98px) { .gallery-filters { align-items: flex-start; flex-direction: column; } }
</style>
