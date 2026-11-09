import { describe, expect, it } from 'vitest'
import { analyzeCv } from '@/utils/cvAnalysis'
import { DESIGN_DEFAULTS } from '@/utils/cvContent'
import { SAMPLE_CV_CONTENT } from '@/utils/cvSample'

const empty = { personal: {}, summary: '', experience: [], education: [], skills: [], languages: [], technologies: [], projects: [], certifications: [], references: [] }

describe('CV analysis', () => {
  it('returns actionable issues for an empty CV without contacting external services', () => {
    const result = analyzeCv(empty, DESIGN_DEFAULTS)
    expect(result.score).toBeLessThan(30)
    expect(result.issues.length).toBeGreaterThan(8)
    expect(result.issues.some((item) => item.tab === 'personal')).toBe(true)
    expect(result.categories.map((item) => item.max)).toEqual([50, 30, 20])
  })

  it('rewards complete content, measurable outcomes and an ATS-friendly template', () => {
    const content = structuredClone(SAMPLE_CV_CONTENT)
    content.personal.website = 'https://denizyilmaz.com'
    content.skills.push({ id: 'extra-1', name: 'Prototipleme', level: 80 }, { id: 'extra-2', name: 'Figma', level: 90 })
    const result = analyzeCv(content, DESIGN_DEFAULTS, 'professional')
    expect(result.score).toBe(100)
    expect(result.level).toBe('excellent')
    expect(result.strengths).toContain('Ölçülebilir deneyim sonuçları')
  })

  it('warns about tiny text and low contrast', () => {
    const content = structuredClone(SAMPLE_CV_CONTENT)
    const result = analyzeCv(content, { ...DESIGN_DEFAULTS, textSize: 10, colorHeaderBg: '#ffffff', colorHeaderText: '#ffffff' })
    expect(result.issues.some((item) => item.title.includes('Metin boyutu'))).toBe(true)
    expect(result.issues.some((item) => item.title.includes('kontrast'))).toBe(true)
  })
})
