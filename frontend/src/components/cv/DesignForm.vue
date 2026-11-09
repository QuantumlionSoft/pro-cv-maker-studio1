<script setup>
import CvTemplateThumbnail from './CvTemplateThumbnail.vue'
import { DESIGN_DEFAULTS } from '@/utils/cvContent'

const props = defineProps({
  design: { type: Object, required: true },
  templates: { type: Array, default: () => [] },
  template: { type: String, required: true },
})
defineEmits(['update:template'])

const FONTS = ['Inter', 'Roboto', 'Poppins', 'Open Sans', 'Lato', 'Montserrat', 'Merriweather']
const PALETTES = [
  { name: 'Lacivert', accent: '#4f46e5', header: '#172033', sidebar: '#eef1f7', text: '#334155' },
  { name: 'Okyanus', accent: '#0f766e', header: '#123b3a', sidebar: '#edf7f5', text: '#294845' },
  { name: 'Bordo', accent: '#9f1239', header: '#3f1d2b', sidebar: '#fbf1f3', text: '#54323e' },
  { name: 'Toprak', accent: '#a16207', header: '#342b25', sidebar: '#f7f3ed', text: '#51443b' },
  { name: 'Grafit', accent: '#475569', header: '#1e293b', sidebar: '#f1f5f9', text: '#334155' },
  { name: 'Mor', accent: '#7c3aed', header: '#312e51', sidebar: '#f4f1fa', text: '#443d5c' },
]

function applyPalette(palette) {
  props.design.colorAccent = palette.accent
  props.design.colorHeaderBg = palette.header
  props.design.colorHeaderText = '#ffffff'
  props.design.colorSidebarBg = palette.sidebar
  props.design.colorSidebarText = palette.text
}

function resetDesign() {
  Object.assign(props.design, DESIGN_DEFAULTS)
}
</script>

<template>
  <div class="design-form">
    <div class="form-section-heading">
      <span class="form-section-icon"><i class="bi bi-palette2"></i></span>
      <div><h5>Görünümü kişiselleştirin</h5><p>İçeriğiniz tüm şablonlarda korunur.</p></div>
    </div>

    <section class="design-section">
      <div class="design-section-title"><span>CV şablonu</span><small>{{ templates.length }} seçenek</small></div>
      <div class="template-picker" role="group" aria-label="CV şablonu">
        <button
          v-for="t in templates"
          :id="`d-template-${t.id}`"
          :key="t.id"
          type="button"
          class="template-option"
          :class="{ 'is-selected': template === t.id }"
          :aria-pressed="template === t.id"
          :title="t.description"
          @click="$emit('update:template', t.id)"
        >
          <span class="template-check"><i class="bi bi-check-lg"></i></span>
          <CvTemplateThumbnail :template="t.id" />
          <span class="template-option-name">{{ t.name }}<i v-if="template === t.id" class="bi bi-check-circle-fill"></i></span>
        </button>
      </div>
    </section>

    <section class="design-section">
      <div class="design-section-title"><span>Hazır renk paletleri</span><small>Tek tıkla uygula</small></div>
      <div class="palette-grid" role="group" aria-label="Hazır renk paletleri">
        <button v-for="palette in PALETTES" :key="palette.name" type="button" class="palette-option" :title="`${palette.name} paletini uygula`" @click="applyPalette(palette)">
          <span class="palette-colors"><i :style="{ background: palette.header }"></i><i :style="{ background: palette.accent }"></i><i :style="{ background: palette.sidebar }"></i></span>
          <span>{{ palette.name }}</span>
        </button>
      </div>
    </section>

    <section class="design-section">
      <div class="design-section-title"><span>Yerleşim</span></div>
      <div class="form-check form-switch design-switch">
        <input id="d-edu" v-model="design.educationInSidebar" class="form-check-input" type="checkbox">
        <label class="form-check-label" for="d-edu">Eğitimi yan sütunda göster</label>
        <div class="form-text">İki sütunlu şablonlarda geçerlidir.</div>
      </div>
      <div class="form-check form-switch design-switch">
        <input id="d-newpage" v-model="design.newPageForExtras" class="form-check-input" type="checkbox">
        <label class="form-check-label" for="d-newpage">Ek bölümler yeni sayfada başlasın</label>
        <div class="form-text">Projeler, sertifikalar ve referanslar için.</div>
      </div>
      <label class="form-label" for="d-align">Üst bilgi hizalama</label>
      <select id="d-align" v-model="design.headerAlign" class="form-select form-select-sm">
        <option value="left">Sola hizala</option><option value="center">Ortala</option><option value="right">Sağa hizala</option>
      </select>
      <label class="form-label mt-3" for="d-font">Yazı tipi</label>
      <select id="d-font" v-model="design.font" class="form-select form-select-sm">
        <option v-for="f in FONTS" :key="f" :value="f">{{ f }}</option>
      </select>
    </section>

    <section class="design-section">
      <div class="design-section-title"><span>Yazı boyutları</span></div>
      <div class="range-field"><label class="form-label" for="d-name">İsim boyutu <output>{{ design.nameSize }}px</output></label><input id="d-name" v-model.number="design.nameSize" type="range" class="form-range" min="24" max="48" step="2"></div>
      <div class="range-field"><label class="form-label" for="d-heading">Başlık boyutu <output>{{ design.headingSize }}px</output></label><input id="d-heading" v-model.number="design.headingSize" type="range" class="form-range" min="12" max="24" step="1"></div>
      <div class="range-field"><label class="form-label" for="d-text">Metin boyutu <output>{{ design.textSize }}px</output></label><input id="d-text" v-model.number="design.textSize" type="range" class="form-range" min="10" max="18" step="1"></div>
    </section>

    <section class="design-section">
      <div class="design-section-title"><span>Görseller</span></div>
      <div class="range-field"><label class="form-label" for="d-photo">Fotoğraf boyutu <output>{{ design.photoSize }}px</output></label><input id="d-photo" v-model.number="design.photoSize" type="range" class="form-range" min="80" max="200" step="10"></div>
      <div class="range-field"><label class="form-label" for="d-qr">QR kod boyutu <output>{{ design.qrSize }}px</output></label><input id="d-qr" v-model.number="design.qrSize" type="range" class="form-range" min="50" max="120" step="5"></div>
    </section>

    <section class="design-section">
      <div class="design-section-title"><span>Özel renkler</span><small>#HEX</small></div>
      <div class="row g-3">
        <div class="col-12"><label class="form-label" for="c-accent">Vurgu rengi</label><div class="color-field"><input id="c-accent" v-model="design.colorAccent" type="color" class="form-control form-control-color"><code>{{ design.colorAccent }}</code></div></div>
        <div class="col-6"><label class="form-label" for="c-hbg">Üst bilgi zemin</label><input id="c-hbg" v-model="design.colorHeaderBg" type="color" class="form-control form-control-color w-100"></div>
        <div class="col-6"><label class="form-label" for="c-htx">Üst bilgi yazı</label><input id="c-htx" v-model="design.colorHeaderText" type="color" class="form-control form-control-color w-100"></div>
        <div class="col-6"><label class="form-label" for="c-sbg">Yan sütun zemin</label><input id="c-sbg" v-model="design.colorSidebarBg" type="color" class="form-control form-control-color w-100"></div>
        <div class="col-6"><label class="form-label" for="c-stx">Yan sütun yazı</label><input id="c-stx" v-model="design.colorSidebarText" type="color" class="form-control form-control-color w-100"></div>
      </div>
    </section>

    <button type="button" class="btn btn-outline-secondary btn-sm w-100" @click="resetDesign"><i class="bi bi-arrow-counterclockwise me-1"></i>Tasarım ayarlarını sıfırla</button>
  </div>
