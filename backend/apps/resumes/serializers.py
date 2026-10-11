from rest_framework import serializers

from apps.media.models import MediaAsset

from .models import CVDocument
from .registry import CV_AVAILABLE_TEMPLATE_IDS
from .schema import normalize_content, normalize_design

from apps.common.viewsets import OwnedDocumentViewSet  # noqa: F401  (keeps import order stable)


class CVDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CVDocument
        fields = ["id", "title", "slug", "template", "design", "content", "version", "created_at", "updated_at"]
        read_only_fields = ["id", "slug", "version", "created_at", "updated_at"]

    def validate_title(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Give the CV a name.")
        return value

    def validate_template(self, value):
        if value not in CV_AVAILABLE_TEMPLATE_IDS:
            raise serializers.ValidationError("This template is not available yet.")
        return value

    def validate_design(self, value):
        return normalize_design(value)

    def validate_content(self, value):
        user = self.context["request"].user

        def owned(media_id):
            return MediaAsset.objects.filter(owner=user, id=media_id).exists()

        return normalize_content(value, owned)
