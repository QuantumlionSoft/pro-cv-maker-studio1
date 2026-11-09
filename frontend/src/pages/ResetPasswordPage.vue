<script setup>
import { computed, ref } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { apiRequest } from '@/services/api'
import { fieldError } from '@/utils/errors'

const route = useRoute()
const uid = computed(() => (typeof route.query.uid === 'string' ? route.query.uid : ''))
const token = computed(() => (typeof route.query.token === 'string' ? route.query.token : ''))
const password = ref('')
const confirm = ref('')
const submitting = ref(false)
const done = ref(false)
const errorMessage = ref('')
const fields = ref({})

async function submit() {
  submitting.value = true
  errorMessage.value = ''
  fields.value = {}
  try {
    await apiRequest('POST', '/auth/password-reset/confirm/', {
      body: { uid: uid.value, token: token.value, new_password: password.value, new_password_confirm: confirm.value },
    })
    done.value = true
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
      <h1 class="h4 mb-1">Yeni şifrenizi belirleyin</h1>
      <template v-if="done">
        <div class="alert alert-success mt-3" role="status">Şifreniz başarıyla yenilendi.</div>
        <RouterLink :to="{ name: 'login' }" class="btn btn-primary w-100">Giriş yap</RouterLink>
      </template>
      <template v-else-if="!uid || !token">
        <div class="alert alert-warning mt-3" role="alert">Bu bağlantı eksik veya geçersiz. Yeni bir sıfırlama bağlantısı isteyin.</div>
        <RouterLink :to="{ name: 'forgot-password' }" class="btn btn-outline-primary w-100">Yeni bağlantı iste</RouterLink>
      </template>
      <template v-else>
        <p class="text-secondary mb-4">En az 10 karakter kullanın ve yaygın şifrelerden kaçının.</p>
        <div v-if="errorMessage" class="alert alert-danger" role="alert">{{ errorMessage }}</div>
        <form novalidate @submit.prevent="submit">
          <div class="mb-3">
            <label class="form-label" for="reset-password">Yeni şifre</label>
            <input id="reset-password" v-model="password" type="password" class="form-control" autocomplete="new-password" required :class="{ 'is-invalid': fieldError(fields, 'new_password') }" />
            <div v-if="fieldError(fields, 'new_password')" class="invalid-feedback">{{ fieldError(fields, 'new_password') }}</div>
          </div>
          <div class="mb-3">
            <label class="form-label" for="reset-confirm">Yeni şifre tekrarı</label>
            <input id="reset-confirm" v-model="confirm" type="password" class="form-control" autocomplete="new-password" required :class="{ 'is-invalid': fieldError(fields, 'new_password_confirm') }" />
            <div v-if="fieldError(fields, 'new_password_confirm')" class="invalid-feedback">{{ fieldError(fields, 'new_password_confirm') }}</div>
          </div>
          <button type="submit" class="btn btn-primary w-100" :disabled="submitting">Yeni şifreyi kaydet</button>
        </form>
      </template>
    </div>
  </div>
</template>
