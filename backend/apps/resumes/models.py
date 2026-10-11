from django.db import models

from apps.common.models import OwnedDocument

from .registry import CV_TEMPLATE_IDS
from .schema import default_design, empty_content


class CVDocument(OwnedDocument):
    """A CV document shell.

    `content` is the versioned CV document (see schema.py); `design` holds visual settings.
    Both are validated by the serializer before they reach the database.
    """

    template = models.CharField(max_length=40, default="modern", choices=[(t, t) for t in sorted(CV_TEMPLATE_IDS)])
    design = models.JSONField(default=default_design, blank=True)
    content = models.JSONField(default=empty_content, blank=True)

    class Meta(OwnedDocument.Meta):
        verbose_name = "CV document"
        verbose_name_plural = "CV documents"
