from django.urls import path

from . import views

urlpatterns = [path("qr/", views.QrSvgView.as_view(), name="qr-svg")]
