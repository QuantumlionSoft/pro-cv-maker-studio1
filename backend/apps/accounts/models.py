import uuid
from pathlib import PurePosixPath

from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.common.models import TimeStampedModel

PHOTO_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def profile_photo_path(instance, filename):
    """Store uploads under a random name: user-supplied filenames are never used on disk."""
    ext = PurePosixPath(filename).suffix.lower()
    if ext not in PHOTO_EXTENSIONS:
        ext = ".img"
    return f"profiles/{instance.user_id}/{uuid.uuid4().hex}{ext}"


class Profile(TimeStampedModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    bio = models.TextField(blank=True, max_length=500)
    photo = models.ImageField(upload_to=profile_photo_path, blank=True, null=True)

    def __str__(self):
        return f"Profile<{self.user_id}>"


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_profile_for_new_user(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)
