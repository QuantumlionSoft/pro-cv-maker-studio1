from django.contrib import admin

from .models import ActivityLog


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ("created_at", "user", "action", "object_type", "object_title")
    list_filter = ("action", "object_type")
    search_fields = ("user__username", "object_title")
    readonly_fields = [f.name for f in ActivityLog._meta.fields]
