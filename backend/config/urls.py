from django.contrib import admin
from django.urls import include, path

from apps.common.views import HealthView

api_patterns = [
    path("health/", HealthView.as_view(), name="health"),
    path("", include("apps.accounts.urls")),
    path("", include("apps.activity.urls")),
    path("", include("apps.resumes.urls")),
    path("", include("apps.portfolios.urls")),
    path("", include("apps.media.urls")),
    path("", include("apps.qr_codes.urls")),
]

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(api_patterns)),
]
