from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from .models import PortfolioDocument

User = get_user_model()


class PortfolioApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user("ada", "ada@example.com", "Sturdy-passphrase-42")
        self.other = User.objects.create_user("eve", "eve@example.com", "Sturdy-passphrase-42")
        self.client.force_login(self.user)

    def test_create_with_valid_template_and_theme(self):
        resp = self.client.post("/api/portfolios/", {"title": "Design Work", "template": "designer", "theme": {"accent": "#111"}}, format="json")
        self.assertEqual(resp.status_code, 201, resp.data)
        self.assertEqual(resp.json()["slug"], "design-work")

    def test_unknown_template_rejected(self):
        resp = self.client.post("/api/portfolios/", {"title": "X", "template": "cv-only"}, format="json")
        self.assertIn("template", resp.json()["error"]["fields"])

    def test_ownership_enforced(self):
        pf = PortfolioDocument.objects.create(owner=self.other, title="Private")
        self.assertEqual(self.client.get(f"/api/portfolios/{pf.pk}/").status_code, 404)
        self.assertEqual(self.client.delete(f"/api/portfolios/{pf.pk}/").status_code, 404)
        self.assertTrue(PortfolioDocument.objects.filter(pk=pf.pk).exists())

    def test_duplicate_and_conflict(self):
        pf = self.client.post("/api/portfolios/", {"title": "Main", "template": "minimal", "theme": {"x": 1}}, format="json").json()
        copy = self.client.post(f"/api/portfolios/{pf['id']}/duplicate/").json()
        self.assertEqual(copy["template"], "minimal")
        self.assertEqual(copy["theme"], {"x": 1})
        self.client.patch(f"/api/portfolios/{pf['id']}/", {"title": "A", "version": 1}, format="json")
        self.assertEqual(self.client.patch(f"/api/portfolios/{pf['id']}/", {"title": "B", "version": 1}, format="json").status_code, 409)

    def test_template_catalogue_has_ten_distinct_entries(self):
        ids = [t["id"] for t in self.client.get("/api/portfolio-templates/").json()]
        self.assertEqual(len(set(ids)), 10)
