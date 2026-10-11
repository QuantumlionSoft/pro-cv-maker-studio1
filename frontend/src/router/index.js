import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  { path: '/', name: 'landing', component: () => import('@/pages/LandingPage.vue'), meta: { title: 'Pro CV Maker Studio' } },

  {
    path: '/',
    component: () => import('@/layouts/AuthLayout.vue'),
    meta: { guestOnly: true },
    children: [
      { path: 'login', name: 'login', component: () => import('@/pages/LoginPage.vue'), meta: { title: 'Sign in' } },
      { path: 'register', name: 'register', component: () => import('@/pages/RegisterPage.vue'), meta: { title: 'Create account' } },
      { path: 'forgot-password', name: 'forgot-password', component: () => import('@/pages/ForgotPasswordPage.vue'), meta: { title: 'Reset password' } },
      { path: 'reset-password', name: 'reset-password', component: () => import('@/pages/ResetPasswordPage.vue'), meta: { title: 'Choose a new password' } },
    ],
  },

  // The CV builder is a full-screen editor, so it sits outside AppLayout (still auth-protected).
  {
    path: '/cvs/:id',
    name: 'cv-detail',
    component: () => import('@/pages/CvBuilderPage.vue'),
    meta: { requiresAuth: true, title: 'CV', kind: 'cv' },
  },

  {
    path: '/',
    component: () => import('@/layouts/AppLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      { path: 'dashboard', name: 'dashboard', component: () => import('@/pages/DashboardPage.vue'), meta: { title: 'Dashboard' } },
      {
        path: 'cvs',
        name: 'cvs',
        component: () => import('@/pages/DocumentListPage.vue'),
        meta: { title: 'My CVs', kind: 'cv' },
      },
      {
        path: 'portfolios',
        name: 'portfolios',
        component: () => import('@/pages/DocumentListPage.vue'),
        meta: { title: 'My Portfolios', kind: 'portfolio' },
      },
      {
        path: 'portfolios/:id',
        name: 'portfolio-detail',
        component: () => import('@/pages/DocumentEditorPage.vue'),
        meta: { title: 'Portfolio', kind: 'portfolio' },
      },
      { path: 'templates', name: 'templates', component: () => import('@/pages/TemplatesPage.vue'), meta: { title: 'Templates' } },
      { path: 'account', name: 'account', component: () => import('@/pages/AccountPage.vue'), meta: { title: 'Account Settings' } },
      {
        path: 'coming-soon/:feature',
        name: 'coming-soon',
        component: () => import('@/pages/PlannedPage.vue'),
        meta: { title: 'Coming soon' },
      },
    ],
  },

  { path: '/:pathMatch(.*)*', name: 'not-found', component: () => import('@/pages/NotFoundPage.vue'), meta: { title: 'Page not found' } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior: () => ({ top: 0 }),
})

router.beforeEach(async (to) => {
  const auth = useAuthStore()
  if (auth.status === 'unknown') {
    try {
      await auth.fetchCurrentUser()
    } catch {
      // Server unreachable: keep the status unknown and let the page show the error.
    }
  }
  if (to.matched.some((record) => record.meta.requiresAuth) && !auth.isAuthenticated) {
    return { name: 'login', query: { next: to.fullPath } }
  }
  if (to.matched.some((record) => record.meta.guestOnly) && auth.isAuthenticated) {
    return { name: 'dashboard' }
  }
  return true
})

router.afterEach((to) => {
  document.title = to.meta.title ? `${to.meta.title} · Pro CV Maker Studio` : 'Pro CV Maker Studio'
})

export default router
