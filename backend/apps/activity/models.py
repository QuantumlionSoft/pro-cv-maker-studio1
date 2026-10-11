from django.conf import settings
from django.db import models


class ActivityLog(models.Model):
    """Product-management activity feed for a user (not billing or revenue analytics)."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="activity_logs")
    action = models.CharField(max_length=40)
    object_type = models.CharField(max_length=40)
    object_id = models.PositiveBigIntegerField(null=True, blank=True)
    object_title = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        indexes = [models.Index(fields=["user", "-created_at"], name="activity_user_recent_idx")]

    def __str__(self):
        return f"{self.user_id} {self.action} {self.object_type} {self.object_title}"
