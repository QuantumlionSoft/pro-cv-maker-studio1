import { defineStore } from 'pinia'
import { apiRequest, ApiError } from '@/services/api'

/** Session state. `status` is 'unknown' until the first /auth/me check completes. */
export const useAuthStore = defineStore('auth', {
  state: () => ({ user: null, status: 'unknown' }),
  getters: {
    isAuthenticated: (state) => state.status === 'authenticated',
    displayName: (state) => {
      if (!state.user) return ''
      const full = [state.user.first_name, state.user.last_name].filter(Boolean).join(' ')
      return full || state.user.username
    },
  },
  actions: {
    setUser(user) {
      this.user = user
      this.status = 'authenticated'
    },
    async fetchCurrentUser() {
      try {
        this.setUser(await apiRequest('GET', '/auth/me/'))
      } catch (error) {
        if (error instanceof ApiError && error.code === 'not_authenticated') {
          this.user = null
          this.status = 'anonymous'
          return
        }
        throw error // network/server problems are shown to the user, not treated as logged out
      }
    },
    async login(identifier, password) {
      this.setUser(await apiRequest('POST', '/auth/login/', { body: { identifier, password } }))
    },
    async register(payload) {
      this.setUser(await apiRequest('POST', '/auth/register/', { body: payload }))
    },
    async logout() {
      try {
        await apiRequest('POST', '/auth/logout/')
      } finally {
        this.user = null
        this.status = 'anonymous'
      }
    },
  },
})
