from django.conf import settings
from django.db import models
from django.utils.text import slugify


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        abstract = True


def unique_slug_for_owner(model, owner, title, exclude_pk=None):
    base = slugify(title)[:60] or "untitled"
    slug, n = base, 2
    qs = model.objects.filter(owner=owner)
    if exclude_pk is not None:
        qs = qs.exclude(pk=exclude_pk)
    while qs.filter(slug=slug).exists():
        slug = f"{base}-{n}"
        n += 1
    return slug


class OwnedDocument(TimeStampedModel):
    """Base for user-owned documents (CVs, portfolios).

    `version` is incremented on every successful save and is used for optimistic
    concurrency: a client that saves with a stale version receives HTTP 409.
    """

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="%(class)ss",
    )
    title = models.CharField(max_length=160)
    slug = models.SlugField(max_length=180, blank=True)
    version = models.PositiveIntegerField(default=1)

    class Meta:
        abstract = True
        ordering = ["-updated_at"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug_for_owner(type(self), self.owner, self.title, exclude_pk=self.pk)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
