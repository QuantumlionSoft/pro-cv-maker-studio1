import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { ApiError } from '@/services/api'
import { useCvBuilder } from '@/composables/useCvBuilder'
import { blankItem, buildExport, parseImport, splitName } from '@/utils/cvContent'

const PROTOTYPE = {
  personal: {
    name: 'Kaan Ergün',
    title: 'Full Stack Developer',
    email: 'kaan@example.com',
    phone: '+90 500 000 00 00',
    location: 'Samsun',
    website: '',
    linkedin: 'kaan',
    github: 'kaan',
    photo: 'data:image/png;base64,AAAA',
    showQr: true,
    qrLink: 'https://www.linkedin.com/in/kaan',
  },
  summary: 'Özet',
  experience: [{ id: 1, company: 'Acme', position: 'Dev', start: '03.2024', end: 'Halen', description: 'x', logo: 'data:image/png;base64,BBBB' }],
  education: [{ id: 1, school: 'Uni', degree: 'BSc', start: '2016', end: '2020', logo: '' }],
  skills: [{ id: 1, name: 'Python', level: 85 }],
  languages: [{ id: 1, name: 'İngilizce', level: 80 }],
  hobbies: [{ id: 1, name: 'Docker' }, { id: 2, name: 'AWS' }],
  projects: [{ id: 1, name: 'P', description: 'd', link: 'https://github.com/x', showQr: true }],
  certifications: [],
  references: [],
  design: { font: 'Roboto', colorAccent: '#ff0000', headerAlign: 'center' },
}

describe('splitName', () => {
  it('splits first, middle and last names', () => {
    expect(splitName('Ayşe Nur Kaya')).toEqual({ firstName: 'Ayşe', middleName: 'Nur', lastName: 'Kaya' })
    expect(splitName('Kaan Ergün')).toEqual({ firstName: 'Kaan', middleName: '', lastName: 'Ergün' })
    expect(splitName('  ')).toEqual({ firstName: '', middleName: '', lastName: '' })
  })
})

describe('parseImport (prototype format)', () => {
  it('converts personal.name and hobbies, drops data-URL images with a warning', () => {
    const { content, design, warnings } = parseImport(JSON.stringify(PROTOTYPE))
    expect(content.personal).toMatchObject({ firstName: 'Kaan', lastName: 'Ergün', photoId: null, showQr: true })
    expect(content.technologies.map((t) => t.name)).toEqual(['Docker', 'AWS'])
    expect(content.experience[0]).toMatchObject({ company: 'Acme', current: true, end: 'Halen', logoId: null })
    expect(warnings.join(' ')).toMatch(/fotoğraf/i)
    expect(warnings.join(' ')).toMatch(/logo/i)
    expect(design).toMatchObject({ font: 'Roboto', colorAccent: '#ff0000', headerAlign: 'center', nameSize: 32 })
  })

  it('regenerates item ids so they are unique and server-safe', () => {
    const { content } = parseImport(JSON.stringify(PROTOTYPE))
    const ids = content.experience.concat(content.education, content.skills).map((i) => i.id)
    expect(new Set(ids).size).toBe(ids.length)
    ids.forEach((id) => expect(id).toMatch(/^[A-Za-z0-9_-]+$/))
  })

  it('accepts the prototype even when the design is missing', () => {
    const { design } = parseImport(JSON.stringify({ personal: { name: 'A B' } }))
    expect(design.font).toBe('Inter')
  })
})

describe('parseImport (own format and errors)', () => {
  it('reads { format, content, design } and drops photo references', () => {
    const exported = {
      format: 'pro-cv-maker-studio',
      content: { schemaVersion: 1, personal: { firstName: 'Ada', lastName: 'L', photoId: 9 }, summary: 's', experience: [], education: [], skills: [], languages: [], technologies: [], projects: [], certifications: [], references: [] },
      design: { colorAccent: '#123456' },
    }
    const { content, design, warnings } = parseImport(JSON.stringify(exported))
    expect(content.personal.photoId).toBeNull()
    expect(design.colorAccent).toBe('#123456')
    expect(warnings.length).toBe(1)
  })

  it('rejects invalid JSON and files without personal data', () => {
    expect(() => parseImport('{not json')).toThrow('Geçersiz JSON')
    expect(() => parseImport('[]')).toThrow('Geçersiz JSON')
    expect(() => parseImport('{"summary":"x"}')).toThrow('kişisel bilgiler')
  })
})

