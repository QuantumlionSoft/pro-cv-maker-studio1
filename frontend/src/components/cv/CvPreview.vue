<script setup>
/* v2 preview: same structure, class names and QR block as the original.
 * Changes are visual only: full-height sidebar, consistent headings with icons,
 * left-aligned body text, fixed logo boxes, empty date badges hidden, shorter URLs. */
import { computed, ref, watch } from 'vue'
import { mediaFileUrl, qrImageUrl } from '@/services/media'
import { DESIGN_DEFAULTS } from '@/utils/cvContent'

const props = defineProps({
  content: { type: Object, required: true },
  design: { type: Object, required: true },
  template: { type: String, default: 'modern' },
  zoom: { type: Number, default: 1 },
})

const FONT_STACKS = {
  Inter: "Inter, 'Segoe UI', Roboto, Arial, sans-serif",
  Roboto: "Roboto, Arial, sans-serif",
  Poppins: "Poppins, Arial, sans-serif",
  'Open Sans': "'Open Sans', Arial, sans-serif",
  Lato: "Lato, Arial, sans-serif",
  Montserrat: "Montserrat, Arial, sans-serif",
  Merriweather: "Merriweather, Georgia, serif",
}

const d = computed(() => ({ ...DESIGN_DEFAULTS, ...props.design }))
const p = computed(() => props.content.personal)
const twoColumn = computed(() => props.template === 'modern')
const minimal = computed(() => props.template === 'minimal')

const fullName = computed(() => [p.value.firstName, p.value.middleName, p.value.lastName].filter(Boolean).join(' '))
const photoBroken = ref(false)
watch(() => p.value.photoId, () => { photoBroken.value = false })
const photoSrc = computed(() => (p.value.photoId && !photoBroken.value ? mediaFileUrl(p.value.photoId) : ''))

const headerBg = computed(() => (minimal.value ? '#ffffff' : d.value.colorHeaderBg))
const headerText = computed(() => (minimal.value ? '#0f172a' : d.value.colorHeaderText))

const docStyle = computed(() => ({
  fontFamily: FONT_STACKS[d.value.font] || FONT_STACKS.Inter,
  fontSize: `${d.value.textSize}px`,
  zoom: props.zoom,
}))

const headerStyle = computed(() => ({
  backgroundColor: headerBg.value,
  color: headerText.value,
  textAlign: d.value.headerAlign,
  // v2: thin accent rule under the header band (replaces the plain edge)
  borderBottom: `4px solid ${d.value.colorAccent}`,
}))

const contactJustify = computed(() => ({
  left: 'flex-start',
  center: 'center',
  right: 'flex-end',
}[d.value.headerAlign] || 'flex-start'))

// v2: one heading colour everywhere (accent), same weight in sidebar and main column
const headingStyle = computed(() => ({
  color: d.value.colorAccent,
  fontSize: `${d.value.headingSize}px`,
  borderBottomColor: 'rgba(15, 23, 42, 0.12)',
}))

const headingAccentStyle = computed(() => ({ background: d.value.colorAccent }))

const sidebarStyle = computed(() => ({
  backgroundColor: d.value.colorSidebarBg,
  color: d.value.colorSidebarText,
}))

const itemTitleStyle = computed(() => ({ fontSize: `${d.value.textSize * 1.1}px` }))

function dateRange(item) {
  const end = item.end || (item.current ? 'Halen' : '')
  return [item.start, end].filter(Boolean).join(' — ')
}

