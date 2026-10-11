"""Portfolio template catalogue. Renderers are added in Phase 4."""

PORTFOLIO_TEMPLATES = [
    {"id": "developer", "name": "Developer Portfolio", "description": "Project-led layout with tech stack and code links."},
    {"id": "creative", "name": "Creative Portfolio", "description": "Bold visual hierarchy for creative work."},
    {"id": "minimal", "name": "Minimal Portfolio", "description": "Quiet layout that lets the work speak."},
    {"id": "professional", "name": "Professional Portfolio", "description": "Corporate-friendly profile and experience focus."},
    {"id": "designer", "name": "Designer Portfolio", "description": "Large imagery and case-study gallery."},
    {"id": "photography", "name": "Photography Portfolio", "description": "Full-bleed gallery with minimal chrome."},
    {"id": "academic", "name": "Academic Portfolio", "description": "Publications, research and teaching."},
    {"id": "freelancer", "name": "Freelancer Portfolio", "description": "Services, testimonials and contact-first layout."},
    {"id": "personal-brand", "name": "Personal Brand", "description": "Hero-driven personal site with social links."},
    {"id": "general", "name": "General Portfolio", "description": "Flexible layout for any profession."},
]

PORTFOLIO_TEMPLATE_IDS = {t["id"] for t in PORTFOLIO_TEMPLATES}
