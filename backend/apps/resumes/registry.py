"""CV template catalogue.

`available` marks templates that have a renderer. Only available templates can be
saved; the rest stay in the catalogue as planned work.
"""

CV_TEMPLATES = [
    {"id": "modern", "name": "Modern", "description": "Koyu başlık, sol menü ve ana içerik iki kolonlu düzen.", "available": True},
    {"id": "professional", "name": "Professional", "description": "Tek kolon, net bölüm çizgileri, kurumsal görünüm.", "available": True},
    {"id": "minimal", "name": "Minimal", "description": "Bol boşluk ve hafif tipografik hiyerarşi.", "available": True},
    {"id": "executive", "name": "Executive", "description": "Üst düzey pozisyonlar için güçlü başlık ve geniş yan sütun.", "available": True},
    {"id": "corporate", "name": "Corporate", "description": "Büyük kurumlar için dengeli, ATS uyumlu ızgara.", "available": True},
    {"id": "creative", "name": "Creative", "description": "Yumuşak köşeler ve ifadeli renk bloklarıyla yaratıcı düzen.", "available": True},
    {"id": "developer", "name": "Developer", "description": "Teknoloji, yetenek ve proje odaklı teknik düzen.", "available": True},
    {"id": "academic", "name": "Academic", "description": "Eğitim ve araştırma geçmişini öne çıkaran klasik düzen.", "available": True},
    {"id": "elegant", "name": "Elegant", "description": "Serif tipografi, ince ayraçlar ve zamansız görünüm.", "available": True},
    {"id": "compact", "name": "Compact", "description": "Yoğun içeriği okunaklı biçimde daha az sayfaya sığdırır.", "available": True},
]

CV_TEMPLATE_IDS = {t["id"] for t in CV_TEMPLATES}
CV_AVAILABLE_TEMPLATE_IDS = {t["id"] for t in CV_TEMPLATES if t["available"]}
