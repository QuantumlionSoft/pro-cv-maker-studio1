from io import BytesIO

import qrcode
import qrcode.image.svg
from django.http import HttpResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

MAX_DATA_LENGTH = 500
LEVELS = {"L": qrcode.constants.ERROR_CORRECT_L, "M": qrcode.constants.ERROR_CORRECT_M,
          "Q": qrcode.constants.ERROR_CORRECT_Q, "H": qrcode.constants.ERROR_CORRECT_H}


class QrSvgView(APIView):
    """Generates a QR code locally as SVG. No third-party QR service is contacted.

    GET /api/qr/?data=<text>&ec=M
    The QR content is only encoded, never fetched or executed.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = request.query_params.get("data", "")
        ec = request.query_params.get("ec", "M").upper()
        if not data.strip():
            return Response({"error": {"code": "invalid", "message": "data is required.", "fields": {"data": ["Required."]}}}, status=400)
        if len(data) > MAX_DATA_LENGTH:
            return Response({"error": {"code": "invalid", "message": "data is too long.", "fields": {"data": [f"At most {MAX_DATA_LENGTH} characters."]}}}, status=400)
        if ec not in LEVELS:
            return Response({"error": {"code": "invalid", "message": "ec must be L, M, Q or H.", "fields": {"ec": ["Invalid level."]}}}, status=400)

        qr = qrcode.QRCode(error_correction=LEVELS[ec], box_size=10, border=2)
        qr.add_data(data)
        qr.make(fit=True)
        image = qr.make_image(image_factory=qrcode.image.svg.SvgPathImage)
        buffer = BytesIO()
        image.save(buffer)
        response = HttpResponse(buffer.getvalue(), content_type="image/svg+xml")
        response["Cache-Control"] = "private, max-age=3600"
        response["X-Content-Type-Options"] = "nosniff"
        return response
