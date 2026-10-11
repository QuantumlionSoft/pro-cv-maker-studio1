<script setup>
defineProps({
  design: { type: Object, required: true },
  templates: { type: Array, default: () => [] },
  template: { type: String, required: true },
})
defineEmits(['update:template'])

const FONTS = ['Inter', 'Roboto', 'Poppins', 'Open Sans', 'Lato', 'Montserrat', 'Merriweather']
</script>

<template>
  <div>
    <h5 class="fw-bold mb-4">Tasarım Ayarları</h5>

    <div class="mb-4 bg-light p-3 rounded">
      <label class="form-label small fw-bold" for="d-template">Şablon</label>
      <select
        id="d-template"
        class="form-select form-select-sm mb-3"
        :value="template"
        @change="$emit('update:template', $event.target.value)"
      >
        <option v-for="t in templates" :key="t.id" :value="t.id">{{ t.name }}</option>
      </select>

      <div class="form-check form-switch mb-3">
        <input id="d-edu" v-model="design.educationInSidebar" class="form-check-input" type="checkbox">
        <label class="form-check-label" for="d-edu">Eğitimi sol menüde göster</label>
        <div class="form-text">Yalnızca Modern şablonda geçerlidir.</div>
      </div>

      <div class="form-check form-switch mb-3">
        <input id="d-newpage" v-model="design.newPageForExtras" class="form-check-input" type="checkbox">
        <label class="form-check-label" for="d-newpage">Projeler ve sertifikalar yeni sayfada başlasın</label>
      </div>

      <label class="form-label small fw-bold" for="d-align">Üst bilgi hizalama</label>
      <select id="d-align" v-model="design.headerAlign" class="form-select form-select-sm">
        <option value="left">Sola hizala</option>
        <option value="center">Ortala</option>
        <option value="right">Sağa hizala</option>
      </select>

      <label class="form-label small fw-bold mt-3" for="d-font">Yazı tipi</label>
      <select id="d-font" v-model="design.font" class="form-select form-select-sm">
        <option v-for="f in FONTS" :key="f" :value="f">{{ f }}</option>
      </select>
    </div>

    <div class="mb-4 bg-light p-3 rounded">
      <div class="fw-bold mb-3">Yazı boyutları</div>
      <label class="form-label small" for="d-name">İsim boyutu: {{ design.nameSize }}px</label>
      <input id="d-name" v-model.number="design.nameSize" type="range" class="form-range" min="24" max="48" step="2">
      <label class="form-label small mt-2" for="d-heading">Başlık boyutu: {{ design.headingSize }}px</label>
      <input id="d-heading" v-model.number="design.headingSize" type="range" class="form-range" min="12" max="24" step="1">
      <label class="form-label small mt-2" for="d-text">Metin boyutu: {{ design.textSize }}px</label>
      <input id="d-text" v-model.number="design.textSize" type="range" class="form-range" min="10" max="18" step="1">
    </div>

    <div class="mb-4 bg-light p-3 rounded">
      <div class="fw-bold mb-3">Görseller</div>
      <label class="form-label small" for="d-photo">Fotoğraf boyutu: {{ design.photoSize }}px</label>
      <input id="d-photo" v-model.number="design.photoSize" type="range" class="form-range" min="80" max="200" step="10">
      <label class="form-label small mt-2" for="d-qr">QR kod boyutu: {{ design.qrSize }}px</label>
      <input id="d-qr" v-model.number="design.qrSize" type="range" class="form-range" min="50" max="120" step="5">
    </div>

    <div class="row g-3 mb-4">
      <div class="col-12"><label class="form-label small fw-bold" for="c-accent">Vurgu rengi</label><input id="c-accent" v-model="design.colorAccent" type="color" class="form-control form-control-color w-100"></div>
      <div class="col-6"><label class="form-label small fw-bold" for="c-hbg">Header arka plan</label><input id="c-hbg" v-model="design.colorHeaderBg" type="color" class="form-control form-control-color w-100"></div>
      <div class="col-6"><label class="form-label small fw-bold" for="c-htx">Header yazı</label><input id="c-htx" v-model="design.colorHeaderText" type="color" class="form-control form-control-color w-100"></div>
      <div class="col-6"><label class="form-label small fw-bold" for="c-sbg">Sol menü arka plan</label><input id="c-sbg" v-model="design.colorSidebarBg" type="color" class="form-control form-control-color w-100"></div>
      <div class="col-6"><label class="form-label small fw-bold" for="c-stx">Sol menü yazı</label><input id="c-stx" v-model="design.colorSidebarText" type="color" class="form-control form-control-color w-100"></div>
    </div>
  </div>
</template>