// v2: show "example.com" instead of "https://www.example.com/path/"
function displayUrl(url) {
  return String(url || '').replace(/^https?:\/\//i, '').replace(/^www\./i, '').replace(/\/$/, '')
}

const sidebarEducation = computed(() => twoColumn.value && d.value.educationInSidebar)
const mainEducation = computed(() => !sidebarEducation.value)
const has = (key) => (props.content[key] || []).length > 0
</script>

<template>
  <div
    class="cv-document"
    :class="{ 'is-minimal': minimal, 'is-two-column': twoColumn }"
    :style="docStyle"
    :data-template="template"
  >
    <!-- Header (unchanged structure; QR block is identical to the original) -->
    <header class="cv-header" :style="headerStyle">
      <div v-if="photoSrc" class="cv-photo-wrap">
        <img
          :src="photoSrc"
          alt=""
          class="cv-photo"
          :style="{ width: d.photoSize + 'px', height: d.photoSize + 'px' }"
          @error="photoBroken = true"
        >
      </div>

      <div class="cv-header-text">
        <h1 class="cv-name" :style="{ fontSize: d.nameSize + 'px' }">{{ fullName || 'Ad Soyad' }}</h1>
        <h4 v-if="p.title" class="cv-title" :style="{ color: d.colorAccent, fontSize: d.textSize * 1.2 + 'px' }">
          {{ p.title }}
        </h4>
        <div class="cv-contact" :style="{ justifyContent: contactJustify }">
          <span v-if="p.location"><i class="bi bi-geo-alt-fill"></i> {{ p.location }}</span>
          <span v-if="p.email"><i class="bi bi-envelope-fill"></i> {{ p.email }}</span>
          <span v-if="p.phone"><i class="bi bi-telephone-fill"></i> {{ p.phone }}</span>
          <span v-if="p.website"><i class="bi bi-globe"></i> {{ displayUrl(p.website) }}</span>
          <span v-if="p.linkedin"><i class="bi bi-linkedin"></i> {{ p.linkedin }}</span>
          <span v-if="p.github"><i class="bi bi-github"></i> {{ p.github }}</span>
        </div>
      </div>

      <div v-if="p.showQr && p.qrLink" class="cv-qr-box">
        <img
          :src="qrImageUrl(p.qrLink)"
          alt="QR kod"
          :style="{ width: d.qrSize + 'px', height: d.qrSize + 'px' }"
        >
      </div>
    </header>

    <!-- Two-column body (modern) -->
    <div v-if="twoColumn" class="cv-body">
      <aside class="cv-sidebar" :style="sidebarStyle">
        <section v-if="has('languages')" class="cv-block">
          <h3 class="cv-heading" :style="headingStyle"><span class="cv-heading-accent" :style="headingAccentStyle"></span><i class="bi bi-translate"></i>Diller</h3>
          <div v-for="lang in content.languages" :key="lang.id" class="cv-bar-item">
            <div class="fw-semibold">{{ lang.name }}</div>
            <div class="cv-bar"><div :style="{ width: lang.level + '%', backgroundColor: d.colorAccent }"></div></div>
          </div>
        </section>

        <section v-if="has('technologies')" class="cv-block">
          <h3 class="cv-heading" :style="headingStyle"><span class="cv-heading-accent" :style="headingAccentStyle"></span><i class="bi bi-cpu"></i>Teknolojiler</h3>
          <div class="cv-chips">
            <span v-for="tech in content.technologies" :key="tech.id" class="cv-chip">{{ tech.name }}</span>
          </div>
        </section>

        <section v-if="has('skills')" class="cv-block">
          <h3 class="cv-heading" :style="headingStyle"><span class="cv-heading-accent" :style="headingAccentStyle"></span><i class="bi bi-stars"></i>Yetenekler</h3>
          <div v-for="skill in content.skills" :key="skill.id" class="cv-bar-item">
            <div class="fw-semibold">{{ skill.name }}</div>
            <div class="cv-bar"><div :style="{ width: skill.level + '%', backgroundColor: d.colorAccent }"></div></div>
          </div>
        </section>

        <section v-if="sidebarEducation && has('education')" class="cv-block">
          <h3 class="cv-heading" :style="headingStyle"><span class="cv-heading-accent" :style="headingAccentStyle"></span><i class="bi bi-mortarboard"></i>Eğitim</h3>
          <div v-for="edu in content.education" :key="edu.id" class="cv-edu">
            <img v-if="edu.logoId" :src="mediaFileUrl(edu.logoId)" alt="" class="cv-logo cv-logo-sm">
            <div>
              <div class="fw-bold">{{ edu.school }}</div>
              <div class="cv-muted">{{ edu.degree }}</div>
              <div v-if="edu.gpa" class="cv-muted">Mezuniyet notu: {{ edu.gpa }}</div>
              <div v-if="[edu.start, edu.end].filter(Boolean).length" class="cv-date">{{ [edu.start, edu.end].filter(Boolean).join(' — ') }}</div>
            </div>
          </div>
        </section>
      </aside>

      <main class="cv-main">
        <section v-if="content.summary" class="cv-block">
          <h3 class="cv-heading" :style="headingStyle"><span class="cv-heading-accent" :style="headingAccentStyle"></span><i class="bi bi-person-badge"></i>Profil</h3>
          <p class="cv-prose">{{ content.summary }}</p>
        </section>

        <section v-if="has('experience')" class="cv-block">
          <h3 class="cv-heading" :style="headingStyle"><span class="cv-heading-accent" :style="headingAccentStyle"></span><i class="bi bi-briefcase"></i>Deneyim</h3>
          <div v-for="exp in content.experience" :key="exp.id" class="cv-item">
            <div class="cv-logo-box">
              <img v-if="exp.logoId" :src="mediaFileUrl(exp.logoId)" alt="" class="cv-logo">
            </div>
            <div class="cv-item-body">
              <div class="cv-item-head">
                <h6 class="fw-bold mb-0" :style="itemTitleStyle">{{ exp.position }}</h6>
                <span v-if="dateRange(exp)" class="cv-date-badge">{{ dateRange(exp) }}</span>
              </div>
              <div class="fw-semibold mb-1 cv-company" :style="{ color: d.colorAccent }">
                {{ exp.company }}<span v-if="exp.location" class="cv-muted"> · {{ exp.location }}</span>
              </div>
              <p class="cv-prose mb-0">{{ exp.description }}</p>
            </div>
          </div>
        </section>

        <section v-if="mainEducation && has('education')" class="cv-block">
          <h3 class="cv-heading" :style="headingStyle"><span class="cv-heading-accent" :style="headingAccentStyle"></span><i class="bi bi-mortarboard"></i>Eğitim</h3>
          <div v-for="edu in content.education" :key="edu.id" class="cv-item">
            <div class="cv-logo-box">
              <img v-if="edu.logoId" :src="mediaFileUrl(edu.logoId)" alt="" class="cv-logo">
            </div>
            <div class="cv-item-body">
              <div class="cv-item-head">
                <h6 class="fw-bold mb-0" :style="itemTitleStyle">{{ edu.school }}</h6>
                <span v-if="[edu.start, edu.end].filter(Boolean).length" class="cv-date-badge">{{ [edu.start, edu.end].filter(Boolean).join(' — ') }}</span>
              </div>
              <div class="cv-muted">{{ edu.degree }}</div>
              <div v-if="edu.gpa" class="cv-muted">Mezuniyet notu: {{ edu.gpa }}</div>
            </div>
          </div>
        </section>
      </main>
    </div>

    <!-- Single-column body (professional, minimal) -->
    <div v-else class="cv-body-single">
      <section v-if="content.summary" class="cv-block">
        <h3 class="cv-heading" :style="headingStyle"><span class="cv-heading-accent" :style="headingAccentStyle"></span><i class="bi bi-person-badge"></i>Profil</h3>
        <p class="cv-prose">{{ content.summary }}</p>
      </section>

      <section v-if="has('experience')" class="cv-block">
        <h3 class="cv-heading" :style="headingStyle"><span class="cv-heading-accent" :style="headingAccentStyle"></span><i class="bi bi-briefcase"></i>Deneyim</h3>
        <div v-for="exp in content.experience" :key="exp.id" class="cv-item">
          <div class="cv-logo-box">
            <img v-if="exp.logoId" :src="mediaFileUrl(exp.logoId)" alt="" class="cv-logo">
          </div>
          <div class="cv-item-body">
            <div class="cv-item-head">
              <h6 class="fw-bold mb-0" :style="itemTitleStyle">{{ exp.position }}</h6>
              <span v-if="dateRange(exp)" class="cv-date-badge">{{ dateRange(exp) }}</span>
            </div>
            <div class="fw-semibold mb-1 cv-company" :style="{ color: d.colorAccent }">
              {{ exp.company }}<span v-if="exp.location" class="cv-muted"> · {{ exp.location }}</span>
            </div>
            <p class="cv-prose mb-0">{{ exp.description }}</p>
          </div>
        </div>
      </section>

      <section v-if="has('education')" class="cv-block">
        <h3 class="cv-heading" :style="headingStyle"><span class="cv-heading-accent" :style="headingAccentStyle"></span><i class="bi bi-mortarboard"></i>Eğitim</h3>
        <div v-for="edu in content.education" :key="edu.id" class="cv-item">
          <div class="cv-logo-box">
            <img v-if="edu.logoId" :src="mediaFileUrl(edu.logoId)" alt="" class="cv-logo">
          </div>
          <div class="cv-item-body">
            <div class="cv-item-head">
              <h6 class="fw-bold mb-0" :style="itemTitleStyle">{{ edu.school }}</h6>
              <span v-if="[edu.start, edu.end].filter(Boolean).length" class="cv-date-badge">{{ [edu.start, edu.end].filter(Boolean).join(' — ') }}</span>
            </div>
            <div class="cv-muted">{{ edu.degree }}</div>
              <div v-if="edu.gpa" class="cv-muted">Mezuniyet notu: {{ edu.gpa }}</div>
          </div>
        </div>
      </section>

      <div class="cv-skill-grid">
        <section v-if="has('skills')" class="cv-block">
          <h3 class="cv-heading" :style="headingStyle"><span class="cv-heading-accent" :style="headingAccentStyle"></span><i class="bi bi-stars"></i>Yetenekler</h3>
          <div v-for="skill in content.skills" :key="skill.id" class="cv-bar-item">
            <div class="fw-semibold">{{ skill.name }}</div>
            <div class="cv-bar"><div :style="{ width: skill.level + '%', backgroundColor: d.colorAccent }"></div></div>
          </div>
        </section>
        <section v-if="has('languages')" class="cv-block">
          <h3 class="cv-heading" :style="headingStyle"><span class="cv-heading-accent" :style="headingAccentStyle"></span><i class="bi bi-translate"></i>Diller</h3>
          <div v-for="lang in content.languages" :key="lang.id" class="cv-bar-item">
            <div class="fw-semibold">{{ lang.name }}</div>
            <div class="cv-bar"><div :style="{ width: lang.level + '%', backgroundColor: d.colorAccent }"></div></div>
          </div>
        </section>
      </div>

      <section v-if="has('technologies')" class="cv-block">
        <h3 class="cv-heading" :style="headingStyle"><span class="cv-heading-accent" :style="headingAccentStyle"></span><i class="bi bi-cpu"></i>Teknolojiler</h3>
        <div class="cv-chips">
          <span v-for="tech in content.technologies" :key="tech.id" class="cv-chip">{{ tech.name }}</span>
        </div>
      </section>
    </div>

    <!-- Extras: projects, certifications, references (new page when enabled) -->
    <section
      v-if="has('projects') || has('certifications') || has('references')"
      class="cv-extras"
      :class="{ 'cv-extras-newpage': d.newPageForExtras }"
    >
      <div v-if="has('projects')" class="cv-block">
        <h3 class="cv-heading" :style="headingStyle"><span class="cv-heading-accent" :style="headingAccentStyle"></span><i class="bi bi-kanban"></i>Projeler</h3>
        <div v-for="proj in content.projects" :key="proj.id" class="cv-item cv-item-split">
          <div class="cv-item-body">
            <h6 class="fw-bold mb-1" :style="itemTitleStyle">{{ proj.name }}</h6>
            <p class="cv-prose mb-1">{{ proj.description }}</p>
            <a v-if="proj.link" :href="proj.link" target="_blank" rel="noopener noreferrer" class="cv-link" :style="{ color: d.colorAccent }">{{ displayUrl(proj.link) }}</a>
          </div>
          <div v-if="proj.showQr && proj.link" class="cv-qr-small">
            <img :src="qrImageUrl(proj.link)" alt="Proje QR kodu">
          </div>
        </div>
      </div>

      <div v-if="has('certifications')" class="cv-block">
        <h3 class="cv-heading" :style="headingStyle"><span class="cv-heading-accent" :style="headingAccentStyle"></span><i class="bi bi-patch-check"></i>Sertifikalar</h3>
        <div v-for="cert in content.certifications" :key="cert.id" class="cv-item cv-item-split">
          <div class="cv-item-body">
            <h6 class="fw-bold mb-1" :style="itemTitleStyle">{{ cert.name }}</h6>
            <div class="cv-muted">{{ cert.issuer }}</div>
            <a v-if="cert.link" :href="cert.link" target="_blank" rel="noopener noreferrer" class="cv-link" :style="{ color: d.colorAccent }">Doğrula</a>
          </div>
          <div v-if="cert.showQr && cert.link" class="cv-qr-small">
            <img :src="qrImageUrl(cert.link)" alt="Sertifika QR kodu">
          </div>
        </div>
      </div>

      <div v-if="has('references')" class="cv-block">
        <h3 class="cv-heading" :style="headingStyle"><span class="cv-heading-accent" :style="headingAccentStyle"></span><i class="bi bi-people"></i>Referanslar</h3>
        <div class="cv-ref-grid">
          <div v-for="ref in content.references" :key="ref.id">
            <h6 class="fw-bold mb-1" :style="itemTitleStyle">{{ ref.name }}</h6>
            <div class="cv-muted">
              {{ ref.position }}<span v-if="ref.company"> @ {{ ref.company }}</span>
            </div>
            <div class="cv-small">
              <div v-if="ref.email"><i class="bi bi-envelope-fill"></i> {{ ref.email }}</div>
              <div v-if="ref.phone"><i class="bi bi-telephone-fill"></i> {{ ref.phone }}</div>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.cv-document {
  width: 210mm;
  min-height: 297mm;
  background: #fff;
  color: #1f2937;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
  display: flex;
  flex-direction: column;
  margin: 0 auto 2rem;
  box-sizing: border-box;
  overflow: hidden;
  line-height: 1.5;
}
.cv-header {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  padding: 1.75rem 2rem;
}
.cv-photo { border-radius: 8px; object-fit: cover; border: 3px solid rgba(255, 255, 255, 0.2); display: block; }
.cv-header-text { flex: 1 1 auto; min-width: 0; }
.cv-name { font-weight: 700; text-transform: uppercase; letter-spacing: 1px; margin: 0 0 0.25rem; line-height: 1.1; overflow-wrap: anywhere; }
.cv-title { margin: 0 0 0.75rem; font-weight: 600; }
.cv-contact { display: flex; flex-wrap: wrap; gap: 0.35rem 1.1rem; opacity: 0.92; font-size: 0.95em; }
.cv-contact i { margin-right: 0.25rem; }
/* QR block: position and size are part of the approved design. Do not change. */
.cv-qr-box { background: #fff; padding: 4px; border-radius: 6px; flex-shrink: 0; box-shadow: 0 1px 3px rgba(0,0,0,.15); }
.cv-qr-box img, .cv-qr-small img { display: block; }

/* Full-height columns: the sidebar background always reaches the bottom of the page. */
.cv-body { display: flex; align-items: stretch; flex-grow: 1; min-height: 0; }
.cv-sidebar { width: 32%; flex-shrink: 0; padding: 2rem; align-self: stretch; }
.cv-main { width: 68%; flex-grow: 1; padding: 2rem 2.5rem; background: #fff; }
.cv-body-single { padding: 1.5rem 2.5rem; flex-grow: 1; }
.cv-skill-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0 2rem; }
.cv-block { margin-bottom: 1.6rem; }
.cv-block-divided { border-top: 1px solid rgba(0, 0, 0, 0.1); margin-top: 2rem; padding-top: 1rem; }

/* Headings: one style everywhere. Thin rule, short accent bar, small icon. */
.cv-heading {
  position: relative;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  text-transform: uppercase;
  font-weight: 700;
  letter-spacing: 1.2px;
  border-bottom: 1px solid;
  padding-bottom: 0.45rem;
  margin: 0 0 1rem;
}
.cv-heading i { font-size: 0.95em; }
.cv-heading-accent {
  position: absolute;
  left: 0;
  bottom: -1px;
  width: 36px;
  height: 2px;
}

.cv-bar-item { margin-bottom: 0.8rem; }
.cv-bar { height: 5px; background: rgba(0, 0, 0, 0.1); border-radius: 999px; overflow: hidden; margin-top: 0.3rem; }
.cv-bar > div { height: 100%; border-radius: 999px; }
.cv-chips { display: flex; flex-wrap: wrap; gap: 0.45rem; }
.cv-chip {
  background: #fff;
  border: 1px solid rgba(0, 0, 0, 0.12);
  border-radius: 999px;
  padding: 2px 10px;
  font-weight: 500;
  font-size: 0.92em;
}

.cv-item { display: flex; align-items: flex-start; gap: 0.9rem; margin-bottom: 1.15rem; break-inside: avoid; }
.cv-item-split { justify-content: space-between; }
.cv-item-body { flex: 1 1 auto; min-width: 0; }
.cv-item-head { display: flex; justify-content: space-between; align-items: center; gap: 0.5rem; margin-bottom: 0.2rem; }
.cv-company { font-weight: 600; }
.cv-date-badge { font-size: 0.82em; border: 1px solid #d1d5db; border-radius: 999px; padding: 1px 10px; white-space: nowrap; background: #f8fafc; color: #334155; }
.cv-date { font-size: 0.85em; opacity: 0.75; }

/* Logo boxes: fixed square so rows line up whatever the logo shape. */
.cv-logo-box {
  width: 52px;
  height: 52px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 4px;
  box-sizing: border-box;
}
.cv-logo { max-width: 100%; max-height: 100%; object-fit: contain; display: block; }
.cv-logo-sm { width: 40px; height: 40px; object-fit: contain; border-radius: 6px; background: #fff; padding: 2px; flex-shrink: 0; }
.cv-edu { display: flex; gap: 0.75rem; align-items: flex-start; margin-bottom: 1rem; }

/* Body text: left aligned to avoid uneven word spacing. */
.cv-prose { white-space: pre-wrap; text-align: left; margin: 0; }
.cv-muted { opacity: 0.8; }
.cv-small { font-size: 0.9em; opacity: 0.85; }
.cv-link { font-weight: 600; text-decoration: none; word-break: break-all; }
.cv-qr-small { flex-shrink: 0; background: #fff; border: 1px solid #e5e7eb; border-radius: 6px; padding: 4px; }
.cv-qr-small img { width: 64px; height: 64px; }
.cv-extras { padding: 2rem 2.5rem; background: #fff; }
.cv-extras-newpage { break-before: page; page-break-before: always; }
.cv-ref-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem 2rem; }
.is-minimal .cv-heading { letter-spacing: 2px; }
.is-minimal .cv-main, .is-minimal .cv-body-single { padding-left: 2.5rem; }
@media print {
  .cv-document { zoom: 1 !important; box-shadow: none !important; margin: 0 !important; }
}
</style>
