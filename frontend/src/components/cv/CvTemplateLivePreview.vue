<script setup>
import { computed } from 'vue'
import CvPreview from './CvPreview.vue'
import { SAMPLE_CV_CONTENT, sampleDesign } from '@/utils/cvSample'

const props = defineProps({ template: { type: String, required: true }, zoom: { type: Number, default: 0.2 } })
const design = computed(() => sampleDesign(props.template))
</script>

<template>
  <div class="live-template-preview" aria-label="Örnek içerikle CV önizlemesi">
    <CvPreview :content="SAMPLE_CV_CONTENT" :design="design" :template="template" :zoom="zoom" />
  </div>
</template>

<style scoped>
.live-template-preview { position: relative; height: 225px; overflow: hidden; padding-top: 18px; background: #eef1f6; pointer-events: none; }
.live-template-preview :deep(.cv-document) { margin: 0 auto; box-shadow: 0 10px 25px rgba(33,42,62,.15); }
.live-template-preview::after { content: ''; position: absolute; right: 0; bottom: 0; left: 0; height: 28px; background: linear-gradient(transparent,#eef1f6); }
</style>
