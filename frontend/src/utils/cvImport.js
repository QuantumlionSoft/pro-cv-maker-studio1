import { blankItem, DESIGN_DEFAULTS, EXPORT_FORMAT, CV_SECTION_ORDER, parseImport, splitName } from './cvContent'
import { mediaFileUrl } from '@/services/media'

const SECTION_PATTERNS = {
  summary: /^(profil|özet|hakkımda|summary|profile|about)/i,
  experience: /^(deneyim|iş deneyimi|çalışma geçmişi|experience|employment)/i,
  education: /^(eğitim|eğitim bilgileri|education)/i,
  skills: /^(yetenekler|beceriler|skills)/i,
  languages: /^(diller|yabancı dil|languages)/i,
  technologies: /^(teknolojiler|araçlar|technologies|tools)/i,
  projects: /^(projeler|projects)/i,
  certifications: /^(sertifikalar|certifications|certificates)/i,
  references: /^(referanslar|references)/i,
}

function sectionKey(line) {
  const clean = line.trim().replace(/:$/, '')
  if (clean.length > 45) return null
  return Object.entries(SECTION_PATTERNS).find(([, pattern]) => pattern.test(clean))?.[0] || null
}

function valuesFromLines(lines, level = 70) {
  return lines.flatMap((line) => line.replace(/^[•●▪*-]\s*/, '').split(/[,;|]/))
    .map((value) => value.trim()).filter((value) => value && value.length <= 100).slice(0, 30)
    .map((name) => ({ ...blankItem('skills'), name, level }))
}

function recordsFromLines(lines, section) {
  const records = []
  let current = null
  for (const raw of lines) {
    const line = raw.trim()
    if (!line) continue
    const isHeading = /^[•●▪*-]/.test(line) || line.includes('|')
    if (isHeading || !current) {
      if (current) records.push(current)
      current = { ...blankItem(section) }
      const clean = line.replace(/^[•●▪*-]\s*/, '')
      const parts = clean.split('|').map((part) => part.trim()).filter(Boolean)
      if (section === 'experience') {
        current.position = parts[0] || clean
        current.company = parts[1] || ''
        current.location = parts[2] || ''
        const date = clean.match(/(?:19|20)\d{2}.{0,30}(?:(?:19|20)\d{2}|halen|present)/i)?.[0]
        if (date) current.description = date
      } else if (section === 'education') {
        current.degree = parts[0] || clean
        current.school = parts[1] || ''
      } else {
        current.name = parts[0] || clean
        if (section === 'certifications') current.issuer = parts[1] || ''
        if (section === 'projects') current.link = parts.find((part) => /^https?:\/\//i.test(part)) || ''
      }
    } else if (section === 'experience' || section === 'projects') {
      current.description = [current.description, line.replace(/^[•●▪*-]\s*/, '')].filter(Boolean).join('\n')
    } else if (section === 'education' && !current.school) current.school = line
    else if (section === 'certifications' && !current.issuer) current.issuer = line
  }
  if (current) records.push(current)
  return records.slice(0, 30)
}

/** Conservative text extraction. Users are explicitly asked to review the result. */
export function parsePlainTextCv(text, template = 'professional') {
  const lines = String(text || '').replace(/\r/g, '').split('\n').map((line) => line.trim())
  const meaningful = lines.filter(Boolean)
  if (meaningful.length < 2) throw new Error('Dosyadan yeterli metin okunamadı. PDF’nin metin içerdiğinden emin olun.')
  const email = text.match(/[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}/)?.[0] || ''
  const phone = text.match(/(?:\+90|0)?\s*\(?\d{3}\)?[\s.-]*\d{3}[\s.-]*\d{2}[\s.-]*\d{2}/)?.[0] || ''
  const urls = text.match(/https?:\/\/[^\s)]+/gi) || []
  const firstLine = meaningful.find((line) => !/^(cv|curriculum vitae|özgeçmiş)$/i.test(line) && !line.includes('@')) || 'Ad Soyad'
  const nameParts = splitName(firstLine.slice(0, 120))
  const firstIndex = meaningful.indexOf(firstLine)
  const possibleTitle = meaningful[firstIndex + 1]
  const title = possibleTitle && possibleTitle.length < 100 && !sectionKey(possibleTitle) && !possibleTitle.includes('@') && !/^https?:/i.test(possibleTitle) ? possibleTitle : ''

  const sections = {}
  let current = null
  for (const line of meaningful) {
    const key = sectionKey(line)
    if (key) { current = key; sections[current] = []; continue }
    if (current) sections[current].push(line)
  }
  const content = {
    schemaVersion: 2,
    sectionOrder: [...CV_SECTION_ORDER],
    hiddenSections: [],
    sectionTitles: {},
    personal: {
      ...nameParts,
      title,
      email,
      phone,
      location: '',
      website: urls.find((url) => !/linkedin\.com|github\.com/i.test(url)) || '',
      linkedin: urls.find((url) => /linkedin\.com/i.test(url)) || '',
      github: urls.find((url) => /github\.com/i.test(url)) || '',
      photoId: null,
      showQr: false,
      qrLink: '',
    },
    summary: (sections.summary || []).join('\n').slice(0, 4000),
    experience: recordsFromLines(sections.experience || [], 'experience'),
    education: recordsFromLines(sections.education || [], 'education'),
    skills: valuesFromLines(sections.skills || [], 70),
    languages: valuesFromLines(sections.languages || [], 70),
    technologies: valuesFromLines(sections.technologies || [], 70).map(({ id, name }) => ({ id, name })),
    projects: recordsFromLines(sections.projects || [], 'projects'),
    certifications: recordsFromLines(sections.certifications || [], 'certifications'),
    references: [],
  }
  const recordCount = ['experience', 'education', 'skills', 'languages', 'technologies', 'projects', 'certifications'].reduce((sum, key) => sum + content[key].length, 0)
  return {
    content,
    design: { ...DESIGN_DEFAULTS },
    template,
    warnings: [`Dosyadan ${recordCount} kayıt çıkarıldı. Otomatik ayrıştırma sınırlıdır; ad, tarihler ve bölümleri kaydetmeden önce kontrol edin.`],
  }
}

