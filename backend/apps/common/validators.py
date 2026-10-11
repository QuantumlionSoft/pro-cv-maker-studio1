import json
from io import BytesIO

from django.conf import settings
from django.core.exceptions import ValidationError as DjangoValidationError
from PIL import Image, UnidentifiedImageError
from rest_framework.exceptions import ValidationError

ALLOWED_IMAGE_FORMATS = {"JPEG": ".jpg", "PNG": ".png", "WEBP": ".webp"}
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_IMAGE_PIXELS = 40_000_000  # guards against decompression-bomb style inputs


def validate_image_upload(uploaded):
    """Validate an uploaded image by extension, size and actual decoded content.

    The extension and the client-supplied content type are never trusted on their
    own: the bytes must decode as a JPEG, PNG or WebP image.
    """
    if uploaded.size > settings.MAX_IMAGE_UPLOAD_BYTES:
        limit_mb = settings.MAX_IMAGE_UPLOAD_BYTES // (1024 * 1024)
        raise ValidationError(f"Image is too large. The limit is {limit_mb} MB.")

    name = (uploaded.name or "").lower()
    if not any(name.endswith(ext) for ext in ALLOWED_IMAGE_EXTENSIONS):
        raise ValidationError("Unsupported file type. Use JPG, PNG or WebP.")

    data = uploaded.read()
    uploaded.seek(0)
    try:
        with Image.open(BytesIO(data)) as img:
            img.verify()
        with Image.open(BytesIO(data)) as img:
            fmt = img.format
            width, height = img.size
    except (UnidentifiedImageError, OSError, SyntaxError, Image.DecompressionBombError):
        raise ValidationError("The file is not a valid image.")

    if fmt not in ALLOWED_IMAGE_FORMATS:
        raise ValidationError("Unsupported image format. Use JPG, PNG or WebP.")
    if width * height > MAX_IMAGE_PIXELS:
        raise ValidationError("Image dimensions are too large.")
    return fmt, width, height


def validate_json_object(value, max_bytes=32 * 1024, field="data"):
    """Accept only a JSON object of bounded size (used for design/theme config)."""
    if not isinstance(value, dict):
        raise ValidationError(f"{field} must be an object.")
    try:
        encoded = json.dumps(value)
    except (TypeError, ValueError):
        raise ValidationError(f"{field} contains values that cannot be stored.")
    if len(encoded.encode("utf-8")) > max_bytes:
        raise ValidationError(f"{field} is too large.")
    return value


def model_validate(model_instance):
    """Run Django model validation and convert errors to DRF errors."""
    try:
        model_instance.full_clean()
    except DjangoValidationError as exc:
        raise ValidationError(exc.message_dict if hasattr(exc, "message_dict") else exc.messages)
