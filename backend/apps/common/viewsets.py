from copy import deepcopy

from django.db import transaction
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.activity.services import log_activity

from .exceptions import ConflictError


class OwnedDocumentViewSet(viewsets.ModelViewSet):
    """CRUD for user-owned documents.

    Ownership is enforced on the server: every queryset is filtered by the
    authenticated user, so another user's object ID simply returns 404.
    Clients never supply an owner.
    """

    model = None
    activity_type = None
    duplicate_fields = ()
    filter_fields = ()  # exact-match query params, e.g. ?template=modern
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["title"]
    ordering_fields = ["updated_at", "created_at", "title"]
    ordering = ["-updated_at"]

    def get_queryset(self):
        queryset = self.model.objects.filter(owner=self.request.user)
        for field in self.filter_fields:
            value = self.request.query_params.get(field)
            if value:
                queryset = queryset.filter(**{field: value})
        return queryset

    def perform_create(self, serializer):
        obj = serializer.save(owner=self.request.user)
        log_activity(self.request.user, "created", self.activity_type, obj)

    def perform_update(self, serializer):
        expected = self.request.data.get("version")
        with transaction.atomic():
            locked = self.get_queryset().select_for_update().get(pk=serializer.instance.pk)
            if expected not in (None, ""):
                try:
                    expected_int = int(expected)
                except (TypeError, ValueError):
                    expected_int = None
                if expected_int != locked.version:
                    raise ConflictError()
            serializer.instance = locked
            obj = serializer.save(version=locked.version + 1)
        log_activity(self.request.user, "updated", self.activity_type, obj)

    def perform_destroy(self, instance):
        log_activity(self.request.user, "deleted", self.activity_type, instance)
        instance.delete()

    @action(detail=True, methods=["post"])
    def duplicate(self, request, pk=None):
        source = self.get_object()
        copy = self.model(owner=request.user, title=f"{source.title} (copy)"[:160])
        for field in self.duplicate_fields:
            setattr(copy, field, deepcopy(getattr(source, field)))
        copy.save()
        log_activity(request.user, "duplicated", self.activity_type, copy)
        return Response(self.get_serializer(copy).data, status=status.HTTP_201_CREATED)
