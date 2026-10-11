from django.contrib import admin

from .models import PortfolioDocument


@admin.register(PortfolioDocument)
class PortfolioDocumentAdmin(admin.ModelAdmin):
    list_display = ("title", "owner", "template", "version", "updated_at")
    list_filter = ("template",)
    search_fields = ("title", "owner__username")
    readonly_fields = ("slug", "version", "created_at", "updated_at")
