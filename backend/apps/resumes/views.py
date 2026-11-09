from django.db import transaction
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.activity.services import log_activity
from apps.common.viewsets import OwnedDocumentViewSet

from .models import CVDocument, CVRevision, record_revision
from .registry import CV_TEMPLATES
from .serializers import CVDocumentSerializer, CVRevisionSerializer


class CVDocumentViewSet(OwnedDocumentViewSet):
    model = CVDocument
    serializer_class = CVDocumentSerializer
    activity_type = "cv"
    duplicate_fields = ("template", "design", "content")
    filter_fields = ("template",)

    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)

    def perform_create(self, serializer):
        super().perform_create(serializer)
        record_revision(serializer.instance)

    def perform_update(self, serializer):
        super().perform_update(serializer)
        record_revision(serializer.instance)

    def perform_destroy(self, instance):
        """Move to trash; permanent deletion is deliberately a separate action."""
        log_activity(self.request.user, "deleted", self.activity_type, instance)
        instance.deleted_at = timezone.now()
        instance.version += 1
        instance.save(update_fields=["deleted_at", "version", "updated_at"])

    def get_trash_object(self):
        from django.shortcuts import get_object_or_404
        return get_object_or_404(CVDocument, owner=self.request.user, pk=self.kwargs["pk"], deleted_at__isnull=False)

    @action(detail=False, methods=["get"])
    def trash(self, request):
        queryset = CVDocument.objects.filter(owner=request.user, deleted_at__isnull=False).order_by("-deleted_at")
        return Response(self.get_serializer(queryset, many=True).data)

    @action(detail=True, methods=["post"])
    def restore(self, request, pk=None):
        document = self.get_trash_object()
        document.deleted_at = None
        document.version += 1
        document.save(update_fields=["deleted_at", "version", "updated_at"])
        record_revision(document)
        log_activity(request.user, "updated", self.activity_type, document, title=f"{document.title} (restored)")
        return Response(self.get_serializer(document).data)

    @action(detail=True, methods=["delete"])
    def permanent(self, request, pk=None):
        document = self.get_trash_object()
        document.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["get"])
    def revisions(self, request, pk=None):
        document = self.get_object()
        revisions = CVRevision.objects.filter(document=document)[:20]
        return Response(CVRevisionSerializer(revisions, many=True).data)

    @action(detail=True, methods=["post"], url_path="restore-revision")
    def restore_revision(self, request, pk=None):
        document = self.get_object()
        try:
            revision_id = int(request.data.get("revision_id"))
        except (TypeError, ValueError):
            return Response({"error": {"message": "Geçerli bir sürüm seçin."}}, status=status.HTTP_400_BAD_REQUEST)
        try:
            revision = CVRevision.objects.get(document=document, pk=revision_id)
        except CVRevision.DoesNotExist:
            return Response({"error": {"message": "Sürüm bulunamadı."}}, status=status.HTTP_404_NOT_FOUND)
        with transaction.atomic():
            document.title = revision.title
            document.template = revision.template
            document.design = revision.design
            document.content = revision.content
            document.version += 1
            document.save()
            record_revision(document)
        log_activity(request.user, "updated", self.activity_type, document, title=f"{document.title} (v{revision.version} restored)")
        return Response(self.get_serializer(document).data)


class CVTemplateListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def list(self, request, *args, **kwargs):
        return Response(CV_TEMPLATES)
