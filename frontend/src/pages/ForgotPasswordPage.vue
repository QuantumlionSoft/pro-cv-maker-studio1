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
      <h1 class="h4 mb-1">Şifrenizi sıfırlayın</h1>
      <template v-if="!sent">
        <p class="text-secondary mb-4">Hesabınıza bağlı e-posta adresini girin; size sıfırlama bağlantısı gönderelim.</p>
        <div v-if="errorMessage" class="alert alert-danger" role="alert">{{ errorMessage }}</div>
        <form novalidate @submit.prevent="submit">
          <label class="form-label" for="forgot-email">E-posta</label>
          <input id="forgot-email" v-model="email" type="email" class="form-control" autocomplete="email" required :class="{ 'is-invalid': fieldError(fields, 'email') }" />
          <div v-if="fieldError(fields, 'email')" class="invalid-feedback">{{ fieldError(fields, 'email') }}</div>
          <button type="submit" class="btn btn-primary w-100 mt-4" :disabled="submitting">Sıfırlama bağlantısı gönder</button>
        </form>
      </template>
      <template v-else>
        <div class="alert alert-success" role="status">
          Bu e-postaya ait bir hesap varsa sıfırlama bağlantısı gönderildi.
        </div>
        <p class="small text-secondary">
          Yerel geliştirme: Bağlantı backend terminaline yazdırılır. Bağlantıyı açıp yeni şifrenizi belirledikten sonra giriş yapabilirsiniz.
        </p>
      </template>
      <p class="text-center small mt-4 mb-0"><RouterLink :to="{ name: 'login' }">Giriş ekranına dön</RouterLink></p>
    </div>
  </div>
</template>
