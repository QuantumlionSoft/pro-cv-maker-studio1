const ATS_TEMPLATES = ['professional', 'minimal', 'corporate', 'academic', 'compact']
const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

function contrastRatio(a, b) {
  const luminance = (hex) => {
    const value = String(hex || '').replace('#', '')
    if (!/^[\da-f]{6}$/i.test(value)) return 0
    const channels = [0, 2, 4].map((offset) => parseInt(value.slice(offset, offset + 2), 16) / 255)
      .map((channel) => channel <= 0.03928 ? channel / 12.92 : ((channel + 0.055) / 1.055) ** 2.4)
    return channels[0] * 0.2126 + channels[1] * 0.7152 + channels[2] * 0.0722
  }
  const first = luminance(a)
  const second = luminance(b)
  return (Math.max(first, second) + 0.05) / (Math.min(first, second) + 0.05)
}

/** Rule-based, transparent CV analysis. No data leaves the browser. */
export function analyzeCv(content, design = {}, template = 'modern') {
  const p = content?.personal || {}
  const list = (key) => Array.isArray(content?.[key]) ? content[key] : []
  const issues = []
  const categories = { completeness: 0, content: 0, ats: 0 }
  const issue = (tab, title, description, severity = 'warning') => issues.push({ id: `${tab}-${issues.length}`, tab, title, description, severity })

  if ([p.firstName, p.lastName].every(Boolean)) categories.completeness += 6
  else issue('personal', 'Ad ve soyad eksik', 'CV’nin üst kısmında okunaklı bir ad-soyad bulunmalı.', 'danger')
  if (p.title) categories.completeness += 4
  else issue('personal', 'Mesleki unvan ekleyin', 'Hedef pozisyonunuz, CV’nizin ilk saniyelerde anlaşılmasını sağlar.')
  if (EMAIL_RE.test(p.email || '')) categories.completeness += 6
  else issue('personal', 'Geçerli bir e-posta girin', 'İşe alım uzmanının size ulaşabilmesi için geçerli bir e-posta gereklidir.', 'danger')
  if (p.phone) categories.completeness += 4
  else issue('personal', 'Telefon numarası ekleyin', 'En az bir doğrudan iletişim kanalı daha ekleyin.')
  if (p.location) categories.completeness += 3
  else issue('personal', 'Konum bilgisi eksik', 'Şehir ve ülke bilgisi çalışma koşullarını netleştirir.', 'info')

  const summaryLength = (content?.summary || '').trim().length
  if (summaryLength >= 40) categories.completeness += 8
  else issue('summary', 'Profil özetinizi güçlendirin', 'En az 2–3 cümleyle uzmanlığınızı, deneyim yılınızı ve hedefinizi anlatın.')
  if (summaryLength >= 40 && summaryLength <= 1200) categories.content += 6
  else if (summaryLength > 1200) issue('summary', 'Özet çok uzun', 'Profil özetini yaklaşık 600–900 karaktere indirerek daha kolay taranabilir yapın.')

  const experience = list('experience')
  if (experience.length) categories.completeness += 7
  else issue('experience', 'Deneyim bilgisi bulunmuyor', 'İş, staj, gönüllü çalışma veya freelance deneyiminizi ekleyin.', 'danger')
  const descriptions = experience.map((item) => item.description || '').filter(Boolean)
  if (experience.length && descriptions.length === experience.length && descriptions.every((text) => text.length >= 40)) categories.content += 8
  else if (experience.length) issue('experience', 'Deneyim açıklamalarını detaylandırın', 'Her pozisyonda sorumluluğunuzu ve ortaya çıkardığınız sonucu açıklayın.')
  if (descriptions.some((text) => /\d/.test(text))) categories.content += 6
  else if (experience.length) issue('experience', 'Ölçülebilir başarılar kullanın', 'Süre, yüzde, bütçe, ekip büyüklüğü veya proje sayısı gibi somut sonuçlar ekleyin.')

  if (list('education').length) categories.completeness += 5
  else issue('education', 'Eğitim geçmişinizi ekleyin', 'Okul, bölüm ve mezuniyet döneminizi ekleyin.')
  if (list('skills').length >= 3) categories.completeness += 4
  else issue('skills', 'Yetenek listenizi genişletin', 'Hedef pozisyonla ilişkili en az 3–6 yetenek ekleyin.')
  if (list('skills').length >= 5) categories.content += 4
  if (list('languages').length) categories.completeness += 3
  else issue('languages', 'Dil bilginizi ekleyin', 'Bildiğiniz dilleri ve seviyelerini belirtin.', 'info')
  if (list('projects').length || list('certifications').length) categories.content += 3
  else issue('projects', 'Proje veya sertifika ekleyin', 'Yeteneklerinizi kanıtlayan bir proje ya da sertifika CV’nizi güçlendirir.', 'info')
  if (p.linkedin || p.website || p.github) categories.content += 3
  else issue('personal', 'Profesyonel bağlantı ekleyin', 'LinkedIn, GitHub veya kişisel web sitenizden birini ekleyin.', 'info')

  if ((design.textSize || 13) >= 11) categories.ats += 4
  else issue('design', 'Metin boyutu çok küçük', 'ATS ve okunabilirlik için metin boyutunu en az 11px yapın.')
  if ((design.headingSize || 16) >= 12) categories.ats += 2
  if (ATS_TEMPLATES.includes(template)) categories.ats += 5
  else issue('design', 'Görsel düzen ATS açısından karmaşık olabilir', 'Başvuru sistemlerine göndereceğiniz sürümde Professional, Minimal veya Corporate şablonunu değerlendirin.', 'info')
  if (EMAIL_RE.test(p.email || '')) categories.ats += 3
  const urls = [p.website, p.qrLink, ...list('projects').map((item) => item.link), ...list('certifications').map((item) => item.link)].filter(Boolean)
  if (urls.every((url) => /^https?:\/\//i.test(url))) categories.ats += 2
  else issue('personal', 'Bağlantı biçimini kontrol edin', 'Web bağlantıları http:// veya https:// ile başlamalıdır.')
  if (contrastRatio(design.colorHeaderBg || '#1e293b', design.colorHeaderText || '#ffffff') >= 4.5) categories.ats += 4
  else issue('design', 'Üst bilgi kontrastını artırın', 'Yazı ve arka plan arasındaki fark okunabilirlik için yetersiz.')

  const score = Math.round(categories.completeness + categories.content + categories.ats)
  const strengths = []
  if (descriptions.some((text) => /\d/.test(text))) strengths.push('Ölçülebilir deneyim sonuçları')
  if (summaryLength >= 40 && summaryLength <= 1200) strengths.push('Dengeli profil özeti')
  if (list('skills').length >= 5) strengths.push('Güçlü yetenek listesi')
  if (ATS_TEMPLATES.includes(template)) strengths.push('ATS dostu şablon seçimi')
  if (contrastRatio(design.colorHeaderBg || '#1e293b', design.colorHeaderText || '#ffffff') >= 4.5) strengths.push('Okunaklı renk kontrastı')

  return {
    score,
    level: score >= 85 ? 'excellent' : score >= 65 ? 'good' : 'needs-work',
    categories: [
      { id: 'completeness', label: 'Tamlık', value: categories.completeness, max: 50 },
      { id: 'content', label: 'İçerik gücü', value: categories.content, max: 30 },
      { id: 'ats', label: 'ATS ve okunabilirlik', value: categories.ats, max: 20 },
    ],
    issues: issues.sort((a, b) => ({ danger: 0, warning: 1, info: 2 }[a.severity] - { danger: 0, warning: 1, info: 2 }[b.severity])),
    strengths,
  }
}
