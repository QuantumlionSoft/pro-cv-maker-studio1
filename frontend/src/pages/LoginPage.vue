<script setup>
import { ref } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useUiStore } from '@/stores/ui'
import { fieldError } from '@/utils/errors'

const auth = useAuthStore()
const ui = useUiStore()
const route = useRoute()
const router = useRouter()

const identifier = ref('')
const password = ref('')
const submitting = ref(false)
const errorMessage = ref('')
const fields = ref({})

async function submit() {
  submitting.value = true
  errorMessage.value = ''
  fields.value = {}
  try {
    await auth.login(identifier.value.trim(), password.value)
    ui.toast('Signed in.', 'success')
    const next = typeof route.query.next === 'string' && route.query.next.startsWith('/') ? route.query.next : '/dashboard'
    router.push(next)
  } catch (error) {
    errorMessage.value = error.message
    fields.value = error.fields || {}
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="auth-card card">
    <div class="card-body p-4 p-md-5">
      <h1 class="h4 mb-1">Sign in</h1>
      <p class="text-secondary mb-4">Welcome back. Pick up where you left off.</p>

      <div v-if="errorMessage" class="alert alert-danger" role="alert">{{ errorMessage }}</div>

      <form novalidate @submit.prevent="submit">
        <div class="mb-3">
          <label class="form-label" for="login-identifier">Username or email</label>
          <input
            id="login-identifier"
            v-model="identifier"
            type="text"
            autocomplete="username"
            required
            class="form-control"
            :class="{ 'is-invalid': fieldError(fields, 'identifier') }"
          />
          <div v-if="fieldError(fields, 'identifier')" class="invalid-feedback">{{ fieldError(fields, 'identifier') }}</div>
        </div>
        <div class="mb-2">
          <label class="form-label" for="login-password">Password</label>
          <input
            id="login-password"
            v-model="password"
            type="password"
            autocomplete="current-password"
            required
            class="form-control"
            :class="{ 'is-invalid': fieldError(fields, 'password') }"
          />
        </div>
        <div class="text-end mb-4">
          <RouterLink :to="{ name: 'forgot-password' }" class="small">Forgot password?</RouterLink>
        </div>
        <button type="submit" class="btn btn-primary w-100" :disabled="submitting">
          <span v-if="submitting" class="spinner-border spinner-border-sm me-2" aria-hidden="true"></span>
          Sign in
        </button>
      </form>

      <p class="text-center small mt-4 mb-0">
        New here? <RouterLink :to="{ name: 'register' }">Create an account</RouterLink>
      </p>
    </div>
  </div>
</template>
