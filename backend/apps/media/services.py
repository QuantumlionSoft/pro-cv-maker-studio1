import os
import re

from apps.common.validators import validate_image_upload

from .models import MediaAsset

FORMAT_TO_MIME = {"JPEG": "image/jpeg", "PNG": "image/png", "WEBP": "image/webp"}
CONTROL_RE = re.compile(r"[\x00-\x1f\x7f]")


def store_image(owner, uploaded, purpose="general"):
    fmt, width, height = validate_image_upload(uploaded)
    name = CONTROL_RE.sub("", os.path.basename(uploaded.name or ""))[:120]
    return MediaAsset.objects.create(
        owner=owner,
        file=uploaded,
        purpose=purpose,
        content_type=FORMAT_TO_MIME[fmt],
        size_bytes=uploaded.size,
        width=width,
        height=height,
        original_name=name,
    )
