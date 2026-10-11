/**
 * CV content helpers: blank items, JSON import/export and conversion of the
 * prototype's `personal.name` format. The server remains the authority for
 * validation; these helpers only shape data for the editor.
 */

export const DESIGN_DEFAULTS = {
  font: 'Inter',
  colorAccent: '#3b82f6',
  colorHeaderBg: '#1e293b',
  colorHeaderText: '#ffffff',
  colorSidebarBg: '#f1f5f9',
  colorSidebarText: '#334155',
  educationInSidebar: false,
  headerAlign: 'left',
  nameSize: 32,
  headingSize: 16,
  textSize: 13,
  photoSize: 140,
  qrSize: 80,
  newPageForExtras: true,
}

export const EXPORT_FORMAT = 'pro-cv-maker-studio'

let seq = 0
/** Client-side item id. Only [A-Za-z0-9_-] so the server keeps it unchanged. */
export function newItemId() {
  seq += 1
  return `i${Date.now().toString(36)}${seq.toString(36)}${Math.random().toString(36).slice(2, 6)}`
}

export function blankItem(section) {
  const id = newItemId()
  switch (section) {
    case 'experience':
      return { id, company: '', position: '', location: '', start: '', end: '', current: false, description: '', logoId: null }
    case 'education':
      return { id, school: '', degree: '', gpa: '', start: '', end: '', logoId: null }
    case 'skills':
    case 'languages':
      return { id, name: '', level: 50 }
    case 'technologies':
      return { id, name: '' }
    case 'projects':
      return { id, name: '', description: '', link: '', showQr: true }
    case 'certifications':
      return { id, name: '', issuer: '', link: '', showQr: true }
    case 'references':
      return { id, name: '', position: '', company: '', email: '', phone: '' }
    default:
      throw new Error(`Unknown section: ${section}`)
  }
}

/** Split a full name into first / middle / last parts. */
export function splitName(full) {
  const parts = String(full || '').trim().split(/\s+/).filter(Boolean)
  if (parts.length === 0) return { firstName: '', middleName: '', lastName: '' }
  if (parts.length === 1) return { firstName: parts[0], middleName: '', lastName: '' }
  return {
    firstName: parts[0],
    middleName: parts.slice(1, -1).join(' '),
    lastName: parts[parts.length - 1],
  }
}

function text(value) {
  return typeof value === 'string' ? value : value == null ? '' : String(value)
}

function level(value) {
  const n = Math.round(Number(value) / 10) * 10
  if (!Number.isFinite(n)) return 50
  return Math.min(100, Math.max(10, n))
}

function withIds(list, mapper, section) {
  if (!Array.isArray(list)) return []
  return list
    .filter((raw) => raw && typeof raw === 'object')
    .map((raw) => ({ ...blankItem(section), ...mapper(raw), id: newItemId() }))
}

