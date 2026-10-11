<script setup>
import ImageField from './ImageField.vue'

defineProps({
  personal: { type: Object, required: true },
})
</script>

<template>
  <div>
    <h5 class="fw-bold mb-4">Kişisel Bilgiler</h5>

    <div class="mb-4 text-center">
      <ImageField v-model="personal.photoId" purpose="photo" label="Fotoğraf" input-id="personal-photo" round />
    </div>

    <div class="row g-2">
      <div class="col-md-4"><label class="form-label small fw-bold" for="p-first">Ad</label><input id="p-first" v-model="personal.firstName" type="text" class="form-control" maxlength="100"></div>
      <div class="col-md-4"><label class="form-label small fw-bold" for="p-middle">İkinci Ad</label><input id="p-middle" v-model="personal.middleName" type="text" class="form-control" maxlength="100"></div>
      <div class="col-md-4"><label class="form-label small fw-bold" for="p-last">Soyad</label><input id="p-last" v-model="personal.lastName" type="text" class="form-control" maxlength="100"></div>
    </div>

    <div class="mt-3"><label class="form-label small fw-bold" for="p-title">Meslek / Ünvan</label><input id="p-title" v-model="personal.title" type="text" class="form-control" maxlength="120"></div>
    <div class="mt-3"><label class="form-label small fw-bold" for="p-email">E-posta</label><input id="p-email" v-model="personal.email" type="email" class="form-control" maxlength="254"></div>
    <div class="mt-3"><label class="form-label small fw-bold" for="p-phone">Telefon</label><input id="p-phone" v-model="personal.phone" type="text" class="form-control" maxlength="40"></div>
    <div class="mt-3"><label class="form-label small fw-bold" for="p-location">Konum (Şehir, Ülke)</label><input id="p-location" v-model="personal.location" type="text" class="form-control" maxlength="120"></div>
    <div class="mt-3"><label class="form-label small fw-bold" for="p-website">Website</label><input id="p-website" v-model="personal.website" type="text" class="form-control" placeholder="Örn: www.site.com" maxlength="500"></div>
    <div class="mt-3"><label class="form-label small fw-bold" for="p-linkedin">LinkedIn Kullanıcı Adı</label><input id="p-linkedin" v-model="personal.linkedin" type="text" class="form-control" maxlength="100"></div>
    <div class="mt-3"><label class="form-label small fw-bold" for="p-github">GitHub Kullanıcı Adı</label><input id="p-github" v-model="personal.github" type="text" class="form-control" maxlength="100"></div>

    <div class="mt-4 bg-light p-3 rounded border">
      <div class="fw-bold small mb-2">Sağ Üst QR Kod</div>
      <div class="form-check form-switch mb-2">
        <input id="p-qr" v-model="personal.showQr" class="form-check-input" type="checkbox">
        <label class="form-check-label small" for="p-qr">QR kod göster</label>
      </div>
      <input
        v-if="personal.showQr"
        v-model="personal.qrLink"
        type="text"
        class="form-control form-control-sm"
        placeholder="QR bağlantısı (örn. LinkedIn adresiniz)"
        aria-label="QR bağlantısı"
        maxlength="500"
      >
    </div>
  </div>
</template>