async function extractPdf(file) {
  const pdfjs = await import('pdfjs-dist')
  const worker = await import('pdfjs-dist/build/pdf.worker.min.mjs?url')
  pdfjs.GlobalWorkerOptions.workerSrc = worker.default
  const document = await pdfjs.getDocument({ data: new Uint8Array(await file.arrayBuffer()) }).promise
  const pages = []
  for (let number = 1; number <= Math.min(document.numPages, 30); number += 1) {
    const page = await document.getPage(number)
    const text = await page.getTextContent()
    const lines = []
    let line = []
    let previousY = null
    for (const item of text.items) {
      const y = item.transform?.[5] ?? previousY
      if (previousY !== null && y !== null && Math.abs(y - previousY) > 4 && line.length) {
        lines.push(line.join(' '))
        line = []
      }
      line.push(item.str)
      previousY = y
      if (item.hasEOL && line.length) { lines.push(line.join(' ')); line = []; previousY = null }
    }
    if (line.length) lines.push(line.join(' '))
    pages.push(lines.join('\n'))
  }
  return pages.join('\n')
}

async function extractDocx(file) {
  const mammoth = await import('mammoth')
  const result = await mammoth.extractRawText({ arrayBuffer: await file.arrayBuffer() })
  return result.value
}

export async function parseDocumentFile(file) {
  const extension = file.name.split('.').pop()?.toLowerCase()
  if (file.size > 20 * 1024 * 1024) throw new Error('Dosya boyutu en fazla 20 MB olabilir.')
  if (extension === 'json') return parseImport(await file.text())
  if (extension === 'txt') return parsePlainTextCv(await file.text())
  if (extension === 'pdf') return parsePlainTextCv(await extractPdf(file))
  if (extension === 'docx') return parsePlainTextCv(await extractDocx(file))
  if (extension === 'zip') {
    const JSZip = (await import('jszip')).default
    const zip = await JSZip.loadAsync(file)
    const jsonEntry = zip.file('cv.json') || zip.file(/\.json$/i)[0]
    if (!jsonEntry) throw new Error('ZIP içinde cv.json bulunamadı.')
    const rawBackup = JSON.parse(await jsonEntry.async('string'))
    const parsed = parseImport(JSON.stringify(rawBackup))
    const sourceContent = rawBackup.content || rawBackup
    parsed.content.personal.photoId = sourceContent.personal?.photoId || null
    for (const section of ['experience', 'education']) {
      ;(parsed.content[section] || []).forEach((item, index) => { item.logoId = sourceContent[section]?.[index]?.logoId || null })
    }
    const manifestEntry = zip.file('manifest.json')
    const manifest = manifestEntry ? JSON.parse(await manifestEntry.async('string')) : { images: [] }
    const media = []
    for (const image of manifest.images || []) {
      const entry = zip.file(image.path)
      if (entry) media.push({ ...image, blob: await entry.async('blob') })
    }
    parsed.media = media
    parsed.warnings = parsed.warnings.filter((warning) => !/Fotoğraflar JSON/i.test(warning))
    return parsed
  }
  throw new Error('Desteklenen biçimler: JSON, ZIP, PDF, DOCX ve TXT.')
}

function extensionFor(type, fallback = 'png') {
  return ({ 'image/jpeg': 'jpg', 'image/png': 'png', 'image/webp': 'webp', 'image/gif': 'gif' }[type] || fallback)
}

/** Full portable backup including owner-only images downloaded through the authenticated API. */
export async function createCvBackup({ title, template, content, design }) {
  const JSZip = (await import('jszip')).default
  const zip = new JSZip()
  const manifest = { format: EXPORT_FORMAT, schemaVersion: 2, createdAt: new Date().toISOString(), images: [] }
  zip.file('cv.json', JSON.stringify({ format: EXPORT_FORMAT, schemaVersion: 2, title, template, content, design }, null, 2))
  const references = []
  if (content.personal.photoId) references.push({ id: content.personal.photoId, purpose: 'photo', field: 'photo' })
  for (const section of ['experience', 'education']) {
    for (const item of content[section] || []) if (item.logoId) references.push({ id: item.logoId, purpose: 'logo', field: section, itemId: item.id })
  }
  const unique = [...new Map(references.map((item) => [item.id, item])).values()]
  const warnings = []
  for (const reference of unique) {
    try {
      const response = await fetch(mediaFileUrl(reference.id), { credentials: 'same-origin' })
      if (!response.ok) throw new Error('download')
      const blob = await response.blob()
      const path = `images/${reference.purpose}-${reference.id}.${extensionFor(blob.type)}`
      zip.file(path, blob)
      manifest.images.push({ originalId: reference.id, purpose: reference.purpose, path, type: blob.type })
    } catch {
      warnings.push(`${reference.id} numaralı görsel yedeğe eklenemedi.`)
    }
  }
  zip.file('manifest.json', JSON.stringify(manifest, null, 2))
  zip.file('BENIOKU.txt', 'Bu ZIP Pro CV Maker Studio yedeğidir. Editörde JSON / ZIP Yükle seçeneğiyle geri yükleyin.')
  const blob = await zip.generateAsync({ type: 'blob', compression: 'DEFLATE', compressionOptions: { level: 6 } })
  return { blob, imageCount: manifest.images.length, warnings }
}
