"""Browser test for the Phase 2 CV builder (backend on :8000, frontend on :5173).

Usage:  python scripts/e2e_cv_builder.py [--base http://localhost:5173] [--shots DIR] [--pdf PATH]

Covers: register, create CV, edit with autosave and persistence after reload,
photo and QR upload (authenticated), prototype JSON import, JSON export,
print-to-PDF output, mobile layout, and that no external service is contacted.
"""
import argparse
import json
import tempfile
import uuid
from pathlib import Path

from playwright.sync_api import expect, sync_playwright

PASSWORD = "Sturdy-passphrase-42"
EXTERNAL_HOSTS = ("qrserver.com", "googleapis.com", "gstatic.com", "jsdelivr.net", "unpkg.com")

PROTOTYPE = {
    "personal": {"name": "Kaan Ergün", "title": "Full Stack Developer", "email": "kaan@example.com",
                 "phone": "+90 500 000 00 00", "location": "Samsun", "website": "", "linkedin": "kaan",
                 "github": "kaan", "photo": "", "showQr": False, "qrLink": ""},
    "summary": "İçe aktarılan özet.",
    "experience": [{"id": 1, "company": "Veri Vizyon", "position": "Developer", "start": "03.2024", "end": "Halen", "description": "x"}],
    "education": [], "skills": [{"id": 1, "name": "Python", "level": 90}], "languages": [],
    "hobbies": [{"id": 1, "name": "Docker"}], "projects": [], "certifications": [], "references": [],
    "design": {"font": "Roboto", "colorAccent": "#ff5500", "headerAlign": "center"},
}


def tab(page, label):
    """Section navigation button in the builder sidebar (the only nav-pill in the editor)."""
    return page.locator(".cv-nav .nav-link", has_text=label)


