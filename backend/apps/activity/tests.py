from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from apps.portfolios.models import PortfolioDocument
from apps.resumes.models import CVDocument

from .models import ActivityLog

User = get_user_model()


class DashboardTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user("ada", "ada@example.com", "Sturdy-passphrase-42")
        self.other = User.objects.create_user("eve", "eve@example.com", "Sturdy-passphrase-42")
        self.client.force_login(self.user)

    def test_counts_only_include_own_documents(self):
        CVDocument.objects.create(owner=self.user, title="A")
        CVDocument.objects.create(owner=self.user, title="B")
        CVDocument.objects.create(owner=self.other, title="Not mine")
        PortfolioDocument.objects.create(owner=self.user, title="P")
        data = self.client.get("/api/dashboard/").json()
        self.assertEqual(data["counts"], {"cvs": 2, "portfolios": 1})
        titles = [d["title"] for d in data["recent_documents"]]
        self.assertNotIn("Not mine", titles)
        self.assertEqual(len(titles), 3)

    def test_recent_activity_recorded_for_document_actions(self):
        self.client.post("/api/cvs/", {"title": "Logged CV"}, format="json")
        cv = CVDocument.objects.get(title="Logged CV")
        self.client.patch(f"/api/cvs/{cv.pk}/", {"title": "Renamed", "version": 1}, format="json")
        self.client.delete(f"/api/cvs/{cv.pk}/")
        actions = list(ActivityLog.objects.filter(user=self.user).values_list("action", flat=True))
        self.assertEqual(actions, ["deleted", "updated", "created"])
        resp = self.client.get("/api/activity/").json()
        self.assertEqual(resp["count"], 3)

    def test_activity_is_private(self):
        ActivityLog.objects.create(user=self.other, action="created", object_type="cv", object_title="secret")
        resp = self.client.get("/api/activity/").json()
        self.assertEqual(resp["count"], 0)

    def test_health_endpoint(self):
        self.client.logout()
        resp = self.client.get("/api/health/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["database"], "ok")
