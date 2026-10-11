<script setup>
import { RouterLink } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()

const templates = [
  { name: 'Modern', text: 'Bold header and clean two-column grid.' },
  { name: 'Professional', text: 'Traditional single column with clear rules.' },
  { name: 'Minimal', text: 'Generous whitespace and light hierarchy.' },
  { name: 'Developer', text: 'Skills-first layout for engineers.' },
  { name: 'Academic', text: 'Publications and research first.' },
  { name: 'Compact', text: 'Dense layout for more content on fewer pages.' },
]

const faqs = [
  {
    q: 'Do I need to pay to use it?',
    a: 'No. The application has no payments, subscriptions or paid feature limits. Everything runs on your own computer.',
  },
  {
    q: 'Where is my data stored?',
    a: 'In the application database you run locally (SQLite by default, PostgreSQL optionally). Browser storage is used only for short-lived recovery drafts.',
  },
  {
    q: 'Is my document private?',
    a: 'Yes. Your documents and uploads are visible only to your signed-in account. Nothing is published unless you export it yourself.',
  },
  {
    q: 'What works today?',
    a: 'Accounts, a dashboard, CV and portfolio documents with rename, duplicate, delete, search, sorting and autosave, plus the template catalogue. The editors and exports are being built phase by phase.',
  },
]
</script>

<template>
  <div class="landing">
    <header class="landing-nav">
      <div class="container d-flex align-items-center justify-content-between py-3">
        <RouterLink :to="{ name: 'landing' }" class="brand-link" aria-label="Pro CV Maker Studio home">
          <span class="brand-mark" aria-hidden="true"><i class="bi bi-file-earmark-richtext"></i></span>
          <span class="fw-semibold">Pro CV Maker Studio</span>
        </RouterLink>
        <nav class="d-flex align-items-center gap-2" aria-label="Public navigation">
          <a href="#how-it-works" class="btn btn-link text-decoration-none d-none d-md-inline">How it works</a>
          <a href="#faq" class="btn btn-link text-decoration-none d-none d-md-inline">FAQ</a>
          <RouterLink v-if="!auth.isAuthenticated" :to="{ name: 'login' }" class="btn btn-outline-secondary btn-sm">Sign in</RouterLink>
          <RouterLink v-else :to="{ name: 'dashboard' }" class="btn btn-outline-secondary btn-sm">Go to dashboard</RouterLink>
        </nav>
      </div>
    </header>

    <section class="hero">
      <div class="container">
        <div class="row align-items-center g-5">
          <div class="col-lg-6">
            <p class="eyebrow">Local-first · No payments · Your data stays with you</p>
            <h1 class="hero-title">Create Your CV. Build Your Portfolio. Showcase Your Work.</h1>
            <p class="lead text-secondary">
              Create professional resumes, build personal websites, showcase projects and certificates, and share your work with custom QR codes.
            </p>
            <div class="d-flex flex-wrap gap-2 mt-4">
              <RouterLink :to="{ name: 'register', query: { next: '/cvs' } }" class="btn btn-primary btn-lg">Create Your CV</RouterLink>
              <RouterLink :to="{ name: 'register', query: { next: '/portfolios' } }" class="btn btn-outline-primary btn-lg">Build Your Portfolio</RouterLink>
              <a href="#templates" class="btn btn-light btn-lg">Explore Templates</a>
            </div>
          </div>
          <div class="col-lg-6">
            <figure class="hero-illustration" aria-label="Illustration of a CV page layout">
              <div class="illus-page">
                <div class="illus-head"></div>
                <div class="illus-line w-50"></div>
                <div class="illus-line w-75"></div>
                <div class="illus-block"></div>
                <div class="illus-line w-90"></div>
                <div class="illus-line w-60"></div>
              </div>
              <figcaption class="small text-secondary mt-2">Illustration only. The live A4 editor is part of Phase 2.</figcaption>
            </figure>
          </div>
        </div>
      </div>
    </section>

    <section id="templates" class="section">
      <div class="container">
        <h2 class="section-title">Template catalogue</h2>
        <p class="text-secondary">Ten CV and ten portfolio templates are planned. Each uses the same content, so switching templates never removes information.</p>
        <div class="row g-3">
          <div v-for="item in templates" :key="item.name" class="col-md-6 col-lg-4">
            <div class="card h-100 feature-card">
              <div class="card-body">
                <h3 class="h6 mb-1">{{ item.name }}</h3>
                <p class="small text-secondary mb-0">{{ item.text }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="section section-alt">
      <div class="container">
        <h2 class="section-title">What works today</h2>
        <div class="row g-3">
          <div class="col-md-4"><div class="card h-100 feature-card"><div class="card-body"><i class="bi bi-person-check feature-icon" aria-hidden="true"></i><h3 class="h6">Private accounts</h3><p class="small text-secondary mb-0">Registration, sign-in, password change and a local password-reset flow.</p></div></div></div>
          <div class="col-md-4"><div class="card h-100 feature-card"><div class="card-body"><i class="bi bi-speedometer2 feature-icon" aria-hidden="true"></i><h3 class="h6">Dashboard</h3><p class="small text-secondary mb-0">Your documents, recent work and activity, with search, sorting and paging.</p></div></div></div>
          <div class="col-md-4"><div class="card h-100 feature-card"><div class="card-body"><i class="bi bi-cloud-check feature-icon" aria-hidden="true"></i><h3 class="h6">Safe saving</h3><p class="small text-secondary mb-0">Autosave with a visible status, conflict detection and draft recovery after a refresh.</p></div></div></div>
        </div>
      </div>
    </section>

    <section id="how-it-works" class="section">
      <div class="container">
        <h2 class="section-title">How it works</h2>
        <ol class="steps">
          <li><strong>Create an account</strong> on your own machine.</li>
          <li><strong>Start a CV or portfolio</strong> from the dashboard and pick a template.</li>
          <li><strong>Your changes save automatically</strong>, and you can rename, duplicate or delete at any time.</li>
        </ol>
      </div>
    </section>

    <section id="faq" class="section section-alt">
      <div class="container">
        <h2 class="section-title">Frequently asked questions</h2>
        <div class="accordion" id="faq-accordion">
          <div v-for="(item, index) in faqs" :key="item.q" class="accordion-item">
            <h3 class="accordion-header">
              <button class="accordion-button" :class="{ collapsed: index > 0 }" type="button" data-bs-toggle="collapse" :data-bs-target="`#faq-${index}`" :aria-expanded="index === 0">
                {{ item.q }}
              </button>
            </h3>
            <div :id="`faq-${index}`" class="accordion-collapse collapse" :class="{ show: index === 0 }" data-bs-parent="#faq-accordion">
              <div class="accordion-body">{{ item.a }}</div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <footer class="landing-footer">
      <div class="container d-flex flex-wrap justify-content-between gap-2 py-4 small">
        <span>© Pro CV Maker Studio · Local-first application</span>
        <span class="text-secondary">No payments, subscriptions or billing.</span>
      </div>
    </footer>
  </div>
</template>
