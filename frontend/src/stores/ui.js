import { defineStore } from 'pinia'

let toastSeq = 0

/** Global UI state: toast notifications and the promise-based confirmation dialog. */
export const useUiStore = defineStore('ui', {
  state: () => ({ toasts: [], confirmRequest: null }),
  actions: {
    toast(message, variant = 'success', timeout = 4500) {
      const id = ++toastSeq
      this.toasts.push({ id, message, variant })
      if (timeout > 0) setTimeout(() => this.dismissToast(id), timeout)
      return id
    },
    dismissToast(id) {
      this.toasts = this.toasts.filter((t) => t.id !== id)
    },
    /** Resolves true when confirmed, false when cancelled. */
    confirm({ title, message, confirmText = 'Onayla', cancelText = 'Vazgeç', danger = true }) {
      return new Promise((resolve) => {
        if (this.confirmRequest) this.confirmRequest.resolve(false)
        this.confirmRequest = { title, message, confirmText, cancelText, danger, resolve }
      })
    },
    resolveConfirm(value) {
      const request = this.confirmRequest
      this.confirmRequest = null
      request?.resolve(value)
    },
  },
})
