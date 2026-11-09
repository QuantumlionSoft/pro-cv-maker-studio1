<script setup>
/* v2 preview: same structure, class names and QR block as the original.
 * Changes are visual only: full-height sidebar, consistent headings with icons,
 * left-aligned body text, fixed logo boxes, empty date badges hidden, shorter URLs. */
import { computed, ref, watch } from 'vue'
import { mediaFileUrl, qrImageUrl } from '@/services/media'
import { CV_SECTION_ORDER, DEFAULT_SECTION_TITLES, DESIGN_DEFAULTS } from '@/utils/cvContent'

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
const TWO_COLUMN_TEMPLATES = ['modern', 'executive', 'corporate', 'creative', 'developer']
const LIGHT_HEADER_TEMPLATES = ['minimal', 'corporate', 'academic', 'elegant', 'compact']
const twoColumn = computed(() => TWO_COLUMN_TEMPLATES.includes(props.template))
const minimal = computed(() => props.template === 'minimal')
const lightHeader = computed(() => LIGHT_HEADER_TEMPLATES.includes(props.template))

const fullName = computed(() => [p.value.firstName, p.value.middleName, p.value.lastName].filter(Boolean).join(' '))
const photoBroken = ref(false)
watch(() => p.value.photoId, () => { photoBroken.value = false })
const photoSrc = computed(() => (p.value.photoId && !photoBroken.value ? mediaFileUrl(p.value.photoId) : ''))

const headerBg = computed(() => (lightHeader.value ? '#ffffff' : d.value.colorHeaderBg))
const headerText = computed(() => (lightHeader.value ? '#172033' : d.value.colorHeaderText))

const docStyle = computed(() => ({
  fontFamily: FONT_STACKS[d.value.font] || FONT_STACKS.Inter,
  fontSize: `${d.value.textSize}px`,
  zoom: props.zoom,
  '--cv-accent': d.value.colorAccent,
}))

