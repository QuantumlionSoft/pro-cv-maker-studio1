from django.urls import path
from rest_framework.routers import SimpleRouter

from . import views

router = SimpleRouter(trailing_slash=True)
router.register("portfolios", views.PortfolioDocumentViewSet, basename="portfolio")

urlpatterns = [
    path("portfolio-templates/", views.PortfolioTemplateListView.as_view(), name="portfolio-templates"),
] + router.urls
