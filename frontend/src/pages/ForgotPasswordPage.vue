<script setup>
import { ref } from 'vue'
import { RouterLink } from 'vue-router'
import { apiRequest } from '@/services/api'
import { fieldError } from '@/utils/errors'

const email = ref('')
const submitting = ref(false)
const sent = ref(false)
const errorMessage = ref('')
const fields = ref({})

async function submit() {
  submitting.value = true
  errorMessage.value = ''
  fields.value = {}
  try {
    await apiRequest('POST', '/auth/password-reset/', { body: { email: email.value.trim() } })
    sent.value = true
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
      <h1 class="h4 mb-1">Reset your password</h1>
      <template v-if="!sent">
        <p class="text-secondary mb-4">Enter the email address on your account and we will send a reset link.</p>
        <div v-if="errorMessage" class="alert alert-danger" role="alert">{{ errorMessage }}</div>
        <form novalidate @submit.prevent="submit">
          <label class="form-label" for="forgot-email">Email</label>
          <input id="forgot-email" v-model="email" type="email" class="form-control" autocomplete="email" required :class="{ 'is-invalid': fieldError(fields, 'email') }" />
          <div v-if="fieldError(fields, 'email')" class="invalid-feedback">{{ fieldError(fields, 'email') }}</div>
          <button type="submit" class="btn btn-primary w-100 mt-4" :disabled="submitting">Send reset link</button>
        </form>
      </template>
      <template v-else>
        <div class="alert alert-success" role="status">
          If an account exists for that email, a reset link has been sent.
        </div>
        <p class="small text-secondary">
          Local development: the link is printed in the backend terminal (the console email backend). Open it, choose a new password, then sign in.
        </p>
      </template>
      <p class="text-center small mt-4 mb-0"><RouterLink :to="{ name: 'login' }">Back to sign in</RouterLink></p>
    </div>
  </div>
</template>
