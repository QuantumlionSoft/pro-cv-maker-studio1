import { CV_SECTION_ORDER } from './cvContent'

export const SAMPLE_CV_CONTENT = {
  schemaVersion: 2,
  sectionOrder: [...CV_SECTION_ORDER],
  hiddenSections: ['references'],
  sectionTitles: {},
  personal: {
    firstName: 'Deniz', middleName: '', lastName: 'Yılmaz', title: 'Kıdemli Ürün Tasarımcısı',
    email: 'deniz@ornek.com', phone: '+90 555 000 00 00', location: 'İstanbul, Türkiye',
    website: 'denizyilmaz.com', linkedin: 'linkedin.com/in/deniz', github: '', photoId: null, showQr: false, qrLink: '',
  },
  summary: 'Kullanıcı odaklı dijital ürünler tasarlayan, araştırma ve tasarım sistemleri deneyimine sahip ürün tasarımcısı.',
  experience: [
    { id: 'sample-exp-1', company: 'Nova Teknoloji', position: 'Kıdemli Ürün Tasarımcısı', location: 'İstanbul', start: '2022', end: '', current: true, description: 'Tasarım sistemini yenileyerek ekip verimliliğini %30 artırdım.', logoId: null },
    { id: 'sample-exp-2', company: 'Studio Dijital', position: 'UI / UX Tasarımcısı', location: 'Ankara', start: '2019', end: '2022', current: false, description: 'Mobil ve web deneyimleri için kullanıcı araştırmaları ve arayüzler geliştirdim.', logoId: null },
  ],
  education: [{ id: 'sample-edu-1', school: 'Mimar Sinan Üniversitesi', degree: 'Endüstriyel Tasarım, Lisans', gpa: '3.60 / 4.00', start: '2015', end: '2019', logoId: null }],
  skills: [{ id: 'sample-s1', name: 'Ürün Stratejisi', level: 90 }, { id: 'sample-s2', name: 'UX Araştırması', level: 80 }, { id: 'sample-s3', name: 'Tasarım Sistemleri', level: 90 }],
  languages: [{ id: 'sample-l1', name: 'Türkçe', level: 100 }, { id: 'sample-l2', name: 'İngilizce', level: 90 }],
  technologies: [{ id: 'sample-t1', name: 'Figma' }, { id: 'sample-t2', name: 'FigJam' }, { id: 'sample-t3', name: 'Maze' }],
  projects: [{ id: 'sample-p1', name: 'Tasarım Sistemi', description: '40+ bileşen ve ortak tasarım dili.', link: 'https://example.com', showQr: false }],
  certifications: [{ id: 'sample-c1', name: 'UX Certification', issuer: 'NN/g', link: '', showQr: false }],
  references: [],
}

export function sampleDesign(template) {
  const presets = {
    modern: { colorAccent: '#4f46e5', colorHeaderBg: '#172033', colorSidebarBg: '#eef1f7' },
    professional: { colorAccent: '#2563eb', colorHeaderBg: '#1e3a5f' },
    minimal: { colorAccent: '#475569' },
    executive: { colorAccent: '#d7b56d', colorHeaderBg: '#111c2e', colorSidebarBg: '#e8edf3' },
    corporate: { colorAccent: '#0f766e', colorSidebarBg: '#eef8f6' },
    creative: { colorAccent: '#ec4899', colorHeaderBg: '#6d28d9', colorSidebarBg: '#f5f3ff' },
    developer: { colorAccent: '#22c55e', colorHeaderBg: '#111827', colorSidebarBg: '#eef2f7' },
    academic: { colorAccent: '#7c2d12' },
    elegant: { colorAccent: '#a16207' },
    compact: { colorAccent: '#0369a1' },
  }
  return {
    font: template === 'elegant' || template === 'academic' ? 'Merriweather' : 'Inter',
    colorHeaderText: '#ffffff', colorSidebarText: '#334155', educationInSidebar: false,
    headerAlign: template === 'elegant' ? 'center' : 'left', nameSize: 32, headingSize: 16,
    textSize: 13, photoSize: 140, qrSize: 80, newPageForExtras: false,
    ...presets[template],
  }
}
