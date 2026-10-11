from django.urls import path

from . import views

urlpatterns = [
    path("media/", views.MediaListUploadView.as_view(), name="media-list"),
    path("media/<int:pk>/", views.MediaDetailView.as_view(), name="media-detail"),
    path("media/<int:pk>/file/", views.MediaFileView.as_view(), name="media-file"),
]
