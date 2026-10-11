from django.contrib import admin

from .models import MediaAsset


@admin.register(MediaAsset)
class MediaAssetAdmin(admin.ModelAdmin):
    list_display = ("id", "owner", "purpose", "content_type", "size_bytes", "created_at")
    list_filter = ("purpose", "content_type")
    readonly_fields = ("created_at",)