/** Convert the prototype's JSON (personal.name, hobbies, data-URL photos) into editor content. */
export function convertPrototypeContent(data) {
  const warnings = []
  const p = data.personal || {}
  if (p.photo) warnings.push('Prototip fotoğrafı içe aktarılamadı; fotoğrafı yeniden yükleyin.')
  const logos = [...(data.experience || []), ...(data.education || [])].filter((e) => e && e.logo)
  if (logos.length) warnings.push('Prototip logoları içe aktarılamadı; logoları yeniden yükleyin.')

  const content = {
    personal: {
      ...splitName(p.name),
      title: text(p.title),
      email: text(p.email),
      phone: text(p.phone),
      location: text(p.location),
      website: text(p.website),
      linkedin: text(p.linkedin),
      github: text(p.github),
      photoId: null,
      showQr: Boolean(p.showQr),
      qrLink: text(p.qrLink),
    },
    summary: text(data.summary),
    experience: withIds(data.experience, (e) => ({
      company: text(e.company),
      position: text(e.position),
      start: text(e.start),
      end: text(e.end),
      current: /^halen$/i.test(text(e.end).trim()),
      description: text(e.description),
    }), 'experience'),
    education: withIds(data.education, (e) => ({
      school: text(e.school),
      degree: text(e.degree),
      gpa: text(e.gpa),
      start: text(e.start),
      end: text(e.end),
    }), 'education'),
    skills: withIds(data.skills, (s) => ({ name: text(s.name), level: level(s.level) }), 'skills'),
    languages: withIds(data.languages, (s) => ({ name: text(s.name), level: level(s.level) }), 'languages'),
    technologies: withIds(data.hobbies || data.technologies, (s) => ({ name: text(s.name) }), 'technologies'),
    projects: withIds(data.projects, (x) => ({
      name: text(x.name), description: text(x.description), link: text(x.link), showQr: Boolean(x.showQr),
    }), 'projects'),
    certifications: withIds(data.certifications, (x) => ({
      name: text(x.name), issuer: text(x.issuer), link: text(x.link), showQr: Boolean(x.showQr),
    }), 'certifications'),
    references: withIds(data.references, (x) => ({
      name: text(x.name), position: text(x.position), company: text(x.company), email: text(x.email), phone: text(x.phone),
    }), 'references'),
  }
  return { content, warnings }
}

function pickDesign(raw) {
  const design = { ...DESIGN_DEFAULTS }
  if (!raw || typeof raw !== 'object') return design
  for (const key of Object.keys(DESIGN_DEFAULTS)) {
    if (raw[key] !== undefined && raw[key] !== null) design[key] = raw[key]
  }
  return design
}

/**
 * Parse an imported JSON document. Accepts this app's export format
 * ({ format, content, design }), bare content objects, and the prototype's format.
 * Throws Error with a Turkish message when the file is not usable.
 */
export function parseImport(jsonText) {
  let root
  try {
    root = JSON.parse(jsonText)
  } catch {
    throw new Error('Geçersiz JSON dosyası.')
  }
  if (!root || typeof root !== 'object' || Array.isArray(root)) {
    throw new Error('Geçersiz JSON dosyası.')
  }
  const source = root.content && typeof root.content === 'object' ? root.content : root
  if (!source.personal || typeof source.personal !== 'object') {
    throw new Error('Dosyada kişisel bilgiler bulunamadı.')
  }

  const isPrototype = 'name' in source.personal && !('firstName' in source.personal)
  if (isPrototype) {
    const { content, warnings } = convertPrototypeContent(source)
    return { content, design: pickDesign(root.design), warnings }
  }

  // Our own format: ids are regenerated so that imported duplicates cannot collide.
  const content = {
    ...source,
    personal: { ...source.personal, photoId: null },
  }
  for (const section of ['experience', 'education', 'skills', 'languages', 'technologies', 'projects', 'certifications', 'references']) {
    content[section] = Array.isArray(source[section])
      ? source[section].filter((item) => item && typeof item === 'object').map((item) => ({ ...item, id: newItemId() }))
      : []
  }
  const warnings = []
  const hadImages = source.personal.photoId || [...(source.experience || []), ...(source.education || [])].some((i) => i && i.logoId)
  if (hadImages) warnings.push('Fotoğraflar JSON dosyasına dahil değildir; yeniden yükleyin.')
  return { content, design: pickDesign(root.design), warnings }
}

/** Export: photo/logo references are omitted because they point at this account's private files. */
export function buildExport({ title, template, content, design }) {
  const strip = (item) => {
    const { logoId, ...rest } = item
    return rest
  }
  const sections = ['experience', 'education', 'skills', 'languages', 'technologies', 'projects', 'certifications', 'references']
  const out = {
    ...content,
    personal: { ...content.personal, photoId: null },
  }
  for (const section of sections) out[section] = (content[section] || []).map(strip)
  return {
    format: EXPORT_FORMAT,
    schemaVersion: content.schemaVersion || 1,
    title,
    template,
    content: out,
    design,
  }
}
