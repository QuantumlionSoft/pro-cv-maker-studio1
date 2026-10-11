"""Browser smoke test for Phase 1 (requires backend on :8000 and frontend on :5173).

Usage:  python scripts/e2e_smoke.py [--base http://localhost:5173] [--shots DIR]
"""
import argparse
import re
import sys
import time
import uuid

from playwright.sync_api import expect, sync_playwright


def run(base, shots):
    errors = []
    suffix = uuid.uuid4().hex[:6]
    username = f"smoke_{suffix}"
    password = "Sturdy-passphrase-42"
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1366, "height": 860})
        page.on("pageerror", lambda exc: errors.append(f"pageerror: {exc}"))
        page.on("console", lambda msg: errors.append(f"console: {msg.text}") if msg.type == "error" and "401" not in msg.text and "403" not in msg.text else None)

        page.goto(base + "/")
        expect(page.get_by_role("heading", name="Create Your CV. Build Your Portfolio. Showcase Your Work.")).to_be_visible()
        page.screenshot(path=f"{shots}/01-landing.png", full_page=False)

        page.goto(base + "/dashboard")
        expect(page).to_have_url(base + "/login?next=/dashboard")

        page.goto(base + "/register")
        page.fill("#reg-username", username)
        page.fill("#reg-email", f"{username}@example.com")
        page.fill("#reg-first", "Smoke")
        page.fill("#reg-password", password)
        page.fill("#reg-password-confirm", password)
        page.get_by_role("button", name="Create account").click()
        expect(page.locator(".page-title", has_text="Smoke")).to_be_visible()
        page.screenshot(path=f"{shots}/02-dashboard-empty.png")

        # Create a CV through the modal
        page.get_by_role("button", name="New CV").first.click()
        page.fill("#doc-title", "Smoke Test CV")
        page.get_by_role("button", name="Create", exact=True).click()
        expect(page).to_have_url(re.compile(r"/cvs/\d+$"))
        expect(page.locator("#editor-title")).to_have_value("Smoke Test CV")
        cv_url = page.url

        # Autosave: edit the title, expect a visible save confirmation
        page.fill("#editor-title", "Smoke Test CV — edited")
        expect(page.locator(".save-status")).to_contain_text("All changes saved", timeout=8000)
        page.screenshot(path=f"{shots}/03-editor.png")

        # Persistence after refresh
        page.reload()
        expect(page.locator("#editor-title")).to_have_value("Smoke Test CV — edited", timeout=8000)

        # Template change persists
        page.select_option("#editor-template", "compact")
        expect(page.locator(".save-status")).to_contain_text("All changes saved", timeout=8000)
        page.reload()
        expect(page.locator("#editor-template")).to_have_value("compact", timeout=8000)

        # List page shows the document
        page.goto(base + "/cvs")
        expect(page.get_by_role("link", name="Smoke Test CV — edited", exact=True)).to_be_visible()
        page.screenshot(path=f"{shots}/04-cv-list.png")

        # Duplicate
        page.get_by_role("button", name=f"Duplicate Smoke Test CV — edited").click()
        expect(page.get_by_role("link", name="Smoke Test CV — edited (copy)", exact=True)).to_be_visible(timeout=8000)

        # Delete with confirmation (cancel first, then confirm)
        page.get_by_role("button", name="Delete Smoke Test CV — edited (copy)").click()
        expect(page.get_by_role("alertdialog")).to_be_visible()
        page.get_by_role("button", name="Cancel").click()
        expect(page.get_by_role("link", name="Smoke Test CV — edited (copy)", exact=True)).to_be_visible()
        page.get_by_role("button", name="Delete Smoke Test CV — edited (copy)").click()
        page.get_by_role("button", name="Delete permanently").click()
        expect(page.get_by_role("link", name="Smoke Test CV — edited (copy)", exact=True)).to_have_count(0, timeout=8000)

        # Mobile layout: the sidebar is hidden until the menu button opens it
        mobile = browser.new_page(viewport={"width": 390, "height": 844})
        mobile.on("pageerror", lambda exc: errors.append(f"mobile pageerror: {exc}"))
        mobile.goto(base + "/login")
        mobile.fill("#login-identifier", username)
        mobile.fill("#login-password", password)
        mobile.get_by_role("button", name="Sign in").click()
        expect(mobile.locator(".page-title").first).to_be_visible()
        mobile.screenshot(path=f"{shots}/05-mobile-dashboard.png")
        mobile.get_by_role("button", name="Toggle navigation").click()
        expect(mobile.locator(".app-sidebar")).to_be_visible()
        mobile.wait_for_timeout(400)  # let the slide-in transition finish before the screenshot
        mobile.screenshot(path=f"{shots}/06-mobile-nav.png")

        # Logout
        page.get_by_role("button", name="Sign out").click()
        expect(page).to_have_url(base + "/login")

        browser.close()

    real_errors = [e for e in errors if "favicon" not in e]
    if real_errors:
        print("Browser errors:")
        for e in real_errors:
            print("  ", e)
        return 1
    print("E2E smoke test passed for", username)
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default="http://localhost:5173")
    parser.add_argument("--shots", default="/tmp/shots")
    args = parser.parse_args()
    import os
    os.makedirs(args.shots, exist_ok=True)
    sys.exit(run(args.base, args.shots))
