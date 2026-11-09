<script setup>
import { ref } from 'vue'
import { blankItem } from '@/utils/cvContent'
import ImageField from './ImageField.vue'

const props = defineProps({
  /** Key into LIST_SECTIONS (from cvSections.js). */
  config: { type: Object, required: true },
  section: { type: String, required: true },
  items: { type: Array, required: true },
})

function add() {
  props.items.push(blankItem(props.section))
}

function remove(index) {
  props.items.splice(index, 1)
}

const draggedIndex = ref(null)
const dragOverIndex = ref(null)
function move(index, direction) {
  const target = index + direction
  if (target < 0 || target >= props.items.length) return
  const [item] = props.items.splice(index, 1)
  props.items.splice(target, 0, item)
}
function drop(index) {
  if (draggedIndex.value === null || draggedIndex.value === index) return
  const [item] = props.items.splice(draggedIndex.value, 1)
  props.items.splice(index, 0, item)
  draggedIndex.value = null
  dragOverIndex.value = null
}
</script>

<template>
  <div>
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h5 class="fw-bold mb-0">{{ config.title }}</h5>
      <button type="button" class="btn btn-sm btn-primary" @click="add">
        <i class="bi bi-plus-lg me-1"></i>{{ config.addLabel }}
      </button>
    </div>

    <p v-if="!items.length" class="text-secondary small mb-0">Henüz kayıt yok.</p>

    <!-- Compact rows: skills, languages, technologies -->
    <template v-if="config.compact">
      <div
        v-for="(item, index) in items"
        :key="item.id"
        class="cv-compact-row d-flex align-items-center gap-2 mb-2 p-2 rounded bg-light"
        :class="{ 'is-drag-over': dragOverIndex === index }"
        @dragover.prevent="dragOverIndex = index"
        @drop.prevent="drop(index)"
      >
        <button type="button" class="item-drag" title="Sürükleyerek sırala" draggable="true" @dragstart="draggedIndex = index" @dragend="draggedIndex = null; dragOverIndex = null"><i class="bi bi-grip-vertical"></i></button>
        <input
          v-model="item.name"
          type="text"
          class="form-control form-control-sm"
          :placeholder="config.fields[0].placeholder"
          :aria-label="`${config.title} ${index + 1} adı`"
          maxlength="100"
        >
        <template v-if="config.fields[1]">
          <input
            v-model.number="item.level"
            type="range"
            class="form-range flex-grow-1"
            min="10"
            max="100"
            step="10"
            :aria-label="`${config.title} ${index + 1} seviyesi`"
          >
          <span class="small text-secondary cv-level">{{ item.level }}%</span>
        </template>
        <span class="item-order-buttons"><button type="button" :disabled="index === 0" aria-label="Yukarı taşı" @click="move(index, -1)"><i class="bi bi-chevron-up"></i></button><button type="button" :disabled="index === items.length - 1" aria-label="Aşağı taşı" @click="move(index, 1)"><i class="bi bi-chevron-down"></i></button></span>
        <button type="button" class="btn btn-sm text-danger flex-shrink-0" :aria-label="`${config.title} ${index + 1} sil`" @click="remove(index)">
          <i class="bi bi-x-circle-fill"></i>
        </button>
      </div>
    </template>

    <!-- Cards: experience, education, projects, certifications, references -->
    <template v-else>
      <div
        v-for="(item, index) in items"
        :key="item.id"
        class="card mb-3 shadow-sm border-0 bg-light cv-sortable-card"
        :class="{ 'is-drag-over': dragOverIndex === index }"
        @dragover.prevent="dragOverIndex = index"
        @drop.prevent="drop(index)"
      >
        <div class="card-body">
          <div class="d-flex justify-content-between align-items-center mb-2">
            <div class="d-flex align-items-center gap-1 min-w-0">
              <button type="button" class="item-drag" title="Sürükleyerek sırala" draggable="true" @dragstart="draggedIndex = index" @dragend="draggedIndex = null; dragOverIndex = null"><i class="bi bi-grip-vertical"></i></button>
              <h6 class="fw-bold text-primary mb-0">{{ config.itemLabel }} {{ index + 1 }}</h6>
              <span class="item-order-buttons"><button type="button" :disabled="index === 0" aria-label="Yukarı taşı" @click="move(index, -1)"><i class="bi bi-chevron-up"></i></button><button type="button" :disabled="index === items.length - 1" aria-label="Aşağı taşı" @click="move(index, 1)"><i class="bi bi-chevron-down"></i></button></span>
            </div>
            <button type="button" class="btn btn-sm btn-link text-danger p-0" @click="remove(index)">
              <i class="bi bi-trash"></i> Sil
            </button>
          </div>
          <div class="row g-2">
            <template v-for="field in config.fields" :key="field.key">
              <div :class="field.half ? 'col-6' : 'col-12'">
                <ImageField
                  v-if="field.kind === 'image'"
                  v-model="item[field.key]"
                  :purpose="field.purpose"
                  :label="field.label"
                  :input-id="`${section}-${item.id}-${field.key}`"
                />
                <div v-else-if="field.kind === 'switch'" class="form-check form-switch mt-1">
                  <input
                    :id="`${section}-${item.id}-${field.key}`"
                    v-model="item[field.key]"
                    class="form-check-input"
                    type="checkbox"
                  >
                  <label class="form-check-label small" :for="`${section}-${item.id}-${field.key}`">{{ field.label }}</label>
                </div>
                <template v-else>
                  <label v-if="field.label" class="form-label small fw-bold mb-1" :for="`${section}-${item.id}-${field.key}`">{{ field.label }}</label>
                  <textarea
                    v-if="field.kind === 'textarea'"
                    :id="`${section}-${item.id}-${field.key}`"
                    v-model="item[field.key]"
                    class="form-control form-control-sm"
                    :rows="field.rows || 3"
                    :placeholder="field.placeholder"
                    maxlength="4000"
                  ></textarea>
                  <input
                    v-else
                    :id="`${section}-${item.id}-${field.key}`"
                    v-model="item[field.key]"
                    :type="field.kind === 'email' ? 'email' : 'text'"
                    class="form-control form-control-sm"
                    :placeholder="field.placeholder"
                    :disabled="field.key === 'end' && item.current"
                    maxlength="1000"
                  >
                </template>
              </div>
            </template>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<style scoped>
.cv-level { min-width: 2.75rem; text-align: right; }
.item-drag { padding: .2rem 0; color: #98a2b3; border: 0; background: transparent; cursor: grab; }
.item-order-buttons { display: inline-flex; }
.item-order-buttons button { width: 24px; height: 25px; padding: 0; color: #8792a5; border: 0; background: transparent; font-size: .68rem; }
.item-order-buttons button:disabled { opacity: .25; }
.is-drag-over { outline: 2px solid var(--pcms-brand); outline-offset: 2px; }
.cv-sortable-card { transition: outline-color .15s; }
</style>
