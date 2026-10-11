import shutil
import tempfile
from io import BytesIO

from django.contrib.auth import get_user_model
from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from PIL import Image
from rest_framework.test import APITestCase, APIClient

from .models import Profile

User = get_user_model()
PASSWORD = "Sturdy-passphrase-42"


def make_image_bytes(fmt="PNG", size=(16, 16)):
    buf = BytesIO()
    Image.new("RGB", size, (200, 30, 30)).save(buf, format=fmt)
    return buf.getvalue()


class AuthTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user("ada", "ada@example.com", PASSWORD)

    def test_csrf_cookie_endpoint_sets_cookie(self):
        response = self.client.get("/api/auth/csrf/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("csrftoken", response.cookies)

    def test_register_creates_user_profile_and_logs_in(self):
        client = APIClient(enforce_csrf_checks=False)
        response = client.post(
            "/api/auth/register/",
            {"username": "grace", "email": "Grace@Example.com", "password": PASSWORD, "password_confirm": PASSWORD},
            format="json",
        )
        self.assertEqual(response.status_code, 201, response.data)
        user = User.objects.get(username="grace")
        self.assertEqual(user.email, "grace@example.com")
        self.assertTrue(user.check_password(PASSWORD))
        self.assertNotEqual(user.password, PASSWORD)  # hashed, never plaintext
        self.assertTrue(Profile.objects.filter(user=user).exists())
        self.assertTrue(client.get("/api/auth/me/").json()["username"] == "grace")

    def test_register_rejects_mismatch_weak_and_duplicate(self):
        client = APIClient()
        resp = client.post("/api/auth/register/", {"username": "bob", "email": "bob@example.com", "password": PASSWORD, "password_confirm": "other"}, format="json")
        self.assertEqual(resp.status_code, 400)
        self.assertIn("password_confirm", resp.json()["error"]["fields"])

        resp = client.post("/api/auth/register/", {"username": "bob", "email": "bob@example.com", "password": "short", "password_confirm": "short"}, format="json")
        self.assertEqual(resp.status_code, 400)
        self.assertIn("password", resp.json()["error"]["fields"])

        resp = client.post("/api/auth/register/", {"username": "ada", "email": "new@example.com", "password": PASSWORD, "password_confirm": PASSWORD}, format="json")
        self.assertIn("username", resp.json()["error"]["fields"])

        resp = client.post("/api/auth/register/", {"username": "bob2", "email": "ADA@example.com", "password": PASSWORD, "password_confirm": PASSWORD}, format="json")
        self.assertIn("email", resp.json()["error"]["fields"])

    def test_login_accepts_username_or_email_and_generic_failure(self):
        client = APIClient()
        self.assertEqual(client.post("/api/auth/login/", {"identifier": "ada", "password": PASSWORD}, format="json").status_code, 200)
        client.post("/api/auth/logout/")
        self.assertEqual(client.post("/api/auth/login/", {"identifier": "ADA@example.com", "password": PASSWORD}, format="json").status_code, 200)

        bad_pw = client.post("/api/auth/login/", {"identifier": "ada", "password": "wrong"}, format="json")
        unknown = client.post("/api/auth/login/", {"identifier": "nobody", "password": "wrong"}, format="json")
        self.assertEqual(bad_pw.status_code, 400)
        self.assertEqual(bad_pw.json()["error"]["message"], unknown.json()["error"]["message"])

    def test_protected_endpoints_require_authentication(self):
        for url in ["/api/auth/me/", "/api/cvs/", "/api/portfolios/", "/api/dashboard/", "/api/profile/"]:
            self.assertIn(self.client.get(url).status_code, (401, 403), url)

    def test_logout_ends_session(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.get("/api/auth/me/").status_code, 200)
        self.client.post("/api/auth/logout/")
        self.assertIn(self.client.get("/api/auth/me/").status_code, (401, 403))

    def test_unsafe_requests_need_csrf_token(self):
        """Login/logout POSTs without a CSRF token must be rejected (login-CSRF protection)."""
        client = APIClient(enforce_csrf_checks=True)
        resp = client.post("/api/auth/login/", {"identifier": "ada", "password": PASSWORD}, format="json")
        self.assertEqual(resp.status_code, 403)

    def test_password_change_requires_current_password(self):
        self.client.force_login(self.user)
        bad = self.client.post("/api/auth/password/change/", {"current_password": "nope", "new_password": "Another-passphrase-9", "new_password_confirm": "Another-passphrase-9"}, format="json")
        self.assertEqual(bad.status_code, 400)
        ok = self.client.post("/api/auth/password/change/", {"current_password": PASSWORD, "new_password": "Another-passphrase-9", "new_password_confirm": "Another-passphrase-9"}, format="json")
        self.assertEqual(ok.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("Another-passphrase-9"))
        # The current session stays valid after a password change.
        self.assertEqual(self.client.get("/api/auth/me/").status_code, 200)

    def test_password_reset_flow_uses_local_email_and_invalidates_token(self):
        client = APIClient()
        resp = client.post("/api/auth/password-reset/", {"email": "nobody@example.com"}, format="json")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(mail.outbox), 0)  # generic response, no email for unknown accounts

        client.post("/api/auth/password-reset/", {"email": "ada@example.com"}, format="json")
        self.assertEqual(len(mail.outbox), 1)
        body = mail.outbox[0].body
        link = [line for line in body.splitlines() if "uid=" in line][0].strip()
        query = dict(part.split("=", 1) for part in link.split("?", 1)[1].split("&"))

        new_pw = "Reset-passphrase-77"
        done = client.post("/api/auth/password-reset/confirm/", {"uid": query["uid"], "token": query["token"], "new_password": new_pw, "new_password_confirm": new_pw}, format="json")
        self.assertEqual(done.status_code, 200, done.data)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(new_pw))

        reused = client.post("/api/auth/password-reset/confirm/", {"uid": query["uid"], "token": query["token"], "new_password": "Third-passphrase-88", "new_password_confirm": "Third-passphrase-88"}, format="json")
        self.assertEqual(reused.status_code, 400)

    def test_password_reset_rejects_bad_token(self):
        resp = APIClient().post("/api/auth/password-reset/confirm/", {"uid": "MQ", "token": "bad", "new_password": PASSWORD, "new_password_confirm": PASSWORD}, format="json")
        self.assertEqual(resp.status_code, 400)


