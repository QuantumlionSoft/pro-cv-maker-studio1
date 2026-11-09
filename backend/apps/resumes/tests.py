from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from apps.media.models import MediaAsset

from .models import CVDocument
from .schema import default_design, empty_content, normalize_content

User = get_user_model()


def make_media(owner, purpose="photo"):
    return MediaAsset.objects.create(
        owner=owner, file="user-1/test.png", purpose=purpose,
        content_type="image/png", size_bytes=10, width=1, height=1,
    )


class CVDocumentApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user("ada", "ada@example.com", "Sturdy-passphrase-42")
        self.other = User.objects.create_user("eve", "eve@example.com", "Sturdy-passphrase-42")
        self.client.force_login(self.user)

    def create_cv(self, title="Software Engineer CV", **extra):
        payload = {"title": title, "template": "modern"}
        payload.update(extra)
        resp = self.client.post("/api/cvs/", payload, format="json")
        self.assertEqual(resp.status_code, 201, resp.data)
        return resp.json()

    def test_new_cv_is_empty_and_has_no_personal_data(self):
        cv = self.create_cv()
        self.assertEqual(cv["content"]["personal"]["firstName"], "")
        self.assertEqual(cv["content"]["experience"], [])
        self.assertEqual(cv["design"], default_design())

    def test_create_and_list_own_cvs_with_slug(self):
        cv = self.create_cv()
        self.assertEqual(cv["slug"], "software-engineer-cv")
        self.create_cv()
        listing = self.client.get("/api/cvs/").json()
        self.assertEqual(listing["count"], 2)
        self.assertEqual(len({item["slug"] for item in listing["results"]}), 2)

    def test_owner_is_never_taken_from_client(self):
        cv = self.create_cv(owner=self.other.pk)
        self.assertEqual(CVDocument.objects.get(pk=cv["id"]).owner, self.user)

    def test_other_users_cannot_read_update_or_delete(self):
        cv = self.create_cv()
        self.client.force_login(self.other)
        self.assertEqual(self.client.get(f"/api/cvs/{cv['id']}/").status_code, 404)
        self.assertEqual(self.client.patch(f"/api/cvs/{cv['id']}/", {"title": "Hacked"}, format="json").status_code, 404)
        self.assertEqual(self.client.delete(f"/api/cvs/{cv['id']}/").status_code, 404)
        self.assertEqual(self.client.post(f"/api/cvs/{cv['id']}/duplicate/").status_code, 404)

    def test_content_round_trip_and_version_increment(self):
        cv = self.create_cv()
        content = cv["content"]
        content["personal"]["firstName"] = "Ayşe"
        content["personal"]["email"] = "ayse@example.com"
        content["experience"] = [{"id": "e1", "company": "Acme", "position": "Dev", "start": "2024", "end": "Halen", "current": True, "description": "Built things"}]
        resp = self.client.patch(f"/api/cvs/{cv['id']}/", {"content": content, "version": 1}, format="json")
        self.assertEqual(resp.status_code, 200, resp.data)
        data = resp.json()
        self.assertEqual(data["version"], 2)
        self.assertEqual(data["content"]["personal"]["firstName"], "Ayşe")
        self.assertEqual(data["content"]["experience"][0]["company"], "Acme")
        self.assertTrue(data["content"]["experience"][0]["current"])

    def test_stale_version_is_rejected_with_409(self):
        cv = self.create_cv()
        self.client.patch(f"/api/cvs/{cv['id']}/", {"title": "First", "version": 1}, format="json")
        stale = self.client.patch(f"/api/cvs/{cv['id']}/", {"title": "Stale", "version": 1}, format="json")
        self.assertEqual(stale.status_code, 409)
        self.assertEqual(CVDocument.objects.get(pk=cv["id"]).title, "First")

    def test_unknown_template_rejected(self):
        self.assertIn("template", self.client.post("/api/cvs/", {"title": "X", "template": "nope"}, format="json").json()["error"]["fields"])

    def test_every_catalogue_template_can_be_used(self):
        catalogue = self.client.get("/api/cv-templates/").json()
        for item in catalogue:
            response = self.client.post("/api/cvs/", {"title": item["name"], "template": item["id"]}, format="json")
            self.assertEqual(response.status_code, 201, response.data)

    def test_unsafe_urls_and_bad_emails_are_rejected(self):
        cv = self.create_cv()
        bad_link = dict(cv["content"], personal=dict(cv["content"]["personal"], website="javascript:alert(1)"))
        resp = self.client.patch(f"/api/cvs/{cv['id']}/", {"content": bad_link, "version": 1}, format="json")
        self.assertEqual(resp.status_code, 400)
        bad_mail = dict(cv["content"], personal=dict(cv["content"]["personal"], email="not-an-email"))
        resp = self.client.patch(f"/api/cvs/{cv['id']}/", {"content": bad_mail, "version": 1}, format="json")
        self.assertEqual(resp.status_code, 400)

    def test_invalid_colour_and_font_rejected(self):
        resp = self.client.post("/api/cvs/", {"title": "X", "template": "modern", "design": {"colorAccent": "red"}}, format="json")
        self.assertEqual(resp.status_code, 400)
        resp = self.client.post("/api/cvs/", {"title": "X", "template": "modern", "design": {"font": "Comic Sans"}}, format="json")
        self.assertEqual(resp.status_code, 400)

    def test_unknown_keys_are_dropped_and_script_is_stored_as_text_only(self):
        cv = self.create_cv()
        content = cv["content"]
        content["personal"]["firstName"] = "<script>alert(1)</script>"
        content["hacker"] = {"x": 1}
        resp = self.client.patch(f"/api/cvs/{cv['id']}/", {"content": content, "version": 1}, format="json")
        data = resp.json()
        self.assertNotIn("hacker", data["content"])
        self.assertEqual(data["content"]["personal"]["firstName"], "<script>alert(1)</script>")  # plain text, escaped by Vue

    def test_foreign_or_missing_media_references_are_dropped(self):
        cv = self.create_cv()
        mine = make_media(self.user)
        theirs = make_media(self.other)
        content = cv["content"]
        content["personal"]["photoId"] = theirs.pk
        content["experience"] = [{"id": "e1", "company": "A", "logoId": mine.pk}]
        data = self.client.patch(f"/api/cvs/{cv['id']}/", {"content": content, "version": 1}, format="json").json()
        self.assertIsNone(data["content"]["personal"]["photoId"])
        self.assertEqual(data["content"]["experience"][0]["logoId"], mine.pk)

    def test_too_many_entries_rejected(self):
        cv = self.create_cv()
        content = cv["content"]
        content["skills"] = [{"name": "x", "level": 50}] * 41
        resp = self.client.patch(f"/api/cvs/{cv['id']}/", {"content": content, "version": 1}, format="json")
        self.assertEqual(resp.status_code, 400)

    def test_duplicate_copies_content_and_design(self):
        cv = self.create_cv(design={"colorAccent": "#112233"})
        copy = self.client.post(f"/api/cvs/{cv['id']}/duplicate/").json()
        self.assertEqual(copy["design"]["colorAccent"], "#112233")
        self.assertEqual(copy["content"], cv["content"])

    def test_search_and_template_filter(self):
        self.create_cv("Backend CV", template="modern")
        self.create_cv("Frontend CV", template="minimal")
        self.assertEqual(self.client.get("/api/cvs/?search=frontend").json()["count"], 1)
        found = self.client.get("/api/cvs/?template=minimal").json()
        self.assertEqual([c["title"] for c in found["results"]], ["Frontend CV"])

    def test_template_catalogue_has_ten_entries_with_availability(self):
        catalogue = self.client.get("/api/cv-templates/").json()
        self.assertEqual(len(catalogue), 10)
        self.assertEqual(sum(1 for t in catalogue if t["available"]), 10)

    def test_schema_normalises_prototype_style_empty_input(self):
        clean = normalize_content(None, lambda _: False)
        self.assertEqual(clean, empty_content())

    def test_revision_history_and_restore(self):
        cv = self.create_cv("First title")
        self.client.patch(f"/api/cvs/{cv['id']}/", {"title": "Second title", "version": 1}, format="json")
        revisions = self.client.get(f"/api/cvs/{cv['id']}/revisions/").json()
        self.assertEqual([item["version"] for item in revisions], [2, 1])
        first = next(item for item in revisions if item["version"] == 1)
        restored = self.client.post(f"/api/cvs/{cv['id']}/restore-revision/", {"revision_id": first["id"]}, format="json")
        self.assertEqual(restored.status_code, 200, restored.data)
        self.assertEqual(restored.json()["title"], "First title")
        self.assertEqual(restored.json()["version"], 3)
        self.assertEqual(self.client.get(f"/api/cvs/{cv['id']}/revisions/").json()[0]["version"], 3)

    def test_soft_delete_trash_restore_and_permanent_delete(self):
        cv = self.create_cv("Trash me")
        self.assertEqual(self.client.delete(f"/api/cvs/{cv['id']}/").status_code, 204)
        self.assertEqual(self.client.get(f"/api/cvs/{cv['id']}/").status_code, 404)
        trash = self.client.get("/api/cvs/trash/").json()
        self.assertEqual([item["id"] for item in trash], [cv["id"]])
        restored = self.client.post(f"/api/cvs/{cv['id']}/restore/")
        self.assertEqual(restored.status_code, 200)
        self.assertIsNone(restored.json()["deleted_at"])
        self.client.delete(f"/api/cvs/{cv['id']}/")
        self.assertEqual(self.client.delete(f"/api/cvs/{cv['id']}/permanent/").status_code, 204)
        self.assertFalse(CVDocument.objects.filter(pk=cv["id"]).exists())

    def test_section_layout_is_normalised(self):
        cv = self.create_cv()
        content = cv["content"]
        content["sectionOrder"] = ["projects", "experience", "projects", "invalid"]
        content["hiddenSections"] = ["references", "invalid"]
        content["sectionTitles"] = {"projects": " Seçili Projeler ", "invalid": "x"}
        response = self.client.patch(f"/api/cvs/{cv['id']}/", {"content": content, "version": 1}, format="json")
        self.assertEqual(response.status_code, 200, response.data)
        clean = response.json()["content"]
        self.assertEqual(clean["sectionOrder"][:2], ["projects", "experience"])
        self.assertEqual(len(clean["sectionOrder"]), 9)
        self.assertEqual(clean["hiddenSections"], ["references"])
        self.assertEqual(clean["sectionTitles"], {"projects": "Seçili Projeler"})


class EducationGpaTests(APITestCase):
    def test_graduation_grade_is_kept_and_trimmed(self):
        from .schema import normalize_content

        raw = empty_content()
        raw["education"] = [{"school": "Uni", "degree": "BSc", "gpa": "  3.45 / 4.00  ", "start": "2016", "end": "2020"}]
        normalized = normalize_content(raw, lambda _: False)
        self.assertEqual(normalized["education"][0]["gpa"], "3.45 / 4.00")
