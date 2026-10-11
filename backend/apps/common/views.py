from django.db import connection
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


class HealthView(APIView):
    """Basic liveness and database diagnostics (no sensitive details)."""

    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            db_ok = True
        except Exception:  # noqa: BLE001 - diagnostic endpoint reports only a boolean
            db_ok = False
        return Response(
            {"status": "ok" if db_ok else "degraded", "database": "ok" if db_ok else "unavailable"},
            status=200 if db_ok else 503,
        )
