<script setup>
import { computed, onMounted, ref } from 'vue'
import { dashboardApi } from '@/services/dashboard'
import { useAuthStore } from '@/stores/auth'
import { useUiStore } from '@/stores/ui'
import { fieldError } from '@/utils/errors'
import { formatDate } from '@/utils/format'

const MAX_PHOTO_MB = 5
const auth = useAuthStore()
const ui = useUiStore()

const profile = ref(null)
const loadError = ref('')
const form = ref({ first_name: '', last_name: '', email: '', bio: '' })
const profileErrors = ref({})
const profileMessage = ref('')
const savingProfile = ref(false)

const photoErrors = ref({})
const photoBusy = ref(false)
const photoVersion = ref(Date.now())
const photoBroken = ref(false)
const photoInput = ref(null)

const passwordForm = ref({ current_password: '', new_password: '', new_password_confirm: '' })
const passwordErrors = ref({})
const passwordMessage = ref('')
const savingPassword = ref(false)

const bioLength = computed(() => form.value.bio.length)
const photoUrl = computed(() => `/api/profile/photo/?v=${photoVersion.value}`)

function applyProfile(data) {
  profile.value = data
  auth.setUser(data)
  form.value = {
    first_name: data.first_name || '',
    last_name: data.last_name || '',
    email: data.email || '',
    bio: data.bio || '',
  }
  photoBroken.value = false
}

async function loadProfile() {
  try {
    applyProfile(await dashboardApi.profile())
    loadError.value = ''
  } catch (error) {
    loadError.value = error.message
  }
}

async function saveProfile() {
  savingProfile.value = true
  profileErrors.value = {}
  profileMessage.value = ''
  try {
    applyProfile(await dashboardApi.updateProfile({ ...form.value }))
    profileMessage.value = 'Profile saved.'
    ui.toast('Profile saved.', 'success')
  } catch (error) {
    profileErrors.value = error.fields || {}
    profileMessage.value = error.message
  } finally {
    savingProfile.value = false
  }
}

function clientPhotoCheck(file) {
  if (!file) return 'Choose an image first.'
  if (!/^image\/(jpeg|png|webp)$/.test(file.type)) return 'Use a JPG, PNG or WebP image.'
  if (file.size > MAX_PHOTO_MB * 1024 * 1024) return `The image must be ${MAX_PHOTO_MB} MB or smaller.`
  return ''
}

async function uploadPhoto(event) {
  const file = event.target.files?.[0]
  photoErrors.value = {}
  const problem = clientPhotoCheck(file)
  if (problem) {
    photoErrors.value = { photo: [problem] }
    event.target.value = ''
    return
  }
  const body = new FormData()
  body.append('photo', file)
  photoBusy.value = true
  try {
    applyProfile(await dashboardApi.updateProfile(body))
    photoVersion.value = Date.now()
    ui.toast('Profile photo updated.', 'success')
  } catch (error) {
    photoErrors.value = error.fields?.photo ? { photo: error.fields.photo } : { photo: [error.message] }
  } finally {
    photoBusy.value = false
    event.target.value = ''
  }
}

async function removePhoto() {
  const confirmed = await ui.confirm({
    title: 'Remove profile photo?',
    message: 'Your photo will be deleted from the server.',
    confirmText: 'Remove photo',
  })
  if (!confirmed) return
  photoBusy.value = true
  try {
    applyProfile(await dashboardApi.updateProfile({ clear_photo: true }))
    photoVersion.value = Date.now()
    ui.toast('Profile photo removed.', 'success')
  } catch (error) {
    photoErrors.value = { photo: [error.message] }
  } finally {
    photoBusy.value = false
  }
}

async function changePassword() {
  passwordErrors.value = {}
  passwordMessage.value = ''
  savingPassword.value = true
  try {
    await dashboardApi.changePassword({ ...passwordForm.value })
    passwordForm.value = { current_password: '', new_password: '', new_password_confirm: '' }
    ui.toast('Password changed.', 'success')
    passwordMessage.value = 'Your password has been changed.'
  } catch (error) {
    passwordErrors.value = error.fields || {}
    passwordMessage.value = error.message
  } finally {
    savingPassword.value = false
  }
}

onMounted(loadProfile)
</script>

