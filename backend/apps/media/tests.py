import shutil
import tempfile
from io import BytesIO

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from PIL import Image
from rest_framework.test import APITestCase

from .models import MediaAsset

User = get_user_model()


def png_bytes(size=(20, 20)):
    buf = BytesIO()
    Image.new("RGB", size, (30, 90, 200)).save(buf, format="PNG")
    return buf.getvalue()


class MediaTests(APITestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.override = override_settings(MEDIA_ROOT=self.tmp)
        self.override.enable()
        self.user = User.objects.create_user("ada", "ada@example.com", "Sturdy-passphrase-42")
        self.other = User.objects.create_user("eve", "eve@example.com", "Sturdy-passphrase-42")
        self.client.force_login(self.user)

    def tearDown(self):
        self.override.disable()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def upload(self, name="../../evil name.png", data=None, purpose="logo"):
        f = SimpleUploadedFile(name, data or png_bytes(), content_type="image/png")
        return self.client.post("/api/media/", {"file": f, "purpose": purpose}, format="multipart")

    def test_upload_stores_random_name_and_reports_dimensions(self):
        resp = self.upload()
        self.assertEqual(resp.status_code, 201, resp.data)
        body = resp.json()
        self.assertEqual((body["width"], body["height"]), (20, 20))
        asset = MediaAsset.objects.get(pk=body["id"])
        self.assertNotIn("evil", asset.file.name)  # client filename never reaches disk
        self.assertNotIn("..", asset.file.name)
        self.assertEqual(asset.owner, self.user)

    def test_owner_can_fetch_file_and_others_get_404(self):
        asset_id = self.upload().json()["id"]
        ok = self.client.get(f"/api/media/{asset_id}/file/")
        self.assertEqual(ok.status_code, 200)
        self.assertEqual(ok["Content-Type"], "image/png")
        self.assertEqual(ok["X-Content-Type-Options"], "nosniff")
        self.client.force_login(self.other)
        self.assertEqual(self.client.get(f"/api/media/{asset_id}/file/").status_code, 404)
        self.assertEqual(self.client.delete(f"/api/media/{asset_id}/").status_code, 404)

    def test_fake_image_and_wrong_extension_rejected(self):
        resp = self.client.post("/api/media/", {"file": SimpleUploadedFile("x.png", b"<html>", content_type="image/png")}, format="multipart")
        self.assertEqual(resp.status_code, 400)
        resp = self.client.post("/api/media/", {"file": SimpleUploadedFile("x.svg", png_bytes(), content_type="image/svg+xml")}, format="multipart")
        self.assertEqual(resp.status_code, 400)

    def test_delete_removes_row(self):
        asset_id = self.upload().json()["id"]
        self.assertEqual(self.client.delete(f"/api/media/{asset_id}/").status_code, 204)
        self.assertFalse(MediaAsset.objects.filter(pk=asset_id).exists())

    def test_unauthenticated_access_denied(self):
        self.client.logout()
        self.assertIn(self.client.get("/api/media/").status_code, (401, 403))


class QrTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user("ada", "ada@example.com", "Sturdy-passphrase-42")
        self.client.force_login(self.user)

    def test_generates_local_svg(self):
        resp = self.client.get("/api/qr/", {"data": "https://www.linkedin.com/in/example"})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp["Content-Type"], "image/svg+xml")
        self.assertIn(b"<svg", resp.content)

    def test_different_data_gives_different_codes(self):
        a = self.client.get("/api/qr/", {"data": "https://a.example"}).content
        b = self.client.get("/api/qr/", {"data": "https://b.example/long/path"}).content
        self.assertNotEqual(a, b)

    def test_validation(self):
        self.assertEqual(self.client.get("/api/qr/", {"data": "   "}).status_code, 400)
        self.assertEqual(self.client.get("/api/qr/", {"data": "x" * 501}).status_code, 400)
        self.assertEqual(self.client.get("/api/qr/", {"data": "x", "ec": "Z"}).status_code, 400)

    def test_requires_authentication(self):
        self.client.logout()
        self.assertIn(self.client.get("/api/qr/", {"data": "x"}).status_code, (401, 403))
