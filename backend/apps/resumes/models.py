from django.db import models

from apps.common.models import OwnedDocument

from .registry import CV_TEMPLATE_IDS
from .schema import default_design, empty_content


class CVDocument(OwnedDocument):
    """A CV document shell with validated JSON content and soft-delete support."""

    template = models.CharField(max_length=40, default="modern", choices=[(t, t) for t in sorted(CV_TEMPLATE_IDS)])
    design = models.JSONField(default=default_design, blank=True)
    content = models.JSONField(default=empty_content, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True, db_index=True)

    class Meta(OwnedDocument.Meta):
        verbose_name = "CV document"
        verbose_name_plural = "CV documents"


class CVRevision(models.Model):
    """Server-side snapshot. Only the latest 20 revisions are retained per CV."""

    document = models.ForeignKey(CVDocument, on_delete=models.CASCADE, related_name="revisions")
    version = models.PositiveIntegerField()
    title = models.CharField(max_length=160)
    template = models.CharField(max_length=40)
    design = models.JSONField(default=dict)
    content = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-version", "-created_at"]
        constraints = [models.UniqueConstraint(fields=["document", "version"], name="unique_cv_revision_version")]
        verbose_name = "CV revision"
        verbose_name_plural = "CV revisions"

    def __str__(self):
        return f"{self.title} · v{self.version}"


def record_revision(document):
    """Store the current document state and prune old snapshots atomically enough for editor saves."""
    CVRevision.objects.update_or_create(
        document=document,
        version=document.version,
        defaults={
            "title": document.title,
            "template": document.template,
            "design": document.design,
            "content": document.content,
        },
    )
    stale = CVRevision.objects.filter(document=document).order_by("-version", "-created_at")[20:]
    stale_ids = [revision.pk for revision in stale]
    if stale_ids:
        CVRevision.objects.filter(pk__in=stale_ids).delete()
