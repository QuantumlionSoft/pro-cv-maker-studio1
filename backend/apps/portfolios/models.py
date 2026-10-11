from django.db import models

from apps.common.models import OwnedDocument

from .registry import PORTFOLIO_TEMPLATE_IDS


class PortfolioDocument(OwnedDocument):
    """A portfolio shell. Content blocks are added in Phase 4 as a versioned
    block structure; `theme` holds only visual settings."""

    template = models.CharField(
        max_length=40, default="general", choices=[(t, t) for t in sorted(PORTFOLIO_TEMPLATE_IDS)]
    )
    theme = models.JSONField(default=dict, blank=True)

    class Meta(OwnedDocument.Meta):
        verbose_name = "portfolio document"
        verbose_name_plural = "portfolio documents"
