from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.common.viewsets import OwnedDocumentViewSet

from .models import CVDocument
from .registry import CV_TEMPLATES
from .serializers import CVDocumentSerializer


class CVDocumentViewSet(OwnedDocumentViewSet):
    model = CVDocument
    serializer_class = CVDocumentSerializer
    activity_type = "cv"
    duplicate_fields = ("template", "design", "content")
    filter_fields = ("template",)


class CVTemplateListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def list(self, request, *args, **kwargs):
        return Response(CV_TEMPLATES)
