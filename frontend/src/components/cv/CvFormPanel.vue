<script setup>
import { computed } from 'vue'
import { LIST_SECTIONS } from './cvSections'
import DesignForm from './DesignForm.vue'
import SectionLayoutForm from './SectionLayoutForm.vue'
import CvAnalysisPanel from './CvAnalysisPanel.vue'
import ItemListForm from './ItemListForm.vue'
import PersonalForm from './PersonalForm.vue'

const props = defineProps({
  activeTab: { type: String, required: true },
  content: { type: Object, required: true },
  design: { type: Object, required: true },
  template: { type: String, required: true },
  templates: { type: Array, default: () => [] },
})
defineEmits(['update:template', 'update:activeTab'])

const listConfig = computed(() => LIST_SECTIONS[props.activeTab] || null)
const SUMMARY_MAX = 4000
</script>

<template>
  <div class="cv-form-panel p-4">
    <PersonalForm v-if="activeTab === 'personal'" :personal="content.personal" />

    <div v-else-if="activeTab === 'summary'">
      <h5 class="fw-bold mb-4">Profil Özeti</h5>
      <label class="form-label small fw-bold visually-hidden" for="summary-text">Profil özeti</label>
      <textarea
        id="summary-text"
        v-model="content.summary"
        class="form-control"
        rows="12"
        :maxlength="SUMMARY_MAX"
        placeholder="Kendinizden kısaca bahsedin…"
      ></textarea>
      <div class="form-text text-end">{{ (content.summary || '').length }} / {{ SUMMARY_MAX }}</div>
    </div>

    <SectionLayoutForm v-else-if="activeTab === 'layout'" :content="content" />

    <CvAnalysisPanel v-else-if="activeTab === 'analysis'" :content="content" :design="design" :template="template" @navigate="$emit('update:activeTab', $event)" />

    <DesignForm
      v-else-if="activeTab === 'design'"
      :design="design"
      :templates="templates"
      :template="template"
      @update:template="$emit('update:template', $event)"
    />

    <ItemListForm
      v-else-if="listConfig"
      :key="activeTab"
      :config="listConfig"
      :section="activeTab"
      :items="content[activeTab]"
    />
  </div>
</template>