describe('buildExport', () => {
  it('omits photo and logo references and keeps format metadata', () => {
    const content = parseImport(JSON.stringify(PROTOTYPE)).content
    content.personal.photoId = 5
    content.experience[0].logoId = 6
    const out = buildExport({ title: 'T', template: 'modern', content, design: { font: 'Inter' } })
    expect(out.format).toBe('pro-cv-maker-studio')
    expect(out.content.personal.photoId).toBeNull()
    expect(out.content.experience[0]).not.toHaveProperty('logoId')
    expect(out.title).toBe('T')
  })
})

describe('blankItem', () => {
  it('gives every new item a unique id', () => {
    const ids = [blankItem('skills'), blankItem('skills'), blankItem('projects')].map((i) => i.id)
    expect(new Set(ids).size).toBe(3)
  })
  it('throws for unknown sections', () => {
    expect(() => blankItem('nope')).toThrow()
  })
})

describe('useCvBuilder autosave', () => {
  const doc = (version = 1) => ({
    id: 1,
    title: 'Backend CV',
    template: 'modern',
    version,
    content: { personal: { firstName: 'A' }, summary: '', experience: [] },
    design: { colorAccent: '#000000' },
  })

  let api
  beforeEach(() => {
    vi.useFakeTimers()
    api = {
      get: vi.fn(async () => doc()),
      update: vi.fn(async (id, body) => ({ ...doc(body.version + 1), title: body.title })),
    }
  })
  afterEach(() => {
    vi.useRealTimers()
  })

  it('loads, marks dirty on edit and saves once after the debounce with the version', async () => {
    const b = useCvBuilder({ id: 1, api, scheduleDelay: 800 })
    await b.load()
    expect(b.status.value).toBe('ready')

    b.title.value = 'New title'
    await vi.advanceTimersByTimeAsync(10)
    expect(b.status.value).toBe('dirty')

    await vi.advanceTimersByTimeAsync(800)
    expect(api.update).toHaveBeenCalledTimes(1)
    expect(api.update.mock.calls[0][1]).toMatchObject({ title: 'New title', version: 1 })
    expect(b.status.value).toBe('saved')
    expect(b.lastSavedAt.value).toBeInstanceOf(Date)
  })

  it('pauses autosave on a conflict and never overwrites the server copy', async () => {
    api.update.mockRejectedValueOnce(new ApiError('conflict', { status: 409 }))
    const b = useCvBuilder({ id: 1, api, scheduleDelay: 800 })
    await b.load()
    b.title.value = 'Local edit'
    await vi.advanceTimersByTimeAsync(900)
    expect(b.status.value).toBe('conflict')

    b.content.value.summary = 'more edits'
    await vi.advanceTimersByTimeAsync(2000)
    expect(api.update).toHaveBeenCalledTimes(1)
  })

  it('reports validation errors from the server and keeps local edits', async () => {
    api.update.mockRejectedValueOnce(new ApiError('bad', { status: 400, fields: { content: ['personal.website: must be an http or https link.'] } }))
    const b = useCvBuilder({ id: 1, api, scheduleDelay: 800 })
    await b.load()
    b.content.value.personal.website = 'javascript:alert(1)'
    await vi.advanceTimersByTimeAsync(900)
    expect(b.status.value).toBe('error')
    expect(b.errorMessage.value).toContain('personal.website')
    expect(b.content.value.personal.website).toBe('javascript:alert(1)')
  })

  it('shows not_found for a missing CV', async () => {
    api.get.mockRejectedValueOnce(new ApiError('nope', { status: 404 }))
    const b = useCvBuilder({ id: 99, api })
    await b.load()
    expect(b.status.value).toBe('not_found')
  })

  it('does not persist anything to localStorage', async () => {
    const spy = vi.spyOn(Storage.prototype, 'setItem')
    const b = useCvBuilder({ id: 1, api, scheduleDelay: 800 })
    await b.load()
    b.title.value = 'x'
    await vi.advanceTimersByTimeAsync(900)
    expect(spy).not.toHaveBeenCalled()
    spy.mockRestore()
  })
})
