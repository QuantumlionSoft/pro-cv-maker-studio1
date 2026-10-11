from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.common.viewsets import OwnedDocumentViewSet

from .models import PortfolioDocument
from .registry import PORTFOLIO_TEMPLATES
from .serializers import PortfolioDocumentSerializer


class PortfolioDocumentViewSet(OwnedDocumentViewSet):
    model = PortfolioDocument
    serializer_class = PortfolioDocumentSerializer
    activity_type = "portfolio"
    duplicate_fields = ("template", "theme")
    filter_fields = ("template",)


class PortfolioTemplateListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def list(self, request, *args, **kwargs):
        return Response(PORTFOLIO_TEMPLATES)
