from django.http import FileResponse, Http404
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import MediaAsset
from .serializers import MediaAssetSerializer, MediaUploadSerializer
from .services import store_image


class MediaListUploadView(APIView):
    """GET: the caller's own assets. POST: upload one image (multipart field `file`)."""

    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request):
        assets = MediaAsset.objects.filter(owner=request.user)[:100]
        return Response(MediaAssetSerializer(assets, many=True).data)

    def post(self, request):
        serializer = MediaUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        asset = store_image(request.user, serializer.validated_data["file"], serializer.validated_data["purpose"])
        return Response(MediaAssetSerializer(asset).data, status=status.HTTP_201_CREATED)


class MediaDetailView(APIView):
    """Owner-only. Other users get 404 for every ID that is not theirs."""

    permission_classes = [IsAuthenticated]

    def _get_asset(self, request, pk):
        try:
            return MediaAsset.objects.get(pk=pk, owner=request.user)
        except MediaAsset.DoesNotExist:
            raise Http404

    def delete(self, request, pk):
        asset = self._get_asset(request, pk)
        asset.file.delete(save=False)
        asset.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MediaFileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            asset = MediaAsset.objects.get(pk=pk, owner=request.user)
        except MediaAsset.DoesNotExist:
            raise Http404
        response = FileResponse(asset.file.open("rb"), content_type=asset.content_type)
        response["Cache-Control"] = "private, max-age=300"
        response["X-Content-Type-Options"] = "nosniff"
        return response
