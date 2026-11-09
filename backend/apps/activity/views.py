from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.portfolios.models import PortfolioDocument
from apps.resumes.models import CVDocument

from .models import ActivityLog
from .serializers import ActivityLogSerializer

RECENT_DOCUMENTS = 8


class DashboardView(APIView):
    """Summary for the signed-in user. Only counts of documents they own."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        cvs = CVDocument.objects.filter(owner=user, deleted_at__isnull=True)
        portfolios = PortfolioDocument.objects.filter(owner=user)

        recent = []
        for kind, qs, path in (("cv", cvs, "/cvs"), ("portfolio", portfolios, "/portfolios")):
            for doc in qs.order_by("-updated_at")[:RECENT_DOCUMENTS]:
                recent.append(
                    {
                        "kind": kind,
                        "id": doc.pk,
                        "title": doc.title,
                        "updated_at": doc.updated_at,
                        "route": f"{path}/{doc.pk}",
                    }
                )
        recent.sort(key=lambda item: item["updated_at"], reverse=True)

        activity = ActivityLog.objects.filter(user=user)[:10]
        return Response(
            {
                "counts": {
                    "cvs": cvs.count(),
                    "portfolios": portfolios.count(),
                },
                "recent_documents": recent[:RECENT_DOCUMENTS],
                "recent_activity": ActivityLogSerializer(activity, many=True).data,
            }
        )


class ActivityListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ActivityLogSerializer

    def get_queryset(self):
        return ActivityLog.objects.filter(user=self.request.user)
