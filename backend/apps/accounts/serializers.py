import re

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework import serializers

from apps.common.validators import validate_image_upload

from .models import Profile

User = get_user_model()
USERNAME_RE = re.compile(r"^[A-Za-z0-9_.-]+$")


def _password_errors(password, user=None):
    try:
        validate_password(password, user=user)
    except DjangoValidationError as exc:
        raise serializers.ValidationError(list(exc.messages))


class UserSerializer(serializers.ModelSerializer):
    bio = serializers.SerializerMethodField()
    has_photo = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "bio", "has_photo", "date_joined"]
        read_only_fields = ["id", "username", "date_joined"]

    def get_bio(self, user):
        profile = Profile.objects.filter(user=user).first()
        return profile.bio if profile else ""

    def get_has_photo(self, user):
        profile = Profile.objects.filter(user=user).first()
        return bool(profile and profile.photo)


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(min_length=3, max_length=150)
    email = serializers.EmailField(max_length=254)
    first_name = serializers.CharField(max_length=150, required=False, allow_blank=True, default="")
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True, default="")
    password = serializers.CharField(write_only=True, trim_whitespace=False, max_length=128)
    password_confirm = serializers.CharField(write_only=True, trim_whitespace=False, max_length=128)

    def validate_username(self, value):
        if not USERNAME_RE.match(value):
            raise serializers.ValidationError("Use letters, numbers, dots, dashes or underscores only.")
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("This username is already taken.")
        return value

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("An account with this email already exists.")
        return value.lower()

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError({"password_confirm": ["Passwords do not match."]})
        candidate = User(username=attrs["username"], email=attrs["email"])
        try:
            validate_password(attrs["password"], user=candidate)
        except DjangoValidationError as exc:
            raise serializers.ValidationError({"password": list(exc.messages)})
        return attrs

    def create(self, validated):
        return User.objects.create_user(
            username=validated["username"],
            email=validated["email"],
            password=validated["password"],
            first_name=validated.get("first_name", ""),
            last_name=validated.get("last_name", ""),
        )


class LoginSerializer(serializers.Serializer):
    identifier = serializers.CharField(max_length=254)
    password = serializers.CharField(write_only=True, trim_whitespace=False, max_length=128)


class ProfileUpdateSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    email = serializers.EmailField(max_length=254, required=False)
    bio = serializers.CharField(max_length=500, required=False, allow_blank=True)
    photo = serializers.FileField(required=False, write_only=True)
    clear_photo = serializers.BooleanField(required=False, default=False)

    def validate_email(self, value):
        user = self.context["request"].user
        if User.objects.filter(email__iexact=value).exclude(pk=user.pk).exists():
            raise serializers.ValidationError("An account with this email already exists.")
        return value.lower()

    def validate_photo(self, value):
        validate_image_upload(value)
        return value

    def update(self, user, validated):
        for field in ("first_name", "last_name", "email"):
            if field in validated:
                setattr(user, field, validated[field])
        user.save()

        profile, _ = Profile.objects.get_or_create(user=user)
        if "bio" in validated:
            profile.bio = validated["bio"]
        old_photo = profile.photo.name if profile.photo else None
        if validated.get("photo"):
            profile.photo.save(validated["photo"].name, validated["photo"], save=False)
        elif validated.get("clear_photo"):
            profile.photo = None
        profile.save()
        if old_photo and (validated.get("photo") or validated.get("clear_photo")):
            profile.photo.storage.delete(old_photo)
        return user


class PasswordChangeSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True, trim_whitespace=False)
    new_password = serializers.CharField(write_only=True, trim_whitespace=False, max_length=128)
    new_password_confirm = serializers.CharField(write_only=True, trim_whitespace=False, max_length=128)

    def validate(self, attrs):
        user = self.context["request"].user
        if not user.check_password(attrs["current_password"]):
            raise serializers.ValidationError({"current_password": ["Current password is incorrect."]})
        if attrs["new_password"] != attrs["new_password_confirm"]:
            raise serializers.ValidationError({"new_password_confirm": ["Passwords do not match."]})
        try:
            validate_password(attrs["new_password"], user=user)
        except DjangoValidationError as exc:
            raise serializers.ValidationError({"new_password": list(exc.messages)})
        return attrs


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=254)


class PasswordResetConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True, trim_whitespace=False, max_length=128)
    new_password_confirm = serializers.CharField(write_only=True, trim_whitespace=False, max_length=128)

    def validate(self, attrs):
        from django.contrib.auth.tokens import default_token_generator

        try:
            user_pk = force_str(urlsafe_base64_decode(attrs["uid"]))
            user = User.objects.get(pk=user_pk, is_active=True)
        except (User.DoesNotExist, ValueError, TypeError, OverflowError):
            raise serializers.ValidationError("This reset link is invalid or has expired.")
        if not default_token_generator.check_token(user, attrs["token"]):
            raise serializers.ValidationError("This reset link is invalid or has expired.")
        if attrs["new_password"] != attrs["new_password_confirm"]:
            raise serializers.ValidationError({"new_password_confirm": ["Passwords do not match."]})
        try:
            validate_password(attrs["new_password"], user=user)
        except DjangoValidationError as exc:
            raise serializers.ValidationError({"new_password": list(exc.messages)})
        attrs["user"] = user
        return attrs
