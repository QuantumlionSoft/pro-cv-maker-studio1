import { describe, expect, it } from 'vitest'
import JSZip from 'jszip'
import { createCvBackup, parsePlainTextCv } from '@/utils/cvImport'
import { DESIGN_DEFAULTS } from '@/utils/cvContent'
import { SAMPLE_CV_CONTENT } from '@/utils/cvSample'

const SAMPLE = `Ada Lovelace
Analytical Engine Engineer
ada@example.com
+90 555 123 45 67
https://github.com/ada

Profil
Sayılar ve algoritmalar üzerine çalışan bir mühendis.

Deneyim
Senior Engineer | Analytical Co | London
2020 - Halen
Ekip verimliliğini %30 artırdım.

Eğitim
BSc Mathematics | University of London
2016 - 2020

Yetenekler
Python, JavaScript, Vue

Diller
Türkçe, İngilizce

Projeler
Analysis Engine | https://example.com
İlk algoritma çalışması.`

describe('plain text CV import', () => {
  it('extracts personal details and common CV sections', () => {
    const result = parsePlainTextCv(SAMPLE)
    expect(result.content.personal).toMatchObject({ firstName: 'Ada', lastName: 'Lovelace', title: 'Analytical Engine Engineer', email: 'ada@example.com' })
    expect(result.content.personal.github).toContain('github.com')
    expect(result.content.summary).toContain('algoritmalar')
    expect(result.content.experience[0]).toMatchObject({ position: 'Senior Engineer', company: 'Analytical Co' })
    expect(result.content.experience[0].description).toContain('%30')
    expect(result.content.education[0].school).toBe('University of London')
    expect(result.content.skills.map((item) => item.name)).toEqual(['Python', 'JavaScript', 'Vue'])
    expect(result.content.projects[0].link).toBe('https://example.com')
    expect(result.warnings[0]).toContain('kontrol')
  })

  it('rejects files without enough text', () => {
    expect(() => parsePlainTextCv('')).toThrow('yeterli metin')
  })

  it('creates a portable ZIP with CV data and a manifest', async () => {
    const result = await createCvBackup({ title: 'Deneme CV', template: 'modern', content: SAMPLE_CV_CONTENT, design: DESIGN_DEFAULTS })
    expect(result.imageCount).toBe(0)
    const zip = await JSZip.loadAsync(result.blob)
    const backup = JSON.parse(await zip.file('cv.json').async('string'))
    const manifest = JSON.parse(await zip.file('manifest.json').async('string'))
    expect(backup.title).toBe('Deneme CV')
    expect(backup.content.personal.firstName).toBe('Deniz')
    expect(manifest.images).toEqual([])
    expect(zip.file('BENIOKU.txt')).not.toBeNull()
  })
})