class ProfileTests(APITestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.override = override_settings(MEDIA_ROOT=self.tmp)
        self.override.enable()
        self.user = User.objects.create_user("ada", "ada@example.com", PASSWORD)
        self.client.force_login(self.user)

    def tearDown(self):
        self.override.disable()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_update_profile_fields(self):
        resp = self.client.patch("/api/profile/", {"first_name": "Ada", "bio": "Engineer"}, format="json")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["first_name"], "Ada")
        self.assertEqual(resp.json()["bio"], "Engineer")

    def test_upload_valid_photo_and_serve_only_to_owner(self):
        photo = SimpleUploadedFile("me.png", make_image_bytes("PNG"), content_type="image/png")
        resp = self.client.patch("/api/profile/", {"photo": photo}, format="multipart")
        self.assertEqual(resp.status_code, 200, resp.data)
        self.assertTrue(resp.json()["has_photo"])
        served = self.client.get("/api/profile/photo/")
        self.assertEqual(served.status_code, 200)
        self.assertEqual(served["Content-Type"], "image/png")

        other = APIClient()
        User.objects.create_user("eve", "eve@example.com", PASSWORD)
        other.force_login(User.objects.get(username="eve"))
        self.assertEqual(other.get("/api/profile/photo/").status_code, 404)

    def test_rejects_fake_image_with_image_extension(self):
        fake = SimpleUploadedFile("evil.png", b"<script>alert(1)</script>", content_type="image/png")
        resp = self.client.patch("/api/profile/", {"photo": fake}, format="multipart")
        self.assertEqual(resp.status_code, 400)
        self.assertIn("photo", resp.json()["error"]["fields"])

    def test_rejects_disallowed_extension_even_if_valid_image(self):
        gif = SimpleUploadedFile("me.gif", make_image_bytes("PNG"), content_type="image/gif")
        resp = self.client.patch("/api/profile/", {"photo": gif}, format="multipart")
        self.assertEqual(resp.status_code, 400)

    @override_settings(MAX_IMAGE_UPLOAD_BYTES=100)
    def test_rejects_oversized_upload(self):
        big = SimpleUploadedFile("big.png", make_image_bytes("PNG", (200, 200)), content_type="image/png")
        resp = self.client.patch("/api/profile/", {"photo": big}, format="multipart")
        self.assertEqual(resp.status_code, 400)
        self.assertIn("too large", resp.json()["error"]["fields"]["photo"][0])

    def test_clear_photo(self):
        photo = SimpleUploadedFile("me.jpg", make_image_bytes("JPEG"), content_type="image/jpeg")
        self.client.patch("/api/profile/", {"photo": photo}, format="multipart")
        resp = self.client.patch("/api/profile/", {"clear_photo": True}, format="json")
        self.assertFalse(resp.json()["has_photo"])
        self.assertEqual(self.client.get("/api/profile/photo/").status_code, 404)