def run(base, shots, pdf_path):
    errors, external = [], []
    suffix = uuid.uuid4().hex[:6]
    username = f"cvbuilder_{suffix}"
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(viewport={"width": 1366, "height": 860}, accept_downloads=True)
        page = context.new_page()
        page.on("pageerror", lambda exc: errors.append(f"pageerror: {exc}"))
        page.on("console", lambda m: errors.append(f"console: {m.text}") if m.type == "error" and "401" not in m.text and "403" not in m.text and "409" not in m.text and "400" not in m.text else None)
        page.on("request", lambda r: external.append(r.url) if any(h in r.url for h in EXTERNAL_HOSTS) else None)

        # 1. Register and create a CV through the API the UI uses.
        page.goto(base + "/register")
        page.fill("#reg-username", username)
        page.fill("#reg-email", f"{username}@example.com")
        page.fill("#reg-first", "Ada")
        page.fill("#reg-password", PASSWORD)
        page.fill("#reg-password-confirm", PASSWORD)
        page.get_by_role("button", name="Create account").click()
        expect(page.locator(".page-title", has_text="Ada")).to_be_visible()
        cv_id = page.evaluate("""async () => {
            await fetch('/api/auth/csrf/', {credentials: 'same-origin'})
            const token = decodeURIComponent(document.cookie.split('; ').find(r => r.startsWith('csrftoken=')).split('=')[1])
            const r = await fetch('/api/cvs/', {method: 'POST', credentials: 'same-origin',
                headers: {'Content-Type': 'application/json', 'X-CSRFToken': token},
                body: JSON.stringify({title: 'Ada CV', template: 'modern'})})
            return (await r.json()).id
        }""")

        # 2. Open the builder and edit.
        page.goto(f"{base}/cvs/{cv_id}")
        expect(page.locator("#p-first")).to_be_visible()
        page.fill("#p-first", "Ada")
        page.fill("#p-last", "Lovelace")
        page.fill("#p-title", "Analytical Engine Engineer")
        page.fill("#p-email", "ada@example.com")
        expect(page.locator(".cv-name")).to_have_text("Ada Lovelace")
        tab(page, "Profil Özeti").click()
        page.fill("#summary-text", "Sayılar üzerine çalışan bir mühendis.")
        tab(page, "Deneyim").click()
        page.get_by_role("button", name="Deneyim ekle").click()
        page.get_by_label("Şirket Adı").first.fill("Analytical Co")
        page.get_by_label("Pozisyon").first.fill("Engineer")
        tab(page, "Yetenekler").click()
        page.get_by_role("button", name="Yetenek ekle").click()
        page.get_by_label("Yetenekler 1 adı").fill("Algorithms")

        # 3. Autosave: wait for a successful PATCH and check the stored content.
        page.wait_for_timeout(2500)  # autosave debounce (800 ms) plus request time
        stored = page.evaluate(f"""async () => (await (await fetch('/api/cvs/{cv_id}/', {{credentials: 'same-origin'}})).json())""")
        assert stored["content"]["personal"]["firstName"] == "Ada", stored["content"]["personal"]
        assert stored["content"]["experience"][0]["company"] == "Analytical Co", stored["content"]["experience"]
        assert stored["content"]["skills"][0]["name"] == "Algorithms"
        assert stored["content"]["summary"].startswith("Sayılar")

        # 4. Photo upload: served through the owner-only media view.
        tab(page, "Kişisel Bilgiler").click()
        page.set_input_files("#personal-photo", "/tmp/photo.png")
        photo = page.locator(".cv-photo")
        expect(photo).to_be_visible(timeout=8000)
        page.wait_for_function("() => { const i = document.querySelector('.cv-photo'); return i && i.complete && i.naturalWidth > 0 }", timeout=8000)
        assert "/api/media/" in photo.get_attribute("src")

        # 5. Local QR code: enabled from the personal tab.
        page.check("#p-qr")
        page.fill("input[aria-label='QR bağlantısı']", "https://www.linkedin.com/in/ada")
        qr = page.locator(".cv-qr-box img")
        expect(qr).to_be_visible()
        page.wait_for_function("() => { const i = document.querySelector('.cv-qr-box img'); return i && i.complete && i.naturalWidth > 0 }", timeout=8000)
        assert "/api/qr/" in qr.get_attribute("src")

        # 6. Persistence after reload (server copy, no localStorage).
        page.wait_for_timeout(1500)
        page.reload()
        expect(page.locator(".cv-name")).to_have_text("Ada Lovelace")
        assert page.input_value("#p-first") == "Ada"
        local_keys = page.evaluate("Object.keys(localStorage)")
        assert not [k for k in local_keys if "cv" in k.lower()], f"CV data in localStorage: {local_keys}"

        # 7. Validation: an unsafe website is rejected by the server and not silently saved.
        page.fill("#p-website", "javascript:alert(1)")
        expect(page.locator(".cv-save-wrap .save-status")).to_contain_text("personal.website", timeout=8000)
        page.fill("#p-website", "")
        page.wait_for_timeout(1500)

        # 8. Prototype JSON import (name split, hobbies -> technologies, confirm dialog).
        tmp = Path(tempfile.mkdtemp()) / "prototype.json"
        tmp.write_text(json.dumps(PROTOTYPE, ensure_ascii=False), encoding="utf-8")
        page.set_input_files("input[type=file][accept*='json']", str(tmp))
        page.get_by_role("button", name="İçe aktar").click()
        expect(page.locator("#p-first")).to_have_value("Kaan", timeout=5000)
        expect(page.locator(".cv-name")).to_have_text("Kaan Ergün")
        tab(page, "Teknolojiler").click()
        expect(page.get_by_text("Docker")).to_be_visible()
        page.wait_for_timeout(1500)

        # 9. JSON export downloads a file in our format and without photo ids.
        with page.expect_download() as download_info:
            page.get_by_role("button", name="JSON İndir").click()
        download = download_info.value
        exported = json.loads(Path(download.path()).read_text(encoding="utf-8"))
        assert exported["format"] == "pro-cv-maker-studio"
        assert exported["content"]["personal"]["photoId"] is None

        # 10. Screenshots and PDF.
        tab(page, "Kişisel Bilgiler").click()
        page.screenshot(path=f"{shots}/cv-desktop.png")
        tab(page, "Tasarım Ayarları").click()
        page.screenshot(path=f"{shots}/cv-design.png")
        page.emulate_media(media="print")
        page.pdf(path=pdf_path, format="A4", print_background=True, prefer_css_page_size=True)
        page.emulate_media(media="screen")
        import os
        assert os.path.getsize(pdf_path) > 5000, "PDF is empty: print layout hides the CV"

        # 11. Mobile layout.
        mobile = context.new_page()
        mobile.set_viewport_size({"width": 390, "height": 844})
        mobile.on("pageerror", lambda exc: errors.append(f"mobile pageerror: {exc}"))
        mobile.goto(f"{base}/cvs/{cv_id}")
        expect(mobile.locator("#p-first")).to_be_visible(timeout=8000)
        mobile.screenshot(path=f"{shots}/cv-mobile-form.png")
        mobile.get_by_role("button", name="Önizleme").click()
        expect(mobile.locator(".cv-document")).to_be_visible()
        mobile.screenshot(path=f"{shots}/cv-mobile-preview.png")
        doc_width = mobile.locator(".cv-document").bounding_box()["width"]
        assert doc_width <= 390, f"A4 preview overflows phone width: {doc_width}"
        mobile.close()

        browser.close()

    assert not external, f"external requests: {external[:3]}"
    assert not errors, "browser errors:\n" + "\n".join(errors[:10])
    print("CV builder E2E OK")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://localhost:5173")
    ap.add_argument("--shots", default="/tmp/shots")
    ap.add_argument("--pdf", default="/tmp/shots/cv.pdf")
    args = ap.parse_args()
    run(args.base, args.shots, args.pdf)
