<script setup>
import { computed, ref } from 'vue'
import { CV_SECTION_ORDER, DEFAULT_SECTION_TITLES } from '@/utils/cvContent'
import { SECTION_TABS } from './cvSections'

const props = defineProps({ content: { type: Object, required: true } })
const dragged = ref(null)
const dragOver = ref(null)
const icons = Object.fromEntries(SECTION_TABS.map((tab) => [tab.id, tab.icon]))

if (!Array.isArray(props.content.sectionOrder)) props.content.sectionOrder = [...CV_SECTION_ORDER]
for (const key of CV_SECTION_ORDER) if (!props.content.sectionOrder.includes(key)) props.content.sectionOrder.push(key)
if (!Array.isArray(props.content.hiddenSections)) props.content.hiddenSections = []
if (!props.content.sectionTitles) props.content.sectionTitles = {}

const sections = computed(() => props.content.sectionOrder.map((key) => ({ key, label: DEFAULT_SECTION_TITLES[key], icon: icons[key] || 'bi-list' })))
const hidden = (key) => props.content.hiddenSections.includes(key)

function move(index, direction) {
  const target = index + direction
  if (target < 0 || target >= props.content.sectionOrder.length) return
  const order = props.content.sectionOrder
  ;[order[index], order[target]] = [order[target], order[index]]
}
function toggle(key) {
  const list = props.content.hiddenSections
  const index = list.indexOf(key)
  if (index >= 0) list.splice(index, 1)
  else list.push(key)
}
function drop(index) {
  if (dragged.value === null || dragged.value === index) return
  const order = props.content.sectionOrder
  const [item] = order.splice(dragged.value, 1)
  order.splice(index, 0, item)
  dragged.value = null
  dragOver.value = null
}
</script>

<template>
  <div>
    <div class="form-section-heading"><span class="form-section-icon"><i class="bi bi-layout-three-columns"></i></span><div><h5>Bölüm düzeni</h5><p>Sürükleyin, gizleyin veya başlıkları değiştirin.</p></div></div>
    <p class="layout-help"><i class="bi bi-info-circle me-1"></i>Gizlenen bölümlerin içeriği silinmez. Tekrar görünür yaptığınızda geri gelir.</p>
    <div class="layout-list">
      <article
        v-for="(section, index) in sections"
        :key="section.key"
        class="layout-item"
        :class="{ 'is-hidden': hidden(section.key), 'is-drag-over': dragOver === index }"
        @dragover.prevent="dragOver = index"
        @dragleave="dragOver = null"
        @drop.prevent="drop(index)"
      >
        <div class="layout-item-top">
          <button type="button" class="layout-drag" title="Sürükleyerek sırala" draggable="true" @dragstart="dragged = index" @dragend="dragged = null; dragOver = null"><i class="bi bi-grip-vertical"></i></button>
          <span class="layout-icon"><i :class="['bi', section.icon]"></i></span>
          <strong>{{ section.label }}</strong>
          <div class="layout-actions">
            <button type="button" class="btn btn-icon" :disabled="index === 0" :aria-label="`${section.label} bölümünü yukarı taşı`" @click="move(index, -1)"><i class="bi bi-chevron-up"></i></button>
            <button type="button" class="btn btn-icon" :disabled="index === sections.length - 1" :aria-label="`${section.label} bölümünü aşağı taşı`" @click="move(index, 1)"><i class="bi bi-chevron-down"></i></button>
            <button type="button" class="btn btn-icon" :class="{ 'text-primary': !hidden(section.key) }" :aria-label="`${section.label} bölümünü ${hidden(section.key) ? 'göster' : 'gizle'}`" @click="toggle(section.key)"><i :class="['bi', hidden(section.key) ? 'bi-eye-slash' : 'bi-eye']"></i></button>
          </div>
        </div>
        <label class="layout-title-field"><span>Başlık</span><input v-model="content.sectionTitles[section.key]" type="text" class="form-control form-control-sm" maxlength="60" :placeholder="section.label"></label>
      </article>
    </div>
  </div>
</template>

<style scoped>
.form-section-heading { display: flex; gap: .75rem; align-items: center; margin-bottom: 1rem; }
.form-section-heading h5 { margin: 0 0 .15rem; font-size: 1rem; font-weight: 700; }
.form-section-heading p { margin: 0; color: var(--pcms-muted); font-size: .78rem; }
.form-section-icon { width: 38px; height: 38px; display: grid; place-items: center; color: var(--pcms-brand); background: var(--pcms-brand-soft); border-radius: 10px; }
.layout-help { padding: .65rem .75rem; color: #596579; background: #f5f6ff; border-radius: 8px; font-size: .72rem; line-height: 1.6; }
.layout-list { display: grid; gap: .55rem; }
.layout-item { padding: .6rem; border: 1px solid #e3e7ee; border-radius: 10px; background: #fff; transition: opacity .15s, border-color .15s; }
.layout-item.is-hidden { opacity: .58; background: #f8f9fb; }
.layout-item.is-drag-over { border-color: var(--pcms-brand); }
.layout-item-top { display: flex; align-items: center; gap: .45rem; }
.layout-item-top strong { min-width: 0; overflow: hidden; text-overflow: ellipsis; font-size: .76rem; white-space: nowrap; }
.layout-drag { padding: .2rem 0; color: #98a2b3; border: 0; background: transparent; cursor: grab; }
.layout-icon { width: 25px; height: 25px; display: grid; place-items: center; flex: 0 0 auto; color: #6159c9; background: #f0efff; border-radius: 6px; font-size: .72rem; }
.layout-actions { display: flex; margin-left: auto; }
.layout-actions .btn { width: 25px; height: 27px; padding: 0; color: #7b8496; border: 0; font-size: .7rem; }
.layout-title-field { display: flex; align-items: center; gap: .5rem; margin: .5rem 0 0 1.65rem; }
.layout-title-field > span { color: #98a2b3; font-size: .62rem; }
.layout-title-field .form-control { min-height: 29px; font-size: .7rem; }
</style>
