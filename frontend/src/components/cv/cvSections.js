/**
 * Editor navigation and per-section field definitions.
 * `kind` values: text | textarea | email | url | level | switch | image | select
 */
export const SECTION_TABS = [
  { id: 'personal', label: 'Kişisel Bilgiler', icon: 'bi-person-vcard' },
  { id: 'summary', label: 'Profil Özeti', icon: 'bi-file-richtext' },
  { id: 'experience', label: 'Deneyim', icon: 'bi-briefcase' },
  { id: 'education', label: 'Eğitim', icon: 'bi-mortarboard' },
  { id: 'skills', label: 'Yetenekler', icon: 'bi-stars' },
  { id: 'languages', label: 'Diller', icon: 'bi-translate' },
  { id: 'technologies', label: 'Teknolojiler', icon: 'bi-cpu' },
  { id: 'projects', label: 'Projeler', icon: 'bi-kanban' },
  { id: 'certifications', label: 'Sertifikalar', icon: 'bi-patch-check' },
  { id: 'references', label: 'Referanslar', icon: 'bi-people' },
  { id: 'design', label: 'Tasarım Ayarları', icon: 'bi-palette' },
]

export const LIST_SECTIONS = {
  experience: {
    title: 'İş Deneyimleri',
    addLabel: 'Deneyim ekle',
    itemLabel: 'Deneyim',
    fields: [
      { key: 'company', label: 'Şirket Adı', kind: 'text', placeholder: 'Şirket Adı' },
      { key: 'position', label: 'Pozisyon', kind: 'text', placeholder: 'Pozisyon / Ünvan' },
      { key: 'location', label: 'Konum', kind: 'text', placeholder: 'Şehir' },
      { key: 'start', label: 'Başlangıç', kind: 'text', placeholder: 'Örn: 03.2024', half: true },
      { key: 'end', label: 'Bitiş', kind: 'text', placeholder: 'Örn: Halen', half: true },
      { key: 'description', label: 'Açıklama', kind: 'textarea', placeholder: 'Neler yaptınız?', rows: 3 },
      { key: 'logoId', label: 'Logo', kind: 'image', purpose: 'logo' },
    ],
  },
  education: {
    title: 'Eğitim Bilgileri',
    addLabel: 'Eğitim ekle',
    itemLabel: 'Eğitim',
    fields: [
      { key: 'school', label: 'Okul / Üniversite', kind: 'text', placeholder: 'Okul Adı' },
      { key: 'degree', label: 'Derece / Bölüm', kind: 'text', placeholder: 'Derece / Bölüm' },
      { key: 'gpa', label: 'Mezuniyet notu', kind: 'text', placeholder: 'Örn: 3.45 / 4.00', half: true },
      { key: 'start', label: 'Başlangıç', kind: 'text', placeholder: 'Örn: 2016', half: true },
      { key: 'end', label: 'Bitiş', kind: 'text', placeholder: 'Örn: 2020', half: true },
      { key: 'logoId', label: 'Logo', kind: 'image', purpose: 'logo' },
    ],
  },
  skills: {
    title: 'Yetenekler',
    addLabel: 'Yetenek ekle',
    compact: true,
    fields: [
      { key: 'name', kind: 'text', placeholder: 'Yetenek adı' },
      { key: 'level', kind: 'level' },
    ],
  },
  languages: {
    title: 'Diller',
    addLabel: 'Dil ekle',
    compact: true,
    fields: [
      { key: 'name', kind: 'text', placeholder: 'Dil' },
      { key: 'level', kind: 'level' },
    ],
  },
  technologies: {
    title: 'Teknolojiler',
    addLabel: 'Teknoloji ekle',
    compact: true,
    fields: [{ key: 'name', kind: 'text', placeholder: 'Örn: Docker' }],
  },
  projects: {
    title: 'Projeler',
    addLabel: 'Proje ekle',
    itemLabel: 'Proje',
    fields: [
      { key: 'name', label: 'Proje Adı', kind: 'text', placeholder: 'Proje Adı' },
      { key: 'description', label: 'Kısa Açıklama', kind: 'textarea', placeholder: 'Kısa açıklama', rows: 2 },
      { key: 'link', label: 'Proje Linki', kind: 'url', placeholder: 'https://…' },
      { key: 'showQr', label: 'Proje QR kodunu göster', kind: 'switch' },
    ],
  },
  certifications: {
    title: 'Sertifikalar',
    addLabel: 'Sertifika ekle',
    itemLabel: 'Sertifika',
    fields: [
      { key: 'name', label: 'Sertifika Adı', kind: 'text', placeholder: 'Sertifika Adı' },
      { key: 'issuer', label: 'Veren Kurum', kind: 'text', placeholder: 'Veren Kurum' },
      { key: 'link', label: 'Doğrulama Linki', kind: 'url', placeholder: 'https://…' },
      { key: 'showQr', label: 'Sertifika QR kodunu göster', kind: 'switch' },
    ],
  },
  references: {
    title: 'Referanslar',
    addLabel: 'Referans ekle',
    itemLabel: 'Referans',
    fields: [
      { key: 'name', label: 'Ad Soyad', kind: 'text', placeholder: 'Ad Soyad' },
      { key: 'position', label: 'Pozisyon', kind: 'text', placeholder: 'Pozisyon / Ünvan', half: true },
      { key: 'company', label: 'Kurum', kind: 'text', placeholder: 'Şirket / Kurum', half: true },
      { key: 'email', label: 'E-posta', kind: 'email', placeholder: 'ornek@mail.com', half: true },
      { key: 'phone', label: 'Telefon', kind: 'text', placeholder: '+90 …', half: true },
    ],
  },
}
