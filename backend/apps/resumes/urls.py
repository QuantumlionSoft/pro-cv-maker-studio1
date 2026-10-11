from django.urls import path
from rest_framework.routers import SimpleRouter

from . import views

router = SimpleRouter(trailing_slash=True)
router.register("cvs", views.CVDocumentViewSet, basename="cv")

urlpatterns = [
    path("cv-templates/", views.CVTemplateListView.as_view(), name="cv-templates"),
] + router.urls
