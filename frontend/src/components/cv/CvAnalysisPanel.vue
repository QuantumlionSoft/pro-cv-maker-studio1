<script setup>
import { computed } from 'vue'
import { analyzeCv } from '@/utils/cvAnalysis'

const props = defineProps({
  content: { type: Object, required: true },
  design: { type: Object, required: true },
  template: { type: String, required: true },
})
const emit = defineEmits(['navigate'])
const analysis = computed(() => analyzeCv(props.content, props.design, props.template))
const levelLabel = computed(() => ({ excellent: 'Başvuruya hazır', good: 'İyi durumda', 'needs-work': 'Geliştirilmeli' }[analysis.value.level]))
</script>

<template>
  <div class="analysis-panel">
    <div class="analysis-hero" :class="`is-${analysis.level}`">
      <div class="analysis-score" :style="{ '--score': `${analysis.score * 3.6}deg` }"><span><strong>{{ analysis.score }}</strong><small>/100</small></span></div>
      <div><p class="eyebrow">Kural tabanlı CV analizi</p><h5>{{ levelLabel }}</h5><p>İçeriğiniz tarayıcınızda analiz edilir; hiçbir veri harici servise gönderilmez.</p></div>
    </div>

    <div class="analysis-categories">
      <div v-for="category in analysis.categories" :key="category.id" class="analysis-category">
        <div><span>{{ category.label }}</span><strong>{{ category.value }}<small>/{{ category.max }}</small></strong></div>
        <div class="analysis-bar"><span :style="{ width: `${category.value / category.max * 100}%` }"></span></div>
      </div>
    </div>

    <section class="analysis-section">
      <div class="analysis-section-title"><i class="bi bi-lightbulb"></i><h6>Öncelikli öneriler</h6><span>{{ analysis.issues.length }}</span></div>
      <div v-if="!analysis.issues.length" class="analysis-empty"><i class="bi bi-check2-circle"></i><strong>Harika görünüyor!</strong><p>Temel içerik ve ATS kontrollerinde iyileştirme gerektiren bir konu bulunamadı.</p></div>
      <button v-for="item in analysis.issues" v-else :key="item.id" type="button" class="analysis-issue" :class="`is-${item.severity}`" @click="emit('navigate', item.tab)">
        <i :class="['bi', item.severity === 'danger' ? 'bi-exclamation-circle' : item.severity === 'warning' ? 'bi-lightbulb' : 'bi-info-circle']"></i>
        <span><strong>{{ item.title }}</strong><small>{{ item.description }}</small></span><i class="bi bi-chevron-right"></i>
      </button>
    </section>

    <section v-if="analysis.strengths.length" class="analysis-section">
      <div class="analysis-section-title"><i class="bi bi-shield-check"></i><h6>Güçlü yönler</h6></div>
      <div class="analysis-strengths"><span v-for="strength in analysis.strengths" :key="strength"><i class="bi bi-check2"></i>{{ strength }}</span></div>
    </section>
    <p class="analysis-note">Bu puan yalnızca rehberlik amaçlıdır; işe alım garantisi veya yapay zekâ değerlendirmesi değildir.</p>
  </div>
</template>

<style scoped>
.analysis-hero { display: flex; align-items: center; gap: 1rem; padding: 1rem; border: 1px solid #e3e7ee; border-radius: 13px; background: linear-gradient(135deg,#f8f8ff,#f5f8fc); }
.analysis-score { --score-color: #4f46e5; width: 86px; height: 86px; display: grid; place-items: center; flex: 0 0 auto; border-radius: 50%; background: conic-gradient(var(--score-color) var(--score), #e5e7f0 0); }
.analysis-score::before { content: ''; grid-area: 1/1; width: 68px; height: 68px; border-radius: 50%; background: #fff; }
.analysis-score > span { z-index: 1; grid-area: 1/1; display: flex; align-items: baseline; }
.analysis-score strong { color: #29354a; font-size: 1.55rem; letter-spacing: -.06em; }
.analysis-score small { color: #98a2b3; font-size: .6rem; }
.analysis-hero.is-excellent .analysis-score { --score-color: #12a17a; }
.analysis-hero.is-needs-work .analysis-score { --score-color: #e29b32; }
.analysis-hero .eyebrow { margin: 0 0 .25rem; font-size: .56rem; }
.analysis-hero h5 { margin: 0 0 .3rem; font-size: 1rem; }
.analysis-hero p:last-child { margin: 0; color: #667085; font-size: .68rem; line-height: 1.55; }
.analysis-categories { display: grid; gap: .75rem; margin: 1.25rem 0; }
.analysis-category > div:first-child { display: flex; justify-content: space-between; margin-bottom: .35rem; color: #596579; font-size: .72rem; }
.analysis-category strong { color: #344054; font-size: .72rem; }
.analysis-category small { color: #98a2b3; font-weight: 500; }
.analysis-bar { height: 6px; overflow: hidden; border-radius: 999px; background: #edf0f4; }
.analysis-bar span { display: block; height: 100%; border-radius: inherit; background: linear-gradient(90deg,#6d64e9,#4f46e5); }
.analysis-section { padding-top: 1rem; border-top: 1px solid #e8ebf0; }
.analysis-section + .analysis-section { margin-top: 1rem; }
.analysis-section-title { display: flex; align-items: center; gap: .45rem; margin-bottom: .7rem; color: #5148c7; }
.analysis-section-title h6 { margin: 0; color: #29354a; font-size: .78rem; }
.analysis-section-title > span { margin-left: auto; padding: .1rem .4rem; border-radius: 999px; background: #f0efff; font-size: .6rem; }
.analysis-issue { display: flex; align-items: flex-start; gap: .6rem; width: 100%; margin-bottom: .45rem; padding: .7rem; color: #596579; border: 1px solid #e6e9ef; border-radius: 9px; background: #fff; text-align: left; }
.analysis-issue:hover { border-color: #bbb6ef; background: #fafaff; }
.analysis-issue > i:first-child { margin-top: .15rem; color: #d28a24; }
.analysis-issue.is-danger > i:first-child { color: #c4322b; }
.analysis-issue.is-info > i:first-child { color: #4784c6; }
.analysis-issue > span { display: grid; gap: .2rem; flex: 1; }
.analysis-issue strong { color: #344054; font-size: .72rem; }
.analysis-issue small { font-size: .65rem; line-height: 1.5; }
.analysis-issue > i:last-child { margin-top: .3rem; color: #a4acba; font-size: .65rem; }
.analysis-strengths { display: flex; flex-wrap: wrap; gap: .4rem; }
.analysis-strengths span { padding: .35rem .5rem; color: #087153; border-radius: 6px; background: #edf9f4; font-size: .64rem; }
.analysis-strengths i { margin-right: .25rem; }
.analysis-note { margin: 1.25rem 0 0; color: #98a2b3; font-size: .62rem; line-height: 1.6; }
.analysis-empty { padding: 1rem; color: #087153; border-radius: 9px; background: #edf9f4; text-align: center; }
.analysis-empty > i { display: block; margin-bottom: .4rem; font-size: 1.5rem; }
.analysis-empty strong { font-size: .8rem; }
.analysis-empty p { margin: .3rem 0 0; color: #52776c; font-size: .68rem; }
</style>