<template>
  <div>
    <section class="page-header">
      <div>
        <h2 class="page-title">Account Settings</h2>
        <p class="text-secondary mb-0">Your profile, photo and password. Only you can see these.</p>
      </div>
    </section>

    <div v-if="loadError" class="alert alert-danger d-flex justify-content-between align-items-center" role="alert">
      <span>Could not load your profile: {{ loadError }}</span>
      <button type="button" class="btn btn-sm btn-outline-danger" @click="loadProfile">Try again</button>
    </div>

    <div class="row g-4">
      <div class="col-lg-4">
        <section class="card h-100">
          <div class="card-body">
            <h3 class="h6">Profile photo</h3>
            <div class="avatar-frame mb-3">
              <img v-if="profile?.has_photo && !photoBroken" :src="photoUrl" alt="Your profile photo" class="avatar-img" @error="photoBroken = true" />
              <span v-else class="avatar-initials" aria-label="No profile photo set">
                <i class="bi bi-person" aria-hidden="true"></i>
              </span>
            </div>
            <p class="small text-secondary">JPG, PNG or WebP, up to {{ MAX_PHOTO_MB }} MB.</p>
            <div v-if="photoErrors.photo" class="alert alert-danger py-2 small" role="alert">{{ photoErrors.photo[0] }}</div>
            <input
              ref="photoInput"
              type="file"
              class="visually-hidden"
              accept="image/jpeg,image/png,image/webp"
              aria-label="Choose profile photo"
              @change="uploadPhoto"
            />
            <div class="d-flex flex-wrap gap-2">
              <button type="button" class="btn btn-outline-primary btn-sm" :disabled="photoBusy" @click="photoInput.click()">
                <span v-if="photoBusy" class="spinner-border spinner-border-sm me-1"></span>
                {{ profile?.has_photo ? 'Replace photo' : 'Upload photo' }}
              </button>
              <button v-if="profile?.has_photo" type="button" class="btn btn-outline-danger btn-sm" :disabled="photoBusy" @click="removePhoto">Remove</button>
            </div>
          </div>
        </section>
      </div>

      <div class="col-lg-8">
        <section class="card mb-4">
          <div class="card-body">
            <h3 class="h6">Personal details</h3>
            <form novalidate @submit.prevent="saveProfile">
              <div class="row g-3">
                <div class="col-sm-6">
                  <label for="acc-first" class="form-label">First name</label>
                  <input id="acc-first" v-model="form.first_name" class="form-control" :class="{ 'is-invalid': fieldError(profileErrors, 'first_name') }" />
                </div>
                <div class="col-sm-6">
                  <label for="acc-last" class="form-label">Last name</label>
                  <input id="acc-last" v-model="form.last_name" class="form-control" :class="{ 'is-invalid': fieldError(profileErrors, 'last_name') }" />
                </div>
                <div class="col-12">
                  <label for="acc-email" class="form-label">Email</label>
                  <input id="acc-email" v-model="form.email" type="email" class="form-control" :class="{ 'is-invalid': fieldError(profileErrors, 'email') }" />
                  <div v-if="fieldError(profileErrors, 'email')" class="invalid-feedback">{{ fieldError(profileErrors, 'email') }}</div>
                </div>
                <div class="col-12">
                  <label for="acc-bio" class="form-label">Short bio <span class="text-secondary small">({{ bioLength }}/500)</span></label>
                  <textarea id="acc-bio" v-model="form.bio" rows="3" maxlength="500" class="form-control" :class="{ 'is-invalid': fieldError(profileErrors, 'bio') }"></textarea>
                  <div v-if="fieldError(profileErrors, 'bio')" class="invalid-feedback">{{ fieldError(profileErrors, 'bio') }}</div>
                </div>
              </div>
              <div class="d-flex align-items-center gap-3 mt-3">
                <button type="submit" class="btn btn-primary" :disabled="savingProfile || !profile">
                  <span v-if="savingProfile" class="spinner-border spinner-border-sm me-2"></span>Save profile
                </button>
                <span v-if="profileMessage && !Object.keys(profileErrors).length" class="small text-success" role="status">{{ profileMessage }}</span>
                <span v-else-if="profileMessage" class="small text-danger" role="alert">{{ profileMessage }}</span>
              </div>
            </form>
          </div>
        </section>

        <section class="card mb-4">
          <div class="card-body">
            <h3 class="h6">Account</h3>
            <dl class="row small mb-0">
              <dt class="col-sm-4 text-secondary">Username</dt><dd class="col-sm-8">{{ profile?.username }}</dd>
              <dt class="col-sm-4 text-secondary">Member since</dt><dd class="col-sm-8">{{ formatDate(profile?.date_joined) }}</dd>
            </dl>
          </div>
        </section>

        <section class="card">
          <div class="card-body">
            <h3 class="h6">Change password</h3>
            <form novalidate @submit.prevent="changePassword">
              <div class="mb-3">
                <label for="pw-current" class="form-label">Current password</label>
                <input id="pw-current" v-model="passwordForm.current_password" type="password" autocomplete="current-password" class="form-control" :class="{ 'is-invalid': fieldError(passwordErrors, 'current_password') }" />
                <div v-if="fieldError(passwordErrors, 'current_password')" class="invalid-feedback">{{ fieldError(passwordErrors, 'current_password') }}</div>
              </div>
              <div class="mb-3">
                <label for="pw-new" class="form-label">New password</label>
                <input id="pw-new" v-model="passwordForm.new_password" type="password" autocomplete="new-password" class="form-control" :class="{ 'is-invalid': fieldError(passwordErrors, 'new_password') }" />
                <div v-if="fieldError(passwordErrors, 'new_password')" class="invalid-feedback">{{ fieldError(passwordErrors, 'new_password') }}</div>
              </div>
              <div class="mb-3">
                <label for="pw-confirm" class="form-label">Confirm new password</label>
                <input id="pw-confirm" v-model="passwordForm.new_password_confirm" type="password" autocomplete="new-password" class="form-control" :class="{ 'is-invalid': fieldError(passwordErrors, 'new_password_confirm') }" />
                <div v-if="fieldError(passwordErrors, 'new_password_confirm')" class="invalid-feedback">{{ fieldError(passwordErrors, 'new_password_confirm') }}</div>
              </div>
              <button type="submit" class="btn btn-primary" :disabled="savingPassword">Change password</button>
              <p v-if="passwordMessage && Object.keys(passwordErrors).length === 0" class="small text-success mt-2 mb-0" role="status">{{ passwordMessage }}</p>
              <p v-else-if="passwordMessage" class="small text-danger mt-2 mb-0" role="alert">{{ passwordMessage }}</p>
            </form>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>
