from rest_framework import serializers

from .models import PURPOSES, MediaAsset


class MediaAssetSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = MediaAsset
        fields = ["id", "purpose", "content_type", "size_bytes", "width", "height", "original_name", "url", "created_at"]
        read_only_fields = fields

    def get_url(self, asset):
        return f"/api/media/{asset.pk}/file/"


class MediaUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
    purpose = serializers.ChoiceField(choices=[p for p, _ in PURPOSES], default="general")
