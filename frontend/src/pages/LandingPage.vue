<script setup>
import { computed } from 'vue'
import { RouterLink } from 'vue-router'
import CvTemplateThumbnail from '@/components/cv/CvTemplateThumbnail.vue'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const primaryTarget = computed(() => auth.isAuthenticated ? { name: 'cvs' } : { name: 'register', query: { next: '/cvs' } })

const templates = [
  { id: 'modern', name: 'Modern', text: 'Dengeli iki sütun ve güçlü görsel hiyerarşi.' },
  { id: 'executive', name: 'Executive', text: 'Liderlik deneyimini öne çıkaran prestijli düzen.' },
  { id: 'creative', name: 'Creative', text: 'Yaratıcı roller için renkli ve özgün kompozisyon.' },
  { id: 'developer', name: 'Developer', text: 'Teknik yetenek ve projeler için geliştirilmiş yapı.' },
  { id: 'elegant', name: 'Elegant', text: 'Serif tipografi ve zamansız editoryal detaylar.' },
  { id: 'compact', name: 'Compact', text: 'Yoğun deneyimi daha az sayfada etkili biçimde sunar.' },
]

const faqs = [
  { q: 'Uygulamayı kullanmak ücretli mi?', a: 'Hayır. Pro CV Maker Studio ödeme, abonelik veya ücretli özellik sınırı içermez. Kendi bilgisayarınızda çalıştırabilirsiniz.' },
  { q: 'Belgelerim ve fotoğraflarım nerede saklanıyor?', a: 'Verileriniz çalıştırdığınız uygulamanın veritabanında saklanır. Tarayıcı depolaması yalnızca kısa süreli kurtarma taslakları ve arayüz tercihleri için kullanılır.' },
  { q: 'Şablon değiştirdiğimde içeriğim silinir mi?', a: 'Hayır. On şablonun tamamı aynı içerik yapısını kullanır. Şablonu, renkleri veya yazı tipini istediğiniz zaman içeriğinizi kaybetmeden değiştirebilirsiniz.' },
  { q: 'CV’mi PDF olarak indirebilir miyim?', a: 'Evet. Canlı A4 önizlemesini kontrol ettikten sonra PDF / Yazdır düğmesini kullanarak tarayıcınız üzerinden PDF olarak kaydedebilirsiniz.' },
]
</script>

