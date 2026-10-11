import uuid
from pathlib import PurePosixPath

from django.conf import settings
from django.db import models

from apps.common.models import TimeStampedModel

ALLOWED_EXT = {".jpg", ".jpeg", ".png", ".webp"}
PURPOSES = [("photo", "Profile photo"), ("logo", "Logo"), ("general", "General")]


def media_upload_path(instance, filename):
    """Random storage name per owner. The client filename is never used on disk."""
    ext = PurePosixPath(filename).suffix.lower()
    if ext not in ALLOWED_EXT:
        ext = ".img"
    return f"user-{instance.owner_id}/{uuid.uuid4().hex}{ext}"


class MediaAsset(TimeStampedModel):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="media_assets")
    file = models.FileField(upload_to=media_upload_path, max_length=255)
    purpose = models.CharField(max_length=20, choices=PURPOSES, default="general")
    content_type = models.CharField(max_length=40)
    size_bytes = models.PositiveIntegerField()
    width = models.PositiveIntegerField()
    height = models.PositiveIntegerField()
    original_name = models.CharField(max_length=120, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["owner", "-created_at"], name="media_owner_recent_idx")]
