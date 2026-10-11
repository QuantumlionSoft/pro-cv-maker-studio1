from django.conf import settings
from django.contrib.auth import authenticate, get_user_model, login, logout, update_session_auth_hash
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Q
from django.http import FileResponse, Http404
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.middleware.csrf import get_token
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from apps.activity.services import log_activity

from .models import PHOTO_EXTENSIONS, Profile
from .serializers import (
    LoginSerializer,
    PasswordChangeSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    ProfileUpdateSerializer,
    RegisterSerializer,
    UserSerializer,
)

User = get_user_model()
BACKEND = "django.contrib.auth.backends.ModelBackend"
PHOTO_MIME = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".webp": "image/webp"}


class AuthScopedAPIView(APIView):
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth"


class CsrfView(APIView):
    """Sets the CSRF cookie. The SPA calls this before any unsafe request."""

    permission_classes = [AllowAny]

    def get(self, request):
        get_token(request)  # marks the CSRF cookie for (re)issue on the response
        return Response({"detail": "CSRF cookie set."})


class RegisterView(AuthScopedAPIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        login(request, user, backend=BACKEND)
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


class LoginView(AuthScopedAPIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        identifier = serializer.validated_data["identifier"].strip()
        password = serializer.validated_data["password"]
        candidate = User.objects.filter(Q(username__iexact=identifier) | Q(email__iexact=identifier)).first()
        user = authenticate(request, username=candidate.username, password=password) if candidate else None
        if user is None or not user.is_active:
            # Same message for unknown user and wrong password: avoids account enumeration.
            raise ValidationError("Invalid username/email or password.")
        login(request, user, backend=BACKEND)  # cycles the session key
        return Response(UserSerializer(user).data)


class LogoutView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        response = Response(UserSerializer(request.user).data)
        response["Cache-Control"] = "no-store"
        return response


class PasswordChangeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data["new_password"])
        request.user.save()
        update_session_auth_hash(request, request.user)  # keep this session, drop others
        log_activity(request.user, "password_changed", "account", title="Password changed")
        return Response({"detail": "Your password has been changed."})


class PasswordResetRequestView(AuthScopedAPIView):
    """Local-development reset. The link is sent through EMAIL_BACKEND
    (console by default, so it appears in the backend terminal)."""

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.filter(email__iexact=serializer.validated_data["email"], is_active=True).first()
        if user:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            link = f"{settings.PASSWORD_RESET_FRONTEND_URL}?uid={uid}&token={token}"
            send_mail(
                "Reset your Pro CV Maker Studio password",
                f"Use this link to choose a new password (valid for a limited time):\n\n{link}\n\n"
                "If you did not request this, you can ignore this email.",
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
            )
        # Generic response regardless of whether the account exists.
        return Response({"detail": "If an account exists for that email, a reset link has been sent."})


class PasswordResetConfirmView(AuthScopedAPIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        user.set_password(serializer.validated_data["new_password"])
        user.save()
        return Response({"detail": "Your password has been reset. You can now sign in."})


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def get(self, request):
        return Response(UserSerializer(request.user).data)

    def patch(self, request):
        serializer = ProfileUpdateSerializer(data=request.data, context={"request": request}, partial=True)
        serializer.is_valid(raise_exception=True)
        user = serializer.update(request.user, serializer.validated_data)
        log_activity(request.user, "updated", "account", title="Profile")
        return Response(UserSerializer(user).data)


class ProfilePhotoView(APIView):
    """Serves the signed-in user's own photo only. Uploads are never publicly reachable."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile = Profile.objects.filter(user=request.user).first()
        if not profile or not profile.photo:
            raise Http404
        ext = "." + profile.photo.name.rsplit(".", 1)[-1].lower() if "." in profile.photo.name else ""
        if ext not in PHOTO_EXTENSIONS:
            raise Http404
        response = FileResponse(profile.photo.open("rb"), content_type=PHOTO_MIME[ext])
        response["Cache-Control"] = "private, max-age=300"
        return response
