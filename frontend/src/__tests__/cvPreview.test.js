import { describe, expect, it } from 'vitest'
import { mount } from '@vue/test-utils'
import CvPreview from '@/components/cv/CvPreview.vue'
import { DESIGN_DEFAULTS } from '@/utils/cvContent'

const content = {
  personal: { firstName: 'Ada', middleName: '', lastName: 'Lovelace', title: 'Software Engineer', photoId: null, showQr: false },
  summary: 'Deneyimli yazılım geliştirici.',
  experience: [{ id: 'e1', company: 'Analytical Engines', position: 'Engineer', start: '2020', end: '', current: true, description: 'Geliştirme', logoId: null }],
  education: [{ id: 'ed1', school: 'University', degree: 'BSc', start: '2016', end: '2020', logoId: null }],
  skills: [{ id: 's1', name: 'JavaScript', level: 90 }],
  languages: [{ id: 'l1', name: 'Türkçe', level: 100 }],
  technologies: [{ id: 't1', name: 'Vue' }],
  projects: [], certifications: [], references: [],
}

const templates = ['modern', 'professional', 'minimal', 'executive', 'corporate', 'creative', 'developer', 'academic', 'elegant', 'compact']

describe('CvPreview template renderers', () => {
  it.each(templates)('renders the complete content with the %s template', (template) => {
    const wrapper = mount(CvPreview, { props: { content, design: DESIGN_DEFAULTS, template, zoom: 1 } })
    expect(wrapper.attributes('data-template')).toBe(template)
    expect(wrapper.text()).toContain('Ada Lovelace')
    expect(wrapper.text()).toContain('Analytical Engines')
    expect(wrapper.text()).toContain('University')
    expect(wrapper.text()).toContain('JavaScript')
    expect(wrapper.find('.cv-document').exists()).toBe(true)
  })

  it.each(['modern', 'executive', 'corporate', 'creative', 'developer'])('uses a two-column body for %s', (template) => {
    const wrapper = mount(CvPreview, { props: { content, design: DESIGN_DEFAULTS, template } })
    expect(wrapper.find('.cv-body').exists()).toBe(true)
    expect(wrapper.find('.cv-sidebar').exists()).toBe(true)
  })

  it('honours hidden sections, custom titles and section ordering', () => {
    const custom = structuredClone(content)
    custom.hiddenSections = ['skills']
    custom.sectionTitles = { experience: 'Çalışma Geçmişi' }
    custom.sectionOrder = ['education', 'experience', 'summary', 'skills', 'languages', 'technologies', 'projects', 'certifications', 'references']
    const wrapper = mount(CvPreview, { props: { content: custom, design: DESIGN_DEFAULTS, template: 'professional' } })
    expect(wrapper.text()).toContain('Çalışma Geçmişi')
    expect(wrapper.find('[data-section="skills"]').exists()).toBe(false)
    expect(wrapper.find('[data-section="education"]').attributes('style')).toContain('order: 0')
  })

  it('always labels a current role as Halen even when an old end date remains', () => {
    const stale = structuredClone(content)
    stale.experience[0].end = '2024'
    const wrapper = mount(CvPreview, { props: { content: stale, design: DESIGN_DEFAULTS, template: 'professional' } })
    expect(wrapper.text()).toContain('2020 — Halen')
    expect(wrapper.text()).not.toContain('2020 — 2024')
  })
})