</template>

<style scoped>
.form-section-heading { display: flex; gap: .75rem; align-items: center; margin-bottom: 1.25rem; }
.form-section-heading h5 { margin: 0 0 .15rem; font-size: 1rem; font-weight: 700; }
.form-section-heading p { margin: 0; color: var(--pcms-muted); font-size: .78rem; }
.form-section-icon { width: 38px; height: 38px; display: grid; place-items: center; flex: 0 0 auto; color: var(--pcms-brand); background: var(--pcms-brand-soft); border-radius: 10px; }
.design-section { padding: 1rem 0; border-top: 1px solid var(--pcms-line); }
.design-section-title { display: flex; align-items: center; justify-content: space-between; gap: .5rem; margin-bottom: .75rem; font-size: .8rem; font-weight: 700; color: #29354a; }
.design-section-title small { font-size: .68rem; font-weight: 500; color: var(--pcms-muted); }
.template-picker { display: grid; grid-template-columns: 1fr 1fr; gap: .65rem; }
.template-option { position: relative; min-width: 0; padding: 5px 5px 8px; background: #fff; color: var(--pcms-ink); border: 1px solid #dfe4ec; border-radius: 12px; text-align: left; transition: border-color .15s, box-shadow .15s, transform .15s; }
.template-option:hover { border-color: #a5b4fc; transform: translateY(-1px); }
.template-option.is-selected { border-color: var(--pcms-brand); box-shadow: 0 0 0 2px rgba(79,70,229,.12); }
.template-option :deep(.template-thumb) { height: 115px; }
.template-option :deep(.thumb-paper) { transform: scale(.78); transform-origin: top center; margin-top: 12px; }
.template-option-name { display: flex; justify-content: space-between; align-items: center; gap: .25rem; padding: 6px 4px 0; font-size: .74rem; font-weight: 650; }
.template-option-name i { color: var(--pcms-brand); }
.template-check { display: none; position: absolute; z-index: 2; top: 9px; right: 9px; width: 21px; height: 21px; place-items: center; border-radius: 50%; color: #fff; background: var(--pcms-brand); font-size: .75rem; }
.is-selected .template-check { display: grid; }
.palette-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: .5rem; }
.palette-option { padding: .5rem .25rem; border: 1px solid var(--pcms-line); border-radius: 8px; background: #fff; font-size: .68rem; color: var(--pcms-muted); }
.palette-option:hover { border-color: #a5b4fc; background: #fafaff; }
.palette-colors { display: flex; justify-content: center; margin-bottom: .3rem; }
.palette-colors i { width: 18px; height: 18px; border: 2px solid #fff; border-radius: 50%; box-shadow: 0 0 0 1px #e2e8f0; }
.palette-colors i + i { margin-left: -4px; }
.design-switch { padding: .35rem 0 .75rem 2.5rem; }
.design-switch .form-check-label { font-size: .8rem; font-weight: 600; }
.design-switch .form-text { font-size: .7rem; }
.design-section .form-label { font-size: .75rem; margin-bottom: .35rem; }
.range-field + .range-field { margin-top: .65rem; }
.range-field .form-label { width: 100%; display: flex; justify-content: space-between; }
.range-field output { color: var(--pcms-brand); font-size: .7rem; font-weight: 700; }
.color-field { display: flex; align-items: center; gap: .5rem; }
.color-field .form-control-color { width: 48px; height: 34px; }
.color-field code { font-size: .75rem; color: var(--pcms-muted); }
.design-form > .btn { margin: .5rem 0 1rem; }
</style>
