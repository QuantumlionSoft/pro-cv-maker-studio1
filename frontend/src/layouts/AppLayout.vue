<script setup>
import { ref, watch } from 'vue'
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
watch(sidebarCollapsed, (value) => localStorage.setItem(SIDEBAR_KEY, value ? 'collapsed' : 'expanded'))
watch(() => route.fullPath, () => {
  mobileNavOpen.value = false
})

// Items with `slug` link to a "coming soon" page that explains the delivery phase.
const navGroups = [
  {
    label: 'Workspace',
    items: [
      { to: '/dashboard', label: 'Dashboard', icon: 'bi-speedometer2' },
      { to: '/cvs', label: 'My CVs', icon: 'bi-file-earmark-person' },
      { to: '/portfolios', label: 'My Portfolios', icon: 'bi-window-sidebar' },
    ],
  },
  {
    label: 'Library',
    items: [
      { slug: 'projects', label: 'Projects', icon: 'bi-kanban', phase: 3 },
      { slug: 'certificates', label: 'Certificates', icon: 'bi-award', phase: 3 },
      { to: '/templates', label: 'Templates', icon: 'bi-palette' },
      { slug: 'qr-codes', label: 'QR Codes', icon: 'bi-qr-code', phase: 3 },
      { slug: 'media', label: 'Media Library', icon: 'bi-images', phase: 3 },
    ],
  },
  {
    label: 'Account',
    items: [
      { slug: 'exports', label: 'Exports', icon: 'bi-download', phase: 5 },
      { to: '/account', label: 'Account Settings', icon: 'bi-person-gear' },
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
    ui.toast(error.message || 'Sign-out failed. Please try again.', 'danger')
    return
  }
  ui.toast('You have signed out.', 'info')
  router.push({ name: 'login' })
}
</script>

<template>
  <div class="app-shell" :class="{ 'sidebar-collapsed': sidebarCollapsed, 'mobile-nav-open': mobileNavOpen }">
    <a href="#main-content" class="skip-link">Skip to content</a>

    <aside class="app-sidebar" aria-label="Main navigation">
      <RouterLink :to="{ name: 'dashboard' }" class="brand-link brand-link--sidebar">
        <span class="brand-mark" aria-hidden="true"><i class="bi bi-file-earmark-richtext"></i></span>
        <span class="brand-name">Pro CV Maker Studio</span>
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

      <div class="sidebar-footer">
        <button type="button" class="nav-link nav-toggle" :aria-expanded="!sidebarCollapsed" @click="toggleNav">
          <i :class="['bi', sidebarCollapsed ? 'bi-layout-sidebar' : 'bi-layout-sidebar-inset']" aria-hidden="true"></i>
          <span class="nav-label">{{ sidebarCollapsed ? 'Expand' : 'Collapse' }} sidebar</span>
        </button>
      </div>
    </aside>

    <div class="mobile-backdrop" @click="mobileNavOpen = false"></div>

    <div class="app-main">
      <header class="app-topbar">
        <button type="button" class="btn btn-light btn-icon" aria-label="Toggle navigation" @click="toggleNav">
          <i class="bi bi-list" aria-hidden="true"></i>
        </button>
        <h1 class="topbar-title">{{ route.meta.title }}</h1>
        <div class="ms-auto d-flex align-items-center gap-2">
          <span class="topbar-user d-none d-md-inline">{{ auth.displayName }}</span>
          <button type="button" class="btn btn-outline-secondary btn-sm" @click="signOut">
            <i class="bi bi-box-arrow-right me-1" aria-hidden="true"></i>Sign out
          </button>
        </div>
      </header>

      <main id="main-content" class="app-content">
        <RouterView :key="route.path" />
      </main>
    </div>
  </div>
</template>