const headerStyle = computed(() => ({
  backgroundColor: headerBg.value,
  color: headerText.value,
  textAlign: d.value.headerAlign,
  borderBottom: `${['minimal', 'academic', 'elegant'].includes(props.template) ? 1 : props.template === 'corporate' ? 6 : 4}px solid ${d.value.colorAccent}`,
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
  const end = item.current ? 'Halen' : item.end
  return [item.start, end].filter(Boolean).join(' — ')
}

// v2: show "example.com" instead of "https://www.example.com/path/"
function displayUrl(url) {
  return String(url || '').replace(/^https?:\/\//i, '').replace(/^www\./i, '').replace(/\/$/, '')
}

const sidebarEducation = computed(() => twoColumn.value && d.value.educationInSidebar)
const mainEducation = computed(() => !sidebarEducation.value)
const sectionOrder = computed(() => {
  if (Array.isArray(props.content.sectionOrder)) return props.content.sectionOrder
  return props.template === 'academic'
    ? ['summary', 'education', 'experience', ...CV_SECTION_ORDER.filter((key) => !['summary', 'education', 'experience'].includes(key))]
    : CV_SECTION_ORDER
})
const visible = (key) => !(props.content.hiddenSections || []).includes(key)
const has = (key) => (props.content[key] || []).length > 0 && visible(key)
const sectionStyle = (key) => ({ order: Math.max(0, sectionOrder.value.indexOf(key)) })
const sectionTitle = (key) => props.content.sectionTitles?.[key]?.trim() || DEFAULT_SECTION_TITLES[key]
</script>

<template>
  <div
    class="cv-document"
    :class="{ 'is-minimal': minimal, 'is-two-column': twoColumn, 'is-light-header': lightHeader }"
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
        <div v-if="template === 'developer'" class="cv-header-kicker">&lt;CURRICULUM_VITAE /&gt;</div>
        <div v-else-if="['corporate', 'executive'].includes(template)" class="cv-header-kicker">PROFESYONEL CV</div>
        <div v-else-if="template === 'elegant'" class="cv-header-kicker">CURRICULUM VITAE</div>
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
        <section v-if="has('languages')" class="cv-block" data-section="languages" :style="sectionStyle('languages')">
          <h3 class="cv-heading" :style="headingStyle"><span class="cv-heading-accent" :style="headingAccentStyle"></span><i class="bi bi-translate"></i>{{ sectionTitle('languages') }}</h3>
          <div v-for="lang in content.languages" :key="lang.id" class="cv-bar-item">
            <div class="fw-semibold">{{ lang.name }}</div>
            <div class="cv-bar"><div :style="{ width: lang.level + '%', backgroundColor: d.colorAccent }"></div></div>
          </div>
        </section>

        <section v-if="has('technologies')" class="cv-block" data-section="technologies" :style="sectionStyle('technologies')">
          <h3 class="cv-heading" :style="headingStyle"><span class="cv-heading-accent" :style="headingAccentStyle"></span><i class="bi bi-cpu"></i>{{ sectionTitle('technologies') }}</h3>
          <div class="cv-chips">
            <span v-for="tech in content.technologies" :key="tech.id" class="cv-chip">{{ tech.name }}</span>
          </div>
        </section>

        <section v-if="has('skills')" class="cv-block" data-section="skills" :style="sectionStyle('skills')">
          <h3 class="cv-heading" :style="headingStyle"><span class="cv-heading-accent" :style="headingAccentStyle"></span><i class="bi bi-stars"></i>{{ sectionTitle('skills') }}</h3>
          <div v-for="skill in content.skills" :key="skill.id" class="cv-bar-item">
            <div class="fw-semibold">{{ skill.name }}</div>
            <div class="cv-bar"><div :style="{ width: skill.level + '%', backgroundColor: d.colorAccent }"></div></div>
          </div>
        </section>

        <section v-if="sidebarEducation && has('education')" class="cv-block" data-section="education" :style="sectionStyle('education')">
          <h3 class="cv-heading" :style="headingStyle"><span class="cv-heading-accent" :style="headingAccentStyle"></span><i class="bi bi-mortarboard"></i>{{ sectionTitle('education') }}</h3>
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
        <section v-if="content.summary && visible('summary')" class="cv-block" data-section="summary" :style="sectionStyle('summary')">
          <h3 class="cv-heading" :style="headingStyle"><span class="cv-heading-accent" :style="headingAccentStyle"></span><i class="bi bi-person-badge"></i>{{ sectionTitle('summary') }}</h3>
          <p class="cv-prose">{{ content.summary }}</p>
        </section>

        <section v-if="has('experience')" class="cv-block" data-section="experience" :style="sectionStyle('experience')">
          <h3 class="cv-heading" :style="headingStyle"><span class="cv-heading-accent" :style="headingAccentStyle"></span><i class="bi bi-briefcase"></i>{{ sectionTitle('experience') }}</h3>
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

        <section v-if="mainEducation && has('education')" class="cv-block" data-section="education" :style="sectionStyle('education')">
          <h3 class="cv-heading" :style="headingStyle"><span class="cv-heading-accent" :style="headingAccentStyle"></span><i class="bi bi-mortarboard"></i>{{ sectionTitle('education') }}</h3>
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
      <section v-if="content.summary && visible('summary')" class="cv-block" data-section="summary" :style="sectionStyle('summary')">
        <h3 class="cv-heading" :style="headingStyle"><span class="cv-heading-accent" :style="headingAccentStyle"></span><i class="bi bi-person-badge"></i>{{ sectionTitle('summary') }}</h3>
        <p class="cv-prose">{{ content.summary }}</p>
      </section>

      <section v-if="has('experience')" class="cv-block" data-section="experience" :style="sectionStyle('experience')">
        <h3 class="cv-heading" :style="headingStyle"><span class="cv-heading-accent" :style="headingAccentStyle"></span><i class="bi bi-briefcase"></i>{{ sectionTitle('experience') }}</h3>
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

      <section v-if="has('education')" class="cv-block" data-section="education" :style="sectionStyle('education')">
        <h3 class="cv-heading" :style="headingStyle"><span class="cv-heading-accent" :style="headingAccentStyle"></span><i class="bi bi-mortarboard"></i>{{ sectionTitle('education') }}</h3>
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
        <section v-if="has('skills')" class="cv-block" data-section="skills" :style="sectionStyle('skills')">
          <h3 class="cv-heading" :style="headingStyle"><span class="cv-heading-accent" :style="headingAccentStyle"></span><i class="bi bi-stars"></i>{{ sectionTitle('skills') }}</h3>
          <div v-for="skill in content.skills" :key="skill.id" class="cv-bar-item">
            <div class="fw-semibold">{{ skill.name }}</div>
            <div class="cv-bar"><div :style="{ width: skill.level + '%', backgroundColor: d.colorAccent }"></div></div>
          </div>
        </section>
        <section v-if="has('languages')" class="cv-block" data-section="languages" :style="sectionStyle('languages')">
          <h3 class="cv-heading" :style="headingStyle"><span class="cv-heading-accent" :style="headingAccentStyle"></span><i class="bi bi-translate"></i>{{ sectionTitle('languages') }}</h3>
          <div v-for="lang in content.languages" :key="lang.id" class="cv-bar-item">
            <div class="fw-semibold">{{ lang.name }}</div>
            <div class="cv-bar"><div :style="{ width: lang.level + '%', backgroundColor: d.colorAccent }"></div></div>
          </div>
        </section>
      </div>

      <section v-if="has('technologies')" class="cv-block" data-section="technologies" :style="sectionStyle('technologies')">
        <h3 class="cv-heading" :style="headingStyle"><span class="cv-heading-accent" :style="headingAccentStyle"></span><i class="bi bi-cpu"></i>{{ sectionTitle('technologies') }}</h3>
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
      <div v-if="has('projects')" class="cv-block" data-section="projects" :style="sectionStyle('projects')">
        <h3 class="cv-heading" :style="headingStyle"><span class="cv-heading-accent" :style="headingAccentStyle"></span><i class="bi bi-kanban"></i>{{ sectionTitle('projects') }}</h3>
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

      <div v-if="has('certifications')" class="cv-block" data-section="certifications" :style="sectionStyle('certifications')">
        <h3 class="cv-heading" :style="headingStyle"><span class="cv-heading-accent" :style="headingAccentStyle"></span><i class="bi bi-patch-check"></i>{{ sectionTitle('certifications') }}</h3>
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

      <div v-if="has('references')" class="cv-block" data-section="references" :style="sectionStyle('references')">
        <h3 class="cv-heading" :style="headingStyle"><span class="cv-heading-accent" :style="headingAccentStyle"></span><i class="bi bi-people"></i>{{ sectionTitle('references') }}</h3>
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
.cv-sidebar { width: 32%; flex-shrink: 0; padding: 2rem; align-self: stretch; display: flex; flex-direction: column; }
.cv-main { width: 68%; flex-grow: 1; padding: 2rem 2.5rem; background: #fff; display: flex; flex-direction: column; }
.cv-body-single { padding: 1.5rem 2.5rem; flex-grow: 1; display: flex; flex-direction: column; }
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
.cv-extras { padding: 2rem 2.5rem; background: #fff; display: flex; flex-direction: column; }
.cv-extras-newpage { break-before: page; page-break-before: always; }
.cv-ref-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem 2rem; }
.is-minimal .cv-heading { letter-spacing: 2px; }
.is-minimal .cv-main, .is-minimal .cv-body-single { padding-left: 2.5rem; }
.cv-header-kicker { margin-bottom: .45rem; color: var(--cv-accent); font-size: .72em; font-weight: 800; letter-spacing: 2px; line-height: 1.2; }

/* Executive — authoritative masthead, round portrait and spacious side rail. */
.cv-document[data-template='executive'] .cv-header { position: relative; padding: 2.25rem 2.5rem; }
.cv-document[data-template='executive'] .cv-photo { border-radius: 50%; border-width: 4px; }
.cv-document[data-template='executive'] .cv-name { letter-spacing: 1.8px; }
.cv-document[data-template='executive'] .cv-sidebar { width: 35%; padding: 2.25rem; }
.cv-document[data-template='executive'] .cv-main { width: 65%; padding: 2.25rem; }
.cv-document[data-template='executive'] .cv-heading { border-bottom: 0; letter-spacing: 1.6px; }
.cv-document[data-template='executive'] .cv-heading-accent { bottom: -5px; width: 28px; height: 3px; }
.cv-document[data-template='executive'] .cv-date-badge { border: 0; border-left: 2px solid var(--cv-accent); border-radius: 0; background: transparent; }

/* Corporate — crisp grid, compact rail and structured section headings. */
.cv-document[data-template='corporate'] .cv-header { padding: 2rem 2.25rem; }
.cv-document[data-template='corporate'] .cv-name { text-transform: none; letter-spacing: -.5px; }
.cv-document[data-template='corporate'] .cv-sidebar { width: 29%; padding: 1.75rem; }
.cv-document[data-template='corporate'] .cv-main { width: 71%; padding: 1.75rem 2.25rem; }
.cv-document[data-template='corporate'] .cv-heading { padding: .45rem .6rem; border: 0; border-left: 4px solid var(--cv-accent); background: #f8fafc; letter-spacing: .8px; }
.cv-document[data-template='corporate'] .cv-heading-accent { display: none; }
.cv-document[data-template='corporate'] .cv-chip { border-radius: 4px; }
.cv-document[data-template='corporate'] .cv-logo-box { border-radius: 4px; }

/* Creative — soft geometry and expressive typography without sacrificing readability. */
.cv-document[data-template='creative'] .cv-header { margin: 1.25rem 1.25rem 0; border: 0 !important; border-radius: 14px; }
.cv-document[data-template='creative'] .cv-name { text-transform: none; letter-spacing: -1px; font-weight: 800; }
.cv-document[data-template='creative'] .cv-photo { border-radius: 18px; }
.cv-document[data-template='creative'] .cv-body { margin-top: 1.25rem; }
.cv-document[data-template='creative'] .cv-sidebar { width: 36%; padding: 1.75rem; border-radius: 0 18px 0 0; }
.cv-document[data-template='creative'] .cv-main { width: 64%; padding: 1.75rem 2rem; }
.cv-document[data-template='creative'] .cv-heading { border: 0; letter-spacing: .4px; text-transform: none; font-size: 1.12em; }
.cv-document[data-template='creative'] .cv-heading-accent { width: 24px; height: 4px; bottom: -5px; border-radius: 5px; }
.cv-document[data-template='creative'] .cv-chip { border-color: var(--cv-accent); border-radius: 7px; }
.cv-document[data-template='creative'] .cv-date-badge { color: #fff; background: var(--cv-accent); border: 0; }

/* Developer — technical details, squared labels and code-inspired accents. */
.cv-document[data-template='developer'] .cv-header-kicker,
.cv-document[data-template='developer'] .cv-title,
.cv-document[data-template='developer'] .cv-chip { font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', monospace; }
.cv-document[data-template='developer'] .cv-name { text-transform: none; letter-spacing: -.6px; }
.cv-document[data-template='developer'] .cv-photo { border-radius: 6px; }
.cv-document[data-template='developer'] .cv-sidebar { width: 38%; padding: 1.75rem; }
.cv-document[data-template='developer'] .cv-main { width: 62%; padding: 1.75rem 2rem; }
.cv-document[data-template='developer'] .cv-heading { letter-spacing: .7px; }
.cv-document[data-template='developer'] .cv-chip { border-radius: 3px; border-color: var(--cv-accent); }
.cv-document[data-template='developer'] .cv-item { padding-left: .85rem; border-left: 2px solid var(--cv-accent); }
.cv-document[data-template='developer'] .cv-logo-box { width: 44px; height: 44px; border-radius: 4px; }
.cv-document[data-template='developer'] .cv-date-badge { border-radius: 4px; font-family: 'SFMono-Regular', Consolas, monospace; }

/* Academic — education leads, with restrained classical details. */
.cv-document[data-template='academic'] .cv-header { padding: 2.25rem 3rem 1.5rem; }
.cv-document[data-template='academic'] .cv-name,
.cv-document[data-template='academic'] .cv-heading { font-family: Merriweather, Georgia, serif; }
.cv-document[data-template='academic'] .cv-name { text-transform: none; letter-spacing: 0; }
.cv-document[data-template='academic'] .cv-body-single { display: flex; flex-direction: column; padding: 1.75rem 3rem; }
.cv-document[data-template='academic'] [data-section='summary'] { order: -2; }
.cv-document[data-template='academic'] [data-section='education'] { order: -1; }
.cv-document[data-template='academic'] .cv-heading { letter-spacing: .5px; text-transform: none; }
.cv-document[data-template='academic'] .cv-heading i { display: none; }
.cv-document[data-template='academic'] .cv-logo-box { border: 0; padding: 0; }
.cv-document[data-template='academic'] .cv-date-badge { border: 0; background: transparent; padding-right: 0; }

/* Elegant — editorial serif details and generous whitespace. */
.cv-document[data-template='elegant'] .cv-header { padding: 2.75rem 3rem 2rem; }
.cv-document[data-template='elegant'] .cv-name,
.cv-document[data-template='elegant'] .cv-heading { font-family: Merriweather, Georgia, serif; }
.cv-document[data-template='elegant'] .cv-name { text-transform: none; font-weight: 500; letter-spacing: -.5px; }
.cv-document[data-template='elegant'] .cv-photo { border-radius: 50%; border-color: #e7e5e4; }
.cv-document[data-template='elegant'] .cv-body-single { padding: 2rem 3rem; }
.cv-document[data-template='elegant'] .cv-heading { justify-content: center; border-bottom-color: #d6d3d1 !important; letter-spacing: 2px; font-weight: 500; }
.cv-document[data-template='elegant'] .cv-heading i { display: none; }
.cv-document[data-template='elegant'] .cv-heading-accent { left: calc(50% - 18px); }
.cv-document[data-template='elegant'] .cv-item-head { align-items: baseline; }
.cv-document[data-template='elegant'] .cv-date-badge { border: 0; background: transparent; font-style: italic; }

/* Compact — reduced vertical rhythm for content-heavy resumes. */
.cv-document[data-template='compact'] .cv-header { padding: 1.2rem 2rem; gap: 1rem; }
.cv-document[data-template='compact'] .cv-name { text-transform: none; letter-spacing: -.3px; }
.cv-document[data-template='compact'] .cv-title { margin-bottom: .4rem; }
.cv-document[data-template='compact'] .cv-body-single { padding: 1rem 2rem; }
.cv-document[data-template='compact'] .cv-block { margin-bottom: .85rem; }
.cv-document[data-template='compact'] .cv-heading { margin-bottom: .55rem; padding-bottom: .25rem; letter-spacing: .6px; }
.cv-document[data-template='compact'] .cv-item { margin-bottom: .65rem; gap: .65rem; }
.cv-document[data-template='compact'] .cv-logo-box { width: 40px; height: 40px; border-radius: 4px; }
.cv-document[data-template='compact'] .cv-prose { line-height: 1.35; }
.cv-document[data-template='compact'] .cv-bar-item { margin-bottom: .45rem; }
.cv-document[data-template='compact'] .cv-extras { padding: 1rem 2rem; }

/* Professional and minimal keep their established, ATS-friendly structures. */
.cv-document[data-template='professional'] .cv-heading-accent { width: 56px; }
.cv-document[data-template='professional'] .cv-body-single { padding-top: 1.75rem; }
.cv-document[data-template='minimal'] .cv-header { padding: 2.5rem 3rem 1.5rem; }
.cv-document[data-template='minimal'] .cv-name { text-transform: none; font-weight: 500; letter-spacing: -1px; }
.cv-document[data-template='minimal'] .cv-heading { border: 0; letter-spacing: 2px; font-weight: 600; }
.cv-document[data-template='minimal'] .cv-heading i,
.cv-document[data-template='minimal'] .cv-heading-accent { display: none; }
.cv-document[data-template='minimal'] .cv-body-single { padding: 1rem 3rem 2.5rem; }
.cv-document[data-template='minimal'] .cv-date-badge { border: 0; background: transparent; padding-right: 0; }
@media print {
  .cv-document { zoom: 1 !important; box-shadow: none !important; margin: 0 !important; }
}
</style>
