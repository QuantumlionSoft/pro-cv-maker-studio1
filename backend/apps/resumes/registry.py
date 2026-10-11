"""CV template catalogue.

`available` marks templates that have a renderer. Only available templates can be
saved; the rest stay in the catalogue as planned work.
"""

CV_TEMPLATES = [
    {"id": "modern", "name": "Modern", "description": "Koyu başlık, sol menü ve ana içerik iki kolonlu düzen.", "available": True},
    {"id": "professional", "name": "Professional", "description": "Tek kolon, net bölüm çizgileri, kurumsal görünüm.", "available": True},
    {"id": "minimal", "name": "Minimal", "description": "Bol boşluk ve hafif tipografik hiyerarşi.", "available": True},
    {"id": "executive", "name": "Executive", "description": "Üst düzey pozisyonlar için sidebar'lı düzen.", "available": False},
    {"id": "corporate", "name": "Corporate", "description": "Büyük kurumlar için yapılandırılmış ızgara.", "available": False},
    {"id": "creative", "name": "Creative", "description": "Vurgu renkli ve ifadeli başlıklar.", "available": False},
    {"id": "developer", "name": "Developer", "description": "Yetenek ve proje odaklı düzen.", "available": False},
    {"id": "academic", "name": "Academic", "description": "Yayın, araştırma ve eğitim öncelikli.", "available": False},
    {"id": "elegant", "name": "Elegant", "description": "Serif tipografi ve ince ayraçlar.", "available": False},
    {"id": "compact", "name": "Compact", "description": "Daha az sayfaya daha fazla içerik.", "available": False},
]

CV_TEMPLATE_IDS = {t["id"] for t in CV_TEMPLATES}
CV_AVAILABLE_TEMPLATE_IDS = {t["id"] for t in CV_TEMPLATES if t["available"]}
