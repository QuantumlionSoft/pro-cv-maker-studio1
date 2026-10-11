from rest_framework import serializers

from apps.common.validators import validate_json_object

from .models import PortfolioDocument
from .registry import PORTFOLIO_TEMPLATE_IDS


class PortfolioDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PortfolioDocument
        fields = ["id", "title", "slug", "template", "theme", "version", "created_at", "updated_at"]
        read_only_fields = ["id", "slug", "version", "created_at", "updated_at"]

    def validate_title(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Give the portfolio a name.")
        return value

    def validate_template(self, value):
        if value not in PORTFOLIO_TEMPLATE_IDS:
            raise serializers.ValidationError("Unknown template.")
        return value

    def validate_theme(self, value):
        return validate_json_object(value, field="theme")
