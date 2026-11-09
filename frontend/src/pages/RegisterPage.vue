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

const form = ref({ username: '', email: '', first_name: '', last_name: '', password: '', password_confirm: '' })
const submitting = ref(false)
const errorMessage = ref('')
const fields = ref({})

async function submit() {
  submitting.value = true
  errorMessage.value = ''
  fields.value = {}
  try {
    await auth.register({ ...form.value, username: form.value.username.trim(), email: form.value.email.trim() })
    ui.toast('Hesabınız oluşturuldu. Hoş geldiniz!', 'success')
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
      <h1 class="h4 mb-1">Hesabınızı oluşturun</h1>
      <p class="text-secondary mb-4">Belgeleriniz yalnızca hesabınıza özeldir.</p>

      <div v-if="errorMessage" class="alert alert-danger" role="alert">{{ errorMessage }}</div>

      <form novalidate @submit.prevent="submit">
        <div class="row g-3">
          <div class="col-sm-6">
            <label class="form-label" for="reg-first">Ad</label>
            <input id="reg-first" v-model="form.first_name" class="form-control" autocomplete="given-name" />
          </div>
          <div class="col-sm-6">
            <label class="form-label" for="reg-last">Soyad</label>
            <input id="reg-last" v-model="form.last_name" class="form-control" autocomplete="family-name" />
          </div>
          <div class="col-12">
            <label class="form-label" for="reg-username">Kullanıcı adı</label>
            <input id="reg-username" v-model="form.username" class="form-control" autocomplete="username" required :class="{ 'is-invalid': fieldError(fields, 'username') }" aria-describedby="reg-username-help" />
            <div id="reg-username-help" class="form-text">Harf, rakam, nokta, tire veya alt çizgi. En az 3 karakter.</div>
            <div v-if="fieldError(fields, 'username')" class="invalid-feedback d-block">{{ fieldError(fields, 'username') }}</div>
          </div>
          <div class="col-12">
            <label class="form-label" for="reg-email">E-posta</label>
            <input id="reg-email" v-model="form.email" type="email" class="form-control" autocomplete="email" required :class="{ 'is-invalid': fieldError(fields, 'email') }" />
            <div v-if="fieldError(fields, 'email')" class="invalid-feedback">{{ fieldError(fields, 'email') }}</div>
          </div>
          <div class="col-12">
            <label class="form-label" for="reg-password">Şifre</label>
            <input id="reg-password" v-model="form.password" type="password" class="form-control" autocomplete="new-password" required :class="{ 'is-invalid': fieldError(fields, 'password') }" aria-describedby="reg-password-help" />
            <div id="reg-password-help" class="form-text">En az 10 karakter. Yaygın şifrelerden kaçının.</div>
            <div v-if="fieldError(fields, 'password')" class="invalid-feedback d-block">{{ fieldError(fields, 'password') }}</div>
          </div>
          <div class="col-12">
            <label class="form-label" for="reg-password-confirm">Şifre tekrarı</label>
            <input id="reg-password-confirm" v-model="form.password_confirm" type="password" class="form-control" autocomplete="new-password" required :class="{ 'is-invalid': fieldError(fields, 'password_confirm') }" />
            <div v-if="fieldError(fields, 'password_confirm')" class="invalid-feedback">{{ fieldError(fields, 'password_confirm') }}</div>
          </div>
        </div>
        <button type="submit" class="btn btn-primary w-100 mt-4" :disabled="submitting">
          <span v-if="submitting" class="spinner-border spinner-border-sm me-2" aria-hidden="true"></span>
          Create account
        </button>
      </form>

      <p class="text-center small mt-4 mb-0">
        Zaten hesabınız var mı? <RouterLink :to="{ name: 'login' }">Giriş yapın</RouterLink>
      </p>
    </div>
  </div>
</template>