<template>
  <div class="landing">
    <header class="landing-nav">
      <div class="container d-flex align-items-center justify-content-between py-2">
        <RouterLink :to="{ name: 'landing' }" class="brand-link" aria-label="Pro CV Maker Studio ana sayfa">
          <span class="brand-mark" aria-hidden="true"><i class="bi bi-file-earmark-richtext"></i></span>
          <span class="brand-name"><strong>Pro CV</strong><small>MAKER STUDIO</small></span>
        </RouterLink>
        <nav class="d-flex align-items-center gap-1 gap-md-2" aria-label="Ana navigasyon">
          <a href="#templates" class="btn btn-link text-decoration-none d-none d-md-inline">Şablonlar</a>
          <a href="#how-it-works" class="btn btn-link text-decoration-none d-none d-md-inline">Nasıl çalışır?</a>
          <a href="#faq" class="btn btn-link text-decoration-none d-none d-lg-inline">SSS</a>
          <RouterLink v-if="!auth.isAuthenticated" :to="{ name: 'login' }" class="btn btn-outline-secondary btn-sm">Giriş yap</RouterLink>
          <RouterLink v-else :to="{ name: 'dashboard' }" class="btn btn-outline-secondary btn-sm">Çalışma alanım</RouterLink>
          <RouterLink :to="primaryTarget" class="btn btn-primary btn-sm d-none d-sm-inline-flex">CV oluştur <i class="bi bi-arrow-right ms-1"></i></RouterLink>
        </nav>
      </div>
    </header>

    <section class="hero">
      <div class="container">
        <div class="row align-items-center g-5">
          <div class="col-lg-7">
            <span class="hero-pill"><i class="bi bi-shield-check"></i> Yerel çalışır · Verileriniz size aittir</span>
            <h1 class="hero-title">Deneyiminizi anlatan <span class="text-gradient">etkileyici bir CV</span> oluşturun.</h1>
            <p class="lead">Profesyonel şablonlar, esnek tasarım kontrolleri ve gerçek zamanlı A4 önizleme ile dakikalar içinde özenli bir CV hazırlayın.</p>
            <div class="d-flex flex-wrap gap-2 mt-4">
              <RouterLink :to="primaryTarget" class="btn btn-primary btn-lg"><i class="bi bi-file-earmark-plus me-2"></i>Ücretsiz CV oluştur</RouterLink>
              <a href="#templates" class="btn btn-outline-secondary btn-lg">Şablonları keşfet <i class="bi bi-arrow-down ms-1"></i></a>
            </div>
            <div class="hero-proof">
              <span><i class="bi bi-check-circle-fill"></i>10 profesyonel şablon</span>
              <span><i class="bi bi-check-circle-fill"></i>Otomatik kayıt</span>
              <span><i class="bi bi-check-circle-fill"></i>PDF çıktısı</span>
            </div>
          </div>
          <div class="col-lg-5">
            <div class="hero-visual">
              <figure class="hero-illustration" aria-label="Modern CV sayfası illüstrasyonu">
                <div class="illus-page">
                  <div class="illus-head"></div>
                  <div class="illus-body">
                    <div class="illus-sidebar"><div class="illus-line illus-line--accent"></div><div class="illus-line"></div><div class="illus-line w-75"></div><div class="illus-line illus-line--accent"></div><div class="illus-line"></div><div class="illus-line w-60"></div></div>
                    <div class="illus-content"><div class="illus-line illus-line--accent"></div><div class="illus-line w-90"></div><div class="illus-line"></div><div class="illus-line w-75"></div><div class="illus-line illus-line--accent"></div><div class="illus-line"></div><div class="illus-line w-90"></div><div class="illus-line w-60"></div></div>
                  </div>
                </div>
              </figure>
              <div class="hero-float hero-float--top"><i class="bi bi-palette"></i><span>Kolay özelleştirme</span></div>
              <div class="hero-float hero-float--bottom"><i class="bi bi-cloud-check"></i><span>Değişiklikler kaydedildi</span></div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section id="templates" class="section">
      <div class="container">
        <div class="d-flex flex-wrap justify-content-between align-items-end gap-3 mb-4">
          <div><p class="section-kicker">Her kariyere uygun</p><h2 class="section-title">Tarzınızı yansıtan şablonu seçin</h2><p class="section-copy mb-0">Kurumsaldan yaratıcıya, akademikten teknik rollere kadar tüm şablonlar aynı içerikle çalışır.</p></div>
          <RouterLink :to="primaryTarget" class="btn btn-outline-primary btn-sm">Tümünü editörde deneyin <i class="bi bi-arrow-right ms-1"></i></RouterLink>
        </div>
        <div class="row g-4">
          <div v-for="item in templates" :key="item.id" class="col-sm-6 col-lg-4">
            <div class="card h-100 landing-template"><CvTemplateThumbnail :template="item.id" /><div class="card-body"><div class="d-flex align-items-center justify-content-between"><h3 class="h6 mb-1">{{ item.name }}</h3><i class="bi bi-arrow-up-right text-secondary"></i></div><p class="small text-secondary mb-0">{{ item.text }}</p></div></div>
          </div>
        </div>
      </div>
    </section>

    <section class="section section-alt">
      <div class="container">
        <div class="text-center mb-4"><p class="section-kicker">Basit ve güvenli</p><h2 class="section-title">İçeriğe odaklanın, gerisini bize bırakın</h2></div>
        <div class="row g-3">
          <div class="col-md-4"><div class="card h-100 feature-card"><div class="card-body"><i class="bi bi-layout-text-sidebar-reverse feature-icon"></i><h3>Gerçek zamanlı önizleme</h3><p class="small text-secondary mb-0">Her düzenlemeyi A4 sayfanızda anında görün. Yazdırmadan önce sonucu tam olarak bilin.</p></div></div></div>
          <div class="col-md-4"><div class="card h-100 feature-card"><div class="card-body"><i class="bi bi-cloud-check feature-icon"></i><h3>Güvenli otomatik kayıt</h3><p class="small text-secondary mb-0">Değişiklikleriniz otomatik kaydedilir; sürüm çakışmaları ve bağlantı hataları görünür biçimde yönetilir.</p></div></div></div>
          <div class="col-md-4"><div class="card h-100 feature-card"><div class="card-body"><i class="bi bi-shield-lock feature-icon"></i><h3>Gizlilik öncelikli</h3><p class="small text-secondary mb-0">Belgeleriniz ve yüklediğiniz görseller yalnızca hesabınıza özeldir. Siz dışa aktarmadıkça yayınlanmaz.</p></div></div></div>
        </div>
      </div>
    </section>

    <section id="how-it-works" class="section">
      <div class="container"><div class="mb-4"><p class="section-kicker">Üç adımda hazır</p><h2 class="section-title">İlk taslaktan PDF’e</h2></div><ol class="steps"><li><strong>Bilgilerinizi ekleyin</strong>Deneyim, eğitim, yetenek ve projelerinizi sade formlarla düzenleyin.</li><li><strong>Tasarımı kişiselleştirin</strong>On şablondan birini seçin; renkleri, yazı tipini ve boyutları ayarlayın.</li><li><strong>PDF olarak kaydedin</strong>A4 önizlemeyi kontrol edin ve profesyonel CV’nizi yazdırın veya indirin.</li></ol></div>
    </section>

    <section id="faq" class="section section-alt">
      <div class="container"><div class="row g-5"><div class="col-lg-4"><p class="section-kicker">Merak edilenler</p><h2 class="section-title">Sık sorulan sorular</h2><p class="section-copy">Başlamadan önce bilmeniz gerekenler.</p></div><div class="col-lg-8"><div class="accordion" id="faq-accordion"><div v-for="(item, index) in faqs" :key="item.q" class="accordion-item"><h3 class="accordion-header"><button class="accordion-button" :class="{ collapsed: index > 0 }" type="button" data-bs-toggle="collapse" :data-bs-target="`#faq-${index}`" :aria-expanded="index === 0">{{ item.q }}</button></h3><div :id="`faq-${index}`" class="accordion-collapse collapse" :class="{ show: index === 0 }" data-bs-parent="#faq-accordion"><div class="accordion-body">{{ item.a }}</div></div></div></div></div></div></div>
    </section>

    <section class="section">
      <div class="container"><div class="landing-cta"><h2 class="h3">Bir sonraki kariyer adımınıza hazır mısınız?</h2><p class="mb-4">İçeriğinizi ekleyin, tarzınızı seçin ve CV’nizi bugün tamamlayın.</p><RouterLink :to="primaryTarget" class="btn btn-light btn-lg">CV oluşturmaya başlayın <i class="bi bi-arrow-right ms-1"></i></RouterLink></div></div>
    </section>

    <footer class="landing-footer"><div class="container d-flex flex-wrap justify-content-between gap-2 py-4 small"><span class="fw-semibold">Pro CV Maker Studio</span><span class="text-secondary">Yerel öncelikli · Abonelik yok · Verileriniz size ait</span></div></footer>
  </div>
</template>
