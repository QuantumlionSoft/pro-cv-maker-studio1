<script setup>
import { computed, ref, watch } from 'vue'
import { RouterLink, RouterView, useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useUiStore } from '@/stores/ui'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const ui = useUiStore()

const SIDEBAR_KEY = 'pcms:sidebar'
const sidebarCollapsed = ref(localStorage.getItem(SIDEBAR_KEY) === 'collapsed')
const mobileNavOpen = ref(false)
const initials = computed(() => String(auth.displayName || 'K').trim().split(/\s+/).slice(0, 2).map((part) => part[0]).join('').toUpperCase())
watch(sidebarCollapsed, (value) => localStorage.setItem(SIDEBAR_KEY, value ? 'collapsed' : 'expanded'))
watch(() => route.fullPath, () => {
  mobileNavOpen.value = false
})

// Items with `slug` link to a "coming soon" page that explains the delivery phase.
const navGroups = [
  {
    label: 'Çalışma alanı',
    items: [
      { to: '/dashboard', label: 'Genel Bakış', icon: 'bi-grid-1x2' },
      { to: '/cvs', label: 'CV’lerim', icon: 'bi-file-earmark-person' },
      { to: '/portfolios', label: 'Portfolyolarım', icon: 'bi-window-sidebar' },
    ],
  },
  {
    label: 'Kütüphane',
    items: [
      { slug: 'projects', label: 'Projeler', icon: 'bi-kanban', phase: 3 },
      { slug: 'certificates', label: 'Sertifikalar', icon: 'bi-award', phase: 3 },
      { to: '/templates', label: 'Şablon Galerisi', icon: 'bi-palette' },
      { slug: 'qr-codes', label: 'QR Kodları', icon: 'bi-qr-code', phase: 3 },
      { slug: 'media', label: 'Medya Kütüphanesi', icon: 'bi-images', phase: 3 },
    ],
  },
  {
    label: 'Hesap',
    items: [
      { slug: 'exports', label: 'Dışa Aktarımlar', icon: 'bi-download', phase: 5 },
      { to: '/account', label: 'Hesap Ayarları', icon: 'bi-person-gear' },
    ],
  },
]

function itemTarget(item) {
  return item.to ?? { name: 'coming-soon', params: { feature: item.slug } }
}

function toggleNav() {
  if (window.matchMedia('(max-width: 991.98px)').matches) {
    mobileNavOpen.value = !mobileNavOpen.value
  } else {
    sidebarCollapsed.value = !sidebarCollapsed.value
  }
}

async function signOut() {
  try {
    await auth.logout()
  } catch (error) {
    ui.toast(error.message || 'Çıkış yapılamadı. Lütfen tekrar deneyin.', 'danger')
    return
  }
  ui.toast('Güvenli şekilde çıkış yaptınız.', 'info')
  router.push({ name: 'login' })
}
</script>

<template>
  <div class="app-shell" :class="{ 'sidebar-collapsed': sidebarCollapsed, 'mobile-nav-open': mobileNavOpen }">
    <a href="#main-content" class="skip-link">İçeriğe geç</a>

    <aside class="app-sidebar" aria-label="Ana menü">
      <RouterLink :to="{ name: 'dashboard' }" class="brand-link brand-link--sidebar">
        <span class="brand-mark" aria-hidden="true"><i class="bi bi-file-earmark-richtext"></i></span>
        <span class="brand-name"><strong>Pro CV</strong><small>MAKER STUDIO</small></span>
      </RouterLink>

      <nav class="sidebar-nav">
        <div v-for="group in navGroups" :key="group.label" class="nav-group">
          <div class="nav-group-label">{{ group.label }}</div>
          <RouterLink
            v-for="item in group.items"
            :key="item.label"
            :to="itemTarget(item)"
            class="nav-link"
            active-class="active"
            :title="item.label"
          >
            <i :class="['bi', item.icon]" aria-hidden="true"></i>
            <span class="nav-label">{{ item.label }}</span>
            <span v-if="item.phase" class="phase-badge" :aria-label="`Planned for phase ${item.phase}`">P{{ item.phase }}</span>
          </RouterLink>
        </div>
      </nav>

      <RouterLink to="/templates" class="sidebar-promo">
        <span class="sidebar-promo-icon"><i class="bi bi-stars"></i></span>
        <span><strong>10 profesyonel şablon</strong><small>Yeni görünümleri keşfedin <i class="bi bi-arrow-right"></i></small></span>
      </RouterLink>

      <div class="sidebar-footer">
        <button type="button" class="nav-link nav-toggle" :aria-expanded="!sidebarCollapsed" @click="toggleNav">
          <i :class="['bi', sidebarCollapsed ? 'bi-layout-sidebar' : 'bi-layout-sidebar-inset']" aria-hidden="true"></i>
          <span class="nav-label">Menüyü {{ sidebarCollapsed ? 'genişlet' : 'daralt' }}</span>
        </button>
      </div>
    </aside>

    <div class="mobile-backdrop" @click="mobileNavOpen = false"></div>

    <div class="app-main">
      <header class="app-topbar">
        <button type="button" class="btn btn-light btn-icon" aria-label="Menüyü aç veya kapat" @click="toggleNav">
          <i class="bi bi-list" aria-hidden="true"></i>
        </button>
        <div class="topbar-heading"><h1 class="topbar-title">{{ route.meta.title }}</h1><span class="topbar-breadcrumb">Çalışma alanı <i class="bi bi-chevron-right"></i> {{ route.meta.title }}</span></div>
        <div class="ms-auto d-flex align-items-center gap-2 gap-md-3">
          <span class="topbar-user d-none d-md-flex"><span class="topbar-avatar">{{ initials }}</span><span><strong>{{ auth.displayName }}</strong><small>Kişisel hesap</small></span></span>
          <button type="button" class="btn btn-outline-secondary btn-sm topbar-signout" title="Çıkış yap" @click="signOut">
            <i class="bi bi-box-arrow-right" aria-hidden="true"></i><span class="d-none d-lg-inline ms-1">Çıkış yap</span>
          </button>
        </div>
      </header>

      <main id="main-content" class="app-content">
        <RouterView :key="route.path" />
      </main>
    </div>
  </div>
</template>
